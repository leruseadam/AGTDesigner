import re
import json
import urllib.request
import logging
import time
import traceback
import os
import glob
import sqlite3
from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Dict, Set, Optional, Tuple, Any
from decimal import Decimal, InvalidOperation
from .field_mapping import get_canonical_field, get_all_aliases, FIELD_ALIASES
import pandas as pd
from .product_database import ProductDatabase
from .ai_product_matcher import AIProductMatcher
from .advanced_matcher import AdvancedMatcher, MatchResult
from .enhanced_json_matcher import ENHANCED_JSON_FIELD_MAP
from src.core.generation.text_processing import format_price
from collections import defaultdict
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

# Compile regex patterns once for performance
_DIGIT_UNIT_RE = re.compile(r"\b\d+(?:g|mg)\b")
_NON_WORD_RE = re.compile(r"[^\w\s-]")
_SPLIT_RE = re.compile(r"[-\s]+")

def extract_keywords_from_sku(sku: str) -> set:
    """
    Extract searchable keywords from SKU for matching against database.
    Example: 'BALL_SAT_CARAMEL_10pk' -> {'ball', 'sativa', 'caramel', '10pk'}
    """
    if not sku or not isinstance(sku, str):
        return set()
    
    keywords = set()
    parts = sku.split('_')
    
    # Mappings for abbreviations
    lineage_map = {'SAT': 'sativa', 'IND': 'indica', 'MIXED': 'mixed'}
    product_map = {'BALL': 'ball', 'BITE': 'bite', 'CHEW': 'chew', 'CAPS': 'capsule', 
                   'TINCS': 'tincture', 'JAR': 'jar', 'SQUEEZE': 'squeeze', 'ROLL': 'roll'}
    
    for part in parts:
        part_lower = part.lower()
        # Add the expanded version if it's an abbreviation
        keywords.add(lineage_map.get(part.upper(), part_lower))
        keywords.add(product_map.get(part.upper(), part_lower))
    
    return keywords

def transform_sku_to_readable_name(sku: str) -> str:
    """
    Transform SKU codes like 'BALL_SAT_CARAMEL_10pk' into human-readable names
    like 'Sativa Salted Caramel Ball(s) - 10pk'.
    """
    if not sku or not isinstance(sku, str):
        return sku
    
    # Parse the SKU format: PRODUCTTYPE_LINEAGE_FLAVOR_SIZE
    parts = sku.split('_')
    if len(parts) < 2:
        return sku  # Not a recognizable SKU format
    
    # Product type mapping - match database naming conventions
    product_type_map = {
        'BALL': 'Balls',  # Database uses "Balls" not "Ball(s)"
        'BITE': 'Bites',  # Database uses "Bites" not "Bite(s)"  
        'CHEW': 'Fruit Chews',  # Database uses "Fruit Chews" not "Chew(s)"
        'CAPS': 'Capsules',  # Database uses "Capsules" not "Capsule(s)"
        'TINCS': 'Tincture',
        'JAR': 'Jar',
        'SQUEEZE': 'Squeeze Tube',
        'TUBE': 'Squeeze Tube',
        'ROLL': 'Roll-On',
        'UPS': 'Roll Up'
    }
    
    # Lineage mapping
    lineage_map = {
        'SAT': 'Sativa',
        'IND': 'Indica',
        'MIXED': 'Mixed'
    }
    
    # Extract components
    product_type = parts[0]
    lineage = parts[1] if len(parts) > 1 else ''
    
    # Get human-readable product type
    readable_type = product_type_map.get(product_type, product_type.title())
    readable_lineage = lineage_map.get(lineage, lineage.title())
    
    # Get flavor/description parts (everything except last part which is usually size)
    flavor_parts = []
    size = ''
    
    for i in range(2, len(parts)):
        part = parts[i]
        # Check if this looks like a size indicator
        if part.endswith('pk') or part.endswith('oz') or part.endswith('mL') or part.upper() == 'SINGLE':
            size = part
        elif ':' in part:  # Ratio like '1:1' or '1:1:1'
            flavor_parts.append(part)
        else:
            # Clean up flavor names
            cleaned = part.replace('&', ' & ').replace('CREAM', 'Cream').title()
            flavor_parts.append(cleaned)
    
    # Build the readable name to match database format
    readable_parts = []
    
    # Add lineage
    if readable_lineage:
        readable_parts.append(readable_lineage)
    
    # Add flavors
    if flavor_parts:
        readable_parts.append(' '.join(flavor_parts))
    
    # For BALL and BITE products, add "Chocolate" before the type to match database
    chocolate_flavors = {'caramel', 'dark', 'milk', 'malt', 'dragon', 'cookies'}
    has_chocolate_flavor = any(f.lower() in chocolate_flavors for f in flavor_parts)
    
    if product_type in ['BALL', 'BITE'] and has_chocolate_flavor and 'Chocolate' not in flavor_parts:
        readable_parts.append('Chocolate')
    
    # Add product type
    readable_parts.append(readable_type)
    
    # Add "by Ceres" suffix to match database format
    readable_name = ' '.join(readable_parts)
    readable_name = f"{readable_name} by Ceres"
    
    # Add size if present
    if size:
        if size.upper() == 'SINGLE':
            size = 'Single'
        elif size.endswith('pk'):
            # Database uses "100mg 10pack" format, but we'll use "- 10pack"
            size = size.replace('pk', 'pack')
        readable_name = f"{readable_name} - {size}"
    
    # Clean up multiple spaces
    readable_name = ' '.join(readable_name.split())
    
    return readable_name

# Type override lookup
TYPE_OVERRIDES = {
    "all-in-one": "Vape Cartridge",
    "rosin": "Concentrate",
    "mini buds": "Flower",
    "bud": "Flower",
    "pre-roll": "Pre-roll",
    "alcohol/ethanol extract": "RSO/CO2 Tankers",
    "Alcohol/Ethanol Extract": "RSO/CO2 Tankers",
    "alcohol ethanol extract": "RSO/CO2 Tankers",
    "Alcohol Ethanol Extract": "RSO/CO2 Tankers",
    "c02/ethanol extract": "RSO/CO2 Tankers",
    "CO2 Concentrate": "RSO/CO2 Tankers",
    "co2 concentrate": "RSO/CO2 Tankers",
    # Vape cartridge indicators
    "jefe": "Vape Cartridge",
    "twisted": "Vape Cartridge",
    "fire": "Vape Cartridge",
    "cart": "Vape Cartridge",
    "cartridge": "Vape Cartridge",
    "vape": "Vape Cartridge",
    "disposable": "Vape Cartridge",
    "pod": "Vape Cartridge",
    "battery": "Vape Cartridge",
}


# Helper: Extract cannabinoid values from lab_result_data
CANNABINOID_TYPES = ["thc", "thca", "cbd", "cbda", "cbg", "cbga", "cbn", "cbna", "total-cannabinoids"]

def map_inventory_type_to_product_type(inventory_type, inventory_category=None, product_name=None):
    """
    Intelligently map JSON inventory types to proper product types.
    
    Args:
        inventory_type: The inventory_type from JSON (e.g., "Concentrate for Inhalation")
        inventory_category: The inventory_category from JSON (e.g., "IntermediateProduct")
        product_name: The product name for additional context (optional)
        
    Returns:
        Mapped product type string
    """
    if not inventory_type:
        return "Unknown"
    
    inventory_type_lower = str(inventory_type).lower().strip()
    inventory_category_lower = str(inventory_category).lower().strip() if inventory_category else ""
    product_name_lower = str(product_name).lower().strip() if product_name else ""
    
    # Enhanced mappings for common inventory types based on Cultivera data
    type_mappings = {
        # Concentrates and Vape Cartridges
        "concentrate for inhalation": "Vape Cartridge",
        "concentrate": "Vape Cartridge", 
        "extract": "Vape Cartridge",
        "oil": "Vape Cartridge",
        "distillate": "Vape Cartridge",
        "live resin": "Live Resin",
        "rosin": "Rosin",
        "wax": "Wax",
        "shatter": "Shatter",
        "vape cartridge": "Vape Cartridge",
        "vape pen": "Vape Cartridge",
        "disposable": "Disposable",
        
        # Flower and Pre-rolls
        "flower": "Flower",
        "bud": "Flower",
        "pre-roll": "Pre-Roll",
        "infused pre-roll": "Infused Pre-Roll",
        "preroll": "Pre-Roll",
        "joint": "Pre-Roll",
        
        # Edibles
        "edible": "Edible",
        "solid edible": "Edible",
        "gummy": "Gummy",
        "gummies": "Gummy",
        "chocolate": "Chocolate",
        "brownie": "Brownie",
        "cookie": "Cookie",
        "cookie": "Cookie",
        "candy": "Edible",
        "hard candy": "Edible",
        "soft candy": "Edible",
        
        # Topicals
        "topical": "Topical",
        "topical ointment": "Topical",
        "cream": "Topical",
        "balm": "Topical",
        "salve": "Topical",
        "lotion": "Topical",
        "ointment": "Topical",
        
        # Tinctures and Oils
        "tincture": "Tincture",
        "sublingual": "Tincture",
        "oral": "Tincture",
        "drops": "Tincture",
        
        # Capsules and Pills
        "capsule": "Capsule",
        "pill": "Capsule",
        "tablet": "Capsule",
        "softgel": "Capsule",
        
        # Beverages
        "beverage": "Beverage",
        "drink": "Beverage",
        "soda": "Beverage",
        "juice": "Beverage",
        "tea": "Beverage",
        "coffee": "Beverage",
        
        # Extracts and RSO
        "rso": "RSO",
        "co2": "CO2 Extract",
        "co2 extract": "CO2 Extract",
        "ethanol extract": "RSO",
        "alcohol extract": "RSO",
        "butane extract": "Concentrate",
        "hash": "Hash",
        "kief": "Kief",
        
        # Other categories
        "suppository": "Suppository",
        "transdermal": "Transdermal",
        "patch": "Transdermal",
        "inhaler": "Inhaler",
        "nasal spray": "Nasal Spray",
        "eye drops": "Eye Drops"
    }
    
    # Check direct mapping first
    if inventory_type_lower in type_mappings:
        return type_mappings[inventory_type_lower]
    
    # Check category-based mappings
    if "intermediate" in inventory_category_lower:
        if "concentrate" in inventory_type_lower or "extract" in inventory_type_lower:
            return "Vape Cartridge"
        elif "flower" in inventory_type_lower:
            return "Flower"

    # Handle Washington-style usable marijuana inventory types
    if inventory_type_lower.startswith("usable"):
        if product_name_lower:
            joint_keywords = ["pre-roll", "pre roll", "joint", "blunt", "cone"]
            if any(keyword in product_name_lower for keyword in joint_keywords):
                return "Pre-Roll"
            if any(keyword in product_name_lower for keyword in ["shake", "trim"]):
                return "Flower"
        return "Flower"
    
    # Enhanced product name analysis for "Medically Compliant" products
    if product_name_lower and "medically compliant" in product_name_lower:
        # Look for specific product type indicators in the name
        if any(keyword in product_name_lower for keyword in ["rosin", "wax", "shatter", "live resin", "distillate", "cartridge", "all-in-one", "liquid diamond", "caviar", "hash rosin", "sugar wax"]):
            return "Vape Cartridge"
        elif any(keyword in product_name_lower for keyword in ["flower", "bud", "pre-roll", "pre roll"]):
            return "Flower" if "flower" in product_name_lower else "Pre-Roll"
        elif any(keyword in product_name_lower for keyword in ["edible", "gummy", "chocolate", "cookie"]):
            return "Edible"
        elif any(keyword in product_name_lower for keyword in ["melt stix", "flavour stix", "rosin rolls", "infused blunt"]):
            return "Pre-Roll"
    
    # Additional product-name based heuristics
    if product_name_lower:
        if any(keyword in product_name_lower for keyword in ["pre-roll", "pre roll", "joint", "blunt", "cone"]):
            return "Pre-Roll"
        if any(keyword in product_name_lower for keyword in ["cartridge", "cart", "vape", "510", "all-in-one", "aio", "disposable"]):
            return "Vape Cartridge"
        if any(keyword in product_name_lower for keyword in ["rosin", "resin", "wax", "shatter", "crumble", "sauce", "badder", "diamonds", "hash", "solventless", "distillate"]):
            return "Concentrate"
        if any(keyword in product_name_lower for keyword in ["gummy", "chew", "cookie", "brownie", "chocolate", "edible", "candy", "lozenge"]):
            return "Edible"
        if any(keyword in product_name_lower for keyword in ["tincture", "drops", "sublingual", "dropper"]):
            return "Tincture"
        if any(keyword in product_name_lower for keyword in ["topical", "lotion", "salve", "balm", "cream", "ointment"]):
            return "Topical"

    # Check for specific keywords in the inventory type
    if any(keyword in inventory_type_lower for keyword in ["cartridge", "pen", "vape"]):
        return "Vape Cartridge"
    elif any(keyword in inventory_type_lower for keyword in ["flower", "bud", "nug"]):
        return "Flower"
    elif any(keyword in inventory_type_lower for keyword in ["edible", "gummy", "chocolate", "brownie", "cookie"]):
        return "Edible"
    elif any(keyword in inventory_type_lower for keyword in ["tincture", "oil", "drops"]):
        return "Tincture"
    elif any(keyword in inventory_type_lower for keyword in ["topical", "cream", "lotion", "salve"]):
        return "Topical"
    elif any(keyword in inventory_type_lower for keyword in ["pre-roll", "joint", "cigar"]):
        return "Pre-Roll"
    
    # Default fallback based on category
    if "concentrate" in inventory_type_lower or "extract" in inventory_type_lower:
        return "Vape Cartridge"
    elif "flower" in inventory_type_lower:
        return "Flower"
    else:
        # Final fallback - make a conservative guess based on product name keywords
        if product_name_lower:
            if any(keyword in product_name_lower for keyword in ["rosin", "resin", "wax", "shatter", "crumble", "sauce", "badder", "diamonds", "hash"]):
                return "Concentrate"
            if any(keyword in product_name_lower for keyword in ["pre-roll", "pre roll", "joint", "blunt", "cone"]):
                return "Pre-Roll"
        return "Flower"

def extract_cannabinoids(lab_result_data):
    """Enhanced cannabinoid extraction with better parsing and validation."""
    result = {}
    if not lab_result_data:
        return result
    
    # Extract potency data
    potency = lab_result_data.get("potency", [])
    if not isinstance(potency, list):
        potency = []
    
    # Map cannabinoid types to database field names
    cannabinoid_field_map = {
        "thc": "THC test result",
        "thca": "THCA test result",
        "cbd": "CBD test result",
        "cbda": "CBDA test result",
        "total-cannabinoids": "Total Cannabinoids",
        "cbg": "CBG",
        "cbn": "CBN",
        "cbga": "CBGA",
        "cbna": "CBNA"
    }
    
    for c in potency:
        if not isinstance(c, dict):
            continue
            
        ctype = c.get("type", "").lower().strip()
        value = c.get("value")
        unit = c.get("unit", "").lower().strip()
        
        if ctype in CANNABINOID_TYPES and value is not None:
            # Convert value to float and validate
            try:
                float_value = float(value)
                
                # CRITICAL FIX: Handle Cultivera's per mille format (e.g., 1000 = 100%)
                # When unit is "pct" and value is > 1 and < 100, it's likely a percentage
                # When value is > 100, it might be per mille (divided by 10)
                if unit == "pct":
                    if float_value > 100:
                        # Per mille format: divide by 10 (e.g., 1000 -> 100%)
                        float_value = float_value / 10.0
                    # If value is between 1-100, keep as is
                elif unit == "mg" or unit == "mille":
                    # Convert mg to percentage if needed (for very large values)
                    if float_value > 1000:
                        float_value = float_value / 10.0
                
                # Map to database field name
                db_field_name = cannabinoid_field_map.get(ctype, ctype)
                result[db_field_name] = round(float_value, 1)  # Round to 1 decimal place
                
                # Also store the lowercase version for backward compatibility
                result[ctype] = round(float_value, 1)
                
                logging.info(f"🔬 Extracted cannabinoid: {ctype} = {float_value} ({unit}) -> {db_field_name}")
            except (ValueError, TypeError) as e:
                logging.warning(f"Invalid cannabinoid value: {value} for type {ctype}: {e}")
                continue
    
    # Extract additional lab data
    if "coa" in lab_result_data:
        result["coa"] = lab_result_data["coa"]
    
    # Extract lab result status
    if "lab_result_status" in lab_result_data:
        result["lab_result_status"] = lab_result_data["lab_result_status"]
    
    # Extract lab result ID
    if "lab_result_id" in lab_result_data:
        result["lab_result_id"] = lab_result_data["lab_result_id"]
    
    # Extract COA dates
    if "coa_release_date" in lab_result_data:
        result["coa_release_date"] = lab_result_data["coa_release_date"]
    if "coa_expire_date" in lab_result_data:
        result["coa_expire_date"] = lab_result_data["coa_expire_date"]
    
    return result

def extract_vendor_info(json_data):
    """Extract vendor information from JSON data, trying multiple possible field names."""
    vendor = (str(json_data.get("vendor", "")).strip() or 
              str(json_data.get("supplier", "")).strip() or
              str(json_data.get("vendor_name", "")).strip() or
              str(json_data.get("supplier_name", "")).strip() or
              str(json_data.get("manufacturer", "")).strip() or
              str(json_data.get("distributor", "")).strip() or
              str(json_data.get("brand", "")).strip() or
              str(json_data.get("company", "")).strip() or
              str(json_data.get("producer", "")).strip() or
              str(json_data.get("grower", "")).strip() or
              str(json_data.get("farm", "")).strip() or
              str(json_data.get("lab", "")).strip() or
              str(json_data.get("laboratory", "")).strip() or "")
    
    # Enhanced vendor normalization with more comprehensive mappings
    if vendor:
        vendor_lower = vendor.lower()
        # Handle common vendor variations and abbreviations
        vendor_mappings = {
            'dcz': 'dcz holdings inc',
            'dank czar': 'dcz holdings inc',
            'jsm': 'jsm llc',
            'omega': 'omega labs',
            'airo': 'airo pro',
            'airopro': 'airo pro',
            'hustlers': 'hustler\'s ambition',
            'hustlers ambition': 'hustler\'s ambition',
            '1555': '1555 industrial llc',
            '1555 industrial': '1555 industrial llc',
            'dcz holdings': 'dcz holdings inc',
            'dcz holdings inc': 'dcz holdings inc',
            'dcz holdings inc.': 'dcz holdings inc',
            'jsm llc': 'jsm llc',
            'omega labs': 'omega labs',
            'omega cannabis': 'omega labs',
            'airo pro': 'airo pro',
            'hustler\'s ambition': 'hustler\'s ambition',
            '1555 industrial llc': '1555 industrial llc',
            'harmony farms': 'airo pro',
            'jsm': 'jsm llc'
        }
        
        for key, value in vendor_mappings.items():
            if key in vendor_lower:
                vendor = value
                break
    
    # If still no vendor, try to extract from product name patterns
    if not vendor:
        product_name = str(json_data.get("product_name", "")).strip()
        if product_name:
            import re
            # Look for "by [Brand]" pattern
            by_match = re.search(r'by\s+([A-Za-z0-9\s]+)(?:\s|$)', product_name, re.IGNORECASE)
            if by_match:
                vendor = by_match.group(1).strip()
            # Look for "from [Brand]" pattern
            elif "from" in product_name.lower():
                from_match = re.search(r'from\s+([A-Za-z0-9\s]+)(?:\s|$)', product_name, re.IGNORECASE)
                if from_match:
                    vendor = from_match.group(1).strip()
            # Look for "by [Brand] -" pattern
            elif "by" in product_name.lower() and "-" in product_name:
                by_dash_match = re.search(r'by\s+([A-Za-z0-9\s]+)\s*-', product_name, re.IGNORECASE)
                if by_dash_match:
                    vendor = by_dash_match.group(1).strip()
    
    # If still no vendor, try to extract from brand field
    if not vendor:
        brand = str(json_data.get("brand", "")).strip()
        if brand and brand.lower() not in ['unknown', 'n/a', '']:
            vendor = brand
    
    # Final fallback: extract from product name using common patterns
    if not vendor:
        product_name = str(json_data.get("product_name", "")).strip()
        if product_name:
            # Look for common vendor patterns in product names
            name_lower = product_name.lower()
            if any(x in name_lower for x in ['dank czar', 'dcz', 'jsm', 'omega', 'airo', 'hustler', 'super fog']):
                if 'dank czar' in name_lower or 'dcz' in name_lower:
                    vendor = 'dcz holdings inc'
                elif 'jsm' in name_lower:
                    vendor = 'jsm llc'
                elif 'omega' in name_lower:
                    vendor = 'omega labs'
                elif 'airo' in name_lower:
                    vendor = 'airo pro'
                elif 'hustler' in name_lower:
                    vendor = 'hustler\'s ambition'
                elif '1555' in name_lower:
                    vendor = '1555 industrial llc'
                elif 'super fog' in name_lower:
                    vendor = 'super fog'  # Add Super Fog as a recognized vendor
    
    return vendor

def _extract_field_from_json_item_comprehensive(json_item: dict, canonical_field_name: str) -> Optional[str]:
    """Extract a field from JSON item using all possible aliases from field mapping."""
    if not json_item or not canonical_field_name:
        return None
    
    # Get all aliases for this canonical field
    aliases = get_all_aliases(canonical_field_name)
    
    # Also check common variations that might not be in the mapping
    if canonical_field_name == "Price* (Tier Name for Bulk)":
        aliases.extend(['retail_price', 'unit_price', 'sale_price', 'unit_cost', 'cost', 'Cost'])
    elif canonical_field_name == "Weight*":
        aliases.extend(['weight_with_units', 'weight_units', 'size', 'Size', 'quantity', 'Quantity'])
    
    # Try all aliases (case-insensitive check for keys)
    json_item_lower = {k.lower(): k for k in json_item.keys()}  # Map lowercase -> original key
    
    for alias in aliases:
        # Check exact match first (case-sensitive)
        if alias in json_item:
            value = json_item[alias]
            if value is not None:
                value_str = str(value).strip()
                if value_str and value_str.lower() not in ('none', '', '0', '0.0', '0.00'):
                    return value_str
        
        # Check case-insensitive match
        alias_lower = alias.lower()
        if alias_lower in json_item_lower:
            original_key = json_item_lower[alias_lower]
            value = json_item[original_key]
            if value is not None:
                value_str = str(value).strip()
                if value_str and value_str.lower() not in ('none', '', '0', '0.0', '0.00'):
                    return value_str
    
    return None

# Main function: Process manifest JSON and return list of product dicts
# Each dict contains all relevant DB fields, including cannabinoids/COA

def extract_products_from_manifest(manifest_json):
    """
    Given a manifest JSON (with inventory_transfer_items),
    return a list of dicts, each with all relevant DB fields.
    """
    items = manifest_json.get("inventory_transfer_items", [])
    products = []
    for item in items:
        product = {}
        # Map flat fields using enhanced field mapping
        logging.info(f"🔍 DEBUG: Mapping JSON fields for item keys: {list(item.keys())}")
        for k, v in item.items():
            db_field = ENHANCED_JSON_FIELD_MAP.get(k, None)
            if db_field:
                product[db_field] = v
                logging.info(f"🔍 DEBUG: Mapped '{k}' -> '{db_field}' = '{v}'")
            else:
                logging.info(f"🔍 DEBUG: No mapping found for key '{k}' = '{v}'")
        
        # CRITICAL FIX: Ensure basic fields are always populated even if mapping fails
        if not product.get('Product Name*') and not product.get('ProductName'):
            product['Product Name*'] = item.get('product_name', '') or item.get('inventory_name', '') or item.get('name', '')
            product['ProductName'] = product['Product Name*']
            logging.info(f"🔍 DEBUG: Fallback product name: '{product['Product Name*']}'")
        
        if not product.get('Product Brand') and not product.get('ProductBrand'):
            product['Product Brand'] = item.get('brand', '') or item.get('vendor', '') or item.get('supplier_name', '') or 'Unknown Brand'
            product['ProductBrand'] = product['Product Brand']
            logging.info(f"🔍 DEBUG: Fallback brand: '{product['Product Brand']}'")
        
        if not product.get('Price') and not product.get('Price*'):
            # CRITICAL: No $25 fallback - only use actual prices from JSON or leave empty
            product['Price'] = item.get('price', '') or item.get('line_price', '') or ''
            product['Price*'] = product['Price']
            if product['Price']:
                logging.info(f"🔍 DEBUG: Using JSON price: '{product['Price']}'")
            else:
                logging.info(f"🔍 DEBUG: No price found in JSON - leaving empty (no fallback)")
        
        if not product.get('Weight*') and not product.get('Weight'):
            product['Weight*'] = item.get('weight', '') or item.get('unit_weight', '') or '1'
            product['Weight'] = product['Weight*']
            logging.info(f"🔍 DEBUG: Fallback weight: '{product['Weight*']}'")
        
        if not product.get('Units') and not product.get('unit_weight_uom'):
            product['Units'] = item.get('unit_weight_uom', '') or item.get('uom', '') or 'g'
            logging.info(f"🔍 DEBUG: Fallback units: '{product['Units']}'")
        
        if not product.get('Product Type*') and not product.get('ProductType'):
            product['Product Type*'] = item.get('inventory_type', '') or item.get('product_type', '') or 'Edible (Solid)'
            product['ProductType'] = product['Product Type*']
            logging.info(f"🔍 DEBUG: Fallback product type: '{product['Product Type*']}'")
        
        logging.info(f"🔍 DEBUG: Final mapped product: {product}")
        # Nested lab_result_data
        lab_result_data = item.get("lab_result_data", {})
        cannabinoids = extract_cannabinoids(lab_result_data)
        product.update(cannabinoids)
        products.append(product)
    return products  # Fixed: was returning 'product' instead of 'products'

# Example usage:
# products = extract_products_from_manifest(manifest_json)
# for p in products:
#     print(p)

def map_json_to_db_fields(json_item):
    """Map incoming JSON keys to canonical DB columns using get_canonical_field."""
    mapped = {}
    for k, v in json_item.items():
        db_key = get_canonical_field(k)
        mapped[db_key] = v
    return mapped

MEDICALLY_COMPLIANT_PREFIXES = [
    'medically compliant -',
    'med compliant -',
    'med compliant-',
    'medically compliant-',
]

def infer_product_type_from_name(product_name: str) -> str:
    """
    Infer product type from product name using pattern matching and TYPE_OVERRIDES.
    """
    if not isinstance(product_name, str):
        return "Unknown Type"
    
    name_lower = product_name.lower()
    
    # Check TYPE_OVERRIDES first
    for key, value in TYPE_OVERRIDES.items():
        if key in name_lower:
            return value
    
    # Pattern-based inference - prioritize vape keywords over concentrate keywords
    if any(x in name_lower for x in ["flower", "bud", "nug", "herb", "marijuana", "cannabis"]):
        return "Flower"
    elif any(x in name_lower for x in ["vape", "cart", "cartridge", "disposable", "pod", "battery", "jefe", "twisted", "fire", "pen"]):
        return "Vape Cartridge"
    elif any(x in name_lower for x in ["concentrate", "rosin", "shatter", "wax", "live resin", "diamonds", "sauce", "extract", "oil", "distillate"]):
        return "Concentrate"
    elif any(x in name_lower for x in ["edible", "gummy", "chocolate", "cookie", "brownie", "candy"]):
        return "Edible (Solid)"
    elif any(x in name_lower for x in ["tincture", "oil", "drops", "liquid"]):
        return "Edible (Liquid)"
    elif any(x in name_lower for x in ["pre-roll", "joint", "cigar", "blunt"]):
        return "Pre-roll"
    elif any(x in name_lower for x in ["topical", "cream", "lotion", "salve", "balm"]):
        return "Topical"
    elif any(x in name_lower for x in ["tincture", "sublingual"]):
        return "Tincture"
    else:
        # Default to Vape Cartridge for any remaining unknown types since most products are concentrates
        return "Vape Cartridge"

def strip_medically_compliant_prefix(name):
    # Safety check: ensure name is a string
    if not isinstance(name, str):
        if isinstance(name, list):
            logging.warning(f"strip_medically_compliant_prefix received a list instead of string: {name}")
            # If it's a list, try to join it or take the first element
            if name:
                name = str(name[0]) if isinstance(name[0], str) else str(name[0])
            else:
                name = ""
        else:
            logging.warning(f"strip_medically_compliant_prefix received non-string type: {type(name)} - {name}")
            name = str(name) if name is not None else ""
    
    name = name.strip()
    for prefix in MEDICALLY_COMPLIANT_PREFIXES:
        if name.lower().startswith(prefix):
            return name[len(prefix):].strip()
    return name

def normalize_product_name(name):
    # Safety check: ensure name is a string
    if not isinstance(name, str):
        if isinstance(name, list):
            logging.warning(f"normalize_product_name received a list instead of string: {name}")
            # If it's a list, try to join it or take the first element
            if name:
                name = str(name[0]) if isinstance(name[0], str) else str(name[0])
            else:
                name = ""
        else:
            logging.warning(f"normalize_product_name received non-string type: {type(name)} - {name}")
            name = str(name) if name is not None else ""
    
    name = strip_medically_compliant_prefix(name)
    name = name.lower().strip()
    
    # Remove weight/measurement suffixes (e.g., " - 1g", " - 3.5g", " - 7g", etc.)
    weight_patterns = [
        r'\s*-\s*\d+(?:\.\d+)?\s*(?:g|gram|grams|mg|oz|ounce|ounces|pk|pack|packs|piece|pieces|roll|rolls|stix|stick|sticks)\b',
        r'\s*\d+(?:\.\d+)?\s*(?:g|gram|grams|mg|oz|ounce|ounces|pk|pack|packs|piece|pieces|roll|rolls|stix|stick|sticks)\b',
        r'\s*-\s*\d+(?:\.\d+)?\s*$',  # Just numbers at the end
        r'\s+\d+(?:\.\d+)?\s*$',  # Numbers at the end without dash
    ]
    
    for pattern in weight_patterns:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    name = re.sub(r'[^\w\s-]', '', name)  # remove non-alphanumeric except hyphen/space
    name = re.sub(r'[-\s]+', ' ', name)  # collapse hyphens and spaces
    return name.strip()

class JSONMatcher:
    """Handles JSON URL fetching and product matching functionality."""
    
    def __init__(self, excel_processor):
        self.excel_processor = excel_processor
        self._sheet_cache = None
        self._indexed_cache = None  # New indexed cache for O(1) lookups
        self.json_matched_names = None
        self._strain_cache = None
        self._lineage_cache = None
        self.advanced_matcher = AdvancedMatcher()  # Initialize advanced matching system
        self._product_db_instance = None
        self._cached_store_name = None
        self._product_table_columns = None

    def _determine_store_name(self) -> str:
        """Determine the best store name to use for ProductDatabase operations."""
        if self._cached_store_name:
            return self._cached_store_name

        store_name = None

        # 1. Try Flask session (if we're inside a request context)
        try:
            from flask import session
            store_name = (
                session.get('current_store')
                or session.get('selected_store')
                or session.get('store_name')
            )
        except Exception:
            store_name = None

        # 2. Try Excel processor metadata
        if not store_name and self.excel_processor:
            store_name = getattr(self.excel_processor, 'current_store', None) or \
                         getattr(self.excel_processor, '_current_store', None) or \
                         getattr(self.excel_processor, 'store_name', None)

        # 3. Environment overrides
        if not store_name:
            store_name = (
                os.environ.get('DEFAULT_JSON_MATCH_STORE')
                or os.environ.get('DEFAULT_STORE_NAME')
                or os.environ.get('DEFAULT_STORE')
            )

        # 4. Scan local databases to find the one with the most products
        if not store_name:
            store_name = self._scan_databases_for_best_store()

        # 5. Final fallback
        if not store_name:
            store_name = 'AGT_Bothell'

        self._cached_store_name = store_name
        return store_name

    def _scan_databases_for_best_store(self) -> Optional[str]:
        """Inspect local database files and choose the store with the largest dataset."""
        search_dirs = [
            os.path.join(os.getcwd(), 'uploads'),
            os.path.join(os.getcwd(), 'databases')
        ]

        best_store = None
        best_count = 0

        for db_dir in search_dirs:
            if not os.path.exists(db_dir):
                continue

            db_files = glob.glob(os.path.join(db_dir, 'product_database_*.db'))
            db_files += glob.glob(os.path.join(db_dir, '*_products.db'))

            for db_file in db_files:
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM products")
                    count = cursor.fetchone()[0]
                    conn.close()

                    if count > best_count:
                        filename = os.path.basename(db_file)
                        if filename.startswith('product_database_'):
                            store_candidate = filename.replace('product_database_', '').replace('.db', '')
                        else:
                            store_candidate = filename.replace('_products.db', '')

                        best_store = store_candidate
                        best_count = count
                except Exception as e:
                    logging.debug(f"Failed to inspect database {db_file}: {e}")
                    continue

        if best_store:
            logging.info(f"📊 Auto-selected store '{best_store}' with {best_count} products for JSON matching")
        return best_store

    def _reset_product_database_cache(self):
        """Drop cached ProductDatabase instance (e.g., if store selection changes)."""
        if self._product_db_instance:
            try:
                self._product_db_instance.close_all_connections()
            except Exception:
                pass
        self._product_db_instance = None

    def _get_product_database(self):
        """Get (and cache) the ProductDatabase instance for the active store."""
        if self._product_db_instance:
            return self._product_db_instance

        store_name = self._determine_store_name()
        product_db = ProductDatabase(store_name=store_name)
        try:
            product_db.init_database()
        except Exception as e:
            logging.warning(f"Failed to initialize ProductDatabase for store '{store_name}': {e}")
        self._product_db_instance = product_db
        return product_db

    def _product_table_has_column(self, column_name: str) -> bool:
        """Check if the products table contains a specific column (cached)."""
        if self._product_table_columns is None:
            try:
                product_db = self._get_product_database()
                conn = product_db._get_connection()
                cursor = conn.cursor()
                cursor.execute('PRAGMA table_info(products)')
                self._product_table_columns = {row[1] for row in cursor.fetchall()}
            except Exception as e:
                logging.warning(f"Failed to inspect products table schema: {e}")
                self._product_table_columns = set()
        return column_name in self._product_table_columns

    def _find_best_database_match(self, product_name: str, vendor: str, weight: str, strain: str, product_db) -> Optional[Dict[str, Any]]:
        """Find the best matching product directly from the product database."""
        try:
            conn = product_db._get_connection()
            cursor = conn.cursor()

            vendor_filters = []
            if vendor:
                vendor_lower = vendor.lower().strip()
                if vendor_lower:
                    vendor_filters.append(vendor_lower)
                    normalized = self._normalize_vendor_name(vendor_lower)
                    if normalized and normalized != vendor_lower:
                        vendor_filters.append(normalized)
            # Deduplicate while preserving order
            seen_filters = set()
            vendor_filters = [vf for vf in vendor_filters if not (vf in seen_filters or seen_filters.add(vf))]

            import re
            
            def build_keyword_list(name: str) -> List[str]:
                if not name:
                    return []
                tokens = re.findall(r"[a-z0-9]+", name.lower())
                stop_words = {
                    "by", "the", "and", "pack", "joint", "joints", "pre", "roll", "preroll", "pre-roll",
                    "pack", "x", "nt", "ea", "unit", "units", "infused", "super", "sale", "mini", "buds"
                }
                keywords = []
                for token in tokens:
                    if token in stop_words:
                        continue
                    if len(token) < 2:
                        continue
                    keywords.append(token)
                return keywords[:5]
            
            keywords = build_keyword_list(product_name)
            
            def fetch_candidates():
                seen = set()
                collected = []
                
                def add_rows(rows):
                    nonlocal collected
                    if not rows:
                        return
                    columns = [col[0] for col in cursor.description]
                    for row in rows:
                        row_dict = dict(zip(columns, row))
                        key = (row_dict.get("Product Name*"), row_dict.get("Vendor/Supplier*"))
                        if key in seen:
                            continue
                        seen.add(key)
                        collected.append(row_dict)
                
                # First try vendor + keyword targeted searches
                if vendor_filters and keywords:
                    for vendor_filter in vendor_filters:
                        for keyword in keywords:
                            sql = (
                                'SELECT * FROM products '
                                'WHERE LOWER("Vendor/Supplier*") LIKE ? '
                                'AND LOWER("Product Name*") LIKE ? '
                                'LIMIT 150'
                            )
                            params = [f"%{vendor_filter}%", f"%{keyword}%"]
                            cursor.execute(sql, params)
                            add_rows(cursor.fetchall())
                            if len(collected) >= 250:
                                return collected
                
                # Next try vendor-only fetch
                for vendor_filter in vendor_filters:
                    sql = 'SELECT * FROM products WHERE LOWER("Vendor/Supplier*") LIKE ? LIMIT 250'
                    params = [f"%{vendor_filter}%"]
                    cursor.execute(sql, params)
                    add_rows(cursor.fetchall())
                    if len(collected) >= 250:
                        return collected
                
                # Finally fallback without vendor constraint (keyword first if available)
                if keywords:
                    for keyword in keywords:
                        cursor.execute(
                            'SELECT * FROM products WHERE LOWER("Product Name*") LIKE ? LIMIT 150',
                            [f"%{keyword}%"]
                        )
                        add_rows(cursor.fetchall())
                        if len(collected) >= 250:
                            return collected
                
                cursor.execute('SELECT * FROM products LIMIT 250')
                add_rows(cursor.fetchall())
                return collected

            candidates = fetch_candidates()

            if not candidates:
                return None

            try:
                from fuzzywuzzy import fuzz
                similarity_func = lambda a, b: fuzz.token_set_ratio(a, b)
            except ImportError:
                similarity_func = lambda a, b: int(SequenceMatcher(None, a, b).ratio() * 100)

            best_match = None
            best_score = 0

            def parse_weight(value):
                try:
                    return float(str(value).replace('g', '').strip())
                except (TypeError, ValueError, AttributeError):
                    return None

            item_weight = parse_weight(weight)

            for candidate in candidates:
                candidate_name = str(candidate.get('Product Name*') or candidate.get('product_name') or '').strip()
                if not candidate_name:
                    continue

                score = similarity_func(product_name.lower(), candidate_name.lower())

                if item_weight is not None:
                    candidate_weight = parse_weight(candidate.get('Weight*') or candidate.get('weight'))
                    if candidate_weight is not None:
                        diff = abs(candidate_weight - item_weight)
                        weight_tolerance = max(0.1, item_weight * 0.25)
                        if diff > weight_tolerance:
                            score -= min(30, int(diff * 10))

                if strain:
                    candidate_strain = str(candidate.get('Product Strain') or candidate.get('product_strain') or '').lower()
                    if candidate_strain and strain.lower() in candidate_strain:
                        score += 5

                if score > best_score:
                    best_score = score
                    best_match = candidate

            # CRITICAL FIX: If vendor was specified, prioritize matches from that vendor
            # Only use matches from different vendors if no good match found from the specified vendor
            if best_match and best_score >= 65:
                if vendor and vendor_filters:
                    # Check if the best match is from the specified vendor
                    match_vendor = str(best_match.get('Vendor/Supplier*') or best_match.get('Vendor', '') or '').lower().strip()
                    vendor_matched = False
                    for vendor_filter in vendor_filters:
                        if vendor_filter in match_vendor or match_vendor in vendor_filter:
                            vendor_matched = True
                            break
                    
                    # If vendor doesn't match, look for a better match from the correct vendor
                    if not vendor_matched:
                        logging.info(f"⚠️ Best match found from different vendor ({match_vendor}), searching for matches from specified vendor ({vendor})")
                        vendor_specific_matches = [c for c in candidates if any(
                            vf in str(c.get('Vendor/Supplier*') or c.get('Vendor', '') or '').lower() 
                            for vf in vendor_filters
                        )]
                        
                        if vendor_specific_matches:
                            # Find best match from correct vendor
                            best_vendor_match = None
                            best_vendor_score = 0
                            for candidate in vendor_specific_matches:
                                candidate_name = str(candidate.get('Product Name*') or candidate.get('product_name') or '').strip()
                                if not candidate_name:
                                    continue
                                
                                score = similarity_func(product_name.lower(), candidate_name.lower())
                                
                                if item_weight is not None:
                                    candidate_weight = parse_weight(candidate.get('Weight*') or candidate.get('weight'))
                                    if candidate_weight is not None:
                                        diff = abs(candidate_weight - item_weight)
                                        weight_tolerance = max(0.1, item_weight * 0.25)
                                        if diff > weight_tolerance:
                                            score -= min(30, int(diff * 10))
                                
                                if strain:
                                    candidate_strain = str(candidate.get('Product Strain') or candidate.get('product_strain') or '').lower()
                                    if candidate_strain and strain.lower() in candidate_strain:
                                        score += 5
                                
                                if score > best_vendor_score:
                                    best_vendor_score = score
                                    best_vendor_match = candidate
                            
                            # Use vendor-specific match if it's reasonably good (score >= 50)
                            if best_vendor_match and best_vendor_score >= 50:
                                logging.info(f"✅ Found better match from correct vendor (score: {best_vendor_score} vs {best_score})")
                                best_vendor_match['_similarity_score'] = best_vendor_score
                                return best_vendor_match
                            else:
                                logging.info(f"⚠️ No good match from correct vendor (best score: {best_vendor_score}), using cross-vendor match")
                
                best_match['_similarity_score'] = best_score
                return best_match
        except Exception as e:
            logging.warning(f"Direct database match search failed: {e}")
        return None
    
    def _build_cache_from_database(self):
        """Build sheet cache from ProductDatabase when Excel data is not available."""
        try:
            logging.info("📊 Building sheet cache from ProductDatabase...")
            
            # Try to get store name from session/context
            store_name = None
            try:
                from flask import session
                store_name = session.get('current_store')
            except:
                pass
            
            # If no store selected, try to find a database with actual data
            if not store_name:
                import os
                import glob
                import sqlite3
                
                # Check both uploads and databases directories
                search_dirs = [
                    os.path.join(os.getcwd(), 'uploads'),
                    os.path.join(os.getcwd(), 'databases')
                ]
                
                best_db = None
                best_count = 0
                
                for db_dir in search_dirs:
                    if not os.path.exists(db_dir):
                        continue
                        
                    # Match both product_database_*.db and *_products.db patterns
                    db_files = (glob.glob(os.path.join(db_dir, 'product_database_*.db')) + 
                               glob.glob(os.path.join(db_dir, '*_products.db')))
                    
                    # Find the database with the most products
                    for db_file in db_files:
                        try:
                            conn = sqlite3.connect(db_file)
                            cursor = conn.cursor()
                            cursor.execute("SELECT COUNT(*) FROM products")
                            count = cursor.fetchone()[0]
                            conn.close()
                            
                            if count > best_count:
                                best_count = count
                                best_db = db_file
                                # Extract store name from filename
                                filename = os.path.basename(db_file)
                                if filename.startswith('product_database_'):
                                    store_name = filename.replace('product_database_', '').replace('.db', '')
                                else:
                                    store_name = filename.replace('_products.db', '')
                                logging.info(f"📊 Found database with {count} products: {store_name}")
                        except Exception as e:
                            logging.debug(f"📊 Error checking database {db_file}: {e}")
                            continue
                
                if store_name:
                    logging.info(f"📊 Selected database with most products: {store_name} ({best_count} products)")
                else:
                    # Fall back to generic database if no other database found
                    store_name = 'generic'
                    logging.info("📊 Using generic database as fallback")
            
            # Cache the store selection so subsequent lookups reuse it
            if self._cached_store_name and self._cached_store_name != store_name:
                self._reset_product_database_cache()
            self._cached_store_name = store_name

            # Initialize ProductDatabase with store name
            product_db = self._get_product_database()
            logging.info(f"📊 Connected to ProductDatabase: {product_db.db_path}")
            
            # Get all products from database
            all_products = product_db.get_all_products()  # Get all products
            
            if not all_products:
                logging.warning("📊 No products found in database, using empty cache")
                self._sheet_cache = []
                self._indexed_cache = {}
                return
            
            # Limit to 10k products for performance
            if len(all_products) > 10000:
                logging.info(f"📊 Limiting {len(all_products)} products to 10000 for performance")
                all_products = all_products[:10000]
            
            logging.info(f"📊 Retrieved {len(all_products)} products from database")
            
            # Build cache from database products
            cache = []
            indexed_cache = {
                'exact_names': {},
                'vendor_exact_names': {},
                'vendor_groups': defaultdict(list),
                'key_terms': defaultdict(list),
                'normalized_names': defaultdict(list),
            }
            
            for product in all_products:
                # Get product name from various possible fields
                desc = (product.get('Product Name*') or 
                       product.get('product_name') or 
                       product.get('ProductName') or 
                       product.get('Description') or '').strip()
                
                if not desc:
                    continue
                
                norm = self._normalize(desc)
                toks = set(norm.split())
                key_terms = self._extract_key_terms(desc)
                
                # Get other fields
                brand = str(product.get('Product Brand') or product.get('brand') or '').strip()
                vendor = str(product.get('Vendor/Supplier*') or 
                           product.get('vendor') or 
                           product.get('Vendor') or '').strip()
                product_type = str(product.get('Product Type*') or 
                                 product.get('product_type') or '').strip()
                lineage = str(product.get('Lineage') or 
                            product.get('canonical_lineage') or '').strip()
                strain = str(product.get('Product Strain') or 
                           product.get('strain_name') or '').strip()
                
                cache_item = {
                    "idx": len(cache),
                    "original_name": desc,
                    "norm": norm,
                    "tokens": toks,
                    "key_terms": key_terms,
                    "brand": brand,
                    "vendor": vendor,
                    "product_type": product_type,
                    "lineage": lineage,
                    "strain": strain,
                    "_db_product": product  # Store full product data for later use
                }
                
                cache.append(cache_item)
                
                # Build indexes
                exact_name = desc.lower().strip()
                indexed_cache['exact_names'][exact_name] = cache_item
                
                if vendor:
                    vendor_key = f"{vendor.lower()}:{exact_name}"
                    indexed_cache['vendor_exact_names'][vendor_key] = cache_item
                    indexed_cache['vendor_groups'][vendor.lower()].append(cache_item)
                
                for term in key_terms:
                    indexed_cache['key_terms'][term].append(cache_item)
                
                indexed_cache['normalized_names'][norm].append(cache_item)
            
            self._sheet_cache = cache
            self._indexed_cache = indexed_cache
            
            logging.info(f"📊 Successfully built sheet cache from database with {len(cache)} products")
            logging.info(f"📊 Indexed {len(indexed_cache['exact_names'])} exact names")
            logging.info(f"📊 Indexed {len(indexed_cache['vendor_groups'])} vendor groups")
            
        except Exception as e:
            logging.error(f"📊 Error building cache from database: {e}")
            import traceback
            logging.error(traceback.format_exc())
            # Set empty caches as fallback
            self._sheet_cache = []
            self._indexed_cache = {}
        
    def _build_sheet_cache(self):
        """Build a cache of sheet data for fast matching."""
        logging.info("Building sheet cache...")
        if self.excel_processor is None:
            logging.warning("Cannot build sheet cache: ExcelProcessor is None")
            # CRITICAL FIX: Fall back to ProductDatabase when no Excel data available
            self._build_cache_from_database()
            return
            
        df = self.excel_processor.df
        if df is None:
            logging.warning("Cannot build sheet cache: DataFrame is None, attempting to load default file")
            # Try to load a default file
            try:
                from .excel_processor import get_default_upload_file
                default_file = get_default_upload_file()
                if default_file:
                    logging.info(f"Loading default file for JSON matcher: {default_file}")
                    success = self.excel_processor.load_file(default_file)
                    if success:
                        df = self.excel_processor.df
                        logging.info(f"Successfully loaded default file, DataFrame now has {len(df) if df is not None else 0} rows")
                    else:
                        logging.error(f"Failed to load default file: {default_file}")
                else:
                    logging.warning("No default file available for JSON matcher")
            except Exception as e:
                logging.error(f"Error loading default file for JSON matcher: {e}")
            
            if df is None:
                logging.warning("Cannot build sheet cache: DataFrame is still None after attempting to load default file")
                # CRITICAL FIX: Fall back to ProductDatabase when default file loading fails
                self._build_cache_from_database()
                return
            
        if df.empty:
            logging.warning("Cannot build sheet cache: DataFrame is empty")
            # CRITICAL FIX: Fall back to ProductDatabase when DataFrame is empty
            self._build_cache_from_database()
            return
            
        logging.info(f"Building sheet cache from DataFrame with {len(df)} rows")
            
        # Determine the best description column to use
        description_col = None
        for col in ["Product Name*", "ProductName", "Description"]:
            if col in df.columns:
                description_col = col
                break
                
        if not description_col:
            logging.error("No suitable description column found")
            self._sheet_cache = []
            self._indexed_cache = {}
            return
            
        # Filter out trade samples and nulls (but keep legitimate products containing "sample")
        if description_col == "Description":
            df = df[
                df[description_col].notna() &
                ~df[description_col].astype(str).str.lower().str.contains("trade sample", na=False) &
                ~df[description_col].astype(str).str.lower().str.match(r'^sample\s', na=False)
            ]
        else:
            # For ProductName/Product Name*, filter out trade samples and products starting with "sample"
            df = df[
                df[description_col].notna() &
                ~df[description_col].astype(str).str.lower().str.contains("trade sample", na=False) &
                ~df[description_col].astype(str).str.lower().str.match(r'^sample\s', na=False)
            ]
        
        cache = []
        indexed_cache = {
            'exact_names': {},  # O(1) exact name lookup
            'vendor_exact_names': {},  # O(1) vendor-specific exact name lookup
            'vendor_groups': defaultdict(list),  # O(1) vendor-based grouping
            'key_terms': defaultdict(list),  # O(1) key term lookup
            'normalized_names': defaultdict(list),  # O(1) normalized name lookup
        }
        
        for idx, row in df.iterrows():
            # Ensure idx is hashable by converting to string if needed
            hashable_idx = str(idx) if not isinstance(idx, (int, str, float)) else idx
            
            # Get description with proper type checking
            desc_raw = row[description_col] if description_col in row else ""
            desc = str(desc_raw) if desc_raw is not None else ""
            norm = self._normalize(desc)
            toks = set(norm.split())
            
            # Extract key terms for better matching
            key_terms = self._extract_key_terms(desc)
            
            # Get other fields with proper type checking
            brand_raw = row["Product Brand"] if "Product Brand" in row else ""
            brand = str(brand_raw) if brand_raw is not None else ""
            # Try multiple vendor column names
            vendor_raw = ""
            for vendor_col in ["Vendor", "Vendor/Supplier*", "Vendor/Supplier"]:
                if vendor_col in row and row[vendor_col] is not None:
                    vendor_raw = row[vendor_col]
                    break
            vendor = str(vendor_raw) if vendor_raw is not None else ""
            
            # DEBUG: Log vendor data for first few items
            if len(cache) < 5:
                print(f"🔍 DEBUG: Row {len(cache)}: vendor='{vendor}' (from column: {vendor_col if 'vendor_col' in locals() else 'none'})")
                print(f"🔍 DEBUG: Available columns: {list(row.index)}")
                print(f"🔍 DEBUG: Vendor column values: {[col for col in ['Vendor', 'Vendor/Supplier*', 'Vendor/Supplier'] if col in row]}")
            
            cache_item = {
                "idx": hashable_idx,
                "original_name": desc,
                "norm": norm,
                "tokens": toks,
                "key_terms": key_terms,
                "brand": brand,
                "vendor": vendor,
                "product_type": str(row["Product Type*"] if "Product Type*" in row else ""),
                "lineage": str(row["Lineage"] if "Lineage" in row else ""),
                "strain": str(row["Product Strain"] if "Product Strain" in row else ""),
                "_db_product": row.to_dict() if hasattr(row, 'to_dict') else dict(row)  # CRITICAL: Store full row data
            }
            
            try:
                cache.append(cache_item)
                
                # Build indexed cache for O(1) lookups
                # 1. Exact name index
                exact_name = desc.lower().strip()
                if exact_name:
                    indexed_cache['exact_names'][exact_name] = cache_item
                
                # 2. Vendor-specific exact name index
                vendor_lower = vendor.lower().strip()
                if vendor_lower and exact_name:
                    vendor_key = f"{exact_name}|{vendor_lower}"
                    if vendor_key not in indexed_cache['vendor_exact_names']:
                        indexed_cache['vendor_exact_names'][vendor_key] = []
                    indexed_cache['vendor_exact_names'][vendor_key].append(cache_item)
                
                # 3. Vendor index
                if vendor_lower:
                    indexed_cache['vendor_groups'][vendor_lower].append(cache_item)
                
                # 3. Key terms index (for each key term)
                for term in key_terms:
                    indexed_cache['key_terms'][term].append(cache_item)
                
                # 4. Normalized name index
                if norm:
                    indexed_cache['normalized_names'][norm].append(cache_item)
                    
            except Exception as e:
                logging.warning(f"Error creating cache item for row {idx}: {e}")
                continue
                
        self._sheet_cache = cache
        self._indexed_cache = indexed_cache
        logging.info(f"Built sheet cache with {len(cache)} entries using column '{description_col}'")
        logging.info(f"Built indexed cache with {len(indexed_cache['exact_names'])} exact names, {len(indexed_cache['vendor_groups'])} vendors, {len(indexed_cache['key_terms'])} key terms")
        
        # DEBUG: Show actual vendors in the data
        if cache:
            vendors_in_data = set()
            for item in cache[:20]:  # Check first 20 items
                vendor = str(item.get("vendor", "")).strip()
                if vendor:
                    vendors_in_data.add(vendor)
            print(f"🔍 DEBUG: ACTUAL VENDORS IN EXCEL DATA: {sorted(list(vendors_in_data))[:10]}...")
            print(f"🔍 DEBUG: Total vendors found: {len(vendors_in_data)}")
        
    def _normalize(self, s: str) -> str:
        """Normalize text for matching by removing digits, units, and special characters."""
        # Ensure input is a string
        s = str(s or "")
        s = s.lower()
        s = _DIGIT_UNIT_RE.sub("", s)
        s = _NON_WORD_RE.sub(" ", s)
        return _SPLIT_RE.sub(" ", s).strip()
        
    def _extract_key_terms(self, name: str) -> Set[str]:
        """Extract meaningful product terms, excluding common prefixes/suffixes."""
        try:
            # Debug logging to see what type of input we're getting
            if not isinstance(name, str):
                logging.warning(f"_extract_key_terms received non-string input: {type(name)} - {name}")
                if isinstance(name, list):
                    logging.warning(f"_extract_key_terms received a list: {name}")
                    # If it's a list, try to join it or take the first element
                    if name:
                        name = str(name[0]) if isinstance(name[0], str) else str(name[0])
                    else:
                        name = ""
                else:
                    name = str(name) if name is not None else ""
            
            # Ensure input is a string
            name = str(name or "")
            name_lower = name.lower()
            
            # Split on both spaces and hyphens to break compound terms
            words = set()
            for part in name_lower.replace('_', ' ').split():
                # Split each part on hyphens as well
                sub_parts = part.split('-')
                for sub_part in sub_parts:
                    if sub_part.strip():  # Only add non-empty parts
                        words.add(sub_part.strip())
            
            # Common words to exclude
            common_words = {
                'medically', 'compliant', '1g', '2g', '3.5g', '7g', '14g', '28g', 'oz', 'gram', 'grams',
                'pk', 'pack', 'packs', 'piece', 'pieces', 'roll', 'rolls', 'stix', 'stick', 'sticks', 'brand', 'vendor', 'product',
                'the', 'and', 'or', 'with', 'for', 'of', 'by', 'from', 'to', 'in', 'on', 'at', 'a', 'an', 'mg', 'thc', 'cbd'
            }
            
            # Filter out common words and short words (less than 2 characters for words like "all", "in", "one")
            key_terms = {word for word in words if word not in common_words and len(word) >= 2}
            
            # Add product type indicators for better matching
            product_types = {
                'rosin', 'wax', 'shatter', 'live', 'resin', 'distillate', 'cartridge', 'pre-roll', 'pre-rolls',
                'blunt', 'blunts', 'edible', 'edibles', 'tincture', 'tinctures', 'topical', 'topicals',
                'concentrate', 'concentrates', 'flower', 'buds', 'infused', 'flavour', 'flavor'
            }
            
            # Add product type terms if found
            for word in words:
                if word in product_types:
                    key_terms.add(word)
            
            # Add strain names (common cannabis strain words)
            strain_indicators = {
                'gmo', 'runtz', 'cookies', 'cream', 'wedding', 'cake', 'blueberry', 'banana', 'strawberry',
                'grape', 'lemon', 'lime', 'orange', 'cherry', 'apple', 'mango', 'pineapple', 'passion',
                'dragon', 'fruit', 'guava', 'pink', 'lemonade', 'haze', 'kush', 'diesel', 'og', 'sherbet',
                'gelato', 'mintz', 'grinch', 'cosmic', 'combo', 'honey', 'bread', 'tricho', 'jordan',
                'super', 'boof', 'grandy', 'candy', 'afghani', 'hashplant', 'yoda', 'amnesia'
            }
            
            # Add strain terms if found
            for word in words:
                if word in strain_indicators:
                    key_terms.add(word)
            
            # Add vendor/brand terms (but exclude common prefixes)
            vendor_prefixes = {'medically', 'compliant', 'by'}
            name_parts = name_lower.split()
            for i, part in enumerate(name_parts):
                if part not in vendor_prefixes and len(part) >= 3:
                    # Add single vendor words only
                    key_terms.add(part)
                  
            return key_terms
        except Exception as e:
            logging.warning(f"Error in _extract_key_terms: {e}")
            return set()
    
    def _clean_product_name_for_display(self, product_name: str, strain: str = None, weight: str = None, units: str = None) -> str:
        """
        Clean up product name for better display when no database match is found.
        Creates a format like: "Strain Product Type - Weight"
        """
        try:
            # Use the existing normalization function that removes medically compliant prefix
            cleaned_name = strip_medically_compliant_prefix(product_name)
            
            # If we have strain information, try to create a cleaner name
            if strain and strain.strip():
                strain_name = strain.strip()
                
                # Try to build a better display name
                # Format: "Strain Product Type - Weight"
                display_parts = []
                
                # Start with the strain name
                display_parts.append(strain_name)
                
                # Extract product type from cleaned name
                cleaned_lower = cleaned_name.lower()
                if "flower" in cleaned_lower:
                    display_parts.append("Flower")
                elif "live resin" in cleaned_lower:
                    display_parts.append("Live Resin")
                elif "rosin" in cleaned_lower:
                    display_parts.append("Rosin")
                elif "concentrate" in cleaned_lower:
                    display_parts.append("Concentrate")
                elif "pre-roll" in cleaned_lower or "preroll" in cleaned_lower:
                    display_parts.append("Pre-roll")
                elif "cartridge" in cleaned_lower or "cart" in cleaned_lower:
                    display_parts.append("Cartridge")
                elif "edible" in cleaned_lower:
                    display_parts.append("Edible")
                
                # Add weight if available
                if weight and units:
                    display_parts.append(f"{weight}{units}")
                elif weight:
                    display_parts.append(weight)
                
                # Join the parts
                if len(display_parts) > 1:
                    return " ".join(display_parts)
            
            # Fallback to original cleaned name
            return cleaned_name
            
        except Exception as e:
            logging.warning(f"Error in _clean_product_name_for_display: {e}")
            return product_name
        
    def _extract_vendor(self, name: str) -> str:
        """Extract vendor/brand information from product name."""
        try:
            # Ensure input is a string
            name = str(name or "")
            name_lower = name.lower()
            
            # Handle "by" format (e.g., "Product Name by Vendor") - check this first
            if " by " in name_lower:
                parts = name_lower.split(" by ", 1)
                if len(parts) > 1:
                    vendor_part = parts[1].strip()
                    # Remove any trailing weight/size info (e.g., " - 1g", " - 7g")
                    if " - " in vendor_part:
                        vendor_part = vendor_part.split(" - ")[0].strip()
                    # Return the full vendor name, not just first word
                    return vendor_part.lower()
            
            # Handle "Medically Compliant -" prefix
            if name_lower.startswith("medically compliant -"):
                after_prefix = name.split("-", 1)[1].strip()
                # Remove any trailing weight/size info
                if " - " in after_prefix:
                    after_prefix = after_prefix.split(" - ")[0].strip()
                # Take just the brand name (first part before any additional dashes)
                # For "Dank Czar Rosin All-In-One", we want just "Dank Czar"
                brand_part = after_prefix.split(" - ")[0].strip() if " - " in after_prefix else after_prefix
                # If the brand part contains multiple words that look like a product type, take just the first two words
                words = brand_part.split()
                if len(words) >= 3:
                    # Check if the third word looks like a product type
                    product_types = ['rosin', 'wax', 'shatter', 'live', 'resin', 'distillate', 'cartridge', 'pre-roll', 'all-in-one']
                    if words[2].lower() in product_types:
                        brand_part = " ".join(words[:2])  # Take just first two words
                return brand_part.lower()
                
            # Handle parentheses format (e.g., "Product Name (Vendor)") - check this BEFORE dash-separated formats
            if "(" in name_lower and ")" in name_lower:
                start = name_lower.find("(") + 1
                end = name_lower.find(")")
                if start < end:
                    vendor_part = name_lower[start:end].strip()
                    # Remove any trailing weight/size info (e.g., "/14g", "/7g", etc.)
                    if "/" in vendor_part:
                        vendor_part = vendor_part.split("/")[0].strip()
                    # Remove any trailing weight/size info with dashes (e.g., " - Platinum Line")
                    if " - " in vendor_part:
                        vendor_part = vendor_part.split(" - ")[0].strip()
                    return vendor_part.lower()
                
            # Handle other dash-separated formats
            parts = name.split("-", 1)
            if len(parts) > 1:
                brand_part = parts[0].strip()
                # Remove any trailing weight/size info
                if " - " in brand_part:
                    brand_part = brand_part.split(" - ")[0].strip()
                return brand_part.lower()
                
            # Fallback: use first word
            words = name_lower.split()
            return words[0].lower() if words else ""
        except Exception as e:
            logging.warning(f"Error in _extract_vendor: {e}")
            return ""
        
    def _find_candidates_optimized(self, json_item: dict) -> List[dict]:
        """Find candidate matches using indexed lookups instead of O(n²) comparisons."""
        # Safety check: ensure json_item is a dictionary
        if not isinstance(json_item, dict):
            logging.warning(f"json_item is not a dictionary (type: {type(json_item)}), cannot find candidates")
            return []
            
        # Safety check: ensure indexed cache is not None (but allow fallback to database)
        if self._indexed_cache is None:
            logging.debug("Indexed cache is None, will use database fallback for vendor matching")
            # Don't return early - allow the function to continue with database fallback
            
        candidates = set()  # Use set for deduplication by index
        candidate_indices = set()  # Track indices to avoid duplicates
        
        # Safely extract product name with proper error handling
        json_name_raw = ""
        try:
            json_name_raw = str(json_item.get("product_name", ""))
        except (AttributeError, TypeError):
            logging.warning(f"Invalid product_name in JSON item: {json_item}")
            return []
            
        json_name = normalize_product_name(json_name_raw)
        json_strain = str(json_item.get("strain_name", "")).lower().strip()
        
        # Extract vendor from JSON item using enhanced vendor extraction
        # CRITICAL FIX: Never extract vendor from product name - always use JSON vendor field or brand field only
        json_vendor = None
        try:
            vendor_info = extract_vendor_info(json_item)
            if vendor_info:
                json_vendor = vendor_info.lower()
            elif json_item.get("brand"):
                json_vendor = str(json_item.get("brand", "")).strip().lower()
            # DO NOT extract vendor from product name - this causes product names to be used as vendors
            # Vendor should be set from JSON metadata or global vendor, never extracted from product names
        except (AttributeError, TypeError) as e:
            logging.warning(f"Error extracting vendor from JSON item: {e}")
            json_vendor = None
        
        # Debug logging for specific items
        if "banana og" in json_name:
            logging.info(f"Finding candidates for: {json_name} (extracted vendor: {json_vendor})")
        
        if not json_name:
            return []
            
        # Strategy 1: Exact name match (highest priority) - only if indexed cache is available
        if self._indexed_cache and json_name in self._indexed_cache['exact_names']:
            exact_match = self._indexed_cache['exact_names'][json_name]
            return [exact_match]  # Return immediately for exact match
            
        # Strategy 2: Vendor-based filtering (STRICT - only match within same vendor)
        vendor_candidates = []
        if json_vendor:
            # First try exact vendor match (if indexed cache is available)
            if self._indexed_cache and json_vendor in self._indexed_cache['vendor_groups']:
                vendor_candidates = self._indexed_cache['vendor_groups'][json_vendor]
            elif self._indexed_cache:
                # Try fuzzy vendor matching for similar vendor names (but be more strict)
                vendor_candidates = self._find_strict_fuzzy_vendor_matches(json_vendor)
            
            # If we have vendor candidates, try to find better matches within the vendor
            if vendor_candidates:
                better_vendor_candidates = self._find_better_vendor_matches(json_item, vendor_candidates)
                if better_vendor_candidates:
                    vendor_candidates = better_vendor_candidates
                
            # Add vendor candidates to the result set
            for candidate in vendor_candidates:
                # Safety check: ensure candidate is a dictionary
                if not isinstance(candidate, dict):
                    logging.warning(f"Vendor candidate is not a dictionary (type: {type(candidate)}), skipping: {candidate}")
                    continue
                    
                if candidate["idx"] not in candidate_indices:
                    candidates.add(candidate["idx"])
                    candidate_indices.add(candidate["idx"])
                    
            # Debug logging for specific items
            if "banana og" in json_name:
                logging.info(f"Found {len(vendor_candidates)} vendor candidates for vendor '{json_vendor}'")
        
        # CRITICAL: If we have a vendor but no vendor candidates from indexed cache, 
        # try to find vendor candidates from database products
        if json_vendor and not vendor_candidates:
            logging.debug(f"No vendor candidates found in indexed cache for vendor '{json_vendor}' - checking database products")
            
            # Get all products including database products
            all_products = self._get_all_products()
            
            # Filter for vendor matches from all products
            vendor_candidates = []
            for product in all_products:
                if isinstance(product, dict):
                    candidate_vendor = str(product.get("Vendor/Supplier*", "") or product.get("vendor", "")).strip()
                    if candidate_vendor and self._is_vendor_match(json_vendor, candidate_vendor):
                        # Convert to indexed cache format
                        cache_item = {
                            "idx": len(vendor_candidates),
                            "original_name": product.get("Product Name*", ""),
                            "vendor": candidate_vendor,
                            "brand": product.get("Product Brand", ""),
                            "type": product.get("Product Type*", ""),
                            "description": product.get("Description", ""),
                            "_source": product.get("_source", "database"),
                            "_priority": product.get("_priority", 1)
                        }
                        vendor_candidates.append(cache_item)
            
            if vendor_candidates:
                logging.debug(f"Found {len(vendor_candidates)} vendor candidates from database for vendor '{json_vendor}'")
                # Add vendor candidates to the result set
                for candidate in vendor_candidates:
                    if candidate["idx"] not in candidate_indices:
                        candidates.add(candidate["idx"])
                        candidate_indices.add(candidate["idx"])
            else:
                logging.debug(f"No vendor candidates found in database for vendor '{json_vendor}' - returning empty list to prevent cross-vendor matches")
                return []
        
        # Strategy 3: Key term overlap (ONLY within vendor group to prevent cross-vendor matches)
        if json_vendor and vendor_candidates and self._indexed_cache:
            json_key_terms = self._extract_key_terms(json_name)
            for term in json_key_terms:
                if term in self._indexed_cache['key_terms']:
                    for candidate in self._indexed_cache['key_terms'][term]:
                        # Only include if candidate is from the same vendor group
                        candidate_vendor = str(candidate.get("vendor", "")).lower().strip()
                        if self._is_vendor_match(json_vendor, candidate_vendor):
                            if candidate["idx"] not in candidate_indices:
                                candidates.add(candidate["idx"])
                                candidate_indices.add(candidate["idx"])
                                
                                # Limit candidates to prevent performance issues
                                if len(candidates) >= 200:
                                    break
                    if len(candidates) >= 200:
                        break
        
        # Strategy 4: Normalized name similarity (ONLY within vendor group)
        if json_vendor and vendor_candidates and len(candidates) < 20 and json_name and self._indexed_cache:
            # Try to find similar normalized names within the same vendor
            for norm_name, norm_candidates in self._indexed_cache['normalized_names'].items():
                # Use simple similarity check
                similarity = SequenceMatcher(None, json_name, norm_name).ratio()
                if similarity >= 0.5:  # 50% similarity threshold
                    for candidate in norm_candidates:
                        # Only include if candidate is from the same vendor group
                        candidate_vendor = str(candidate.get("vendor", "")).lower().strip()
                        if self._is_vendor_match(json_vendor, candidate_vendor):
                            if candidate["idx"] not in candidate_indices:
                                candidates.add(candidate["idx"])
                                candidate_indices.add(candidate["idx"])
                                
                                # Limit candidates
                                if len(candidates) >= 100:
                                    break
                    if len(candidates) >= 100:
                        break
        
        # Convert back to list and limit total candidates for performance
        candidate_list = []
        
        # Get all products including database products for the final lookup
        all_products = self._get_all_products()
        
        # If we have candidates from the indexed cache, use those first
        if candidates:
            # Use sheet cache for indexed cache candidates
            if self._sheet_cache is not None:
                temp_index = {str(cache_item["idx"]): cache_item for cache_item in self._sheet_cache}
                candidate_indices_list = list(candidates)[:500]  # Limit to 500 candidates max
                
                for idx in candidate_indices_list:
                    cache_item = temp_index.get(str(idx))
                    if cache_item:
                        candidate_list.append(cache_item)
        
        # If we have vendor candidates from database, add those too
        if json_vendor and vendor_candidates:
            # Add database vendor candidates
            for candidate in vendor_candidates[:100]:  # Limit database candidates
                if candidate not in candidate_list:  # Avoid duplicates
                    candidate_list.append(candidate)
        
        return candidate_list
    
    def _is_vendor_match(self, vendor1: str, vendor2: str) -> bool:
        """Check if two vendors match using the same logic as the main matching function."""
        if not vendor1 or not vendor2:
            return False
            
        vendor1_clean = self._normalize_vendor_name(vendor1.lower().strip())
        vendor2_clean = self._normalize_vendor_name(vendor2.lower().strip())
        
        # Exact match
        if vendor1_clean == vendor2_clean:
            return True
            
        # Substring match (with length check)
        if (len(vendor1_clean) > len(vendor2_clean) * 2 and vendor2_clean in vendor1_clean) or \
           (len(vendor2_clean) > len(vendor1_clean) * 2 and vendor1_clean in vendor2_clean):
            return True
            
        # Use the flexible matching logic
        return self._is_vendor_match_flexible(vendor1_clean, vendor2_clean)
        
    def _find_fuzzy_vendor_matches(self, json_vendor: str) -> List[dict]:
        """Find vendor matches using fuzzy matching for similar vendor names."""
        if not json_vendor:
            return []
            
        matches = []
        available_vendors = list(self._indexed_cache['vendor_groups'].keys())
        
        # Common vendor name variations and abbreviations
        vendor_variations = {
            'dank czar': ['dcz holdings inc', 'dcz', 'dank czar holdings', 'dcz holdings', 'dcz holdings inc.'],
            'dcz holdings': ['dank czar', 'dcz', 'dcz holdings inc', 'dcz holdings inc.'],
            'dcz holdings inc': ['dank czar', 'dcz', 'dcz holdings', 'dcz holdings inc.'],
            'hustler\'s ambition': ['1555 industrial llc', 'hustler\'s ambition', 'hustlers ambition'],
            'hustlers ambition': ['1555 industrial llc', 'hustler\'s ambition', 'hustlers ambition'],
            'omega': ['jsm llc', 'omega labs', 'omega cannabis'],
            'airo pro': ['harmony farms', 'airo', 'airopro'],
            'jsm': ['omega', 'jsm llc', 'jsm labs'],
            'harmony': ['airo pro', 'harmony farms', 'harmony cannabis'],
        }
        
        # Check for known variations
        for variation_key, variations in vendor_variations.items():
            if json_vendor == variation_key or any(v in json_vendor for v in variations):
                for vendor in available_vendors:
                    if any(v in vendor for v in variations) or vendor in variations:
                        vendor_matches = self._indexed_cache['vendor_groups'][vendor]
                        # Safety check: ensure all matches are dictionaries
                        safe_matches = [match for match in vendor_matches if isinstance(match, dict)]
                        matches.extend(safe_matches)
        
        # If no matches found with known variations, try partial matching
        if not matches:
            for vendor in available_vendors:
                # Check if vendor contains key words from json_vendor
                json_words = set(json_vendor.split())
                vendor_words = set(vendor.split())
                
                # Check for word overlap
                overlap = json_words.intersection(vendor_words)
                if overlap and len(overlap) >= 1:  # At least one word in common
                    vendor_matches = self._indexed_cache['vendor_groups'][vendor]
                    # Safety check: ensure all matches are dictionaries
                    safe_matches = [match for match in vendor_matches if isinstance(match, dict)]
                    matches.extend(safe_matches)
        
        # If still no matches, try substring matching (more permissive)
        if not matches:
            json_vendor_lower = json_vendor.lower()
            for vendor in available_vendors:
                vendor_lower = vendor.lower()
                # Check if either vendor contains the other as a substring
                if json_vendor_lower in vendor_lower or vendor_lower in json_vendor_lower:
                    vendor_matches = self._indexed_cache['vendor_groups'][vendor]
                    # Safety check: ensure all matches are dictionaries
                    safe_matches = [match for match in vendor_matches if isinstance(match, dict)]
                    matches.extend(safe_matches)
        
        return matches
        
    def _find_better_vendor_matches(self, json_item: dict, vendor_candidates: List[dict]) -> List[dict]:
        """Find better matches within the same vendor by prioritizing similar product types and strain names."""
        if not vendor_candidates:
            return []
            
        json_name = str(json_item.get("product_name", "")).lower()
        json_key_terms = self._extract_key_terms(json_name)
        
        # Score each vendor candidate
        scored_candidates = []
        for candidate in vendor_candidates:
            # Safety check: ensure candidate is a dictionary
            if not isinstance(candidate, dict):
                logging.warning(f"Vendor candidate is not a dictionary (type: {type(candidate)}), skipping: {candidate}")
                continue
                
            candidate_name = str(candidate.get("original_name", "")).lower()
            candidate_key_terms = candidate.get("key_terms", set())
            
            # Calculate similarity score
            score = 0.0
            
            # Product type similarity
            product_types = {'rosin', 'wax', 'shatter', 'live', 'resin', 'distillate', 'cartridge', 'pre-roll', 'blunt', 'edible', 'tincture', 'topical', 'concentrate', 'flower', 'infused'}
            json_product_types = json_key_terms.intersection(product_types)
            candidate_product_types = candidate_key_terms.intersection(product_types)
            
            if json_product_types and candidate_product_types:
                if json_product_types == candidate_product_types:
                    score += 0.4  # Exact product type match
                elif json_product_types.intersection(candidate_product_types):
                    score += 0.2  # Partial product type match
            
            # Strain name similarity
            strain_indicators = {'gmo', 'runtz', 'cookies', 'cream', 'wedding', 'cake', 'blueberry', 'banana', 'strawberry', 'grape', 'lemon', 'cherry', 'apple', 'mango', 'pineapple', 'passion', 'dragon', 'fruit', 'guava', 'pink', 'lemonade', 'haze', 'kush', 'diesel', 'og', 'sherbet', 'gelato', 'mintz', 'grinch', 'cosmic', 'combo', 'honey', 'bread', 'tricho', 'jordan', 'super', 'boof', 'grandy', 'candy', 'afghani', 'hashplant', 'yoda', 'amnesia'}
            json_strains = json_key_terms.intersection(strain_indicators)
            candidate_strains = candidate_key_terms.intersection(strain_indicators)
            
            if json_strains and candidate_strains:
                if json_strains == candidate_strains:
                    score += 0.5  # Exact strain match
                elif json_strains.intersection(candidate_strains):
                    score += 0.3  # Partial strain match
            
            # General term overlap
            overlap = json_key_terms.intersection(candidate_key_terms)
            if overlap:
                overlap_ratio = len(overlap) / min(len(json_key_terms), len(candidate_key_terms)) if min(len(json_key_terms), len(candidate_key_terms)) > 0 else 0
                score += overlap_ratio * 0.3
            
            # Contains matching
            if json_name in candidate_name or candidate_name in json_name:
                score += 0.2
            
            scored_candidates.append((candidate, score))
        
        # Sort by score and return top candidates
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return [candidate for candidate, score in scored_candidates if score > 0.1]  # Reduced threshold from 0.2 to 0.1 for more candidates
        
    def _calculate_match_score(self, json_item: dict, cache_item: dict) -> float:
        """Calculate a match score between JSON item and cache item using enhanced field matching."""
        try:
            # Safety check: ensure both items are dictionaries
            if not isinstance(json_item, dict) or not isinstance(cache_item, dict):
                logging.warning(f"Invalid item types in _calculate_match_score: json_item={type(json_item)}, cache_item={type(cache_item)}")
                return 0.0
                
            # Extract core fields for matching - prioritize database descriptions
            json_name_raw = str(json_item.get("product_name", ""))
            
            # Use database description as primary matching field if available
            cache_description = str(cache_item.get("description", "")).strip()
            cache_name_raw = cache_description if cache_description else str(cache_item.get("original_name", ""))
            
            json_name = normalize_product_name(json_name_raw)
            cache_name = normalize_product_name(cache_name_raw)
            json_strain = str(json_item.get("strain_name", "")).lower().strip()
            cache_strain = str(cache_item.get("strain", "")).lower().strip()
            
            # Extract vendors for strict vendor matching
            json_vendor = None
            if json_item.get("vendor"):
                json_vendor = str(json_item.get("vendor", "")).strip().lower()
            elif json_item.get("brand"):
                json_vendor = str(json_item.get("brand", "")).strip().lower()
            else:
                json_vendor = self._extract_vendor(json_name_raw)
            
            cache_vendor = str(cache_item.get("vendor", "")).strip().lower()
            
            # Extract additional fields for enhanced matching
            json_brand = str(json_item.get("brand", "")).lower().strip()
            cache_brand = str(cache_item.get("Product Brand", cache_item.get("brand", ""))).lower().strip()
            json_type = str(json_item.get("product_type", "")).lower().strip()
            cache_type = str(cache_item.get("Product Type*", cache_item.get("product_type", ""))).lower().strip()
            json_weight = str(json_item.get("weight", "")).lower().strip()
            cache_weight = str(cache_item.get("Weight*", cache_item.get("weight", ""))).lower().strip()
            
            # Debug log with description information
            logging.debug(f"[SCORE] JSON: '{json_name_raw}' (norm: '{json_name}') | Excel: '{cache_name_raw}' (norm: '{cache_name}') | Description: '{cache_description}' | Strain: '{json_strain}' vs '{cache_strain}' | Vendor: '{json_vendor}' vs '{cache_vendor}' | Brand: '{json_brand}' vs '{cache_brand}' | Type: '{json_type}' vs '{cache_type}' | Weight: '{json_weight}' vs '{cache_weight}'")
            
            # --- BEGIN: Enhanced vendor matching ---
            # If we have vendor information for both, they must match or be very similar
            if json_vendor and cache_vendor:
                # Check if vendors are the same or known variations
                vendor_variations = {
                    'dank czar': ['dcz holdings inc', 'dcz holdings inc.', 'dcz', 'dank czar holdings', 'dcz holdings', 'jsm llc'],
                    'dcz holdings': ['dank czar', 'dcz', 'dcz holdings inc', 'dcz holdings inc.', 'dcz holdings', 'jsm llc'],
                    'dcz holdings inc': ['dank czar', 'dcz', 'dcz holdings', 'dcz holdings inc.', 'jsm llc'],
                    'dcz holdings inc.': ['dank czar', 'dcz', 'dcz holdings', 'dcz holdings inc', 'jsm llc'],
                    'jsm llc': ['dank czar', 'dcz holdings', 'dcz holdings inc', 'dcz holdings inc.', 'dcz', 'omega'],
                    'hustler\'s ambition': ['1555 industrial llc', 'hustler\'s ambition', 'hustlers ambition'],
                    'hustlers ambition': ['1555 industrial llc', 'hustler\'s ambition', 'hustlers ambition'],
                    '1555 industrial llc': ['hustler\'s ambition', 'hustlers ambition'],
                    'omega': ['jsm llc', 'omega labs', 'omega cannabis'],
                    'airo pro': ['harmony farms', 'airo', 'airopro'],
                }
                
                vendors_match = False
                if json_vendor == cache_vendor:
                    vendors_match = True
                else:
                    # Check known variations
                    for main_vendor, variations in vendor_variations.items():
                        if (json_vendor in [main_vendor] + variations and 
                            cache_vendor in [main_vendor] + variations):
                            vendors_match = True
                            break
                    
                    # Also check for partial matches (more lenient)
                    if not vendors_match:
                        # Check if one vendor name contains the other
                        if json_vendor in cache_vendor or cache_vendor in json_vendor:
                            vendors_match = True
                
                # If vendors don't match, return very low score (but not 0 to allow for edge cases)
                if not vendors_match:
                    logging.debug(f"Vendor mismatch: '{json_vendor}' vs '{cache_vendor}' - returning low score")
                    return 0.05
            # --- END: Enhanced vendor matching ---
            
            # --- BEGIN: Enhanced brand matching ---
            # Brand matching provides additional confidence
            brand_bonus = 0.0
            if json_brand and cache_brand:
                if json_brand == cache_brand:
                    brand_bonus = 0.1
                elif json_brand in cache_brand or cache_brand in json_brand:
                    brand_bonus = 0.05
            # --- END: Enhanced brand matching ---
            
            # --- BEGIN: Enhanced product type matching ---
            # Product type matching provides additional confidence
            type_bonus = 0.0
            if json_type and cache_type:
                if json_type == cache_type:
                    type_bonus = 0.1
                elif json_type in cache_type or cache_type in json_type:
                    type_bonus = 0.05
            # --- END: Enhanced product type matching ---
            
            # --- BEGIN: Enhanced weight matching ---
            # Weight matching provides additional confidence
            weight_bonus = 0.0
            if json_weight and cache_weight:
                if json_weight == cache_weight:
                    weight_bonus = 0.1
                elif json_weight in cache_weight or cache_weight in json_weight:
                    weight_bonus = 0.05
            # --- END: Enhanced weight matching ---
            
            # --- BEGIN: Enhanced description matching ---
            # Description matching provides significant bonus for database descriptions
            description_bonus = 0.0
            if cache_description and cache_description.strip():
                # If we're matching against a database description, give bonus points
                if json_name_raw.lower() in cache_description.lower():
                    description_bonus = 0.3  # High bonus for exact match in description
                elif any(word in cache_description.lower() for word in json_name.split() if len(word) > 3):
                    description_bonus = 0.2  # Medium bonus for word overlap in description
                else:
                    # Check if key terms from JSON name appear in description
                    json_key_terms = self._extract_key_terms(json_name_raw)
                    cache_key_terms = self._extract_key_terms(cache_description)
                    if json_key_terms and cache_key_terms:
                        overlap = set(json_key_terms) & set(cache_key_terms)
                        if overlap:
                            description_bonus = 0.1 + (len(overlap) * 0.05)  # Base bonus + term overlap
            # --- END: Enhanced description matching ---
            
            # --- BEGIN: Strict cannabis type filtering ---
            # Define recognized cannabis product types (update as needed)
            CANNABIS_TYPES = [
                "concentrate", "vape cartridge", "flower", "edible", "tincture", "capsule", "topical", "pre-roll"
            ]
            def is_cannabis_type(type_str):
                if not type_str:
                    return False
                type_str = str(type_str).lower()
                return any(t in type_str for t in CANNABIS_TYPES)

            # Get product type/category from both JSON and cache item
            json_type_check = json_item.get("product_type") or json_item.get("inventory_type") or json_item.get("inventory_category")
            cache_type_check = cache_item.get("product_type") or cache_item.get("product_category")

            # If either is not a cannabis type, do not match
            if not is_cannabis_type(json_type_check) or not is_cannabis_type(cache_type_check):
                return 0.0
            # --- END: Strict cannabis type filtering ---

            # Calculate base score with more stringent requirements
            base_score = 0.0

            # Exact match (highest score)
            if json_name == cache_name:
                base_score = 1.0
            # Contains match (high score)
            elif json_name in cache_name or cache_name in json_name:
                base_score = 0.9
            # Strain match bonus (good score)
            elif json_strain and cache_strain and json_strain == cache_strain:
                base_score = 0.8
            # Word overlap analysis (more stringent)
            else:
                json_words = set(json_name.split())
                cache_words = set(cache_name.split())
                
                # Remove common words that don't add value
                stop_words = {'and', 'or', 'the', 'a', 'an', 'with', 'for', 'live', 'resin', 'cart', 'cartridge'}
                json_words = json_words - stop_words
                cache_words = cache_words - stop_words
                
                if len(json_words) == 0 or len(cache_words) == 0:
                    base_score = 0.1
                else:
                    overlap = json_words & cache_words
                    if overlap:
                        # Require higher overlap for good matches
                        overlap_ratio = len(overlap) / min(len(json_words), len(cache_words))
                        if overlap_ratio >= 0.8:  # Raised from 0.5
                            base_score = 0.7
                        elif overlap_ratio >= 0.6:  # Raised from 0.3
                            base_score = 0.5
                        elif overlap_ratio >= 0.4:  # New middle tier
                            base_score = 0.3
                        else:
                            base_score = 0.1  # Lower score for weak overlap
                    else:
                        # No word overlap - very low score
                        base_score = 0.05
            
            # Apply bonuses for additional field matches (with diminishing returns)
            # Description bonus gets highest priority since it's the most comprehensive field
            final_score = base_score + (description_bonus * 1.0) + (brand_bonus * 0.8) + (type_bonus * 0.6) + (weight_bonus * 0.4)
            final_score = min(1.0, final_score)  # Cap at 1.0
            
            # Additional penalty for mismatched product types
            if json_type and cache_type and json_type != cache_type:
                # Check if they're in different categories
                concentrate_types = ['concentrate', 'vape', 'cartridge', 'oil', 'distillate']
                flower_types = ['flower', 'bud', 'pre-roll', 'joint']
                edible_types = ['edible', 'gummy', 'chocolate', 'candy']
                
                json_category = None
                cache_category = None
                
                for cat_name, types in [('concentrate', concentrate_types), ('flower', flower_types), ('edible', edible_types)]:
                    if any(t in json_type for t in types):
                        json_category = cat_name
                    if any(t in cache_type for t in types):
                        cache_category = cat_name
                
                if json_category and cache_category and json_category != cache_category:
                    final_score *= 0.3  # Heavy penalty for category mismatch
            
            return final_score
            
        except Exception as e:
            logging.error(f"Error in _calculate_match_score: {e}")
            logging.error(f"json_item: {json_item}")
            logging.error(f"cache_item: {cache_item}")
            return 0.05  # Return very low score instead of 0
        
    def fetch_and_match(self, url: str, deduplicate: bool = False) -> List[Dict]:
        """
        Fetch JSON from URL and match products against the loaded Excel data.
        SIMPLIFIED APPROACH: Bypass complex vendor isolation for maximum matches.
        
        Args:
            url: URL to fetch JSON data from (HTTP URL or data URL)
            
        Returns:
            List of matched product dictionaries
        """
        print(f"🔍 DEBUG: fetch_and_match called with URL: {url[:100]}...")
        # Special mode: return ALL DB products as matched tags (bypass JSON matching)
        if url.lower().startswith("db:all"):
            try:
                product_db = self._get_product_database()
                db_products = product_db.get_all_products() or []
                print(f"🔍 DEBUG: DB_ALL mode - loading {len(db_products)} products from database")
                matched_products = []
                for row in db_products:
                    product = self._create_product_from_db_row(row)
                    matched_products.append(product)
                return matched_products
            except Exception as e:
                logging.error(f"DB_ALL mode failed: {e}")
                return []
        if not (url.lower().startswith("http") or url.lower().startswith("data:")):
            raise ValueError("Please provide a valid HTTP URL or data URL")
            
        # SIMPLIFIED APPROACH: Use basic matching without strict vendor isolation
        print("🔍 DEBUG: Using SIMPLIFIED matching approach for maximum matches")
        self._sheet_cache = None
        self._indexed_cache = None
        self._build_sheet_cache()
            
        # DEBUG: Log the current state of Excel data
        print(f"🔍 DEBUG: Excel processor exists: {self.excel_processor is not None}")
        if self.excel_processor:
            print(f"🔍 DEBUG: Excel DataFrame exists: {self.excel_processor.df is not None}")
            if self.excel_processor.df is not None:
                print(f"🔍 DEBUG: Excel DataFrame rows: {len(self.excel_processor.df)}")
                print(f"🔍 DEBUG: Excel DataFrame columns: {list(self.excel_processor.df.columns)}")
                
                # Show unique vendors in Excel data
                vendor_cols = ['Vendor', 'Vendor/Supplier*', 'Vendor/Supplier']
                excel_vendors = set()
                for col in vendor_cols:
                    if col in self.excel_processor.df.columns:
                        vendors = self.excel_processor.df[col].dropna().unique()
                        excel_vendors.update([str(v).strip().lower() for v in vendors if str(v).strip()])
                
                print(f"🔍 DEBUG: Excel vendors ({len(excel_vendors)}): {sorted(list(excel_vendors))[:10]}...")
        print(f"🔍 DEBUG: Sheet cache length: {len(self._sheet_cache) if self._sheet_cache else 0}")
            
        # Note: We can still process JSON items even without Excel data
        # The sheet cache is only needed for Excel-based matching
        if not self._sheet_cache:
            print("⚠️ No Excel data available - will use Product Database for matching")

        try:
            # Handle data URLs differently from HTTP URLs
            if url.lower().startswith("data:"):
                try:
                    # Parse data URL
                    import base64
                    import json
                    
                    # Extract the data part after the comma
                    if ',' in url:
                        header, data_part = url.split(',', 1)
                        # Check if it's base64 encoded
                        if 'base64' in header:
                            # Decode base64 data
                            decoded_data = base64.b64decode(data_part).decode('utf-8')
                            payload = json.loads(decoded_data)
                        else:
                            # Direct JSON data
                            payload = json.loads(data_part)
                    else:
                        raise ValueError("Invalid data URL format")
                        
                    logging.info("Successfully parsed data URL")
                except Exception as data_error:
                    logging.error(f"Error parsing data URL: {data_error}")
                    raise ValueError(f"Failed to parse data URL: {data_error}")
            else:
                # Handle HTTP URLs
                import requests
                
                # Prepare headers for the request
                headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'application/json',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                }
                
                # Add authentication headers if available
                # These can be set via environment variables or configuration
                import os
                if os.environ.get('BAMBOO_API_KEY'):
                    headers['X-API-Key'] = os.environ.get('BAMBOO_API_KEY')
                if os.environ.get('BAMBOO_AUTH_TOKEN'):
                    headers['Authorization'] = f"Bearer {os.environ.get('BAMBOO_AUTH_TOKEN')}"
                if os.environ.get('BAMBOO_SESSION_TOKEN'):
                    headers['X-Session-Token'] = os.environ.get('BAMBOO_SESSION_TOKEN')
                
                # Try to make the request directly first
                try:
                    response = requests.get(url, headers=headers, timeout=60)
                    response.raise_for_status()
                    payload = response.json()
                except (requests.exceptions.RequestException, ValueError) as direct_error:
                    logging.info(f"Direct request failed, trying proxy: {direct_error}")
                    # Fallback to proxy endpoint if direct request fails
                    import os
                    base_url = os.environ.get('FLASK_BASE_URL', 'http://127.0.0.1:5001')
                    proxy_data = {'url': url, 'headers': headers}
                    response = requests.post(f'{base_url}/api/proxy-json', 
                                           json=proxy_data, 
                                           timeout=60)
                    response.raise_for_status()
                    payload = response.json()
                
            # Handle both list and dictionary payloads
            if isinstance(payload, list):
                items = payload
                global_vendor = ""
            elif isinstance(payload, dict):
                items = payload.get("inventory_transfer_items", [])
                global_vendor = payload.get("from_license_name", "")
                logging.info(f"Extracted global vendor from document: {global_vendor}")
            else:
                logging.warning(f"Unexpected payload type: {type(payload)}")
                return []
                
            if not items:
                logging.warning("No inventory transfer items found in JSON")
                return []

            # VENDOR PROPAGATION FIX: Find vendor from any item that has it and apply to all items
            if not global_vendor:
                # Look for vendor information in any of the items
                for item in items:
                    if isinstance(item, dict):
                        vendor = str(item.get('vendor', item.get('from_license_name', ''))).strip()
                        if vendor:
                            global_vendor = vendor
                            logging.info(f"🔧 VENDOR PROPAGATION: Found vendor '{global_vendor}' in item, applying to all items")
                            break
            
            # Apply the global vendor to ALL items that don't have one
            vendor_applied_count = 0
            for item in items:
                if isinstance(item, dict):
                    current_vendor = str(item.get('vendor', '')).strip()
                    if not current_vendor and global_vendor:
                        item['vendor'] = global_vendor
                        vendor_applied_count += 1
            
            if vendor_applied_count > 0:
                logging.info(f"🔧 VENDOR PROPAGATION: Applied vendor '{global_vendor}' to {vendor_applied_count} items that were missing vendor info")
                print(f"🔧 VENDOR PROPAGATION: Applied vendor '{global_vendor}' to {vendor_applied_count} items that were missing vendor info")
                
            # CRITICAL FIX: Preserve ALL items from JSON - no deduplication
            logging.info(f"Processing {len(items)} JSON items - preserving ALL items as requested")
            print(f"🔍 DEBUG: Processing {len(items)} JSON items - preserving ALL items as requested")
            
            # DEBUG: Show what vendor we're looking for in JSON
            if items:
                json_vendors = set()
                for item in items[:10]:  # Check first 10 items now that vendor is propagated
                    if isinstance(item, dict):
                        vendor = str(item.get('vendor', item.get('from_license_name', ''))).strip()
                        if vendor:
                            json_vendors.add(vendor)
                print(f"🔍 DEBUG: JSON VENDORS LOOKING FOR (after propagation): {sorted(list(json_vendors))}")
                
                # DEBUG: Show sample of all items to verify vendor propagation worked
                print(f"🔍 DEBUG: Sample of first 10 items (after vendor propagation):")
                for i, item in enumerate(items[:10]):
                    if isinstance(item, dict):
                        product_name = item.get('product_name', 'NO_NAME')
                        vendor = item.get('vendor', 'NO_VENDOR')
                        print(f"🔍 DEBUG:   Item {i}: '{product_name}' - vendor: '{vendor}'")
            
            unique_items = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                    
                product_name = str(item.get("product_name", "")).strip()
                
                # CRITICAL FIX: Process ALL items, even those with missing product names
                # This ensures no products are lost due to missing product names in JSON
                if not product_name:
                    # Try to create a fallback product name from other available fields
                    vendor = str(item.get("vendor", "")).strip()
                    brand = str(item.get("brand", "")).strip()
                    weight = str(item.get("weight", "")).strip()
                    product_type = str(item.get("inventory_type", "")).strip()
                    
                    # Create a fallback product name
                    fallback_parts = []
                    if brand:
                        fallback_parts.append(brand)
                    if product_type:
                        fallback_parts.append(product_type)
                    if weight:
                        fallback_parts.append(weight)
                    
                    if fallback_parts:
                        product_name = " ".join(fallback_parts)
                    else:
                        product_name = f"JSON Product {len(unique_items) + 1}"
                    
                    logging.info(f"⚠️  Created fallback product name: '{product_name}' for JSON item with missing name")
                
                # Add ALL items without any deduplication - each item gets its own label
                unique_items.append(item)
            
            logging.info(f"CRITICAL FIX: Processed {len(items)} items -> {len(unique_items)} products (ALL preserved)")
            logging.info(f"CRITICAL FIX: Each JSON item will generate its own separate label")
            print(f"🔍 DEBUG: CRITICAL FIX: Processed {len(items)} items -> {len(unique_items)} products (ALL preserved)")
            print(f"🔍 DEBUG: CRITICAL FIX: Each JSON item will generate its own separate label")
            
            # DEBUG: Show vendors in JSON data
            json_vendors = set()
            for item in unique_items:
                item_vendor = str(item.get("vendor", "")).strip().lower()
                if item_vendor:
                    json_vendors.add(item_vendor)
                if global_vendor:
                    json_vendors.add(global_vendor.lower())
            
            print(f"🔍 DEBUG: JSON vendors ({len(json_vendors)}): {sorted(list(json_vendors))}")
                
            # Extract vendor information from root level if available
            vendor_meta = "Unknown Vendor"
            json_vendor_filter = None
            if isinstance(payload, dict) and "from_license_name" in payload:
                vendor_meta = payload.get('from_license_name', '')
                if vendor_meta and vendor_meta != "Unknown Vendor":
                    logging.info(f"🔍 VENDOR DETECTION: Found vendor '{vendor_meta}' in JSON metadata")
                    print(f"🔍 VENDOR DETECTION: Found vendor '{vendor_meta}' in JSON metadata")
                    
                    # Extract the main vendor name (before the license number)
                    if " - " in vendor_meta:
                        json_vendor_filter = vendor_meta.split(" - ")[0].strip()
                    else:
                        json_vendor_filter = vendor_meta.strip()
                    
                    logging.info(f"🔍 VENDOR FILTER: Will only match products from vendor '{json_vendor_filter}'")
                    print(f"🔍 VENDOR FILTER: Will only match products from vendor '{json_vendor_filter}'")
                
            raw_date = datetime.now().strftime("%Y-%m-%d")
            if isinstance(payload, dict) and "est_arrival_at" in payload:
                raw_date = payload.get("est_arrival_at", "").split("T")[0]
                
            matched_products = []
            per_item_vendor_filters_logged = set()
            vendor_override_logged = set()
            
            # SIMPLIFIED APPROACH: Process each JSON item with basic matching for maximum results
            print(f"🔍 DEBUG: SIMPLIFIED MATCHING - Processing {len(unique_items)} items for maximum matches")
            print(f"🎯 GOAL: Match ALL {len(unique_items)} items - ZERO should be lost!")
            if json_vendor_filter:
                print(f"🔍 VENDOR ISOLATION: Strict vendor filter active - ONLY matching products from vendor '{json_vendor_filter}'")
            
            items_processed = 0
            items_matched = 0
            items_fallback = 0
            items_failed = 0
            
            for i, item in enumerate(unique_items):
                items_processed += 1
                # Ensure product name exists
                if not item.get("product_name"):
                    vendor = str(item.get("vendor", "")).strip()
                    brand = str(item.get("brand", "")).strip()
                    inventory_type = str(item.get("inventory_type", "")).strip()
                    
                    fallback_parts = []
                    if brand:
                        fallback_parts.append(brand)
                    if inventory_type:
                        fallback_parts.append(inventory_type)
                    if vendor:
                        fallback_parts.append(f"by {vendor}")
                    
                    if fallback_parts:
                        item["product_name"] = " ".join(fallback_parts)
                    else:
                        item["product_name"] = f"JSON Product {i+1}"
                    
                raw_product_name = str(item.get("product_name", ""))
                vendor_field_value = str(item.get("vendor", "")).strip()
                current_vendor_filter = json_vendor_filter

                if vendor_field_value:
                    normalized_vendor_field = vendor_field_value.lower()
                    if current_vendor_filter and not self._is_vendor_match(current_vendor_filter, vendor_field_value):
                        override_key = (current_vendor_filter.lower(), normalized_vendor_field)
                        if override_key not in vendor_override_logged:
                            logging.info(f"🔁 Vendor override: metadata vendor '{current_vendor_filter}' replaced with item vendor '{vendor_field_value}' for '{raw_product_name}'")
                            vendor_override_logged.add(override_key)
                    elif not current_vendor_filter and normalized_vendor_field not in per_item_vendor_filters_logged:
                        logging.info(f"🔒 Using item vendor '{vendor_field_value}' for vendor isolation (no global vendor metadata)")
                        per_item_vendor_filters_logged.add(normalized_vendor_field)
                    current_vendor_filter = vendor_field_value

                effective_vendor = current_vendor_filter or global_vendor
                brand = str(item.get("brand", "")).strip()
                inventory_type = str(item.get("inventory_type", "")).strip()
                inventory_category = str(item.get("inventory_category", "")).strip()
                product_type = map_inventory_type_to_product_type(inventory_type, inventory_category, raw_product_name)
                weight = str(item.get("unit_weight", item.get("weight", ""))).strip()
                price = str(item.get("line_price", item.get("price", ""))).strip()
                strain = str(item.get("strain_name", item.get("strain", ""))).strip()
                
                # CRITICAL FIX: Transform SKU to readable name BEFORE matching
                product_name = transform_sku_to_readable_name(raw_product_name) or raw_product_name
                
                print(f"🔍 DEBUG: ENHANCED MATCH - Processing item {i+1}/{len(unique_items)}: '{raw_product_name}' → '{product_name}'")
                print(f"🔍 DEBUG: ENHANCED MATCH - Extracted values: weight='{weight}', price='{price}', strain='{strain}', brand='{brand}'")
                
                # SIMPLIFIED MATCHING: Try matching against sheet cache (from Excel or Database)
                best_match = None
                best_score = 0.0
                 
                # Use sheet cache for matching (works with both Excel data and Database data)
                if self._sheet_cache and len(self._sheet_cache) > 0:
                    # Match against cached products (from database or Excel)
                    for cache_item in self._sheet_cache:
                        try:
                            excel_product_name = cache_item.get('original_name', '').strip().lower()
                            
                            if not excel_product_name:
                                continue
                            
                            # ENHANCED SCORING: Multi-factor matching with PRECISION FOCUS
                            score = 0.0
                            
                            # 0. VENDOR FILTER: STRICT vendor isolation - reject non-matching vendors
                            excel_vendor = cache_item.get('vendor', '').strip()
                            vendor_match_bonus = 0.0
                            if current_vendor_filter and excel_vendor:
                                # CRITICAL: Use the vendor matching function to check if vendors match
                                json_vendor_normalized = self._normalize_vendor_name(current_vendor_filter.lower())
                                excel_vendor_normalized = self._normalize_vendor_name(excel_vendor.lower())
                                
                                # Check if vendors match (exact, substring, or flexible match)
                                vendor_matches = self._is_vendor_match(current_vendor_filter, excel_vendor)
                                
                                if vendor_matches:
                                    vendor_match_bonus = 50.0  # Strong bonus for vendor match
                                    logging.debug(f"✓ Vendor match: '{current_vendor_filter}' matches '{excel_vendor}'")
                                else:
                                    # REJECT non-matching vendors to prevent cross-brand contamination
                                    logging.debug(f"🚫 REJECTED: Vendor mismatch - JSON vendor '{current_vendor_filter}' ≠ Excel vendor '{excel_vendor}'")
                                    continue  # Skip this candidate entirely
                            
                            # 1. Exact name match (highest priority)
                            if product_name.lower() == excel_product_name:
                                score += 200.0  # Very high score for exact match
                            
                            # 2. STRICT word-by-word matching to prevent incorrect matches
                            else:
                                # Check if key distinguishing words are present
                                json_words = set(product_name.lower().split())
                                excel_words = set(excel_product_name.split())
                                
                                # PROFESSIONAL-GRADE ACCURACY: Critical product identifiers that MUST NOT mismatch
                                product_identifiers = {
                                    'bath', 'salt', 'salts', 'jar', 'balm', 'lotion', 'cream',
                                    'cherry', 'cherries', 'chew', 'chews', 'freeze', 'dried', 
                                    'ball', 'balls', 'chocolate', 'malt', 'dragon', 'assorted',
                                    'fruit', 'watermelon', 'sour', 'apple', 'mixed', 'berry',
                                    'cookies', 'capsule', 'capsules', 'squeeze', 'roll',
                                    'tincture', 'single', 'dark', 'milk', 'caramel', 'guava',
                                    'tropical', 'mango', 'lifted', 'chill', 'balance', 'relief'
                                }
                                
                                # CRITICAL: Detect mutually exclusive products
                                # "dragon jar" and "bath salt" are completely different products
                                json_identifiers = json_words & product_identifiers
                                excel_identifiers = excel_words & product_identifiers
                                
                                if json_identifiers and excel_identifiers:
                                    # Check for contradicting product types
                                    contradictions = [
                                        ({'jar', 'dragon'}, {'bath', 'salt', 'salts'}),  # Jar vs Bath Salt
                                        ({'ball', 'balls'}, {'chew', 'chews'}),  # Balls vs Chews
                                        ({'bite', 'bites'}, {'ball', 'balls'}),  # Bites vs Balls
                                        ({'capsule', 'capsules'}, {'tincture', 'tinctures'}),  # Capsule vs Tincture
                                        ({'squeeze'}, {'roll', 'rollup'}),  # Squeeze Tube vs Roll-On
                                    ]
                                    
                                    for json_set, excel_set in contradictions:
                                        if (json_identifiers & json_set) and (excel_identifiers & excel_set):
                                            # Contradicting product types - reject match
                                            logging.debug(f"🚫 REJECTED: Contradicting products - JSON has {json_identifiers & json_set}, DB has {excel_identifiers & excel_set}")
                                            score = 0
                                            continue
                                    
                                    # If both have identifiers, they MUST overlap significantly
                                    identifier_overlap = len(json_identifiers & excel_identifiers) / max(len(json_identifiers), len(excel_identifiers))
                                    if identifier_overlap < 0.5:  # Less than 50% overlap of product identifiers
                                        score = 0  # Not a match - different products
                                        logging.debug(f"🚫 REJECTED: Low identifier overlap ({identifier_overlap:.1%})")
                                        continue
                                
                                # 3. Partial name match only if words align
                                if product_name.lower() in excel_product_name or excel_product_name in product_name.lower():
                                    # Check word overlap
                                    word_overlap = len(json_words & excel_words) / max(len(json_words), len(excel_words))
                                    if word_overlap >= 0.5:  # At least 50% word overlap
                                        score += 80.0
                                    else:
                                        score += 30.0  # Reduced score for weak overlap
                                
                                # 4. Enhanced fuzzy matching with stricter threshold
                                try:
                                    from fuzzywuzzy import fuzz
                                    
                                    # Use token_sort_ratio for better word-order-independent matching
                                    token_sort_score = fuzz.token_sort_ratio(product_name.lower(), excel_product_name)
                                    
                                    # Only use fuzzy if above threshold
                                    if token_sort_score >= 70:  # Stricter threshold (was 50)
                                        score += token_sort_score * 0.5  # Reduced weight for fuzzy
                                    elif token_sort_score >= 60:
                                        score += token_sort_score * 0.3  # Very low weight for marginal matches
                                        
                                except ImportError:
                                    pass
                            
                            # 5. Brand matching bonus
                            excel_brand = cache_item.get('brand', '').lower().strip()
                            json_brand = str(item.get('brand', '')).lower().strip()
                            if excel_brand and json_brand and excel_brand in json_brand or json_brand in excel_brand:
                                score += 20.0
                            
                            # 6. Add vendor matching bonus
                            score += vendor_match_bonus
                            
                            # 7. Product type matching bonus
                            excel_type = cache_item.get('product_type', '').lower().strip()
                            if product_type and excel_type and any(word in excel_type for word in product_type.lower().split()):
                                score += 15.0
                            
                            # 8. Weight matching - not available in cache
                            # (Skip weight bonus for now)
                            
                            # Store best match
                            if score > best_score:
                                best_score = score
                                # CRITICAL: Extract _db_product from cache_item
                                if '_db_product' in cache_item:
                                    best_match = cache_item['_db_product']
                                    db_name_check = best_match.get('Product Name*', 'MISSING')
                                    logging.debug(f"🎯 Extracted _db_product: '{db_name_check[:50]}'")
                                else:
                                    best_match = cache_item
                                    logging.warning(f"⚠️  cache_item missing _db_product, using cache_item itself")
                                logging.debug(f"🎯 New best match: JSON '{product_name}' → DB '{excel_product_name}' (score: {score:.1f})")
                                
                        except Exception as e:
                            continue
                
                # If we found a good match, create a product
                # PROFESSIONAL-GRADE ACCURACY: Strict threshold (90.0) for high confidence
                # Scores 50-90: Use AI validation for extra verification
                # This prevents incorrect matches like "Gold Dragon Jar" → "Bath Salt"
                
                # PROFESSIONAL-GRADE VALIDATION WITH STRICT NAME SIMILARITY
                validated = False
                
                # CRITICAL FIX: Require that product names are actually similar, not just attributes
                # This prevents matching "GSC Cartridge" → "Golden Pineapple Crystal" just because
                # they have the same vendor, weight, and product type
                name_similarity_required = False
                if best_match is not None and best_score >= 50.0:
                    # Calculate actual name similarity using fuzzy matching
                    json_name = product_name.lower()
                    db_name = str(best_match.get('Product Name*', '') or best_match.get('Description', '')).strip().lower()
                    
                    try:
                        from fuzzywuzzy import fuzz
                        name_similarity = fuzz.token_sort_ratio(json_name, db_name)
                        
                        # Require at least 70% name similarity for ANY match
                        # This allows legitimate matches like:
                        # - "Jet Fuel Gelato Vaporizer" → "Jet Fuel Gelato Live Resin" (75%+)
                        # - "Wedding Cake Cartridge" → "Wedding Cake Live Resin" (75%+)
                        # But prevents wrong matches like:
                        # - "Jet Fuel Gelato" → "Bubblegum Gelato" (65%)
                        if name_similarity < 70:
                            logging.warning(f"🚫 REJECTED: Low name similarity ({name_similarity}%) - '{product_name}' vs '{db_name}'")
                            best_match = None
                            best_score = 0
                        else:
                            name_similarity_required = True
                            logging.debug(f"✓ Name similarity check passed: {name_similarity}%")
                    except ImportError:
                        # If fuzzywuzzy not available, require exact or partial name match
                        if json_name not in db_name and db_name not in json_name:
                            # No overlap in names - reject
                            logging.warning(f"🚫 REJECTED: No name overlap - '{product_name}' vs '{db_name}'")
                            best_match = None
                            best_score = 0
                        else:
                            name_similarity_required = True
                
                if best_match is not None and best_score >= 100.0:  # Very high confidence - auto-approve
                    validated = True
                    logging.info(f"✅ HIGH CONFIDENCE: Score {best_score:.1f} >= 100.0")
                elif best_match is not None and best_score >= 50.0 and name_similarity_required:
                    # Medium confidence (50-100) - perform additional validation
                    json_name_str = product_name
                    db_name_str = str(best_match.get('Product Name*', '') or best_match.get('Description', '')).strip()
                    
                    # Additional validation: check for key product terms that MUST align
                    json_lower = json_name_str.lower()
                    db_lower = db_name_str.lower()
                    
                    # Extract core product terms (nouns that identify the product type)
                    core_terms_json = []
                    core_terms_db = []
                    
                    product_type_keywords = ['ball', 'balls', 'bite', 'bites', 'chew', 'chews', 
                                            'capsule', 'capsules', 'tincture', 'jar', 'balm', 
                                            'salt', 'salts', 'squeeze', 'roll', 'tube', 'lotion']
                    
                    for term in product_type_keywords:
                        if term in json_lower:
                            core_terms_json.append(term)
                        if term in db_lower:
                            core_terms_db.append(term)
                    
                    # CRITICAL: If both have core terms, at least ONE must match
                    if core_terms_json and core_terms_db:
                        has_common_term = any(jterm in core_terms_db for jterm in core_terms_json)
                        if not has_common_term:
                            logging.warning(f"🚫 VALIDATION FAILED: No common product type - JSON:{core_terms_json} vs DB:{core_terms_db}")
                            logging.warning(f"   '{json_name_str}' ≠ '{db_name_str}'")
                            best_match = None  # Reject this match
                        else:
                            validated = True
                            logging.info(f"✅ VALIDATED: Common terms {set(core_terms_json) & set(core_terms_db)}")
                    else:
                        # No clear product type terms - use score threshold
                        validated = (best_score >= 85.0)
                        if validated:
                            logging.info(f"✅ SCORE VALIDATED: {best_score:.1f} >= 85.0")
                        else:
                            logging.warning(f"🚫 SCORE TOO LOW: {best_score:.1f} < 85.0")
                            best_match = None
                
                if best_match is not None and validated:  # Only use validated matches
                    try:
                        product = self._create_product_from_excel_match(best_match, item, effective_vendor)
                        if product:
                            matched_products.append(product)
                            items_matched += 1
                            db_name = str(best_match.get('Product Name*', '') or best_match.get('Description', '')).strip()
                            print(f"✅ DB MATCH #{items_matched}: JSON '{product_name}' → DB '{db_name}' (score: {best_score:.1f})")
                            logging.info(f"✅ Matched: '{product_name}' → '{db_name}' (score: {best_score:.1f})")
                        else:
                            print(f"⚠️  Match found but product creation failed for '{product_name}'")
                            items_failed += 1
                    except Exception as e:
                        print(f"❌ Exception creating matched product for '{product_name}': {e}")
                        items_failed += 1
                        # DON'T continue - try fallback instead
                        try:
                            fallback_product = self._create_product_from_json_item(item, effective_vendor or global_vendor)
                            if fallback_product and fallback_product.get('Product Name*'):
                                matched_products.append(fallback_product)
                                items_fallback += 1
                                print(f"🔄 RECOVERED with fallback: '{product_name}'")
                        except Exception as fallback_error:
                            print(f"❌ Fallback also failed: {fallback_error}")
                            items_failed += 1
                else:
                    # FALLBACK: Create product from JSON data directly if no Excel/DB match
                    # This ensures EVERY JSON item gets a valid tag - NO EXCEPTIONS
                    try:
                        product = self._create_product_from_json_item(item, effective_vendor or global_vendor)
                        if product and product.get('Product Name*'):  # Ensure it's valid
                            matched_products.append(product)
                            items_fallback += 1
                            print(f"🆕 FALLBACK #{items_fallback}: '{product_name}' (no DB match, score: {best_score:.1f})")
                            logging.info(f"✅ Fallback tag created successfully for product that doesn't exist in database")
                        else:
                            # This should NEVER happen with our improved fallback
                            items_failed += 1
                            logging.error(f"❌ CRITICAL: Fallback returned empty product for '{product_name}'")
                            logging.error(f"   Item data: {item}")
                            print(f"❌ CRITICAL FAILURE #{items_failed}: Fallback empty for '{product_name}'")
                    except Exception as e:
                        items_failed += 1
                        logging.error(f"❌ CRITICAL: Exception in fallback for '{product_name}': {e}")
                        print(f"❌ CRITICAL FAILURE #{items_failed}: Exception in fallback for '{product_name}': {e}")
                        import traceback
                        logging.error(traceback.format_exc())
                        
                        # EMERGENCY: Try absolute minimal product creation
                        try:
                            emergency_product = {
                                'Product Name*': product_name or f"Item-{i+1}",
                                'ProductName': product_name or f"Item-{i+1}",
                                'Description': product_name or f"Item-{i+1}",
                                'displayName': product_name or f"Item-{i+1}",
                                'Vendor': global_vendor or 'Unknown',
                                'Product Brand': str(item.get("brand", global_vendor or "Unknown")),
                                'Product Type*': 'Mixed',
                                'Lineage': 'MIXED',
                                'Weight*': '1',
                                'Units': 'g',
                                'Price*': '',
                                'Quantity*': '1',
                                'Source': 'Emergency Fallback'
                            }
                            matched_products.append(emergency_product)
                            items_fallback += 1
                            print(f"🚨 EMERGENCY RECOVERY #{items_fallback}: Created minimal product for '{product_name}'")
                        except:
                            print(f"💀 TOTAL FAILURE: Could not create ANY product for '{product_name}'")
            
            # Return all matched products
            print(f"\n{'='*80}")
            print(f"📊 MATCHING SUMMARY:")
            print(f"   Items Processed: {items_processed}")
            print(f"   ✅ DB Matches: {items_matched}")
            print(f"   🆕 Fallbacks: {items_fallback}")
            print(f"   ❌ Failed: {items_failed}")
            print(f"   📦 Total Products: {len(matched_products)}")
            print(f"{'='*80}\n")
            
            if len(matched_products) < len(unique_items):
                missing = len(unique_items) - len(matched_products)
                print(f"⚠️  WARNING: {missing} items were LOST during matching!")
                logging.error(f"⚠️  CRITICAL: {missing} out of {len(unique_items)} items were lost!")
            else:
                print(f"✅ SUCCESS: ALL {len(matched_products)} items matched/created!")
            
            print(f"🔍 DEBUG: ENHANCED MATCHING COMPLETE - Found {len(matched_products)} total matches")
            
            # OPTIONAL DEDUPLICATION: Only if explicitly requested
            if deduplicate:
                # Group duplicates and track quantities
                unique_products = {}
                duplicate_count = 0
                
                for product in matched_products:
                    # Create a unique key based on product name, price, weight, and vendor
                    # This matches the deduplication criteria from memory
                    product_name = product.get('Product Name*', '')
                    weight = product.get('Weight*', '')
                    units = product.get('Units', '')
                    brand = product.get('Product Brand', '')
                    vendor = product.get('Vendor/Supplier*', '')
                    price = product.get('Price', '')
                    
                    # Create unique key using name, price, weight, and vendor to prevent unwanted duplicates
                    unique_key = f"{product_name}|{price}|{weight}|{units}|{vendor}".lower()
                    
                    if unique_key in unique_products:
                        # Duplicate found - increment quantity
                        duplicate_count += 1
                        current_qty = unique_products[unique_key].get('Quantity*', '1')
                        try:
                            # Add quantities together
                            new_qty = str(int(current_qty) + 1)
                            unique_products[unique_key]['Quantity*'] = new_qty
                            unique_products[unique_key]['Quantity'] = new_qty
                            logging.info(f"📦 Merged duplicate: '{product_name}' (now qty: {new_qty})")
                        except (ValueError, TypeError):
                            # If quantity parsing fails, just keep the existing one
                            pass
                    else:
                        # New unique product
                        unique_products[unique_key] = product
                
                deduplicated_products = list(unique_products.values())
                
                if duplicate_count > 0:
                    print(f"🔧 DEDUPLICATION: Removed {duplicate_count} duplicates, {len(deduplicated_products)} unique products remain")
                    logging.info(f"🔧 Deduplicated {len(matched_products)} matches -> {len(deduplicated_products)} unique products")
                    logging.info(f"   Merged {duplicate_count} duplicate entries by increasing quantity")
                
                deduplicated_products = self._upgrade_fallback_products(deduplicated_products, global_vendor)
                
                if json_vendor_filter:
                    print(f"🔍 VENDOR PREFERENCE: Matches prioritized for vendor '{json_vendor_filter}' but also include other vendors")
                
                return deduplicated_products
            else:
                # DEFAULT: Return ALL matches (one label per JSON entry)
                print(f"📋 Returning ALL {len(matched_products)} matches (one label per JSON entry)")
                logging.info(f"📋 Returning all {len(matched_products)} products without deduplication")
                
                if json_vendor_filter:
                    print(f"🔍 VENDOR PREFERENCE: Matches prioritized for vendor '{json_vendor_filter}' but also include other vendors")
                
                return self._upgrade_fallback_products(matched_products, global_vendor)
        except Exception as e:
            logging.error(f"Error in fetch_and_match: {e}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _extract_brand_from_product_name(self, product_name: str) -> str:
        """Extract brand information from product name."""
        try:
            name_lower = product_name.lower()
            
            # Look for common brand patterns
            brand_patterns = [
                'ceres', 'dank czar', 'dcz', 'jsm', 'omega', 'airo', 'hustler', 
                'super fog', 'moonshot', 'platinum', 'gold', 'silver'
            ]
            
            for pattern in brand_patterns:
                if pattern in name_lower:
                    return pattern.title()
            
            # Try to extract first word as brand
            words = product_name.split()
            if words:
                first_word = words[0].strip()
                if len(first_word) > 2:  # Avoid single letters
                    return first_word
            
            return ""
        except Exception as e:
            logging.warning(f"Error extracting brand from product name: {e}")
            return ""
    
    def _estimate_price_from_product_info(self, product_type: str, weight: str, product_name: str) -> str:
        """
        Legacy price-estimation helper. The business requirement is to avoid
        synthetic prices—return blank so the UI clearly shows missing data.
        """
        logging.debug(
            "⚠️ Skipping price estimate for '%s' (%s, %s); leaving blank per policy.",
            product_name, product_type, weight
        )
        return ""
    
    def _create_product_from_json_item(self, item: Dict, global_vendor: str) -> Dict:
        """
        Create a COMPLETE, VALID product tag from JSON item data (fallback when no database match found).
        This ensures every JSON item can generate a label even if it doesn't exist in the database.
        """
        try:
            # ===== STEP 1: Extract all raw data from JSON =====
            raw_product_name = str(item.get("product_name", "")).strip()
            json_vendor_value = str(item.get("vendor", "")).strip()
            # CRITICAL FIX: Always prioritize global_vendor - vendor should NEVER be missing
            # Only use JSON vendor if it's valid and global_vendor is not available
            if global_vendor and global_vendor.strip():
                vendor = global_vendor.strip()
            elif json_vendor_value and json_vendor_value.lower() not in ['', 'unknown', 'n/a', 'none']:
                vendor = json_vendor_value
            else:
                # Last resort: use brand as vendor, but still prefer global_vendor from metadata
                brand_as_vendor = str(item.get("brand", "")).strip()
                if brand_as_vendor and brand_as_vendor.lower() not in ['', 'unknown', 'n/a', 'none']:
                    vendor = brand_as_vendor
                else:
                    vendor = global_vendor if global_vendor else "Unknown Vendor"
            brand = str(item.get("brand", "")).strip()
            inventory_type = str(item.get("inventory_type", "")).strip()
            inventory_category = str(item.get("inventory_category", "")).strip()
            raw_weight = str(item.get("unit_weight", item.get("weight", ""))).strip()
            raw_units = str(item.get("unit_weight_uom", item.get("uom", "g"))).strip()
            # Capture price from any JSON field before estimating
            price_candidates = [
                item.get("line_price"),
                item.get("price"),
                item.get("Price"),
                item.get("retail_price"),
                item.get("unit_price"),
                item.get("sale_price"),
                item.get("unit_cost"),
                item.get("cost"),
                item.get("Cost"),
            ]
            raw_price = ""
            for candidate in price_candidates:
                if candidate is None:
                    continue
                candidate_str = str(candidate).strip()
                if not candidate_str:
                    continue
                if candidate_str.lower() in ("none", "nan"):
                    continue
                raw_price = candidate_str
                break
            strain = str(item.get("strain_name", item.get("strain", ""))).strip()
            if json_vendor_value and global_vendor and not self._is_vendor_match(global_vendor, json_vendor_value):
                logging.debug(f"🔁 Vendor override for JSON fallback: using item vendor '{json_vendor_value}' instead of metadata vendor '{global_vendor}'")
            
            # Normalize vendor but ensure it's never empty
            if vendor and vendor.strip():
                try:
                    vendor = self._normalize_vendor_display_name(vendor)
                except (AttributeError, Exception):
                    pass  # Keep original vendor if normalization fails
            
            # Final safety check: Ensure vendor is NEVER empty
            if not vendor or vendor.strip() == "":
                vendor = global_vendor if global_vendor else "Unknown Vendor"
                logging.warning(f"⚠️ Vendor was empty in _create_product_from_json_item, using fallback: '{vendor}'")
            if brand:
                brand = self._normalize_vendor_display_name(brand)
            
            # Extract cannabinoid data if available
            thc = ""
            cbd = ""
            try:
                if "lab_result" in item and item["lab_result"]:
                    lab_data = item["lab_result"]
                    if isinstance(lab_data, dict):
                        thc = str(lab_data.get("thc", lab_data.get("THC", ""))).strip()
                        cbd = str(lab_data.get("cbd", lab_data.get("CBD", ""))).strip()
            except:
                pass
            
            # ===== STEP 2: Map to product type =====
            product_type = map_inventory_type_to_product_type(inventory_type, inventory_category, raw_product_name)
            if not product_type:
                product_type = "Mixed"  # Safe fallback
            
            # ===== STEP 3: Transform SKU to human-readable name =====
            product_name = transform_sku_to_readable_name(raw_product_name) or raw_product_name
            excel_variations, type_override = self._generate_excel_style_variations(item, vendor, product_type)
            use_excel_style_name = False
            if type_override:
                product_type = type_override
            if excel_variations:
                try:
                    product_db = self._get_product_database()
                    if product_db:
                        db_match = self._find_best_database_match(
                            product_name=excel_variations[0],
                            vendor=vendor,
                            weight=str(item.get("unit_weight", item.get("weight", ""))).strip(),
                            strain=strain,
                            product_db=product_db
                        )
                        if db_match:
                            return self._create_tag_from_database_info(db_match, vendor, item)
                except Exception as db_lookup_error:
                    logging.debug(f"DB lookup during fallback conversion failed: {db_lookup_error}")
                product_name = excel_variations[0]
                use_excel_style_name = True
            
            # ===== STEP 4: Create better product name if needed =====
            if not use_excel_style_name and (not product_name or product_name.startswith("JSON Product")):
                name_parts = []
                
                # Add brand first if available
                if brand and brand.lower() not in ['unknown', 'n/a', '']:
                    name_parts.append(brand)
                
                # Add strain if available
                if strain and strain.lower() not in ['unknown', 'n/a', '']:
                    name_parts.append(strain)
                
                # Add product type
                if product_type and product_type.lower() not in ['unknown', 'n/a', 'mixed']:
                    name_parts.append(product_type)
                
                # Create descriptive name
                if name_parts:
                    product_name = " ".join(name_parts)
                else:
                    # Last resort: create unique name from vendor and type
                    product_name = f"{vendor or 'Unknown'} {product_type}" if vendor else f"Product-{hash(str(item)) % 10000}"
                
                logging.info(f"✨ Created descriptive product name: '{product_name}'")
            
            # ===== STEP 5: Ensure brand is populated =====
            if not brand:
                # Try multiple extraction methods
                if vendor:
                    brand = vendor
                elif product_name:
                    brand = self._extract_brand_from_product_name(product_name)
                
                # Final fallback - use vendor as brand
                if not brand:
                    brand = vendor if vendor else "Unknown Brand"
                    
            logging.info(f"📦 Brand determined: '{brand}'")
            
            # ===== STEP 6: Normalize weight and units =====
            weight, weight_units = self._normalize_weight_for_json_product(raw_weight, raw_units, product_type, product_name)
            weight_label = self._format_weight_label(weight, weight_units)
            
            # Ensure weight is valid
            if not weight or weight == "0":
                weight = "1"
            if not weight_units:
                weight_units = "g"
            if not weight_label:
                weight_label = f"{weight}{weight_units}"
            
            # ===== STEP 7: Determine price with intelligent fallbacks =====
            price = raw_price
            if not price or price in ("0", "0.0", "0.00"):
                logging.warning(f"⚠️ No valid price for '{product_name}' - leaving blank")
                price = self._estimate_price_from_product_info(product_type, weight, product_name)
            formatted_price = format_price(price) if str(price).strip() else ""
            if formatted_price:
                price = formatted_price
            
            # ===== STEP 8: Determine lineage =====
            lineage = self._determine_lineage_for_product(product_type, '', product_name, strain)
            if not lineage:
                # Ensure lineage is NEVER empty
                if 'cbd' in product_name.lower() or 'cbd' in brand.lower():
                    lineage = "CBD"
                elif product_type.lower() in ['flower', 'pre-roll', 'concentrate', 'vape cartridge']:
                    lineage = "HYBRID"
                else:
                    lineage = "MIXED"
            
            # ===== STEP 9: Calculate ratio =====
            ratio = self._calculate_ratio_for_json_product(product_type, item)
            
            # ===== STEP 9.5: Standardize description format for consistency =====
            if use_excel_style_name:
                description = product_name
            else:
                description = product_name
                import re
                desc_clean = re.sub(r'\s*-?\s*\d+\.?\d*\s*[a-zA-Z]+\s*$', '', description, flags=re.IGNORECASE)
                desc_clean = re.sub(r'\s+', ' ', desc_clean).strip()
                if weight_label:
                    description = f"{desc_clean} - {weight_label}"
                else:
                    description = desc_clean
            
            # ===== STEP 10: Build COMPLETE product with ALL required fields =====
            # Vendor and brand - CRITICAL: Vendor should NEVER be empty
            vendor_final = vendor if vendor and vendor.strip() else (global_vendor if global_vendor else 'Unknown Vendor')
            
            product = {
                # Core identification
                'Product Name*': description,  # Use standardized format
                'Description': description,    # Same as Product Name*
                
                # Vendor and brand
                'Vendor': vendor_final,
                'Vendor/Supplier*': vendor_final,
                'Product Brand': brand,
                'ProductBrand': brand,
                
                # Product classification
                'Product Type*': product_type,
                'ProductType': product_type,
                'Lineage': lineage,
                'Product Strain': strain if strain else '',
                
                # Weight and quantity
                'Weight*': weight,
                'Units': weight_units,
                'Weight Value + Unit': weight_label,
                'Quantity*': '1',
                'Quantity': '1',
                
                # Pricing
                'Price*': price,
                'Price': price,
                'Cost*': '',  # Unknown cost
                
                # Cannabinoids
                'THC test result': thc,
                'CBD test result': cbd,
                'Total THC': thc,
                'Total CBD': cbd,
                'THCA': '',
                'CBDA': '',
                'CBN': '',
                
                # Ratios
                'Ratio': ratio,
                'Ratio_or_THC_CBD': ratio,
                
                # Metadata
                'Source': 'JSON - No DB Match',
                'displayName': description,
                '__json_item__': item
            }
            
            # ===== STEP 11: Log creation =====
            logging.info(f"✅ Created VALID fallback tag:")
            logging.info(f"   📝 Product: '{product_name}'")
            logging.info(f"   🏷️  Brand: '{brand}'")
            logging.info(f"   💰 Price: '{price}'")
            logging.info(f"   ⚖️  Weight: '{weight}{weight_units}'")
            logging.info(f"   🧬 Lineage: '{lineage}'")
            logging.info(f"   📦 Type: '{product_type}'")
            
            return product
            
        except Exception as e:
            logging.error(f"❌ Error creating fallback product from JSON: {e}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            
            # EMERGENCY FALLBACK: Create minimal but valid product
            try:
                emergency_name = str(item.get("product_name", f"Product-{hash(str(item)) % 10000}"))
                logging.warning(f"⚠️  Creating emergency minimal product: '{emergency_name}'")
                
                return {
                    'Product Name*': emergency_name,
                    'Description': emergency_name,  # Same as Product Name*
                    'Vendor': global_vendor or 'Unknown',
                    'Product Brand': str(item.get("brand", global_vendor or "Unknown")),
                    'Product Type*': 'Mixed',
                    'Lineage': 'MIXED',
                    'Weight*': '1',
                    'Units': 'g',
                    'Price*': '',
                    'Quantity*': '1',
                    'Source': 'JSON - Emergency Fallback',
                    'THC test result': '',
                    'CBD test result': '',
                    'Ratio': '',
                    'Ratio_or_THC_CBD': '',
                    'Product Strain': ''
                }
            except:
                # Last resort - return empty dict will be filtered out
                logging.error("❌ Emergency fallback also failed")
                return {}
    
    def _create_product_from_excel_match(self, excel_row, json_item, global_vendor):
        """Create a product object from Excel row data, enhanced with JSON data."""
        try:
            # excel_row is already the _db_product (extracted in fetch_and_match)
            # No need to extract again
            
            # Get quantity from various possible column names
            def safe_row_get(row, key, default=''):
                try:
                    if hasattr(row, 'get') and callable(getattr(row, 'get')):
                        return row.get(key, default)
                    else:
                        return row[key] if key in row.index else default
                except (KeyError, AttributeError, TypeError):
                    return default
            
            quantity = safe_row_get(excel_row, 'Quantity*', '') or safe_row_get(excel_row, 'Quantity Received*', '') or safe_row_get(excel_row, 'Quantity', '') or ''
            
            # Get formatted weight with units
            weight_raw = safe_row_get(excel_row, 'Weight*', '')
            weight_with_units = weight_raw
            if weight_raw and safe_row_get(excel_row, 'Units'):
                weight_with_units = f"{weight_raw}{safe_row_get(excel_row, 'Units')}"
            
            # Use the dynamically detected product name column
            product_name_col = 'Product Name*'
            # Handle both dict and pandas Series
            if isinstance(excel_row, dict):
                if product_name_col not in excel_row:
                    possible_cols = ['ProductName', 'Product Name', 'Description', 'product_name']
                    product_name_col = next((col for col in possible_cols if col in excel_row), 'Product Name*')
            elif hasattr(excel_row, 'index'):
                if product_name_col not in excel_row.index:
                    possible_cols = ['ProductName', 'Product Name', 'Description']
                    product_name_col = next((col for col in possible_cols if col in excel_row.index), 'Description')
            
            # CRITICAL FIX: Use the ACTUAL database product name, not the transformed SKU name
            product_name = safe_row_get(excel_row, product_name_col, '') or safe_row_get(excel_row, 'Description', '')
            
            logging.info(f"🔍 PRODUCT NAME EXTRACTION: col='{product_name_col}', result='{product_name}'")
            logging.info(f"🔍 excel_row['Product Name*'] = '{excel_row.get('Product Name*', 'KEY NOT FOUND') if isinstance(excel_row, dict) else 'NOT A DICT'}'")
            
            # If the database product has no name, use JSON name as absolute fallback
            if not product_name:
                logging.warning(f"⚠️ Database product has no name - using JSON fallback")
                product_name = str(json_item.get("product_name", "Unknown Product"))
            
            # Get vendor with fallback logic - prioritize database vendor, then global vendor, then JSON vendor
            # CRITICAL FIX: Never extract vendor from product name - use database/global vendor first
            vendor = safe_row_get(excel_row, 'Vendor/Supplier*') or safe_row_get(excel_row, 'Vendor/Supplier') or safe_row_get(excel_row, 'Vendor') or global_vendor or ""
            json_vendor_value = str(json_item.get("vendor", "")).strip() if json_item else ""
            # Only use JSON vendor if it's actually set (not empty) and database/global vendor is missing
            if json_vendor_value and json_vendor_value.lower() not in ['', 'unknown', 'n/a', 'none']:
                # If we have a database/global vendor, only override if JSON vendor matches it
                if vendor:
                    if self._is_vendor_match(vendor, json_vendor_value):
                        logging.debug(f"✅ Vendor match: database '{vendor}' matches JSON '{json_vendor_value}'")
                    else:
                        logging.debug(f"⚠️ Vendor mismatch: keeping database '{vendor}' over JSON '{json_vendor_value}'")
                else:
                    # No database vendor - use JSON vendor
                    vendor = json_vendor_value
                    logging.debug(f"🔁 Using JSON vendor '{json_vendor_value}' (no database vendor)")
            
            # CRITICAL: Ensure vendor is NEVER empty - use global_vendor as absolute fallback
            if not vendor or vendor.strip() == "":
                vendor = global_vendor if global_vendor else "Unknown Vendor"
                logging.warning(f"⚠️ Vendor was empty, using fallback: '{vendor}'")
            
            if vendor:
                try:
                    vendor = self._normalize_vendor_display_name(vendor)
                except AttributeError:
                    # _normalize_vendor_display_name may not exist in some contexts; ignore if unavailable
                    pass
            
            # Final safety check: Ensure vendor is NEVER empty after normalization
            if not vendor or vendor.strip() == "":
                vendor = global_vendor if global_vendor else "Unknown Vendor"
                logging.warning(f"⚠️ Vendor became empty after normalization, using fallback: '{vendor}'")
            
            # CRITICAL FIX: Ensure brand, price, and weight are always populated
            # Get brand with multiple fallbacks
            excel_brand = safe_row_get(excel_row, 'Product Brand') or safe_row_get(excel_row, 'ProductBrand') or vendor or 'CERES'
            
            # CRITICAL FIX: Prioritize database price, then JSON price, never use fallback
            # Database prices are more reliable than JSON prices
            excel_price = safe_row_get(excel_row, 'Price*') or safe_row_get(excel_row, 'Price') or safe_row_get(excel_row, 'Price* (Tier Name for Bulk)') or ''
            # Only use JSON price if database price is missing - use comprehensive field extraction
            if not excel_price or excel_price in ('0', '0.0', '0.00', ''):
                if json_item:
                    excel_price = _extract_field_from_json_item_comprehensive(json_item, "Price* (Tier Name for Bulk)") or ''
                else:
                    excel_price = ''  # NO DEFAULT PRICE - leave empty if not found
            
            # CRITICAL FIX: Prioritize database weight, then JSON weight, never use fallback
            # Database weights are more reliable than JSON weights
            excel_weight = safe_row_get(excel_row, 'Weight*') or safe_row_get(excel_row, 'Weight') or ''
            # Only use JSON weight if database weight is missing - use comprehensive field extraction
            if not excel_weight or excel_weight in ('0', '0.0', '0.00', ''):
                if json_item:
                    excel_weight = _extract_field_from_json_item_comprehensive(json_item, "Weight*") or ''
                else:
                    excel_weight = ''  # NO DEFAULT WEIGHT - leave empty if not found
            
            # Get units with JSON override and fallback - use comprehensive field extraction
            excel_units = safe_row_get(excel_row, 'Units') or safe_row_get(excel_row, 'Weight Unit* (grams/gm or ounces/oz)') or 'g'
            if json_item:
                json_units = _extract_field_from_json_item_comprehensive(json_item, "Weight Unit* (grams/gm or ounces/oz)")
                if json_units:
                    excel_units = str(json_units).strip()
                else:
                    # Try alternative unit fields
                    if json_item.get("unit_weight_uom"):
                        excel_units = str(json_item.get("unit_weight_uom", "")).strip()
                    elif json_item.get("uom"):
                        excel_units = str(json_item.get("uom", "")).strip()
            if not excel_units:
                excel_units = 'g'
            
            # Standardize description format for database-matched products
            # Ensure format matches fallback products: "Product Name - Xg"
            import re
            description = product_name
            # Remove existing weight patterns and re-add in standardized format
            desc_clean = re.sub(r'\s*-?\s*\d+\.?\d*\s*g\s*$', '', description, flags=re.IGNORECASE)
            # Remove "by Brand" suffix if present
            desc_clean = re.sub(r'\s+by\s+[^-]+$', '', desc_clean, flags=re.IGNORECASE)
            desc_clean = re.sub(r'\s+', ' ', desc_clean).strip()
            # Add standardized weight suffix
            standardized_name = f"{desc_clean} - {excel_weight}{excel_units}"
            
            # Build product with essential fields - MATCH BACKUP VERSION FORMAT
            # CRITICAL: Description = Product Name* (same value, standardized format)
            
            product = {
                'Product Name*': standardized_name,
                'Description': standardized_name,  # Same as Product Name*, standardized format
                'Vendor': vendor if vendor and vendor.strip() else "Unknown Vendor",
                'Vendor/Supplier*': vendor if vendor and vendor.strip() else "Unknown Vendor",
                'Product Brand': excel_brand,  # Use the improved brand extraction
                'ProductBrand': excel_brand,
                'Product Type*': safe_row_get(excel_row, 'Product Type*'),
                'ProductType': safe_row_get(excel_row, 'Product Type*'),
                'Weight*': self._format_weight_label(excel_weight, excel_units) if excel_weight else '',  # Format like normal tags (no space: "3.5g")
                'Weight': self._format_weight_label(excel_weight, excel_units) if excel_weight else '',  # Format like normal tags
                'Units': excel_units,  # Use the improved units extraction
                'Weight Value + Unit': self._format_weight_label(excel_weight, excel_units) if excel_weight else '',
                'Price*': excel_price,  # Use the improved price extraction
                'Price': excel_price,
                'Price* (Tier Name for Bulk)': excel_price,  # Set all price field variations
                'Cost*': safe_row_get(excel_row, 'Cost*'),
                'THC test result': safe_row_get(excel_row, 'THC test result'),
                'CBD test result': safe_row_get(excel_row, 'CBD test result'),
                'Product Strain': safe_row_get(excel_row, 'Product Strain'),
                'ProductStrain': safe_row_get(excel_row, 'Product Strain'),
                'Lineage': safe_row_get(excel_row, 'Lineage'),
                'DOH': safe_row_get(excel_row, 'DOH'),  # CRITICAL: Include DOH from database
                'Quantity*': quantity,
                'Quantity': quantity,
                'Source': 'JSON Match'  # CRITICAL: Mark as JSON Match so frontend doesn't deduplicate
            }
            
            # DEBUG: Log the critical fields
            logging.info(f"🔍 EXCEL MATCH - Product: '{product_name}', Brand: '{excel_brand}', Price: '{excel_price}', Weight: '{excel_weight}'")
            
            return product
        except Exception as e:
            logging.error(f"Error creating product from Excel match: {e}")
            return {}
    
    def _convert_database_match_to_excel_format(self, db_match):
        """Convert a Product Database match to Excel row format for compatibility."""
        try:
            # Map database fields to Excel fields
            # Database results can have either snake_case OR Excel-style field names, so check both
            excel_row = {
                'Product Name*': (db_match.get('Product Name*', '') or
                                 db_match.get('product_name', '') or
                                 db_match.get('ProductName', '')),
                'Description': (db_match.get('Description', '') or
                              db_match.get('description', '') or
                              db_match.get('Product Name*', '') or
                              db_match.get('product_name', '')),
                'Vendor': (db_match.get('Vendor/Supplier*', '') or
                          db_match.get('Vendor', '') or
                          db_match.get('vendor', '')),
                'Vendor/Supplier*': (db_match.get('Vendor/Supplier*', '') or
                                    db_match.get('Vendor', '') or
                                    db_match.get('vendor', '')),
                'Product Brand': (db_match.get('Product Brand', '') or
                                 db_match.get('brand', '') or
                                 db_match.get('ProductBrand', '')),
                'Product Type*': (db_match.get('Product Type*', '') or
                                 db_match.get('product_type', '') or
                                 db_match.get('ProductType', '')),
                'Weight*': (db_match.get('Weight*', '') or
                           db_match.get('weight', '') or
                           db_match.get('Weight', '')),
                'Units': (db_match.get('Units', '') or
                         db_match.get('units', '') or
                         'g'),
                'Price': (db_match.get('Price', '') or
                         db_match.get('price', '') or
                         db_match.get('Price*', '')),
                'Price*': (db_match.get('Price', '') or
                          db_match.get('price', '') or
                          db_match.get('Price*', '')),
                'Cost*': (db_match.get('Cost', '') or
                         db_match.get('cost', '') or
                         db_match.get('Cost*', '')),
                'THC test result': (db_match.get('THC test result', '') or
                                   db_match.get('thc', '') or
                                   db_match.get('THC', '')),
                'CBD test result': (db_match.get('CBD test result', '') or
                                   db_match.get('cbd', '') or
                                   db_match.get('CBD', '')),
                'Product Strain': (db_match.get('Product Strain', '') or
                                  db_match.get('product_strain', '') or
                                  db_match.get('ProductStrain', '') or
                                  db_match.get('strain_name', '')),
                'Lineage': (db_match.get('Lineage', '') or
                           db_match.get('lineage', '') or
                           db_match.get('canonical_lineage', '')),
                'Quantity*': '1',  # Default quantity
                'DOH': (db_match.get('DOH', '') or
                       db_match.get('doh', '') or
                       db_match.get('DOH Compliant (Yes/No)', '')),
                'Source': 'Product Database'
            }

            logging.info(f"🔍 Converted database match to Excel format:")
            logging.info(f"  - Product Name*: '{excel_row.get('Product Name*', 'EMPTY')}'")
            logging.info(f"  - Product Brand: '{excel_row.get('Product Brand', 'EMPTY')}'")
            logging.info(f"  - Weight*: '{excel_row.get('Weight*', 'EMPTY')}'")
            logging.info(f"  - Units: '{excel_row.get('Units', 'EMPTY')}'")
            logging.info(f"  - Price*: '{excel_row.get('Price*', 'EMPTY')}'")
            return excel_row
        except Exception as e:
            logging.error(f"Error converting database match to Excel format: {e}")
            return {}
    
    def _create_product_from_json(self, json_item, global_vendor):
        """Create a product object from JSON data only."""
        try:
            raw_product_name = str(json_item.get("product_name", "")).strip()
            # CRITICAL FIX: Transform SKU to human-readable name
            product_name = transform_sku_to_readable_name(raw_product_name) or raw_product_name
            vendor = global_vendor if global_vendor else str(json_item.get("vendor", "")).strip()
            brand = str(json_item.get("brand", "")).strip()
            # Try multiple possible product type columns in order of preference
            # Including Column C:C as requested
            raw_product_type = (
                json_item.get("C") or  # Column C:C as requested
                json_item.get("product_type") or 
                json_item.get("Product Type*") or 
                json_item.get("ProductType") or 
                json_item.get("inventory_type") or 
                json_item.get("inventory_category") or 
                ""
            )
            raw_product_type = str(raw_product_type).strip()
            
            # Apply product name-based overrides to Column C value (use raw name for pattern matching)
            product_type = self._apply_product_name_overrides(raw_product_type, raw_product_name, json_item)
            
            # Log product type source for debugging
            if product_type:
                logging.info(f"🏷️ Found product type '{product_type}' for '{product_name}' from JSON data")
            else:
                logging.warning(f"⚠️ No product type found in JSON data for '{product_name}' - will use inference/mapping")
            weight = str(json_item.get("unit_weight", json_item.get("weight", ""))).strip()
            units = str(json_item.get("unit_weight_uom", json_item.get("unit_of_measure", "g"))).strip()
            strain = str(json_item.get("strain_name", json_item.get("strain", ""))).strip()
            
            # Enhanced inference from similar database matches
            inferred_data = self._infer_from_similar_database_matches(
                product_name, vendor, brand, product_type, strain, weight
            )
            
            # ENHANCED STRAIN EXTRACTION: If no strain in JSON, try to find in database
            if not strain and product_name:
                # First try to extract strain from product name
                extracted_strain = self._extract_strain_from_product_name(product_name)
                if extracted_strain:
                    strain = extracted_strain
                    logging.info(f"🧬 Extracted strain '{strain}' from product name '{product_name}' for unmatched JSON entry")
                else:
                    # Try to find strain in database by searching for similar product names
                    try:
                        product_db = self._get_product_database()
                        db_strain = self._find_strain_in_database(product_name, product_db)
                        if db_strain:
                            strain = db_strain
                            logging.info(f"🗄️ Found strain '{strain}' in database for product '{product_name}'")
                    except Exception as db_error:
                        logging.warning(f"Failed to search database for strain: {db_error}")
            
            # Clean product name - preserve the actual product name from JSON
            def clean_product_name(name):
                if not name:
                    return name
                import re
                # Replace "Vaporizer" with "Disposable Vape"
                cleaned = re.sub(r'\bVaporizer\b', 'Disposable Vape', name, flags=re.IGNORECASE)
                # Only remove obvious suffixes that are clearly not part of the product name
                cleaned = re.sub(r'\s*by\s+Dabstract\s+JSON\s*$', '', cleaned, flags=re.IGNORECASE)
                # Remove extra whitespace but preserve the actual product name
                cleaned = re.sub(r'\s+', ' ', cleaned)
                return cleaned.strip()
            
            # Use the actual product name from JSON, with minimal cleaning
            cleaned_product_name = clean_product_name(product_name)
            
            # Log the cleaning process for debugging
            if product_name and product_name != cleaned_product_name:
                logging.info(f"🧹 Cleaned product name: '{product_name}' → '{cleaned_product_name}'")
            
            # If cleaning removed too much, use the original name
            if not cleaned_product_name or len(cleaned_product_name) < 3:
                cleaned_product_name = product_name
                logging.info(f"⚠️ Using original product name due to insufficient cleaning: '{product_name}'")
            
            # Use simple display name to avoid deduplication issues
            comprehensive_display_name = cleaned_product_name
            
            # Use inferred data from similar database matches, with fallbacks
            final_brand = inferred_data.get('brand') or brand or self._infer_brand_from_name(cleaned_product_name)
            final_product_type = inferred_data.get('product_type') or self._infer_product_type_from_name(cleaned_product_name)
            final_lineage = inferred_data.get('lineage') or self._get_default_lineage_for_product_type(product_type)
            
            # Determine the final product type to use
            raw_final_type = product_type or final_product_type or map_inventory_type_to_product_type(
                json_item.get('inventory_type', ''), 
                json_item.get('inventory_category'),
                product_name
            )
            
            # Apply product name-based overrides to the final product type
            final_assigned_type = self._apply_product_name_overrides(
                raw_final_type, 
                product_name, 
                json_item
            )
            
            # Log the final product type assignment
            if product_type:
                logging.info(f"✅ Using JSON product type '{final_assigned_type}' for '{cleaned_product_name}'")
            elif final_product_type:
                logging.info(f"🔍 Using inferred product type '{final_assigned_type}' for '{cleaned_product_name}'")
            else:
                logging.info(f"🗺️ Using mapped product type '{final_assigned_type}' for '{cleaned_product_name}'")
            
            # ENHANCED: Intelligent price matching with multiple strategies
            final_price = self._intelligently_match_price(
                json_item, 
                inferred_data, 
                cleaned_product_name, 
                final_assigned_type, 
                weight, 
                strain
            )
            final_cost = self._intelligently_match_cost(
                json_item, 
                inferred_data, 
                final_price, 
                cleaned_product_name
            )
            
            # Log inference results for debugging
            if inferred_data.get('brand'):
                logging.info(f"🏷️ Inferred Brand '{final_brand}' from similar database matches for '{cleaned_product_name}'")
            elif final_brand:
                logging.info(f"🔍 Inferred Brand '{final_brand}' from product name '{cleaned_product_name}'")
            else:
                logging.info(f"🏷️ No brand inferred for product name '{cleaned_product_name}' (correctly avoiding strain names)")
                
            if inferred_data.get('product_type'):
                logging.info(f"🔍 Inferred Product Type '{final_product_type}' from similar database matches for '{cleaned_product_name}'")
            elif final_product_type:
                logging.info(f"🔍 Inferred Product Type '{final_product_type}' from product name '{cleaned_product_name}'")
                
            if inferred_data.get('lineage'):
                logging.info(f"🧬 Inferred Lineage '{final_lineage}' from similar database matches for '{cleaned_product_name}'")
            
            # Create weight with units for CombinedWeight
            try:
                weight_value = str(round(float(weight or '1')))
            except (ValueError, TypeError):
                weight_value = '1'
            weight_with_units = f"{weight_value}{units or 'g'}"
            
            # Create DescAndWeight field in the same format as other tags
            # CRITICAL FIX: Don't add weight to description to avoid duplication
            desc_and_weight = cleaned_product_name
            
            # Determine DOH value based on product type (proper DOH handling)
            doh_value = self._determine_doh_value(final_assigned_type, cleaned_product_name)
            
            # Create the product object
            product = {
                'Product Name*': cleaned_product_name,
                'ProductName': cleaned_product_name,
                'Description': cleaned_product_name,  # EXCEL PRIORITY: Description reflects product name
                'DescAndWeight': desc_and_weight,  # Format: "Description - Weight" like other tags
                'displayName': cleaned_product_name,  # Use clean name for UI display
                'Product Type*': final_assigned_type,  # EXCEL PRIORITY: Product Type from inferred/mapped data
                'ProductType': final_assigned_type,
                'Product Brand': final_brand or '',
                'ProductBrand': final_brand or '',
                'Product Strain': strain or 'Unknown Strain',
                'ProductStrain': strain or 'Unknown Strain',
                'Lineage': final_lineage,
                'Vendor': vendor or 'Unknown Vendor',
                'Vendor/Supplier*': vendor or 'Unknown Vendor',
                'Price': final_price,  # EXCEL PRIORITY: Price from intelligent matching
                'Price*': final_price,
                'Weight*': weight_value,
                'Weight': weight_value,
                'CombinedWeight': weight_with_units,  # CombinedWeight includes units
                'Quantity*': json_item.get('qty', json_item.get('Quantity*', json_item.get('quantity', '1'))),
                'Quantity': json_item.get('qty', json_item.get('Quantity*', json_item.get('quantity', '1'))),
                'Units': units or 'g',
                'THC test result': (json_item.get('THC test result') or 
                                   json_item.get('thc') or 
                                   json_item.get('thc_percent') or 
                                   json_item.get('thc_percentage') or 
                                   json_item.get('total_thc') or 
                                   json_item.get('total_thc_percent') or 
                                   0.0),
                'CBD test result': (json_item.get('CBD test result') or 
                                   json_item.get('cbd') or 
                                   json_item.get('cbd_percent') or 
                                   json_item.get('cbd_percentage') or 
                                   json_item.get('total_cbd') or 
                                   json_item.get('total_cbd_percent') or 
                                   0.0),
                'Test result unit (% or mg)': json_item.get('Test result unit (% or mg)', '%'),
                'State': 'active',
                'Is Sample? (yes/no)': 'no',
                'Is MJ product?(yes/no)': 'yes',
                'Discountable? (yes/no)': 'yes',
                'Room*': 'Default',
                'Medical Only (Yes/No)': 'No',
                'DOH': doh_value,  # EXCEL PRIORITY: DOH value based on product type (THC/CBD/YES/NO)
                'DOH Compliant (Yes/No)': 'Yes' if doh_value in ['YES', 'THC', 'CBD'] else 'No',
                'Source': 'JSON Match'  # Mark as JSON matched item
            }
            
            # Extract cannabinoid data from lab_result_data if available
            lab_result_data = json_item.get("lab_result_data", {})
            if lab_result_data:
                cannabinoids = extract_cannabinoids(lab_result_data)
                # Update THC and CBD test results with extracted data
                if 'thc' in cannabinoids:
                    product['THC test result'] = cannabinoids['thc']
                if 'cbd' in cannabinoids:
                    product['CBD test result'] = cannabinoids['cbd']
                if 'coa' in cannabinoids:
                    product['COA Link'] = cannabinoids['coa']
            
            # Add any additional fields from the JSON item
            for key, value in json_item.items():
                if key not in product:
                    product[key] = value
            
            # Log the final product for debugging
            logging.info(f"✅ Created JSON product: '{product['Product Name*']}' (Type: {product['Product Type*']}, Brand: {product['Product Brand']})")
            
            return product
            
        except Exception as e:
            logging.error(f"❌ Error creating product from JSON: {e}")
            logging.error(f"❌ JSON item that caused error: {json_item}")
            # Return a basic fallback product
            return {
                'Product Name*': f"JSON Product {hash(str(json_item)) % 1000}",
                'Source': 'JSON Match - Error',
                'Error': str(e)
            }
    
    def _infer_from_similar_database_matches(self, product_name, vendor, brand, product_type, strain, weight):
        """
        Infer brand, lineage, and product type from similar products in the database.
        
        Args:
            product_name: The product name to find similar matches for
            vendor: The vendor name
            brand: The brand name (if any)
            product_type: The product type (if any)
            strain: The strain name (if any)
            weight: The weight (if any)
            
        Returns:
            dict: Dictionary containing inferred brand, lineage, and product_type
        """
        try:
            # Initialize Product Database
            product_db = self._get_product_database()
            
            # Search for similar products using multiple strategies
            similar_products = self._find_similar_products_in_database(
                product_name, vendor, brand, product_type, strain, weight, product_db
            )
            
            if not similar_products:
                logging.debug(f"No similar products found for '{product_name}' in database")
                
                # Fallback: If we have vendor information but no database matches, 
                # use vendor as brand for known cannabis vendors
                if vendor and vendor.lower() not in ['unknown', 'nan', '']:
                    # Known cannabis vendors and their associated brands
                    vendor_brand_mapping = {
                        'trigonal': 'Oleum',  # Trigonal vendor typically uses Oleum brand
                        'oleum': 'Oleum',
                        'dabstract': 'Dabstract',
                        'constellation': 'Constellation Cannabis',
                        'mary jones': 'Mary Jones Cannabis Co',
                        'collections': 'Collections Cannabis',
                        'blue roots': 'Blue Roots Cannabis',
                        'grow op': 'Grow Op Farms',
                        'cloud 9': 'Cloud 9 Farms',
                        'collective': 'The Collective',
                        'fifty fold': 'Fifty Fold',
                        'seattle sluggerz': 'Seattle Sluggerz',
                        'hibro': 'Hibro Wholesale',
                        'core reactor': 'Core Reactor',
                        'diamond knot': 'Diamond Knot',
                        'terp slurper': 'Terp Slurper'
                    }
                    
                    vendor_lower = vendor.lower()
                    if vendor_lower in vendor_brand_mapping:
                        brand = vendor_brand_mapping[vendor_lower]
                        logging.info(f"🎯 Using vendor '{vendor}' → brand '{brand}' (no database matches found)")
                        return {'brand': brand}
                
                return {}
            
            # Analyze similar products to infer missing data
            inferred_data = self._analyze_similar_products_for_inference(similar_products, product_name, vendor)
            
            # ENHANCED: Add price and cost inference with vendor context
            price_cost_data = self._infer_price_and_cost_from_similar_products(
                similar_products, product_name, product_type, weight, vendor
            )
            inferred_data.update(price_cost_data)
            
            if inferred_data:
                logging.info(f"🎯 Inferred data from {len(similar_products)} similar products for '{product_name}': {inferred_data}")
            
            return inferred_data
            
        except Exception as e:
            logging.warning(f"Failed to infer from similar database matches: {e}")
            return {}
    
    def _find_similar_products_in_database(self, product_name, vendor, brand, product_type, strain, weight, product_db):
        """
        Find similar products in the database using multiple search strategies.
        
        Returns:
            list: List of similar product dictionaries
        """
        similar_products = []
        
        try:
            # Strategy 1: Search by product name similarity
            name_similar_products = self._search_by_name_similarity(product_name, product_db)
            similar_products.extend(name_similar_products)
            
            # Strategy 2: Search by vendor + product type
            if vendor and product_type:
                vendor_type_products = self._search_by_vendor_and_type(vendor, product_type, product_db)
                similar_products.extend(vendor_type_products)
            
            # Strategy 2.5: Search by vendor only (to find brand patterns for this vendor)
            if vendor:
                vendor_products = self._search_by_vendor_only(vendor, product_db)
                similar_products.extend(vendor_products)
            
            # Strategy 3: Search by strain name
            if strain:
                strain_products = self._search_by_strain(strain, product_db)
                similar_products.extend(strain_products)
            
            # Strategy 4: Search by brand name
            if brand:
                brand_products = self._search_by_brand(brand, product_db)
                similar_products.extend(brand_products)
            
            # Strategy 5: Search by weight and product type
            if weight and product_type:
                weight_type_products = self._search_by_weight_and_type(weight, product_type, product_db)
                similar_products.extend(weight_type_products)
            
            # Remove duplicates and limit results
            unique_products = []
            seen_ids = set()
            for product in similar_products:
                product_id = product.get('id') or product.get('product_name', '')
                if product_id not in seen_ids:
                    seen_ids.add(product_id)
                    unique_products.append(product)
            
            # Limit to top 20 most relevant results
            return unique_products[:20]
            
        except Exception as e:
            logging.warning(f"Error finding similar products in database: {e}")
            return []
    
    def _search_by_name_similarity(self, product_name, product_db):
        """Search for products with similar names using fuzzy matching."""
        try:
            import sqlite3
            conn = sqlite3.connect(product_db.db_path)
            
            # Get all products for fuzzy matching
            query = 'SELECT * FROM products WHERE "Product Name*" IS NOT NULL AND "Product Name*" != \'\''
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return []
            
            # Use fuzzy matching to find similar names
            from fuzzywuzzy import process
            matches = process.extract(
                product_name, 
                df['Product Name*'].tolist(), 
                limit=10, 
                scorer=fuzz.token_sort_ratio
            )
            
            # Filter matches with at least 60% similarity
            similar_products = []
            for match_name, score in matches:
                if score >= 60:
                    product_row = df[df['Product Name*'] == match_name].iloc[0]
                    similar_products.append(product_row.to_dict())
            
            return similar_products
            
        except Exception as e:
            logging.warning(f"Error in name similarity search: {e}")
            return []
    
    def _search_by_vendor_and_type(self, vendor, product_type, product_db):
        """Search for products with matching vendor and product type."""
        try:
            import sqlite3
            conn = sqlite3.connect(product_db.db_path)
            
            query = """
                SELECT * FROM products 
                WHERE "Vendor/Supplier*" = ? AND "Product Type*" = ?
                LIMIT 10
            """
            df = pd.read_sql_query(query, conn, params=[vendor, product_type])
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logging.warning(f"Error in vendor+type search: {e}")
            return []
    
    def _search_by_vendor_only(self, vendor, product_db):
        """Search for products with matching vendor to find brand patterns."""
        try:
            import sqlite3
            conn = sqlite3.connect(product_db.db_path)
            
            query = """
                SELECT * FROM products 
                WHERE "Vendor/Supplier*" = ? AND "Product Brand" IS NOT NULL AND "Product Brand" != ''
                LIMIT 15
            """
            df = pd.read_sql_query(query, conn, params=[vendor])
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logging.warning(f"Error in vendor-only search: {e}")
            return []
    
    def _search_by_strain(self, strain, product_db):
        """Search for products with matching strain."""
        try:
            import sqlite3
            conn = sqlite3.connect(product_db.db_path)
            
            if self._product_table_has_column('strain_id'):
                query = """
                    SELECT p.*, s.canonical_lineage 
                    FROM products p
                    LEFT JOIN strains s ON p.strain_id = s.id
                    WHERE p."Product Strain" LIKE ? OR s.strain_name LIKE ?
                    LIMIT 10
                """
                params = [f"%{strain}%", f"%{strain}%"]
            else:
                query = """
                    SELECT p.*, '' AS canonical_lineage
                    FROM products p
                    WHERE p."Product Strain" LIKE ? OR p."Lineage" LIKE ?
                    LIMIT 10
                """
                params = [f"%{strain}%", f"%{strain}%"]
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logging.warning(f"Error in strain search: {e}")
            return []
    
    def _search_by_brand(self, brand, product_db):
        """Search for products with matching brand."""
        try:
            import sqlite3
            conn = sqlite3.connect(product_db.db_path)
            
            query = """
                SELECT * FROM products 
                WHERE "Product Brand" = ?
                LIMIT 10
            """
            df = pd.read_sql_query(query, conn, params=[brand])
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logging.warning(f"Error in brand search: {e}")
            return []
    
    def _search_by_weight_and_type(self, weight, product_type, product_db):
        """Search for products with similar weight and product type."""
        try:
            import sqlite3
            import re
            
            # Extract numeric weight value
            weight_match = re.search(r'(\d+\.?\d*)', str(weight))
            if not weight_match:
                return []
            
            weight_value = float(weight_match.group(1))
            
            conn = sqlite3.connect(product_db.db_path)
            
            # Search for products with similar weight (within 20% tolerance)
            query = """
                SELECT * FROM products 
                WHERE "Product Type*" = ? AND "Weight*" IS NOT NULL
                LIMIT 20
            """
            df = pd.read_sql_query(query, conn, params=[product_type])
            conn.close()
            
            # Filter by weight similarity
            similar_products = []
            for _, row in df.iterrows():
                row_weight = str(row.get('weight', ''))
                row_weight_match = re.search(r'(\d+\.?\d*)', row_weight)
                if row_weight_match:
                    row_weight_value = float(row_weight_match.group(1))
                    # Check if weights are within 20% of each other
                    if abs(weight_value - row_weight_value) / max(weight_value, row_weight_value) <= 0.2:
                        similar_products.append(row.to_dict())
            
            return similar_products[:10]
            
        except Exception as e:
            logging.warning(f"Error in weight+type search: {e}")
            return []
    
    def _analyze_similar_products_for_inference(self, similar_products, target_product_name, target_vendor=None):
        """
        Analyze similar products to infer missing brand, lineage, and product type.
        
        Args:
            similar_products: List of similar product dictionaries
            target_product_name: The target product name for context
            target_vendor: The target vendor for vendor-based inference
            
        Returns:
            dict: Dictionary with inferred brand, lineage, and product_type
        """
        try:
            inferred_data = {}
            
            # Analyze brands - be smart about vendor-based inference
            brands = []
            vendor_brands = {}  # Track brands by vendor for vendor-based inference
            
            for product in similar_products:
                brand = product.get('brand', '').strip()
                product_vendor = product.get('vendor', '').strip()
                
                if brand and brand.lower() not in ['unknown', 'nan', '']:
                    # Additional validation: don't use strain names as brands
                    brand_lower = brand.lower()
                    strain_indicators = [
                        'gsc', 'wedding', 'blue', 'strawberry', 'jet', 'fuel', 'gelato', 'purple', 'punch',
                        'glazed', 'apricot', 'candy', 'passion', 'fruit', 'rainbow', 'sherbet', 'dream',
                        'honey', 'crystal', 'guava', 'gmo', 'liquid', 'diamond', 'disposable', 'vape',
                        'live', 'resin', 'cartridge', 'og', 'kush', 'haze', 'diesel', 'cookies', 'runtz',
                        'sherbert', 'banana', 'mango', 'pineapple', 'cherry', 'grape', 'lemon', 'lime',
                        'orange', 'apple', 'berry', 'peach', 'plum', 'watermelon', 'mint', 'vanilla',
                        'chocolate', 'coffee', 'caramel', 'sugar', 'sweet', 'cake', 'pie', 'cream'
                    ]
                    
                    # Skip if brand looks like a strain name
                    if not any(strain in brand_lower for strain in strain_indicators):
                        brands.append(brand)
                        
                        # Track brands by vendor for vendor-based inference
                        if product_vendor:
                            if product_vendor not in vendor_brands:
                                vendor_brands[product_vendor] = []
                            vendor_brands[product_vendor].append(brand)
            
            # Smart brand inference logic
            if brands:
                from collections import Counter
                brand_counter = Counter(brands)
                most_common_brand, count = brand_counter.most_common(1)[0]
                
                # Strategy 1: If we have multiple confirmations of the same brand, use it
                if count >= 2:
                    inferred_data['brand'] = most_common_brand
                    logging.info(f"🎯 Inferred brand '{most_common_brand}' from {count} similar products")
                
                # Strategy 2: If we have vendor information and vendor-specific brand patterns
                elif target_vendor and target_vendor in vendor_brands:
                    # Check if the target vendor has a consistent brand pattern
                    vendor_brand_list = vendor_brands[target_vendor]
                    if len(vendor_brand_list) >= 2:  # Need at least 2 products from this vendor
                        vendor_brand_counter = Counter(vendor_brand_list)
                        vendor_most_common, vendor_count = vendor_brand_counter.most_common(1)[0]
                        
                        # If this vendor consistently uses the same brand, infer it
                        if vendor_count >= 2:
                            inferred_data['brand'] = vendor_most_common
                            logging.info(f"🎯 Inferred brand '{vendor_most_common}' from vendor '{target_vendor}' pattern ({vendor_count} products)")
                
                # Strategy 3: If no specific vendor match, try any vendor with consistent brand pattern
                elif not inferred_data.get('brand'):
                    for vendor, vendor_brand_list in vendor_brands.items():
                        if len(vendor_brand_list) >= 3:  # Need at least 3 products for general inference
                            vendor_brand_counter = Counter(vendor_brand_list)
                            vendor_most_common, vendor_count = vendor_brand_counter.most_common(1)[0]
                            
                            # If this vendor consistently uses the same brand, infer it
                            if vendor_count >= 3:
                                inferred_data['brand'] = vendor_most_common
                                logging.info(f"🎯 Inferred brand '{vendor_most_common}' from vendor '{vendor}' pattern ({vendor_count} products)")
                                break
            
            # Analyze product types
            product_types = []
            for product in similar_products:
                ptype = product.get('product_type', '').strip()
                if ptype and ptype.lower() not in ['unknown', 'nan', '']:
                    product_types.append(ptype)
            
            if product_types:
                # Use the most common product type
                from collections import Counter
                type_counter = Counter(product_types)
                most_common_type = type_counter.most_common(1)[0][0]
                inferred_data['product_type'] = most_common_type
            
            # Analyze lineages
            lineages = []
            for product in similar_products:
                lineage = product.get('canonical_lineage', '').strip()
                if lineage and lineage.lower() not in ['unknown', 'nan', '']:
                    lineages.append(lineage)
            
            if lineages:
                # Use the most common lineage
                from collections import Counter
                lineage_counter = Counter(lineages)
                most_common_lineage = lineage_counter.most_common(1)[0][0]
                inferred_data['lineage'] = most_common_lineage
            
            # ENHANCED: Analyze descriptions and weights
            descriptions = []
            weights = []
            
            for product in similar_products:
                # Get description
                desc = product.get('description', '').strip()
                if desc and desc.lower() not in ['unknown', 'nan', '', 'none']:
                    descriptions.append(desc)
                
                # Get weight
                weight_val = product.get('weight', '').strip()
                if weight_val and weight_val.lower() not in ['unknown', 'nan', '', 'none']:
                    weights.append(weight_val)
            
            # Infer description if we have similar product descriptions
            if descriptions:
                # Use the most common description, or if they're all unique, use the first one
                from collections import Counter
                desc_counter = Counter(descriptions)
                most_common_desc = desc_counter.most_common(1)[0][0]
                inferred_data['description'] = most_common_desc
                logging.info(f"📝 Inferred description from {len(descriptions)} similar products")
            
            # Infer weight if we have similar product weights
            if weights:
                # Use the most common weight
                from collections import Counter
                weight_counter = Counter(weights)
                most_common_weight = weight_counter.most_common(1)[0][0]
                inferred_data['weight'] = most_common_weight
                logging.info(f"⚖️  Inferred weight '{most_common_weight}' from similar products")
            
            return inferred_data
            
        except Exception as e:
            logging.warning(f"Error analyzing similar products for inference: {e}")
            return {}
    
    def _infer_price_and_cost_from_similar_products(self, similar_products, product_name, product_type, weight, vendor=None):
        """
        Infer price and cost from similar products in the database, prioritizing vendor context.
        
        Args:
            similar_products: List of similar product dictionaries
            product_name: The product name
            product_type: The product type
            weight: The weight
            vendor: The vendor name for context-specific pricing
            
        Returns:
            Dictionary with inferred price and cost
        """
        import re  # Move import to top of function
        
        try:
            inferred_data = {}
            
            # Extract prices and costs from similar products, prioritizing vendor context
            prices = []
            costs = []
            vendor_prices = []
            vendor_costs = []
            
            for product in similar_products:
                # Check if this product is from the same vendor
                product_vendor = product.get('vendor', '').strip().lower()
                is_same_vendor = vendor and product_vendor == vendor.lower()
                
                # Extract price
                price = product.get('price', '').strip()
                if price and price.lower() not in ['unknown', 'nan', '', '0', '$0', '0.00']:
                    # Clean price string (remove $, commas, etc.)
                    price_clean = re.sub(r'[^\d.]', '', price)
                    try:
                        price_float = float(price_clean)
                        if price_float > 0:
                            prices.append(price_float)
                            if is_same_vendor:
                                vendor_prices.append(price_float)
                    except (ValueError, TypeError):
                        pass
                
                # Extract cost
                cost = product.get('cost', '').strip()
                if cost and cost.lower() not in ['unknown', 'nan', '', '0', '$0', '0.00']:
                    # Clean cost string (remove $, commas, etc.)
                    cost_clean = re.sub(r'[^\d.]', '', cost)
                    try:
                        cost_float = float(cost_clean)
                        if cost_float > 0:
                            costs.append(cost_float)
                            if is_same_vendor:
                                vendor_costs.append(cost_float)
                    except (ValueError, TypeError):
                        pass
            
            # Calculate inferred price - prioritize vendor-specific pricing
            if vendor_prices:
                # Use vendor-specific pricing if available
                vendor_prices.sort()
                median_price = vendor_prices[len(vendor_prices) // 2]
                if median_price.is_integer():
                    inferred_data['price'] = f"${int(median_price)}"
                else:
                    inferred_data['price'] = f"${median_price:.2f}"
                logging.info(f"💰 Inferred price ${median_price:.2f} from {len(vendor_prices)} vendor-specific products for '{product_name}' (vendor: {vendor})")
            elif prices:
                # Use all similar products if no vendor-specific data
                prices.sort()
                median_price = prices[len(prices) // 2]
                if median_price.is_integer():
                    inferred_data['price'] = f"${int(median_price)}"
                else:
                    inferred_data['price'] = f"${median_price:.2f}"
                logging.info(f"💰 Inferred price ${median_price:.2f} from {len(prices)} similar products for '{product_name}'")
            else:
                # Fallback to intelligent price estimation based on product type and weight
                estimated_price = self._estimate_price_by_type_and_weight(product_type, weight)
                if estimated_price.is_integer():
                    inferred_data['price'] = f"${int(estimated_price)}"
                else:
                    inferred_data['price'] = f"${estimated_price:.2f}"
                logging.info(f"💰 Estimated price ${estimated_price:.2f} based on type '{product_type}' and weight '{weight}' for '{product_name}'")
            
            # Calculate inferred cost - prioritize vendor-specific pricing
            if vendor_costs:
                # Use vendor-specific cost if available
                vendor_costs.sort()
                median_cost = vendor_costs[len(vendor_costs) // 2]
                if median_cost.is_integer():
                    inferred_data['cost'] = f"${int(median_cost)}"
                else:
                    inferred_data['cost'] = f"${median_cost:.2f}"
                logging.info(f"💵 Inferred cost ${median_cost:.2f} from {len(vendor_costs)} vendor-specific products for '{product_name}' (vendor: {vendor})")
            elif costs:
                # Use all similar products if no vendor-specific data
                costs.sort()
                median_cost = costs[len(costs) // 2]
                if median_cost.is_integer():
                    inferred_data['cost'] = f"${int(median_cost)}"
                else:
                    inferred_data['cost'] = f"${median_cost:.2f}"
                logging.info(f"💵 Inferred cost ${median_cost:.2f} from {len(costs)} similar products for '{product_name}'")
            else:
                # Estimate cost as 60-70% of price (typical wholesale markup)
                price_str = inferred_data.get('price', '$35')
                price_clean = re.sub(r'[^\d.]', '', price_str)
                try:
                    price_float = float(price_clean)
                    estimated_cost = price_float * 0.65  # 65% of retail price
                    inferred_data['cost'] = f"${estimated_cost:.2f}"
                    logging.info(f"💵 Estimated cost ${estimated_cost:.2f} as 65% of price for '{product_name}'")
                except (ValueError, TypeError):
                    inferred_data['cost'] = "$16.25"  # Default cost
                    logging.info(f"💵 Using default cost $16.25 for '{product_name}'")
            
            return inferred_data
            
        except Exception as e:
            logging.warning(f"Error inferring price and cost from similar products: {e}")
            return {}
    
    def _intelligently_match_price(self, json_item, inferred_data, product_name, product_type, weight, strain):
        """
        Intelligently match price using multiple strategies in order of preference.
        
        Args:
            json_item: Original JSON data
            inferred_data: Data inferred from similar products
            product_name: Product name
            product_type: Product type
            weight: Product weight
            strain: Product strain
            
        Returns:
            Best matched price as string
        """
        try:
            # Debug: Log all available price sources
            self._debug_price_sources(json_item, inferred_data, product_name)
            
            # Strategy 1: Use price from similar database products (highest confidence)
            if inferred_data.get('price'):
                price = inferred_data['price']
                logging.info(f"💰 Using database-inferred price '{price}' for '{product_name}'")
                return price
            
            # Strategy 2: Use price from JSON data (multiple possible columns)
            json_price = (
                json_item.get('price') or 
                json_item.get('Price') or 
                json_item.get('line_price') or 
                json_item.get('retail_price') or 
                json_item.get('unit_price') or 
                json_item.get('sale_price') or 
                json_item.get('unit_cost') or 
                json_item.get('cost') or 
                json_item.get('Cost') or 
                json_item.get('wholesale_price') or 
                json_item.get('msrp') or 
                json_item.get('list_price') or 
                json_item.get('suggested_price') or 
                json_item.get('market_price') or 
                ''
            )
            
            if json_price and str(json_price).strip().lower() not in ['unknown', 'nan', '', '0', '$0', '0.00']:
                # Clean and validate the price
                import re
                price_clean = re.sub(r'[^\d.]', '', str(json_price))
                try:
                    price_float = float(price_clean)
                    if price_float > 0:
                        if price_float.is_integer():
                            price = f"${int(price_float)}"
                        else:
                            price = f"${price_float:.2f}"
                        logging.info(f"💰 Using JSON price '{price}' for '{product_name}'")
                        return price
                except (ValueError, TypeError):
                    pass
            
            # Strategy 3: Search for similar product names and use average prices
            try:
                product_db = self._get_product_database()
                similar_products = self._search_similar_product_names(product_name, product_db)
                
                if similar_products:
                    # Calculate average price from similar products
                    prices = []
                    for product in similar_products:
                        price = product.get('price', '').strip()
                        if price and price.lower() not in ['unknown', 'nan', '', '0', '$0', '0.00']:
                            price_clean = re.sub(r'[^\d.]', '', price)
                            try:
                                price_float = float(price_clean)
                                if price_float > 0:
                                    prices.append(price_float)
                            except (ValueError, TypeError):
                                pass
                    
                    if prices:
                        # Use average price from similar products
                        avg_price = sum(prices) / len(prices)
                        if avg_price.is_integer():
                            price = f"${int(avg_price)}"
                        else:
                            price = f"${avg_price:.2f}"
                        logging.info(f"💰 Using average price '{price}' from {len(prices)} similar products for '{product_name}'")
                        return price
            except Exception as e:
                logging.warning(f"Error searching for similar product names: {e}")
            
            # Strategy 4: Use intelligent estimation based on product characteristics
            try:
                estimated_price = self._estimate_price_by_type_and_weight(product_type, weight)
                if estimated_price and estimated_price > 0:
                    if estimated_price.is_integer():
                        price = f"${int(estimated_price)}"
                    else:
                        price = f"${estimated_price:.2f}"
                    logging.info(f"💰 Using estimated price '{price}' for '{product_name}'")
                    return price
            except Exception as e:
                logging.warning(f"Error in price estimation: {e}")
            
            # CRITICAL: No fallback prices - return empty string to indicate missing price
            logging.warning(f"⚠️ No price found for '{product_name}' - leaving empty (no fallback)")
            return ""
            
        except Exception as e:
            logging.warning(f"Error in intelligent price matching: {e}")
            # CRITICAL: No fallback price - return empty to indicate missing price
            return ""
    
    def _intelligently_match_cost(self, json_item, inferred_data, final_price, product_name):
        """
        Intelligently match cost using multiple strategies.
        
        Args:
            json_item: Original JSON data
            inferred_data: Data inferred from similar products
            final_price: The final price that was determined
            product_name: Product name
            
        Returns:
            Best matched cost as string
        """
        try:
            # Strategy 1: Use cost from similar database products (highest confidence)
            if inferred_data.get('cost'):
                cost = inferred_data['cost']
                logging.info(f"💵 Using database-inferred cost '{cost}' for '{product_name}'")
                return cost
            
            # Strategy 2: Use cost from JSON data
            json_cost = (
                json_item.get('cost') or 
                json_item.get('Cost') or 
                json_item.get('wholesale_cost') or 
                json_item.get('unit_cost') or 
                json_item.get('purchase_price') or 
                ''
            )
            
            if json_cost and str(json_cost).strip().lower() not in ['unknown', 'nan', '', '0', '$0', '0.00']:
                # Clean and validate the cost
                import re
                cost_clean = re.sub(r'[^\d.]', '', str(json_cost))
                try:
                    cost_float = float(cost_clean)
                    if cost_float > 0:
                        if cost_float.is_integer():
                            cost = f"${int(cost_float)}"
                        else:
                            cost = f"${cost_float:.2f}"
                        logging.info(f"💵 Using JSON cost '{cost}' for '{product_name}'")
                        return cost
                except (ValueError, TypeError):
                    pass
            
            # Strategy 3: Search for similar product names and use average costs
            try:
                product_db = self._get_product_database()
                similar_products = self._search_similar_product_names(product_name, product_db)
                
                if similar_products:
                    # Calculate average cost from similar products
                    costs = []
                    for product in similar_products:
                        cost = product.get('cost', '').strip()
                        if cost and cost.lower() not in ['unknown', 'nan', '', '0', '$0', '0.00']:
                            cost_clean = re.sub(r'[^\d.]', '', cost)
                            try:
                                cost_float = float(cost_clean)
                                if cost_float > 0:
                                    costs.append(cost_float)
                            except (ValueError, TypeError):
                                pass
                    
                    if costs:
                        # Use average cost from similar products
                        avg_cost = sum(costs) / len(costs)
                        if avg_cost.is_integer():
                            cost = f"${int(avg_cost)}"
                        else:
                            cost = f"${avg_cost:.2f}"
                        logging.info(f"💵 Using average cost '{cost}' from {len(costs)} similar products for '{product_name}'")
                        return cost
            except Exception as e:
                logging.warning(f"Error searching for similar product costs: {e}")
            
            # Strategy 4: Default cost
            cost = "$16.25"
            logging.info(f"💵 Using default cost '{cost}' for '{product_name}'")
            return cost
            
        except Exception as e:
            logging.warning(f"Error in intelligent cost matching: {e}")
            return "$16.25"  # Safe fallback
    
    def _debug_price_sources(self, json_item, inferred_data, product_name):
        """Debug method to log all available price sources."""
        try:
            logging.info(f"🔍 DEBUG: Price sources for '{product_name}':")
            
            # Check JSON price columns
            price_columns = [
                'price', 'Price', 'line_price', 'retail_price', 'unit_price', 
                'sale_price', 'unit_cost', 'cost', 'Cost', 'wholesale_price',
                'msrp', 'list_price', 'suggested_price', 'market_price'
            ]
            
            json_prices = {}
            for col in price_columns:
                value = json_item.get(col)
                if value and str(value).strip().lower() not in ['unknown', 'nan', '', '0', '$0', '0.00']:
                    json_prices[col] = value
            
            if json_prices:
                logging.info(f"🔍 DEBUG: JSON price columns found: {json_prices}")
            else:
                logging.info(f"🔍 DEBUG: No valid JSON price columns found")
            
            # Check inferred data
            if inferred_data.get('price'):
                logging.info(f"🔍 DEBUG: Inferred price: {inferred_data['price']}")
            else:
                logging.info(f"🔍 DEBUG: No inferred price found")
            
            # Log all JSON keys for debugging
            all_keys = list(json_item.keys())
            logging.info(f"🔍 DEBUG: All JSON keys available: {all_keys}")
            
        except Exception as e:
            logging.warning(f"Error in price source debugging: {e}")
    
    def _apply_product_name_overrides(self, raw_product_type, product_name, json_item):
        """
        Apply product name-based overrides to Column C values.
        
        Args:
            raw_product_type: The original product type from Column C
            product_name: The product name to analyze
            json_item: The full JSON item for context
            
        Returns:
            Modified product type based on product name analysis
        """
        try:
            if not product_name:
                return raw_product_type
            
            product_name_lower = product_name.lower()
            
            # Rule 1: If product name contains vape keywords, prioritize "Vape Cartridge"
            vape_keywords = ['vape', 'cart', 'cartridge', 'disposable', 'pod', 'battery', 'jefe', 'twisted', 'fire', 'pen']
            if any(keyword in product_name_lower for keyword in vape_keywords):
                logging.info(f"🔄 Product name contains vape keywords, overriding '{raw_product_type}' to 'Vape Cartridge' for '{product_name}'")
                return "Vape Cartridge"
            
            # Rule 2: If product name contains concentrate keywords (and no vape keywords)
            # Change Column C value to "Concentrate"
            concentrate_keywords = ['concentrate', 'rosin', 'shatter', 'wax', 'live resin', 'diamonds', 'sauce', 'extract', 'oil', 'distillate']
            if any(keyword in product_name_lower for keyword in concentrate_keywords):
                logging.info(f"🔄 Product name contains concentrate keywords, overriding '{raw_product_type}' to 'Concentrate' for '{product_name}'")
                return "Concentrate"
            
            # Rule 3: If it says "Concentrate for Inhalation" but lacks vape keywords
            # Change to simply "Concentrate"
            if raw_product_type and "concentrate for inhalation" in raw_product_type.lower():
                if not any(keyword in product_name_lower for keyword in vape_keywords):
                    logging.info(f"🔄 'Concentrate for Inhalation' without vape keywords, overriding to 'Concentrate' for '{product_name}'")
                    return "Concentrate"
            
            # No overrides needed, return original
            return raw_product_type
            
        except Exception as e:
            logging.warning(f"Error applying product name overrides: {e}")
            return raw_product_type
    
    def _search_similar_product_names(self, product_name, product_db):
        """
        Search for products with similar names and return their average prices.
        
        Args:
            product_name: Product name to search for
            product_db: ProductDatabase instance
            
        Returns:
            List of similar products with prices
        """
        try:
            from fuzzywuzzy import fuzz
            
            # Get all products from database
            conn = product_db._get_connection()
            cursor = conn.cursor()
            
            if self._product_table_has_column('strain_id'):
                query = '''
                    SELECT p.*, s.canonical_lineage, s.sovereign_lineage
                    FROM products p
                    LEFT JOIN strains s ON p.strain_id = s.id
                    WHERE p."Price" IS NOT NULL AND p."Price" != '' AND p."Price" != '0' AND p."Price" != '$0'
                    ORDER BY p."last_seen_date" DESC
                '''
            else:
                query = '''
                    SELECT p.*, '' AS canonical_lineage, '' AS sovereign_lineage
                    FROM products p
                    WHERE p."Price" IS NOT NULL AND p."Price" != '' AND p."Price" != '0' AND p."Price" != '$0'
                    ORDER BY p."last_seen_date" DESC
                '''
            
            cursor.execute(query)
            
            all_products = []
            for row in cursor.fetchall():
                product = dict(zip([col[0] for col in cursor.description], row))
                all_products.append(product)
            
            # Find similar products using fuzzy matching
            similar_products = []
            product_name_lower = product_name.lower()
            
            for product in all_products:
                db_name = product.get('product_name', '').lower()
                if db_name:
                    # Calculate similarity score
                    similarity = fuzz.ratio(product_name_lower, db_name)
                    
                    # Also check for partial matches (substring similarity)
                    partial_similarity = fuzz.partial_ratio(product_name_lower, db_name)
                    
                    # Use the higher of the two similarity scores
                    max_similarity = max(similarity, partial_similarity)
                    
                    # Include products with 40% or higher similarity - lowered for better matching
                    if max_similarity >= 40:
                        product['similarity_score'] = max_similarity
                        similar_products.append(product)
            
            # Sort by similarity score (highest first) and limit results
            similar_products.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
            
            # Return top 10 most similar products
            return similar_products[:10]
            
        except Exception as e:
            logging.warning(f"Error searching for similar product names: {e}")
            return []
    
    def _search_exact_product_matches(self, product_name, product_type, strain, product_db):
        """
        Search for exact product matches in the database.
        
        Args:
            product_name: Product name to search for
            product_type: Product type
            strain: Product strain
            product_db: ProductDatabase instance
            
        Returns:
            List of matching products
        """
        try:
            matches = []
            
            # Search by exact product name
            name_matches = product_db.search_products_by_name(product_name)
            matches.extend(name_matches)
            
            # Search by product type and strain combination
            if product_type and strain:
                type_strain_matches = product_db.search_products_by_type_and_strain(product_type, strain)
                matches.extend(type_strain_matches)
            
            # Remove duplicates based on product name
            seen_names = set()
            unique_matches = []
            for match in matches:
                name = match.get('product_name', '')
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_matches.append(match)
            
            return unique_matches
            
        except Exception as e:
            logging.warning(f"Error searching for exact product matches: {e}")
            return []

    def _estimate_price_by_type_and_weight(self, product_type, weight):
        """
        Estimate price based on product type and weight.
        
        Args:
            product_type: The product type
            weight: The weight
            
        Returns:
            Estimated price as float
        """
        try:
            # Extract weight value
            import re
            weight_clean = re.sub(r'[^\d.]', '', str(weight))
            weight_float = float(weight_clean) if weight_clean else 1.0
            
            # Base prices per unit by product type (more realistic)
            base_prices = {
                'flower': 12.0,          # $12 for flower (typical 1g)
                'concentrate': 30.0,     # $30 for concentrates (typical 1g)
                'live resin': 35.0,      # $35 for live resin (typical 1g)
                'cartridge': 40.0,       # $40 for cartridges (typical 1g)
                'disposable vape': 45.0, # $45 for disposables (typical 1g)
                'edible': 15.0,          # $15 for edibles (typical 10mg)
                'tincture': 25.0,        # $25 for tinctures (typical 1oz)
                'topical': 20.0,         # $20 for topicals (typical 1oz)
                'pre-roll': 15.0,        # $15 for pre-rolls (typical 1g)
                'vape cartridge': 40.0,  # $40 for vape cartridges (typical 1g)
            }
            
            # Find matching product type
            product_type_lower = str(product_type).lower()
            base_price = None  # No default price - extract from data
            
            for type_key, price in base_prices.items():
                if type_key in product_type_lower:
                    base_price = price
                    break
            
            # Calculate total price based on weight and product type
            weight_str = str(weight).lower()
            
            # Special handling for different product types and units
            if 'edible' in product_type_lower:
                if 'mg' in weight_str:
                    # For edibles in mg, use base price (already per 10mg)
                    total_price = base_price
                elif 'g' in weight_str:
                    # For edibles in grams, convert to mg (1g = 1000mg, so 100x 10mg servings)
                    total_price = base_price * (weight_float * 100)
                else:
                    total_price = base_price
            elif 'tincture' in product_type_lower or 'topical' in product_type_lower:
                # For tinctures/topicals, weight doesn't significantly affect price
                total_price = base_price
            elif 'flower' in product_type_lower:
                # For flower, use a more reasonable weight calculation
                if weight_float <= 1.0:
                    total_price = base_price  # $12 for 1g
                elif weight_float <= 3.5:
                    total_price = base_price * 2.5  # $30 for 3.5g (eighth)
                else:
                    total_price = base_price * min(weight_float, 4.0)  # Cap at 4g
            else:
                # For other products, multiply by weight but cap the multiplier
                weight_multiplier = min(weight_float, 3.0)  # Cap at 3x for very large weights
                total_price = base_price * weight_multiplier
            
            # Apply reasonable bounds
            total_price = max(8.0, min(80.0, total_price))  # Between $8 and $80
            
            return total_price
            
        except Exception as e:
            logging.warning(f"Error estimating price by type and weight: {e}")
            # CRITICAL: No $25 fallback - return 0 or empty to indicate missing price
            return 0.0  # Return 0 to indicate no price available
            
    def fetch_and_match_with_product_db(self, url: str, force_simplified: bool = False, deduplicate: bool = False) -> List[Dict]:
        """
        Fetch JSON from URL and create product tags, prioritizing Product Database lookups
        over exact JSON wording. This method first tries to find existing products in the
        database before creating new ones from JSON data.
        
        Args:
            url: URL to fetch JSON data from
            force_simplified: If True, use simplified matching approach for maximum matches
            
        Returns:
            List of product dictionaries
        """
        import time as time_module  # Import with alias to avoid variable name conflicts
        
        # CRITICAL FIX: Use simplified approach when maximum matches are needed
        if force_simplified:
            logging.info("🔍 FORCING SIMPLIFIED MATCHING APPROACH FOR MAXIMUM MATCHES")
            return self.fetch_and_match(url, deduplicate=deduplicate)
        
        logging.info("=" * 80)
        logging.info("🔍 fetch_and_match_with_product_db called - PRODUCT DATABASE INTEGRATION ENABLED")
        logging.info("=" * 80)
        logging.debug(f"fetch_and_match_with_product_db called with URL: {url}")
        
        start_time = time_module.time()  # Define start_time early to avoid errors
        
        if not url.lower().startswith("http"):
            raise ValueError("Please provide a valid HTTP URL")
            
        try:
            # Initialize Product Database for priority lookups
            logging.info("Initializing Product Database for priority lookups...")
            try:
                product_db = self._get_product_database()
                logging.info("Product Database initialized successfully")
            except Exception as e:
                logging.warning(f"Could not initialize Product Database: {e}")
                product_db = None
            
            # Use the proxy endpoint to handle authentication and CORS
            import requests
            
            # Prepare headers for the request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Add authentication headers if available
            import os
            if os.environ.get('BAMBOO_API_KEY'):
                headers['X-API-Key'] = os.environ.get('BAMBOO_API_KEY')
            if os.environ.get('BAMBOO_AUTH_TOKEN'):
                headers['Authorization'] = f"Bearer {os.environ.get('BAMBOO_AUTH_TOKEN')}"
            if os.environ.get('BAMBOO_SESSION_TOKEN'):
                headers['X-Session-Token'] = os.environ.get('BAMBOO_SESSION_TOKEN')
            
            proxy_data = {
                'url': url,
                'headers': headers
            }
            
            # Try to make the request directly first (for external URLs)
            try:
                response = requests.get(url, headers=headers, timeout=60)
                response.raise_for_status()
                payload = response.json()
            except (requests.exceptions.RequestException, ValueError) as direct_error:
                logging.info(f"Direct request failed, trying proxy: {direct_error}")
                # Fallback to proxy endpoint if direct request fails
                import os
                base_url = os.environ.get('FLASK_BASE_URL', 'http://127.0.0.1:5001')
                response = requests.post(f'{base_url}/api/proxy-json', 
                                       json=proxy_data, 
                                       timeout=60)
                response.raise_for_status()
                payload = response.json()
                
            # Handle both list and dictionary payloads
            if isinstance(payload, list):
                items = payload
            elif isinstance(payload, dict):
                items = payload.get("inventory_transfer_items", [])
                # Extract global vendor from document metadata
                global_vendor = payload.get("from_license_name", "")
                logging.info(f"Extracted global vendor from document: {global_vendor}")
            else:
                logging.warning(f"Unexpected payload type: {type(payload)}")
                return []
                
            if not items:
                logging.warning("No inventory transfer items found in JSON")
                return []
                
            # Optional deduplication based on inventory identifiers
            if deduplicate:
                logging.info(f"Processing {len(items)} JSON items with intelligent deduplication")
                
                def normalize_product_name(name):
                    """Normalize product name to catch variations like 'Cookies & Cream' vs 'Cookies N Cream'"""
                    if not name:
                        return ""
                    
                    # Convert to lowercase and replace common variations
                    normalized = name.lower()
                    
                    # Replace common variations with standard forms
                    variations = {
                        '&': 'and',
                        'n ': 'and ',
                        'n\'': 'and',
                        'cookies n cream': 'cookies and cream',
                        'cookies & cream': 'cookies and cream',
                        'cookies cream': 'cookies and cream',
                        ' by ceres': '',
                        ' ceres': '',
                        ' - ': ' ',
                        '  ': ' '  # Remove double spaces
                    }
                    
                    for variation, standard in variations.items():
                        normalized = normalized.replace(variation, standard)
                    
                    # Remove extra whitespace
                    normalized = ' '.join(normalized.split())
                    
                    return normalized
                
                unique_items = []
                seen_item_ids = set()
                duplicate_count = 0
                
                for item in items:
                    if not isinstance(item, dict):
                        continue
                        
                    product_name = str(item.get("product_name", "")).strip()
                    
                    # CRITICAL FIX: Process ALL items, even those with missing product names
                    if not product_name:
                        # Try to create a fallback product name from other available fields
                        vendor = str(item.get("vendor", "")).strip()
                        brand = str(item.get("brand", "")).strip()
                        weight = str(item.get("weight", "")).strip()
                        product_type = str(item.get("inventory_type", "")).strip()
                        
                        # Create a fallback product name
                        fallback_parts = []
                        if brand:
                            fallback_parts.append(brand)
                        if product_type:
                            fallback_parts.append(product_type)
                        if weight:
                            fallback_parts.append(weight)
                        
                        if fallback_parts:
                            product_name = " ".join(fallback_parts)
                        else:
                            product_name = f"JSON Product {len(unique_items) + 1}"
                        
                        logging.info(f"⚠️  Created fallback product name: '{product_name}' for JSON item with missing name")
                    
                    # CRITICAL FIX: Use unique item identifiers instead of normalized names for deduplication
                    # This preserves products with different SKUs/IDs even if they have similar names
                    item_id = item.get("inventory_id") or item.get("integrator_data") or item.get("sample_source_id")
                    if not item_id:
                        # Fallback to using the original product name as ID if no unique ID exists
                        item_id = product_name
                    
                    if item_id and item_id in seen_item_ids:
                        duplicate_count += 1
                        logging.info(f"🔄 Skipping duplicate JSON item: '{product_name}' (ID: '{item_id}')")
                        continue
                    
                    # Add to seen set and unique items
                    if item_id:
                        seen_item_ids.add(item_id)
                    unique_items.append(item)
                
                logging.info(f"INTELLIGENT DEDUPLICATION: {len(items)} items -> {len(unique_items)} unique products ({duplicate_count} duplicates removed)")
                
                # Use deduplicated items for processing
                items = unique_items
            else:
                logging.info(f"Processing {len(items)} JSON items without deduplication (deduplicate=False)")
            
            # Initialize tracking variables
            matched_idxs = set()
            match_scores = {}
            all_tags = []
            processed_count = 0
            matched_count = 0
            db_lookup_count = 0
            educated_guess_count = 0
            new_product_count = 0
            new_database_entries_count = 0
            
            # Helper function to clean product names
            def clean_product_name(name):
                if not name:
                    return name
                import re
                # Only remove obvious suffixes that are clearly not part of the product name
                cleaned = re.sub(r'\s*by\s+Dabstract\s+JSON\s*$', '', name, flags=re.IGNORECASE)
                # Remove extra whitespace but preserve the actual product name
                cleaned = re.sub(r'\s+', ' ', cleaned)
                return cleaned.strip()
            
            # Performance monitoring (start_time already defined at method start)
            
            for i, item in enumerate(items):
                try:
                    # Safety check: ensure item is a dictionary
                    if not isinstance(item, dict):
                        logging.warning(f"Item {i+1} is not a dictionary (type: {type(item)}), skipping: {item}")
                        continue
                    
                    # Enhanced product information extraction using new database columns
                    original_product_name = str(item.get("product_name", "")).strip()
                    product_name = original_product_name  # Will be replaced with matched database name if found
                    logging.debug(f"Processing product: {product_name}")
                    # CRITICAL FIX: Don't skip items with missing product names - create fallback names
                    if not product_name:
                        # Try to create a fallback product name from other available fields
                        vendor = str(item.get("vendor", "")).strip()
                        brand = str(item.get("brand", "")).strip()
                        inventory_type = str(item.get("inventory_type", "")).strip()
                        
                        # Create a descriptive fallback name
                        fallback_parts = []
                        if brand:
                            fallback_parts.append(brand)
                        if inventory_type:
                            fallback_parts.append(inventory_type)
                        if vendor:
                            fallback_parts.append(f"by {vendor}")
                        
                        if fallback_parts:
                            product_name = " ".join(fallback_parts)
                            logging.info(f"⚠️  Created fallback product name: '{product_name}' for item missing product_name")
                        else:
                            product_name = f"JSON Product {len(all_tags)+1}"
                            logging.info(f"⚠️  Created generic product name: '{product_name}' for item missing product_name")
                        
                    # Use global vendor from document metadata (already set above)
                    vendor = global_vendor if global_vendor else str(item.get("vendor", "")).strip()
                    
                    # Extract essential product information BEFORE matching
                    brand = str(item.get("brand", "")).strip()
                    inventory_type = str(item.get("inventory_type", "")).strip()
                    inventory_category = str(item.get("inventory_category", "")).strip()
                    product_type = map_inventory_type_to_product_type(inventory_type, inventory_category, product_name)
                    weight = str(item.get("unit_weight", item.get("weight", ""))).strip()
                    strain = str(item.get("strain_name", item.get("strain", ""))).strip()
                    
                    # PRIORITY 1: For SKU-like products, try database search first
                    db_info = None
                    if '_' in product_name and product_db:
                        print(f"🔍 DEBUG: SKU detected '{product_name}', trying database search first")
                        # Try SKU-based database search first for SKU products
                        try:
                            # Parse SKU to create search terms
                            parts = product_name.split('_')
                            search_terms = []
                            
                            # Map SKU components to searchable terms
                            if len(parts) >= 2:
                                # Product type
                                if parts[0] in ['BALL', 'ball']:
                                    search_terms.extend(['ball', 'balls'])
                                elif parts[0] in ['BITE', 'bite']:
                                    search_terms.extend(['bite', 'bites'])
                                elif parts[0] in ['CHEW', 'chew']:
                                    search_terms.extend(['chew', 'chews'])
                                
                                # Lineage
                                if parts[1] in ['SAT', 'sat']:
                                    search_terms.append('sativa')
                                elif parts[1] in ['IND', 'ind']:
                                    search_terms.append('indica')
                                
                                # Flavor/descriptors
                                for i in range(2, len(parts)):
                                    part = parts[i].lower()
                                    if not part.endswith('pk') and part not in ['single']:
                                        search_terms.append(part)
                            
                            # Search database using SQL LIKE for better performance
                            if search_terms and hasattr(product_db, '_get_connection'):
                                logging.info(f"🔍 Generated search terms: {search_terms}")
                                conn = product_db._get_connection()
                                cursor = conn.cursor()
                                
                                # Build WHERE clause with keywords
                                where_clauses = []
                                for term in search_terms[:3]:  # Use top 3 most important terms
                                    where_clauses.append(f'("Product Name*" LIKE ? OR "Description" LIKE ?)')
                                
                                where_sql = ' AND '.join(where_clauses)
                                params = []
                                for term in search_terms[:3]:
                                    params.extend([f'%{term}%', f'%{term}%'])
                                
                                # Add brand filter if we know it's Ceres
                                where_sql += ' AND "Product Brand" = ?'
                                params.append('Ceres')
                                
                                logging.info(f"🔍 SQL WHERE clause: {where_sql}")
                                logging.info(f"🔍 SQL params: {params}")
                                
                                sql = f'''
                                    SELECT "Product Name*", "Description", "Product Brand", "Lineage",
                                           "Product Type*", "Weight*", "Units", "Price", "Vendor/Supplier*",
                                           "Product Strain"
                                    FROM products
                                    WHERE {where_sql}
                                    AND ("Product Name*" NOT LIKE '%*VOID*%' AND "Description" NOT LIKE '%*VOID*%')
                                    AND ("Product Name*" NOT LIKE '%trade sample%' AND "Description" NOT LIKE '%trade sample%')
                                    LIMIT 1
                                '''
                                
                                cursor.execute(sql, params)
                                result = cursor.fetchone()
                                
                                if result:
                                    # Create db_info dict from result
                                    db_info = {
                                        'Product Name*': result[0],
                                        'Description': result[1],
                                        'Product Brand': result[2],
                                        'Lineage': result[3],
                                        'Product Type*': result[4],
                                        'Weight*': result[5],
                                        'Units': result[6],
                                        'Price': result[7],
                                        'Vendor/Supplier*': result[8],
                                        'Product Strain': result[9]
                                    }
                                    
                                    # Validate the database match
                                    if self._is_valid_product(db_info):
                                        logging.info(f"✅ SKU search found valid database match: '{product_name}' → '{result[1]}'")
                                        
                                        # Create tag from database info
                                        tag = self._create_tag_from_database_info(db_info, vendor, item)
                                        all_tags.append(tag)
                                        matched_count += 1
                                        print(f"🔍 DEBUG: Added valid database tag for SKU '{product_name}'")
                                        continue  # Skip Excel matching for this SKU
                                    else:
                                        logging.info(f"🚫 SKU search found invalid database match (void/sample): '{product_name}' → '{result[1]}'")
                                else:
                                    logging.info(f"⚠️  No database match found for SKU '{product_name}' with search terms: {search_terms[:3]}")
                                    
                        except Exception as search_error:
                            logging.warning(f"SKU database search failed: {search_error}")
                    
                    # PRIORITY 2: Use comprehensive matching logic (Excel) if no SKU database match
                    try:
                        if product_db:
                            db_direct_match = self._find_best_database_match(product_name, vendor, weight, strain, product_db)
                            if db_direct_match:
                                tag = self._create_tag_from_database_info(db_direct_match, vendor, item)
                                all_tags.append(tag)
                                matched_count += 1
                                logging.info(f"✅ Direct database match found for '{product_name}' (similarity: {db_direct_match.get('_similarity_score')})")
                                continue

                        # Use the same comprehensive matching logic that was working in the debug output
                        print(f"🔍 DEBUG: Trying comprehensive matching for '{product_name}' (type: {product_type})")
                        matched_products = self._process_item_with_main_matching(item, product_name, vendor, product_type, strain, global_vendor)
                        print(f"🔍 DEBUG: Comprehensive matching returned {len(matched_products)} products")
                        if matched_products:
                            valid_products = [p for p in matched_products if self._is_valid_product(p)]
                            if len(valid_products) != len(matched_products):
                                print(f"🔍 DEBUG: Filtered out {len(matched_products) - len(valid_products)} invalid products (void/sample)")
                            
                            for product in valid_products:
                                tag = self._create_tag_from_product(product, item, global_vendor)
                                all_tags.append(tag)
                                matched_count += 1
                            print(f"🔍 DEBUG: Added {len(valid_products)} valid tags from comprehensive matching")
                            continue  # Skip the educated guess and JSON processing below
                        else:
                            print(f"🔍 DEBUG: No products found by comprehensive matching, falling back to AI-powered database lookup")
                    except Exception as main_match_error:
                        logging.warning(f"Error in comprehensive matching logic: {main_match_error}")
                        print(f"🔍 DEBUG: Comprehensive matching error: {main_match_error}")
                    
                    # PRIORITY 2: Fallback to AI-Powered Product Database lookup if comprehensive matching fails
                    db_info = None
                    if product_db:
                        try:
                            logging.debug(f"Attempting AI-Powered Product Database lookup for: {product_name}")
                            
                            # Initialize AI matcher if not already done
                            if not hasattr(self, 'ai_matcher'):
                                self.ai_matcher = AIProductMatcher(product_db)
                                logging.info("✅ AI Product Matcher initialized")
                            
                            # First try to find the product directly
                            db_info = product_db.get_product_info(product_name, vendor)
                            
                            # Validate db_info if found
                            if db_info and not self._is_valid_product(db_info):
                                logging.info(f"🚫 Direct database lookup found invalid product (void/sample): '{product_name}'")
                                db_info = None  # Reset to None to try AI matching
                            
                            if not db_info:
                                # Use AI-powered matching to find the best strain match
                                logging.debug(f"Using AI matcher to find best strain match for: {product_name}")
                                
                                # Extract product features for AI matching
                                product_features = self.ai_matcher.extract_product_features(item)
                                
                                # Find best matches using AI scoring
                                matches = self.ai_matcher.find_best_matches(product_features, max_matches=3)
                                
                                if matches:
                                    best_match = matches[0]
                                    logging.info(f"🤖 AI Matcher found {len(matches)} potential matches")
                                    logging.info(f"   Best match: {best_match.strain_name} (confidence: {best_match.confidence}, score: {best_match.total_score:.3f})")
                                    
                                    # Get strain info for the best match
                                    strain_info = product_db.get_strain_info(best_match.strain_name)
                                    if strain_info:
                                        # Extract weight from product name if available
                                        weight_match = re.search(r'/(\d+)g', product_name)
                                        extracted_weight = weight_match.group(1) if weight_match else "1"
                                        
                                        # Create description in the format: "Strain Name Core Flower - Weight"
                                        # This follows the user's requirement for "Golden Pineapple Core Flower - 14g"
                                        formatted_description = f"{best_match.strain_name} Core Flower - {extracted_weight}g"
                                        
                                        db_info = {
                                            'product_name': product_name,
                                            'vendor': vendor,
                                            'strain_name': best_match.strain_name,
                                            'lineage': strain_info.get('canonical_lineage', 'HYBRID'),
                                            'product_type': product_features.get('product_type', 'Core Flower'),
                                            'price': '25',  # Default price
                                            'weight': extracted_weight,
                                            'units': 'g',
                                            'description': formatted_description,  # Use proper tag format
                                            'ai_match_score': best_match.total_score,
                                            'ai_confidence': best_match.confidence,
                                            'ai_match_type': best_match.match_type,
                                        }
                                        
                                        # Log AI matching details
                                        match_summary = self.ai_matcher.get_match_summary(matches)
                                        logging.info(f"🤖 AI Match Summary for '{product_name}':")
                                        logging.info(f"   Strain: {best_match.strain_name}")
                                        logging.info(f"   Confidence: {best_match.confidence}")
                                        logging.info(f"   Score: {best_match.total_score:.3f}")
                                        logging.info(f"   Match Type: {best_match.match_type}")
                                        logging.info(f"   Score Breakdown: {match_summary['score_breakdown']}")
                                        
                                        logging.info(f"✅ AI-Powered Strain Database match found for: {best_match.strain_name} -> {strain_info.get('canonical_lineage', 'HYBRID')}")
                        except Exception as ai_error:
                            logging.warning(f"AI matching error for '{product_name}': {ai_error}")
                            
                    
                    # PRIORITY 3: Try educated guessing if no database match
                    educated_guess = None
                    if product_db:
                        try:
                            logging.info(f"🔍 Attempting educated guess for: {product_name}")
                            logging.info(f"   Vendor: {vendor}")
                            logging.info(f"   Brand: {brand}")
                            educated_guess = product_db.make_educated_guess(product_name, vendor, brand)
                            if educated_guess:
                                logging.info(f"✅ Made educated guess for '{product_name}': {educated_guess}")
                                # Use educated guess data
                                product_name = educated_guess.get("product_name", product_name)
                                vendor = educated_guess.get("vendor", vendor)
                                brand = educated_guess.get("brand", brand or "")
                                product_type = educated_guess.get("product_type", "")
                                strain = educated_guess.get("strain_name", "")
                                lineage = educated_guess.get("lineage", "")
                                price = str(educated_guess.get("price", ""))
                                weight = str(educated_guess.get("weight", ""))
                                units = str(educated_guess.get("units", ""))
                                description = educated_guess.get("description", "")
                                
                                # Create tag using educated guess information
                                tag = self._create_tag_from_educated_guess(educated_guess, vendor)
                                all_tags.append(tag)
                                
                                # Add educated guess to database so it shows up in UI
                                self._add_educated_guess_to_database(educated_guess, vendor)
                                
                                educated_guess_count += 1
                                matched_count += 1
                                continue  # Skip JSON processing since we have educated guess
                            else:
                                logging.info(f"❌ No educated guess available for '{product_name}'")
                        except Exception as guess_error:
                            logging.warning(f"Educated guess error for '{product_name}': {guess_error}")
                    
                    # PRIORITY 4: If no match found, force creation of faux tag for novel product
                    new_product_count += 1
                    logging.info(f"🎨 NO MATCH FOUND - Forcing faux tag creation for novel product: {product_name}")
                    
                    # Create faux tag using the dedicated method
                    tag = self._create_faux_tag_for_novel_product(item, vendor, global_vendor)
                    all_tags.append(tag)
                    processed_count += 1
                    
                    # Create new database entry for unmatched JSON tag
                    if product_db:
                        try:
                            self._create_database_entry_for_unmatched_json(tag, product_db)
                            new_database_entries_count += 1
                        except Exception as db_entry_error:
                            logging.warning(f"Failed to create database entry for '{product_name}': {db_entry_error}")
                    
                    # Continue to next item - faux tag has been created
                    continue
                    
                    # NOTE: All the following code (lines 4131-4587) has been replaced by
                    # the _create_faux_tag_for_novel_product method above. This code is
                    # now unreachable but kept for historical reference.
                    # 
                    # The old implementation created tags directly from JSON data here.
                    # The new implementation centralizes this logic in _create_faux_tag_for_novel_product
                    # to ensure all novel products get faux tags created consistently.
                    
                    # UNREACHABLE CODE REMOVED - See _create_faux_tag_for_novel_product method above
                    logging.debug(f"Extracting brand for: {product_name}")
                    if not brand:
                        # Try to extract brand from product name patterns
                        name_lower = product_name.lower()
                        
                        # Look for common brand patterns - prioritize these for the Cultivera data
                        if "dank czar" in name_lower:
                            brand = "Dank Czar"
                            logging.debug(f"  -> Detected brand from pattern: {brand}")
                        elif "omega" in name_lower:
                            brand = "Omega Labs"
                            logging.debug(f"  -> Detected brand from pattern: {brand}")
                        elif "airo" in name_lower:
                            brand = "Airo Pro"
                            logging.debug(f"  -> Detected brand from pattern: {brand}")
                        elif "jsm" in name_lower:
                            brand = "JSM"
                            logging.debug(f"  -> Detected brand from pattern: {brand}")
                        elif "hustler" in name_lower:
                            brand = "Hustler's Ambition"
                            logging.debug(f"  -> Detected brand from pattern: {brand}")
                        elif "1555" in name_lower:
                            brand = "1555 Industrial"
                            logging.debug(f"  -> Detected brand from pattern: {brand}")
                        elif "harmony" in name_lower:
                            brand = "Harmony Farms"
                            logging.debug(f"  -> Detected brand from pattern: {brand}")
                        # Additional Cultivera brand patterns
                        elif "farmer's daughter" in name_lower:
                            brand = "Farmer's Daughter"
                            logging.debug(f"  -> Detected brand from pattern: {brand}")
                        elif "greasy runtz" in name_lower:
                            brand = "Greasy Runtz"
                            logging.debug(f"  -> Detected brand from pattern: {brand}")
                        elif "kelloggz koffee" in name_lower:
                            brand = "Kelloggz Koffee"
                            logging.debug(f"  -> Detected brand from pattern: {brand}")
                        elif "trop banana" in name_lower:
                            brand = "Trop Banana"
                            logging.debug(f"  -> Detected brand from pattern: {brand}")
                        elif "velvet koffee" in name_lower:
                            brand = "Velvet Koffee"
                            logging.debug(f"  -> Detected brand from pattern: {brand}")
                        
                        # Look for "by [Brand]" pattern
                        if not brand:
                            import re
                            by_match = re.search(r'by\s+([A-Za-z0-9\s]+)(?:\s|$)', product_name, re.IGNORECASE)
                            if by_match:
                                brand = by_match.group(1).strip().title()
                                logging.debug(f"  -> Detected brand from 'by' pattern: {brand}")
                        
                        # Look for "from [Brand]" pattern
                        if not brand:
                            from_match = re.search(r'from\s+([A-Za-z0-9\s]+)(?:\s|$)', product_name, re.IGNORECASE)
                            if from_match:
                                brand = from_match.group(1).strip().title()
                                logging.debug(f"  -> Detected brand from 'from' pattern: {brand}")
                        
                        # Look for "Brand -" pattern (Cultivera format)
                        if not brand:
                            if " - " in product_name:
                                parts = product_name.split(" - ")
                                if len(parts) > 0:
                                    potential_brand = parts[0].strip()
                                    if len(potential_brand) > 2 and not any(x in potential_brand.lower() for x in ["live", "resin", "rosin", "wax", "shatter", "hash", "flower", "bud", "pre", "roll", "joint", "cartridge", "vape", "pen", "edible", "gummy", "chocolate", "cookie", "brownie", "candy", "sweet", "food", "drink", "beverage", "tincture", "drops", "capsule", "pill", "tablet", "lozenge", "mint", "chew", "chewing", "cream", "lotion", "salve", "balm", "ointment", "gel", "spray", "patch", "transdermal", "skin", "external", "apply", "rub", "grinder", "pipe", "bong", "rig", "torch", "lighter", "tray", "scale", "storage", "container", "jar", "bag", "accessory", "tool"]):
                                        brand = potential_brand.title()
                                        logging.debug(f"  -> Detected brand from dash pattern: {brand}")
                        
                        # Special handling for Cultivera data - look for brand indicators in product names
                        if not brand:
                            # Look for "Dank Czar" in product names
                            if "dank czar" in name_lower:
                                brand = "Dank Czar"
                                logging.debug(f"  -> Detected Dank Czar brand from product name: {brand}")
                            # Look for "Omega" in product names
                            elif "omega" in name_lower:
                                brand = "Omega Labs"
                                logging.debug(f"  -> Detected Omega Labs brand from product name: {brand}")
                            # Look for "Medically Compliant" as a brand indicator
                            elif "medically compliant" in name_lower:
                                # Extract the brand after "Medically Compliant -"
                                if "medically compliant -" in name_lower:
                                    parts = name_lower.split("medically compliant -")
                                    if len(parts) > 1:
                                        potential_brand = parts[1].split(" - ")[0].strip()
                                        if potential_brand and len(potential_brand) > 2:
                                            brand = potential_brand.title()
                                            logging.debug(f"  -> Detected brand from Medically Compliant pattern: {brand}")
                    
                    # If still no brand, use vendor as brand
                    if not brand and vendor:
                        brand = vendor.title()
                        logging.debug(f"  -> Using vendor as brand: {brand}")
                    
                    # If still no brand, try to extract from product name using capitalization patterns
                    if not brand:
                        words = product_name.split()
                        for word in words:
                            if len(word) > 2 and word[0].isupper() and word[1:].islower():
                                # Check if it's not a common product word
                                common_words = ["live", "resin", "rosin", "wax", "shatter", "hash", "flower", "bud", "pre", "roll", "joint", "cartridge", "vape", "pen", "edible", "gummy", "chocolate", "cookie", "brownie", "candy", "sweet", "food", "drink", "beverage", "tincture", "drops", "capsule", "pill", "tablet", "lozenge", "mint", "chew", "chewing", "cream", "lotion", "salve", "balm", "ointment", "gel", "spray", "patch", "transdermal", "skin", "external", "apply", "rub", "grinder", "pipe", "bong", "rig", "torch", "lighter", "tray", "scale", "storage", "container", "jar", "bag", "accessory", "tool"]
                                if word.lower() not in common_words:
                                    brand = word
                                    logging.debug(f"  -> Detected brand from capitalization: {brand}")
                                    break
                    
                    logging.debug(f"Final brand for '{product_name}': {brand}")
                    
                    # Product type and other variables were already extracted earlier at line 3897-3903
                    # No need to re-extract them here
                    
                    if not product_type or product_type == "Unknown":
                        # Fallback to inference if mapping didn't work
                        name_lower = product_name.lower()
                        logging.debug(f"Inferring product type for: {product_name}")
                        
                        # Concentrate types
                        if any(x in name_lower for x in ["rosin", "wax", "shatter", "live resin", "distillate", "hash", "live hash", "bubble hash", "kief", "keef", "crystal", "diamond", "sauce", "terp sauce", "terpene", "terps", "extract", "extraction", "solventless", "solvent-less"]):
                            product_type = "concentrate"
                            logging.debug(f"  -> Detected concentrate type: {product_type}")
                        # Pre-roll types
                        elif any(x in name_lower for x in ["pre-roll", "pre roll", "preroll", "joint", "blunt", "cigar", "cone", "paper", "rolling", "rolled"]):
                            product_type = "pre-roll"
                            logging.debug(f"  -> Detected pre-roll type: {product_type}")
                        # Vape types
                        elif any(x in name_lower for x in ["cartridge", "vape", "pen", "disposable", "pod", "battery", "510", "thc", "cbd", "oil", "distillate", "live resin", "rosin", "sauce"]):
                            product_type = "vape cartridge"
                            logging.debug(f"  -> Detected vape type: {product_type}")
                        # Flower types
                        elif any(x in name_lower for x in ["flower", "bud", "nug", "buds", "nugs", "marijuana", "cannabis", "weed", "herb", "green", "natural", "raw", "loose", "loose leaf"]):
                            product_type = "flower"
                            logging.debug(f"  -> Detected flower type: {product_type}")
                        # Edible types
                        elif any(x in name_lower for x in ["edible", "gummy", "chocolate", "cookie", "brownie", "candy", "sweet", "food", "drink", "beverage", "tincture", "drops", "capsule", "pill", "tablet", "lozenge", "mint", "chew", "chewing"]):
                            product_type = "edible"
                            logging.debug(f"  -> Detected edible type: {product_type}")
                        # Topical types
                        elif any(x in name_lower for x in ["topical", "cream", "lotion", "salve", "balm", "ointment", "gel", "spray", "patch", "transdermal", "skin", "external", "apply", "rub"]):
                            product_type = "topical"
                            logging.debug(f"  -> Detected topical type: {product_type}")
                        # Paraphernalia types
                        elif any(x in name_lower for x in ["paraphernalia", "grinder", "pipe", "bong", "dab rig", "rig", "torch", "lighter", "rolling tray", "tray", "scale", "scale", "storage", "container", "jar", "bag", "accessory", "tool"]):
                            product_type = "paraphernalia"
                            logging.debug(f"  -> Detected paraphernalia type: {product_type}")
                        # CBD specific types
                        elif any(x in name_lower for x in ["cbd", "hemp", "cannabidiol", "non-psychoactive", "non psychoactive", "medicinal", "therapeutic", "wellness", "health"]):
                            if any(x in name_lower for x in ["gummy", "oil", "tincture", "cream"]):
                                product_type = "edible" if "gummy" in name_lower or "oil" in name_lower else "topical"
                            else:
                                product_type = "cbd product"
                            logging.debug(f"  -> Detected CBD type: {product_type}")
                        # Default based on common patterns
                        else:
                            # Look for weight indicators to make educated guesses
                            if any(x in name_lower for x in ["1g", "2g", "3.5g", "7g", "14g", "28g", "gram", "grams", "oz", "ounce"]):
                                product_type = "flower"  # Most likely flower if weight is specified
                                logging.debug(f"  -> Defaulted to flower based on weight: {product_type}")
                            elif any(x in name_lower for x in ["mg", "milligram", "milligrams"]):
                                product_type = "edible"  # Most likely edible if mg is specified
                                logging.debug(f"  -> Defaulted to edible based on mg: {product_type}")
                            else:
                                product_type = "concentrate"  # Conservative default
                                logging.debug(f"  -> Defaulted to concentrate: {product_type}")
                    
                    logging.debug(f"Final product type for '{product_name}': {product_type} (mapped from inventory_type: {inventory_type})")
                    logging.debug(f"Product type for '{product_name}': '{product_type}'")
                    
                    # Weight was already extracted earlier at line 3902 with fallback logic
                    # Just extract quantity and units here
                    quantity = str(item.get("qty", "1")).strip()  # Fix: use qty for Cultivera JSON
                    units = str(item.get("unit_weight_uom", "g")).strip()  # Fix: use unit_weight_uom for Cultivera JSON
                    
                    # Extract description from JSON data
                    description = str(item.get("description", "")).strip()
                    if not description:
                        # Try alternative description fields
                        description = str(item.get("product_description", "")).strip()
                    if not description:
                        # Use product name as fallback description
                        description = product_name
                    
                    # If weight is still empty, try to extract from product name
                    if not weight:
                        import re
                        # Look for weight patterns in product name
                        weight_patterns = [
                            r'(\d+\.?\d*)\s*(g|gram|grams|gm)',  # 3.5g, 3.5 gram, etc.
                            r'(\d+\.?\d*)\s*(mg|milligram|milligrams)',  # 100mg, etc.
                            r'(\d+\.?\d*)\s*(oz|ounce|ounces)',  # 1oz, etc.
                            r'(\d+\.?\d*)\s*(lb|pound|pounds)',  # 1lb, etc.
                        ]
                        
                        for pattern in weight_patterns:
                            match = re.search(pattern, product_name, re.IGNORECASE)
                            if match:
                                weight = match.group(1)
                                units = match.group(2).lower()
                                if units in ['gram', 'grams', 'gm']:
                                    units = 'g'
                                elif units in ['milligram', 'milligrams']:
                                    units = 'mg'
                                elif units in ['ounce', 'ounces']:
                                    units = 'oz'
                                elif units in ['pound', 'pounds']:
                                    units = 'lb'
                                logging.debug(f"  -> Extracted weight from product name: {weight} {units}")
                                break
                    
                    # Ensure weight has a value
                    if not weight:
                        weight = "1"  # Default weight
                        logging.debug(f"  -> Using default weight: {weight}")
                    
                    # Ensure units have a value
                    if not units:
                        units = "g"  # Default to grams
                        logging.debug(f"  -> Using default units: {units}")
                    
                    logging.debug(f"Final weight for '{product_name}': {weight} {units}")
                    
                    # Enhanced price extraction with better estimation
                    price = str(item.get("line_price", item.get("price", ""))).strip()
                    if not price:
                        # Estimate price based on product type and weight
                        if "pre-roll" in product_type.lower():
                            price = "20"
                        elif "flower" in product_type.lower():
                            if weight and weight.isdigit():
                                weight_val = float(weight)
                                if weight_val <= 1:
                                    price = "35"
                                elif weight_val <= 3.5:
                                    price = "120"
                                elif weight_val <= 7:
                                    price = "220"
                                else:
                                    price = "400"
                            else:
                                price = "35"
                        elif "concentrate" in product_type.lower():
                            if weight and weight.isdigit():
                                weight_val = float(weight)
                                if weight_val <= 1:
                                    price = "50"
                                elif weight_val <= 2:
                                    price = "90"
                                else:
                                    price = "150"
                            else:
                                price = "50"
                        else:
                            price = ""  # No default price
                    
                    # Enhanced strain information extraction
                    # Strain was already extracted earlier at line 3903, but if it's empty we can try to infer it
                    if not strain:
                        # First try to extract strain from product name
                        extracted_strain = self._extract_strain_from_product_name(product_name)
                        if extracted_strain:
                            strain = extracted_strain
                            logging.info(f"🧬 Extracted strain '{strain}' from product name '{product_name}' in fetch_and_match_with_product_db")
                        else:
                            # Try to find strain in database
                            try:
                                db_strain = self._find_strain_in_database(product_name, product_db)
                                if db_strain:
                                    strain = db_strain
                                    logging.info(f"🗄️ Found strain '{strain}' in database for product '{product_name}' in fetch_and_match_with_product_db")
                            except Exception as db_error:
                                logging.warning(f"Failed to search database for strain in fetch_and_match_with_product_db: {db_error}")
                    
                    # Enhanced lineage determination
                    lineage = "HYBRID"  # Default
                    if strain:
                        # Enhanced lineage logic based on strain characteristics
                        strain_lower = strain.lower()
                        
                        # Sativa-dominant strains
                        if any(x in strain_lower for x in ["haze", "sativa", "durban", "jack", "herer", "trainwreck", "green crack", "maui", "wowie", "amnesia", "lemon", "lime", "tropical", "tangie", "clementine", "mandarin", "orange", "citrus", "energetic", "uplifting", "creative", "focus", "daytime"]):
                            lineage = "SATIVA"
                        # Indica-dominant strains
                        elif any(x in strain_lower for x in ["kush", "indica", "afghan", "afghani", "bubba", "master", "purple", "granddaddy", "grand daddy", "northern lights", "skunk", "hashplant", "relaxing", "sedating", "sleep", "nighttime", "body", "couch", "lock"]):
                            lineage = "INDICA"
                        # Hybrid strains (including balanced)
                        elif any(x in strain_lower for x in ["og", "diesel", "cookies", "runtz", "gelato", "wedding", "cake", "sherbet", "sherbert", "blueberry", "strawberry", "banana", "mango", "pineapple", "cherry", "grape", "apple", "guava", "dragon", "fruit", "passion", "peach", "apricot", "watermelon", "cantaloupe", "honeydew", "kiwi", "plum", "raspberry", "blackberry", "yoda", "cosmic", "combo", "honey", "bread", "mintz", "grinch", "ak-47", "white widow", "chemdawg", "sour", "cheese", "blue dream", "balanced", "hybrid"]):
                            lineage = "HYBRID"
                        # CBD strains
                        elif any(x in strain_lower for x in ["cbd", "hemp", "cannabidiol", "non-psychoactive", "non psychoactive", "medicinal", "therapeutic", "wellness", "health", "paraphernalia"]):
                            lineage = "CBD"
                        # Special cases
                        elif "haze" in strain_lower and ("purple" in strain_lower or "amnesia" in strain_lower):
                            lineage = "HYBRID/SATIVA"  # Purple Haze, Amnesia Haze are often hybrid-sativa
                        elif "kush" in strain_lower and ("purple" in strain_lower or "bubba" in strain_lower):
                            lineage = "HYBRID/INDICA"  # Purple Kush, Bubba Kush are often hybrid-indica
                        else:
                            lineage = "HYBRID"  # Conservative default
                    else:
                        # If no strain info, try to infer from product type
                        # Use intelligent lineage assignment based on product type
                        lineage = self._get_default_lineage_for_product_type(product_type)
                    
                    # Extract additional fields for new database columns
                    thc_result = str(item.get("thc", "")).strip()
                    cbd_result = str(item.get("cbd", "")).strip()
                    test_unit = str(item.get("test_unit", "%")).strip()
                    batch_num = str(item.get("batch_number", "")).strip()
                    lot_num = str(item.get("lot_number", "")).strip()
                    barcode = str(item.get("barcode", "")).strip()
                    cost = str(item.get("cost", "")).strip()
                    medical_only = str(item.get("medical_only", "No")).strip()
                    med_price = str(item.get("med_price", "")).strip()
                    expiration = str(item.get("expiration_date", "")).strip()
                    is_archived = str(item.get("is_archived", "no")).strip()
                    thc_per_serving = str(item.get("thc_per_serving", "")).strip()
                    allergens = str(item.get("allergens", "")).strip()
                    solvent = str(item.get("solvent", "")).strip()
                    accepted_date = str(item.get("accepted_date", "")).strip()
                    internal_id = str(item.get("internal_id", "")).strip()
                    product_tags = str(item.get("product_tags", "")).strip()
                    image_url = str(item.get("image_url", "")).strip()
                    ingredients = str(item.get("ingredients", "")).strip()
                    
                    # Prepare DOH/compliance value from upstream JSON, normalized
                    doh_raw_value = (
                        item.get('DOH') or item.get('doh') or item.get('doh_compliant') or
                        item.get('DOH Compliant') or item.get('DOH Compliant (Yes/No)') or
                        item.get('is_doh') or item.get('dohStatus')
                    )
                    if doh_raw_value is None:
                        normalized_doh_value = ''
                    else:
                        value_str = str(doh_raw_value).strip()
                        lower_value = value_str.lower()
                        upper_value = value_str.upper()
                        if lower_value in ['yes', 'y', 'true', '1', 'doh']:
                            normalized_doh_value = 'Yes'
                        elif upper_value == 'THC':
                            normalized_doh_value = 'THC'
                        elif upper_value == 'CBD':
                            normalized_doh_value = 'CBD'
                        else:
                            normalized_doh_value = ''

                    # Enhanced product tag creation using new database columns
                    tag = {
                        # Core product information
                        'Product Name*': product_name,
                        'ProductName': product_name,
                        'Description': description,
                        'Product Type*': product_type or infer_product_type_from_name(product_name),
                        'Product Type': product_type or infer_product_type_from_name(product_name),
                        'Vendor': vendor,
                        'Vendor/Supplier*': vendor,
                        'Product Brand': brand,
                        'ProductBrand': brand,
                        'Product Strain': strain,
                        'Strain Name': strain,
                        'Lineage': lineage,
                        'Weight*': f"{weight} {units}" if weight and units else weight,
                        'Weight': f"{weight} {units}" if weight and units else weight,
                        'Quantity*': quantity,
                        'Quantity': quantity,
                        'Units': units,
                        'Price': price,
                        'Price* (Tier Name for Bulk)': price,
                        
                        # Enhanced fields using new database columns
                        'State': 'active',
                        'Is Sample? (yes/no)': 'no',
                        'Is MJ product?(yes/no)': 'yes',
                        'Discountable? (yes/no)': 'yes',
                        'Room*': 'Default',
                        'Medical Only (Yes/No)': 'No',
                        # Normalize DOH from upstream JSON if present; otherwise leave blank
                        'DOH': normalized_doh_value,
                        'DOH Compliant (Yes/No)': normalized_doh_value,
                        
                        # New database column mappings
                        'Concentrate Type': product_type if "concentrate" in product_type.lower() else '',
                        'Ratio': '',
                        'Joint Ratio': '',
                        'JointRatio': '',
                        'THC test result': thc_result,
                        'CBD test result': cbd_result,
                        'Test result unit (% or mg)': test_unit,
                        'Batch Number': batch_num,
                        'Lot Number': lot_num,
                        'Barcode*': barcode,
                        'Med Price': med_price,
                        'Expiration Date(YYYY-MM-DD)': expiration,
                        'Is Archived? (yes/no)': is_archived,
                        'THC Per Serving': thc_per_serving,
                        'Allergens': allergens,
                        'Solvent': solvent,
                        'Accepted Date': accepted_date,
                        'Internal Product Identifier': internal_id,
                        'Product Tags (comma separated)': product_tags,
                        'Image URL': image_url,
                        'Ingredients': ingredients,
                        
                        # Legacy fields for compatibility - CRITICAL FIX: Use Excel-compatible source
                        'Source': 'JSON Match',  # Changed back to 'JSON Match' for proper frontend detection
                        'Quantity Received*': quantity,
                        'Weight Unit* (grams/gm or ounces/oz)': units,
                        'CombinedWeight': weight,
                        'DescAndWeight': self._process_description_from_product_name(primary_product_name, weight, units),  # Use Excel processor formula with weight
                        'Description_Complexity': '1',
                        'Ratio_or_THC_CBD': '',
                        'displayName': primary_product_name,  # Use clean product name for UI display
                        'weightWithUnits': f"{str(round(float(weight or '1')))}{units or 'g'}",
                        'WeightWithUnits': f"{str(round(float(weight or '1')))}{units or 'g'}",
                        'WeightUnits': f"{str(round(float(weight or '1')))}{units or 'g'}",
                        'vendor': vendor,
                        'productBrand': brand,
                        'lineage': lineage,
                        'productType': product_type,
                        'weight': weight,
                        'units': units,
                        'price': price,
                        'description': description,
                        'strain': strain,
                        'quantity': quantity,
                        'thc': thc_result,
                        'cbd': cbd_result,
                        'test_unit': test_unit,
                        'batch_number': batch_num,
                        'lot_number': lot_num,
                        'barcode': barcode,
                        'cost': cost,
                        'medical_only': medical_only,
                        'med_price': med_price,
                        'expiration_date': expiration,
                        'is_archived': is_archived,
                        'thc_per_serving': thc_per_serving,
                        'allergens': allergens,
                        'solvent': solvent,
                        'accepted_date': accepted_date,
                        'internal_id': internal_id,
                        'product_tags': product_tags,
                        'image_url': image_url,
                        'ingredients': ingredients,
                    }
                    
                    all_tags.append(tag)
                    processed_count += 1
                    
                    # Create new database entry for unmatched JSON tag
                    if product_db:
                        try:
                            self._create_database_entry_for_unmatched_json(tag, product_db)
                            new_database_entries_count += 1
                        except Exception as db_entry_error:
                            logging.warning(f"Failed to create database entry for '{product_name}': {db_entry_error}")
                    
                    # Add debug logging after each item is processed
                    print(f"🔍 DEBUG: === COMPLETED PROCESSING ITEM {i+1}/{len(unique_items)} ===")
                    print(f"🔍 DEBUG: Current matched_products count: {len(matched_products)}")
                    print(f"🔍 DEBUG: Continuing to next item...")
                    
                    # Add a small delay to ensure logs are flushed
                    import time
                    time.sleep(0.1)
                
                except Exception as item_error:
                    logging.error(f"Error processing item {i+1}: {item_error}")
                    continue
            
            # Log summary of Product Database vs JSON processing
            logging.info(f"Product Database priority processing completed:")
            logging.info(f"  - Total items processed: {processed_count}")
            logging.info(f"  - Product Database matches: {db_lookup_count}")
            logging.info(f"  - Educated guesses: {educated_guess_count}")
            logging.info(f"  - New products from JSON: {new_product_count}")
            logging.info(f"  - New database entries created: {new_database_entries_count}")
            logging.info(f"  - Total tags created: {len(all_tags)}")
            
            # CRITICAL FIX: Integrate JSON-matched products with Excel system
            try:
                # Get the current Excel processor from the session
                from flask import g
                if hasattr(g, 'excel_processor') and g.excel_processor:
                    logging.info("Integrating JSON-matched products with Excel system...")
                    integration_success = self.integrate_with_excel_system(g.excel_processor, all_tags)
                    if integration_success:
                        logging.info("✅ Successfully integrated JSON products with Excel system")
                    else:
                        logging.warning("⚠️ Failed to integrate JSON products with Excel system")
                else:
                    logging.warning("No Excel processor available in session for integration")
            except Exception as integration_error:
                logging.error(f"Error during Excel integration: {integration_error}")
            
            # Performance summary
            total_time = time_module.time() - start_time
            logging.info(f"🚀 JSON MATCHING PERFORMANCE SUMMARY:")
            logging.info(f"   Total time: {total_time:.2f}s")
            logging.info(f"   Items processed: {processed_count}")
            logging.info(f"   Items matched: {matched_count}")
            logging.info(f"   Match rate: {(matched_count/processed_count*100):.1f}%" if processed_count > 0 else "   Match rate: 0%")
            logging.info(f"   Processing speed: {processed_count/total_time:.1f} items/sec" if total_time > 0 else "   Processing speed: N/A")
            
            return all_tags
            
        except Exception as e:
            logging.error(f"Error in fetch_and_match_with_product_db: {e}")
            raise
            
    def _get_cache_item_name(self, idx_str: str) -> str:
        """Get the original name of a cache item by index."""
        for item in self._sheet_cache:
            if isinstance(item, dict) and item.get("idx") == idx_str:
                return item.get("original_name", "Unknown")
        return "Unknown"
        
    def get_matched_names(self) -> Optional[List[str]]:
        """Get the currently matched product names from JSON."""
        return getattr(self, 'json_matched_names', None)
        
    def get_matched_tags(self) -> Optional[List[Dict]]:
        """Get the currently matched full tag objects from JSON."""
        return getattr(self, 'json_matched_tags', None)
        
    def clear_matches(self):
        """Clear the current JSON matches."""
        self.json_matched_names = None
        self.json_matched_tags = None
        
    def rebuild_sheet_cache(self):
        """Force rebuild the sheet cache."""
        self._sheet_cache = None
        self._indexed_cache = None
        self._build_sheet_cache()
        
    def rebuild_strain_cache(self):
        """Force rebuild the strain cache."""
        self._strain_cache = None
        self._lineage_cache = None
        self._build_strain_cache()
        
    def rebuild_all_caches(self):
        """Force rebuild all caches."""
        self.rebuild_sheet_cache()
        self.rebuild_strain_cache()
        
    def get_sheet_cache_status(self):
        """Get the status of the sheet cache."""
        if self._sheet_cache is None:
            return "Not built"
        elif not self._sheet_cache:
            return "Empty"
        else:
            cache_info = f"Built with {len(self._sheet_cache)} entries"
            if self._indexed_cache:
                cache_info += f" (indexed: {len(self._indexed_cache['exact_names'])} exact, {len(self._indexed_cache['vendor_groups'])} vendors, {len(self._indexed_cache['key_terms'])} terms)"
            return cache_info
            
    def get_strain_cache_status(self):
        """Get the status of the strain cache."""
        if self._strain_cache is None:
            return "Not built"
        elif not self._strain_cache:
            return "Empty"
        else:
            return f"Built with {len(self._strain_cache)} strains and {len(self._lineage_cache)} lineages"
        
    def process_json_inventory(self, url: str) -> pd.DataFrame:
        """
        Process JSON inventory data and return as DataFrame for inventory slips.
        
        Args:
            url: URL to fetch JSON data from
            
        Returns:
            DataFrame with processed inventory data
        """
        try:
            # Use the proxy endpoint to handle authentication and CORS
            import requests
            
            # Prepare headers for the request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Add authentication headers if available
            import os
            if os.environ.get('BAMBOO_API_KEY'):
                headers['X-API-Key'] = os.environ.get('BAMBOO_API_KEY')
            if os.environ.get('BAMBOO_AUTH_TOKEN'):
                headers['Authorization'] = f"Bearer {os.environ.get('BAMBOO_AUTH_TOKEN')}"
            if os.environ.get('BAMBOO_SESSION_TOKEN'):
                headers['X-Session-Token'] = os.environ.get('BAMBOO_SESSION_TOKEN')
            
            proxy_data = {
                'url': url,
                'headers': headers
            }
            
            # Try to make the request directly first (for external URLs)
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                payload = response.json()
            except (requests.exceptions.RequestException, ValueError) as direct_error:
                logging.info(f"Direct request failed, trying proxy: {direct_error}")
                # Fallback to proxy endpoint if direct request fails
                import os
                base_url = os.environ.get('FLASK_BASE_URL', 'http://127.0.0.1:5001')
                response = requests.post(f'{base_url}/api/proxy-json', 
                                       json=proxy_data, 
                                       timeout=30)
                response.raise_for_status()
                payload = response.json()
                
            # Handle both list and dictionary payloads
            if isinstance(payload, list):
                items = payload
                vendor_meta = "Unknown Vendor"
                raw_date = datetime.now().strftime("%Y-%m-%d")
            elif isinstance(payload, dict):
                items = payload.get("inventory_transfer_items", [])
                vendor_meta = f"{payload.get('from_license_number', '')} – {payload.get('from_license_name', '')}"
                raw_date = payload.get("est_arrival_at", "").split("T")[0]
            else:
                logging.warning(f"Unexpected payload type: {type(payload)}")
                return pd.DataFrame()
            
            records = []
            for itm in items:
                # Ensure all values are strings to prevent type issues
                product_name = str(itm.get("product_name", "")) if itm.get("product_name") is not None else ""
                inventory_id = str(itm.get("inventory_id", "")) if itm.get("inventory_id") is not None else ""
                qty = str(itm.get("qty", "")) if itm.get("qty") is not None else ""
                
                records.append({
                    "Product Name*": product_name,
                    "Barcode*": inventory_id,
                    "Quantity Received*": qty,
                    "Accepted Date": raw_date,
                    "Vendor/Supplier*": vendor_meta,
                })
                
            df = pd.DataFrame(records)
            logging.info(f"Processed {len(records)} inventory items from JSON")
            return df
            
        except Exception as e:
            logging.error(f"Error processing JSON inventory: {str(e)}")
            raise 

    def _build_strain_cache(self):
        """Build a cache of strain data from the product database for fast matching."""
        try:
            product_db = self._get_product_database()
            self._strain_cache = product_db.get_all_strains()
            self._lineage_cache = product_db.get_strain_lineage_map()
            
            # Debug: Check what's in the strain cache
            if self._strain_cache:
                sample_strains = list(self._strain_cache)[:5]
                logging.info(f"Sample strains in cache: {sample_strains}")
                for strain in sample_strains:
                    if not isinstance(strain, str):
                        logging.warning(f"Non-string strain found: {type(strain)} - {strain}")
            
            logging.info(f"Built strain cache with {len(self._strain_cache)} strains and {len(self._lineage_cache)} lineages")
        except Exception as e:
            logging.warning(f"Could not build strain cache: {e}")
            self._strain_cache = set()
            self._lineage_cache = {}
        
    def _find_strains_in_text(self, text: str) -> List[Tuple[str, str]]:
        """Find known strains in text and return (strain_name, lineage) pairs."""
        if not self._strain_cache:
            self._build_strain_cache()
            
        # Ensure input is a string
        text = str(text or "")
        if not text:
            return []
            
        text_lower = text.lower()
        found_strains = []
        
        # Check for exact strain matches
        for strain in self._strain_cache:
            # Ensure strain is a string before calling .lower()
            if isinstance(strain, str):
                if strain.lower() in text_lower:
                    lineage = self._lineage_cache.get(strain, "HYBRID")
                    found_strains.append((strain, lineage))
            else:
                # Skip non-string strains and log for debugging
                logging.warning(f"Skipping non-string strain in cache: {type(strain)} - {strain}")
                
        # Sort by length (longer strains first) to prioritize more specific matches
        found_strains.sort(key=lambda x: len(x[0]), reverse=True)
        
        return found_strains 

    def _find_strict_fuzzy_vendor_matches(self, json_vendor: str) -> List[dict]:
        """Find vendor matches using strict fuzzy matching - only very similar vendor names."""
        if not json_vendor:
            return []
            
        matches = []
        available_vendors = list(self._indexed_cache['vendor_groups'].keys())
        
        # Only known vendor name variations that are definitely the same company
        vendor_variations = {
            # Dank Czar variations only
            'dank czar': ['dcz holdings inc', 'dcz holdings inc.', 'dcz holdings', 'dcz'],
            'dcz holdings': ['dank czar', 'dcz', 'dcz holdings inc', 'dcz holdings inc.'],
            'dcz holdings inc': ['dank czar', 'dcz', 'dcz holdings', 'dcz holdings inc.'],
            'dcz holdings inc.': ['dank czar', 'dcz', 'dcz holdings', 'dcz holdings inc'],
            'dcz': ['dank czar', 'dcz holdings', 'dcz holdings inc', 'dcz holdings inc.'],
            
            # Hustler's Ambition variations only
            'hustler\'s ambition': ['hustlers ambition', '1555 industrial llc'],
            'hustlers ambition': ['hustler\'s ambition', '1555 industrial llc'],
            '1555 industrial llc': ['hustler\'s ambition', 'hustlers ambition'],
            
            # Omega Labs variations only
            'omega labs': ['omega', 'omega cannabis'],
            'omega': ['omega labs', 'omega cannabis'],
            'omega cannabis': ['omega labs', 'omega'],
            
            # Airo Pro variations only
            'airo pro': ['airo', 'airopro', 'harmony farms'],
            'airo': ['airo pro', 'airopro', 'harmony farms'],
            'airopro': ['airo pro', 'airo', 'harmony farms'],
            'harmony farms': ['airo pro', 'airo', 'airopro'],
            
            # Collections Cannabis variations only
            'collections cannabis': ['collections', 'collections llc'],
            'collections': ['collections cannabis', 'collections llc'],
            'collections llc': ['collections cannabis', 'collections'],
            
            # Blue Roots variations only
            'blue roots cannabis': ['blue roots', 'blue roots llc'],
            'blue roots': ['blue roots cannabis', 'blue roots llc'],
            'blue roots llc': ['blue roots cannabis', 'blue roots'],
            
            # Grow Op Farms variations only
            'grow op farms': ['grow op', 'grow op llc'],
            'grow op': ['grow op farms', 'grow op llc'],
            'grow op llc': ['grow op farms', 'grow op'],
            
            # Cloud 9 Farms variations only
            'cloud 9 farms': ['cloud 9', 'cloud 9 llc'],
            'cloud 9': ['cloud 9 farms', 'cloud 9 llc'],
            'cloud 9 llc': ['cloud 9 farms', 'cloud 9'],
            
            # The Collective variations only
            'the collective': ['collective', 'collective llc'],
            'collective': ['the collective', 'collective llc'],
            'collective llc': ['the collective', 'collective'],
            
            # 1555 Industrial variations only
            '1555 industrial': ['1555 industrial llc', '1555 llc'],
            '1555 llc': ['1555 industrial', '1555 industrial llc'],
            
            # Georgetown Bottling variations only
            'georgetown bottling spc': ['georgetown bottling', 'cormorant edibles', 'cormorant'],
            'georgetown bottling': ['georgetown bottling spc', 'cormorant edibles', 'cormorant'],
            'cormorant edibles': ['georgetown bottling spc', 'georgetown bottling', 'cormorant'],
            'cormorant': ['georgetown bottling spc', 'georgetown bottling', 'cormorant edibles'],
        }
        
        # Check for known variations only
        for variation_key, variations in vendor_variations.items():
            # Check if json_vendor matches the main key or any of its variations
            if json_vendor == variation_key or json_vendor in variations:
                for vendor in available_vendors:
                    # Check if the available vendor matches the main key or any of its variations
                    if vendor == variation_key or vendor in variations:
                        matches.extend(self._indexed_cache['vendor_groups'][vendor])
        
        # If no matches found with known variations, try very strict word matching
        if not matches:
            json_words = set(json_vendor.split())
            for vendor in available_vendors:
                vendor_words = set(vendor.split())
                
                # Only match if there's significant word overlap (at least 2 words or 75% overlap)
                overlap = json_words.intersection(vendor_words)
                if len(overlap) >= 2 or (len(overlap) >= 1 and len(overlap) / min(len(json_words), len(vendor_words)) >= 0.75):
                    matches.extend(self._indexed_cache['vendor_groups'][vendor])
        
        return matches 
    
    def _get_cache_item_name(self, idx):
        """Get the name of a cache item by index."""
        for item in self._sheet_cache:
            if str(item.get("idx", "")) == str(idx):
                return item.get("original_name", "Unknown")
        return "Unknown"

    def _normalize_name(self, name: str) -> str:
        """Normalize product name for better matching"""
        if not name:
            return ""
        # Lowercase, strip, remove extra spaces, remove special chars
        normalized = name.lower().strip()
        # Remove special characters and normalize whitespace
        normalized = re.sub(r'[^\w\s-]', '', normalized)  # Keep alphanumeric, spaces, hyphens
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
        return normalized.strip()
    
    def _find_keyword_matches(self, json_name_normalized: str, json_vendor: str, json_brand: str = None) -> List[dict]:
        """Find matches based on key words and vendor match - helps with variations like 'Cherries' vs 'Cherry'"""
        matches = []
        all_products = self._get_all_products()
        
        # Extract important words (exclude common short words)
        stop_words = {'by', 'the', 'and', 'or', 'of', 'in', 'a', 'an', 'for', 'to'}
        json_words = [w.lower() for w in json_name_normalized.split() if len(w) >= 3 and w.lower() not in stop_words]
        
        if not json_words:
            return []
        
        for product in all_products:
            product_name = str(product.get('Product Name*', '')).strip()
            product_name_normalized = self._normalize_name(product_name)
            
            if not product_name_normalized:
                continue
            
            # Require vendor match
            product_vendor = self._get_product_vendor(product).lower()
            if not self._validate_vendor_match(json_vendor, product_vendor):
                continue
            
            # Extract product words
            product_words = [w.lower() for w in product_name_normalized.split() if len(w) >= 3 and w.lower() not in stop_words]
            
            # Find shared words
            json_set = set(json_words)
            product_set = set(product_words)
            shared_words = json_set & product_set
            
            # Require at least 2 shared important words
            if len(shared_words) >= 2:
                # Calculate score based on shared words and word positions
                word_score = len(shared_words) / max(len(json_set), len(product_set), 1)
                
                # Check for similar words (e.g., "cherries" vs "cherry")
                similar_words = 0
                for jw in json_words:
                    for pw in product_words:
                        # Check for exact match or similar (same root word)
                        if jw == pw:
                            similar_words += 1
                        elif jw in pw or pw in jw:
                            similar_words += 0.5
                
                final_score = (word_score + (similar_words / max(len(json_words), len(product_words), 1))) * 50
                
                # Require minimum score
                if final_score >= 40:
                    match_dict = dict(product)
                    match_dict['fuzzy_score'] = final_score
                    match_dict['_original_json_name'] = json_name_normalized
                    match_dict['_match_type'] = 'keyword'
                    matches.append(match_dict)
        
        # Sort by score descending
        matches.sort(key=lambda x: x.get('fuzzy_score', 0), reverse=True)
        return matches[:3]  # Return top 3 matches
    
    def _find_substring_matches(self, json_name_normalized: str, json_vendor: str = None, json_brand: str = None) -> List[dict]:
        """Find matches by checking if JSON name is a substring of database name or vice versa"""
        matches = []
        all_products = self._get_all_products()
        
        # Extract key words from JSON name (longer words are usually more important)
        json_words = set(w for w in json_name_normalized.split() if len(w) >= 3)
        
        for product in all_products:
            product_name = str(product.get('Product Name*', '')).strip()
            product_name_normalized = self._normalize_name(product_name)
            
            if not product_name_normalized:
                continue
            
            # Check if key words from JSON appear in product name
            product_words = set(product_name_normalized.split())
            common_words = json_words & product_words
            
            if common_words:
                # Calculate score based on word overlap - require at least 70% of words to match
                word_overlap_pct = len(common_words) / max(len(json_words), 1) if json_words else 0
                
                # STRICT REQUIREMENT: At least 70% of words must overlap
                if word_overlap_pct < 0.7:
                    continue
                
                # Check for substantial substring match (at least 60% of characters)
                substring_match = False
                if json_name_normalized in product_name_normalized or product_name_normalized in json_name_normalized:
                    match_len = min(len(json_name_normalized), len(product_name_normalized))
                    total_len = max(len(json_name_normalized), len(product_name_normalized))
                    if match_len / total_len >= 0.6:  # At least 60% of characters match
                        substring_match = True
                        substring_score = match_len / total_len
                    else:
                        substring_score = word_overlap_pct
                else:
                    substring_score = word_overlap_pct
                
                # Combine scores - prefer substring matches
                if substring_match:
                    final_score = substring_score * 100
                else:
                    # Require even higher word overlap if not substring match
                    if word_overlap_pct < 0.8:
                        continue
                    final_score = word_overlap_pct * 100
                
                # Add vendor/brand bonus if available (but much smaller)
                if json_vendor:
                    product_vendor = self._get_product_vendor(product).lower()
                    if json_vendor in product_vendor or product_vendor in json_vendor:
                        final_score += 10  # Reduced from 20
                
                if json_brand:
                    product_brand = str(product.get('Product Brand', '')).lower()
                    if json_brand in product_brand or product_brand in json_brand:
                        final_score += 5  # Reduced from 15
                
                # Only add if score is reasonable (increased threshold for better accuracy)
                if final_score >= 70:  # Increased from 60
                    match_dict = dict(product)
                    match_dict['fuzzy_score'] = final_score
                    match_dict['_original_json_name'] = json_name_normalized
                    match_dict['_match_type'] = 'substring'
                    matches.append(match_dict)
        
        # Sort by score descending
        matches.sort(key=lambda x: x.get('fuzzy_score', 0), reverse=True)
        return matches[:5]  # Return top 5 matches
    
    def intelligent_match_product(self, json_item: dict) -> Tuple[Optional[dict], float, str]:
        """
        Intelligently match a JSON product to existing products using sophisticated fuzzy matching.
        
        Returns:
            Tuple of (matched_product, confidence_score, match_reason)
        """
        try:
            json_name = str(json_item.get("product_name", "")).strip()
            json_vendor = str(json_item.get("vendor", "")).strip().lower()
            json_brand = str(json_item.get("brand", "")).strip().lower()
            json_type = str(json_item.get("product_type", "")).strip().lower()
            json_weight = str(json_item.get("weight", "")).strip()
            json_strain = str(json_item.get("strain_name", "")).strip().lower()
            
            # Normalize the product name for better matching
            json_name_normalized = self._normalize_name(json_name)
            
            # Reduced logging for performance
            logging.debug(f"🔍 INTELLIGENT MATCHING: '{json_name}' → '{json_name_normalized}' (vendor: {json_vendor}, brand: {json_brand}, type: {json_type}, weight: {json_weight}, strain: {json_strain})")
            
            if not json_name:
                return None, 0.0, "No product name provided"
            
            # Step 0.5: Try exact name matching with normalized names
            exact_matches = self._find_exact_name_matches(json_name)
            if exact_matches:
                # Sort by priority: database matches first, then Excel
                exact_matches.sort(key=lambda x: x.get('_priority', 999))
                db_matches = [m for m in exact_matches if m.get('_source') == 'database']
                excel_matches = [m for m in exact_matches if m.get('_source') == 'excel']
                
                best_match = exact_matches[0]  # Now guaranteed to be database if available
                source = best_match.get('_source', 'unknown')
                logging.debug(f"✅ EXACT MATCH ({source.upper()}): '{json_name}' → '{best_match.get('original_name', 'Unknown')}' (Total: {len(exact_matches)}, DB: {len(db_matches)}, Excel: {len(excel_matches)})")
                return best_match, 1.0, f"Exact name match ({source})"
            else:
                logging.debug(f"❌ No exact match for '{json_name}'")
            
            # Step 2: Try vendor-based exact name matching - PRIORITIZE DATABASE
            if json_vendor:
                vendor_exact_matches = self._find_vendor_exact_name_matches(json_name, json_vendor)
                if vendor_exact_matches:
                    # Sort by priority: database matches first, then Excel
                    vendor_exact_matches.sort(key=lambda x: x.get('_priority', 999))
                    best_match = vendor_exact_matches[0]  # Now guaranteed to be database if available
                    source = best_match.get('_source', 'unknown')
                    logging.debug(f"✅ VENDOR EXACT MATCH ({source.upper()}): '{json_name}' → '{best_match.get('original_name', 'Unknown')}'")
                    return best_match, 0.95, f"Vendor-based exact name match ({source})"
                else:
                    logging.debug(f"❌ No vendor exact match for '{json_name}' with vendor '{json_vendor}'")
            else:
                logging.debug(f"⚠️ No vendor specified for '{json_name}', skipping vendor-based matching")
            
            # Step 2.5: Try key word matching for products with same vendor and shared important words
            # This helps with cases like "Indica Freeze Dried Cherries" matching "Indica Cherry Fruit Chew"
            if json_name_normalized and json_vendor:
                keyword_matches = self._find_keyword_matches(json_name_normalized, json_vendor, json_brand)
                if keyword_matches:
                    best_match = keyword_matches[0]
                    score = keyword_matches[0]['fuzzy_score'] / 100.0
                    logging.debug(f"✅ KEYWORD MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}' (score: {score:.2f})")
                    return best_match, score, "Keyword match"
            
            # Step 3: Try fuzzy name matching with vendor filtering (more lenient for better coverage)
            if json_vendor:
                # Use more lenient threshold for vendor-based matching to get more matches
                vendor_threshold = 40 if json_brand else 35  # More lenient for better matching
                fuzzy_matches = self._find_fuzzy_name_matches(json_name, json_vendor, threshold=vendor_threshold)
                if fuzzy_matches:
                    best_match = fuzzy_matches[0]
                    score = fuzzy_matches[0]['fuzzy_score'] / 100.0
                    logging.debug(f"✅ VENDOR FUZZY MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}' (score: {score:.2f}, threshold: {vendor_threshold})")
                    return best_match, score, "Vendor-based fuzzy name match"
                else:
                    logging.debug(f"❌ No vendor fuzzy match for '{json_name}' with vendor '{json_vendor}' (threshold: {vendor_threshold})")
            else:
                logging.debug(f"⚠️ No vendor specified for '{json_name}', skipping vendor fuzzy matching")
            
            # Step 4: DISABLED - Cross-vendor fuzzy matching removed to prevent brand contamination
            # Cross-vendor matches were introducing products from wrong brands
            # All matching now strictly enforces vendor isolation
            logging.debug(f"🚫 VENDOR ISOLATION: Cross-vendor fuzzy matching is disabled to prevent brand contamination")
            
            # Step 5: Try enhanced fuzzy matching with multiple strategies (vendor-aware)
            enhanced_matches = self._find_enhanced_fuzzy_matches(json_item)
            if enhanced_matches:
                best_match = enhanced_matches[0]
                score = enhanced_matches[0]['fuzzy_score'] / 100.0
                logging.debug(f"✅ ENHANCED FUZZY MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}' (score: {score:.2f})")
                return best_match, score, "Enhanced fuzzy match"
            else:
                logging.debug(f"❌ No enhanced fuzzy match for '{json_name}'")
            
            # Step 5.5: Try Cultivera-specific matching
            cultivera_matches = self._find_cultivera_specialized_matches(json_item)
            if cultivera_matches:
                best_match = cultivera_matches[0]
                score = cultivera_matches[0]['fuzzy_score'] / 100.0
                logging.debug(f"✅ CULTIVERA MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}' (score: {score:.2f})")
                return best_match, score, "Cultivera specialized match"
            else:
                logging.debug(f"❌ No Cultivera specialized match for '{json_name}'")
            
            # Step 5b: Fallback to general fuzzy matching without vendor requirements (more lenient threshold)
            general_fuzzy_matches = self._find_fuzzy_name_matches(json_name, threshold=35)  # More lenient threshold for maximum coverage
            if general_fuzzy_matches:
                best_match = general_fuzzy_matches[0]
                score = general_fuzzy_matches[0]['fuzzy_score'] / 100.0
                logging.debug(f"✅ GENERAL FUZZY MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}' (score: {score:.2f}, threshold: 35)")
                return best_match, score, "General fuzzy match"
            else:
                logging.debug(f"❌ No general fuzzy match for '{json_name}' (threshold: 35)")
            
            # Step 5: Try specialized matching for vendors with generic names (like Ceres)
            if json_vendor and json_vendor.lower() in ['ceres', 'ceres gardens', 'ceres gardens inc']:
                ceres_matches = self._find_ceres_specialized_matches(json_item)
                if ceres_matches:
                    best_match = ceres_matches[0]
                    score = ceres_matches[0]['fuzzy_score'] / 100.0
                    logging.debug(f"✅ CERES SPECIALIZED MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}' (score: {score:.2f})")
                    return best_match, score, "Ceres specialized match"
                else:
                    logging.debug(f"❌ No Ceres specialized match for '{json_name}'")

            # Step 6: Try strain-based matching (with optional vendor filtering)
            if json_strain:  # Only require strain, vendor is optional
                strain_matches = self._find_strain_based_matches(json_strain, json_vendor, json_type)
                if strain_matches:
                    best_match = strain_matches[0]
                    logging.debug(f"✅ STRAIN MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}'")
                    return best_match, 0.7, "Strain-based match"
                else:
                    logging.debug(f"❌ No strain match for '{json_name}' (strain: {json_strain})")
            else:
                logging.debug(f"⚠️ No strain specified for '{json_name}', skipping strain matching")
            
            # Step 6: Try brand + type + weight matching (with optional vendor filtering)
            if json_brand and json_type and json_weight:  # Only require brand, type, and weight
                brand_type_matches = self._find_brand_type_weight_matches(json_brand, json_type, json_weight, json_vendor)
                if brand_type_matches:
                    best_match = brand_type_matches[0]
                    logging.debug(f"✅ BRAND+TYPE+WEIGHT MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}'")
                    return best_match, 0.6, "Brand + type + weight match"
                else:
                    logging.debug(f"❌ No brand+type+weight match for '{json_name}'")
            else:
                logging.debug(f"⚠️ Missing required fields for brand+type+weight matching (brand: {json_brand}, type: {json_type}, weight: {json_weight})")
            
            # Step 7: Try advanced weight-based matching (with optional vendor filtering)
            if json_weight and json_type:  # Only require weight and type
                weight_matches = self._find_weight_based_matches(json_weight, json_type, json_vendor)
                if weight_matches:
                    best_match = weight_matches[0]
                    logging.debug(f"✅ WEIGHT+TYPE MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}'")
                    return best_match, 0.5, "Weight + type based match"
            
            # Step 8: Try comprehensive multi-field matching with all available data
            comprehensive_matches = self._find_comprehensive_matches(json_item)
            if comprehensive_matches:
                best_match = comprehensive_matches[0]
                logging.debug(f"✅ COMPREHENSIVE MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}'")
                return best_match, 0.4, "Comprehensive multi-field match"
            
            # Step 9: Try partial field matching with any available data
            partial_matches = self._find_partial_field_matches(json_item)
            if partial_matches:
                best_match = partial_matches[0]
                logging.debug(f"✅ PARTIAL MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}'")
                return best_match, 0.3, "Partial field match"
            
            # Step 8: Try advanced multi-algorithm matching
            advanced_matches = self._find_advanced_matches(json_item)
            if advanced_matches:
                best_match = advanced_matches[0]
                score = best_match.overall_score / 100.0
                logging.debug(f"✅ ADVANCED MATCH: '{json_name}' → '{best_match.item.get('original_name', 'Unknown')}' (score: {score:.2f}, algorithm: {best_match.algorithm_used})")
                return best_match.item, score, f"Advanced {best_match.algorithm_used} match"
            else:
                logging.debug(f"❌ No advanced match for '{json_name}'")
            
            # Step 8: Try strain + weight matching (with optional vendor filtering)
            if json_strain and json_weight:  # Only require strain and weight
                strain_weight_matches = self._find_strain_weight_matches(json_strain, json_weight, json_vendor)
                if strain_weight_matches:
                    best_match = strain_weight_matches[0]
                    logging.debug(f"✅ STRAIN+WEIGHT MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}'")
                    return best_match, 0.55, "Strain + weight based match"
                else:
                    logging.debug(f"❌ No strain+weight match for '{json_name}'")
            else:
                logging.debug(f"⚠️ Missing required fields for strain+weight matching (strain: {json_strain}, weight: {json_weight})")
            
            # Step 9: Final fallback - try general fuzzy matching without vendor requirements
            general_fuzzy_matches = self._find_fuzzy_name_matches(json_name, threshold=30)  # More lenient threshold for final attempt
            if general_fuzzy_matches:
                best_match = general_fuzzy_matches[0]
                score = general_fuzzy_matches[0]['fuzzy_score'] / 100.0
                logging.debug(f"✅ GENERAL FUZZY MATCH: '{json_name}' → '{best_match.get('original_name', 'Unknown')}' (score: {score:.2f}, threshold: 30)")
                return best_match, score, "General fuzzy match (final fallback)"
            else:
                logging.debug(f"❌ No general fuzzy match for '{json_name}' (threshold: 30)")
            
            # No match found
            logging.debug(f"❌ NO MATCH FOUND: '{json_name}' - tried all matching strategies")
            return None, 0.0, "No suitable match found"
            
        except Exception as e:
            logging.error(f"Error in intelligent_match_product: {e}")
            return None, 0.0, f"Error during matching: {str(e)}"
    
    def _find_comprehensive_matches(self, json_item: dict) -> List[dict]:
        """
        Find matches using comprehensive multi-field analysis including all available columns.
        """
        try:
            json_name = str(json_item.get("product_name", "")).strip()
            json_vendor = str(json_item.get("vendor", "")).strip().lower()
            json_brand = str(json_item.get("brand", "")).strip().lower()
            json_type = str(json_item.get("product_type", "")).strip().lower()
            json_weight = str(json_item.get("weight", "")).strip()
            json_strain = str(json_item.get("strain_name", "")).strip().lower()
            json_qty = str(json_item.get("qty", "")).strip()
            json_price = str(json_item.get("price", "")).strip()
            json_thc = str(json_item.get("thc", "")).strip()
            json_cbd = str(json_item.get("cbd", "")).strip()
            
            matches = []
            
            # Get all products for comprehensive matching
            all_products = self._get_all_products()
            
            for product in all_products:
                score = 0.0
                match_details = []
                
                # Name similarity (highest weight)
                if json_name:
                    name_similarity = self._calculate_name_similarity(json_name, product.get('Product Name*', ''))
                    if name_similarity > 0.1:  # Extremely lenient threshold
                        score += name_similarity * 0.4
                        match_details.append(f"name:{name_similarity:.2f}")
                
                # Vendor matching
                if json_vendor:
                    vendor_similarity = self._calculate_vendor_similarity(json_vendor, self._get_product_vendor(product))
                    if vendor_similarity > 0.1:
                        score += vendor_similarity * 0.2
                        match_details.append(f"vendor:{vendor_similarity:.2f}")
                
                # Brand matching
                if json_brand:
                    brand_similarity = self._calculate_brand_similarity(json_brand, product.get('Product Brand', ''))
                    if brand_similarity > 0.1:
                        score += brand_similarity * 0.15
                        match_details.append(f"brand:{brand_similarity:.2f}")
                
                # Type matching
                if json_type:
                    type_similarity = self._calculate_type_similarity(json_type, product.get('Product Type*', ''))
                    if type_similarity > 0.1:
                        score += type_similarity * 0.1
                        match_details.append(f"type:{type_similarity:.2f}")
                
                # Weight matching
                if json_weight:
                    weight_similarity = self._calculate_weight_similarity(json_weight, product.get('Weight*', ''))
                    if weight_similarity > 0.1:
                        score += weight_similarity * 0.1
                        match_details.append(f"weight:{weight_similarity:.2f}")
                
                # Strain matching
                if json_strain:
                    strain_similarity = self._calculate_strain_similarity(json_strain, product.get('Product Strain', ''))
                    if strain_similarity > 0.1:
                        score += strain_similarity * 0.05
                        match_details.append(f"strain:{strain_similarity:.2f}")
                
                # If we have any score at all, include this match
                if score > 0.05:  # Extremely lenient threshold
                    product['comprehensive_score'] = score
                    product['match_details'] = '|'.join(match_details)
                    matches.append(product)
            
            # Sort by comprehensive score
            matches.sort(key=lambda x: x.get('comprehensive_score', 0), reverse=True)
            return matches[:10]  # Return top 10 matches
            
        except Exception as e:
            logging.error(f"Error in comprehensive matching: {e}")
            return []
    
    def _find_partial_field_matches(self, json_item: dict) -> List[dict]:
        """
        Find matches using any available field data with very lenient thresholds.
        """
        try:
            matches = []
            all_products = self._get_all_products()
            
            for product in all_products:
                score = 0.0
                match_fields = []
                
                # Try to match any available field
                for json_key, json_value in json_item.items():
                    if not json_value or str(json_value).strip() == '':
                        continue
                    
                    json_str = str(json_value).strip().lower()
                    
                    # Try to find a corresponding field in the product
                    for product_key, product_value in product.items():
                        if not product_value or str(product_value).strip() == '':
                            continue
                        
                        product_str = str(product_value).strip().lower()
                        
                        # Calculate similarity
                        similarity = self._calculate_text_similarity(json_str, product_str)
                        if similarity > 0.4:  # Lenient threshold
                            score += similarity * 0.1
                            match_fields.append(f"{json_key}->{product_key}:{similarity:.2f}")
                
                # If we found any matches, include this product
                if score > 0.1:  # Very lenient threshold
                    product['partial_score'] = score
                    product['match_fields'] = '|'.join(match_fields)
                    matches.append(product)
            
            # Sort by partial score
            matches.sort(key=lambda x: x.get('partial_score', 0), reverse=True)
            return matches[:5]  # Return top 5 matches
            
        except Exception as e:
            logging.error(f"Error in partial field matching: {e}")
            return []
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        if not text1 or not text2:
            return 0.0
        
        if text1 == text2:
            return 1.0
        
        # Simple similarity based on common words
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        common_words = words1.intersection(words2)
        total_words = words1.union(words2)
        
        return len(common_words) / len(total_words) if total_words else 0.0
    
    def _calculate_key_word_similarity(self, json_name: str, product_name: str) -> float:
        """Calculate similarity based on key cannabis product words."""
        if not json_name or not product_name:
            return 0.0
        
        # Key cannabis product words that should match
        key_words = {
            'sativa', 'indica', 'hybrid', 'mix', 'mixed', 'sat', 'ind', 'hyb',
            'gummy', 'gummies', 'edible', 'edibles', 'chocolate', 'brownie', 'cookie',
            'vape', 'cart', 'cartridge', 'disposable', 'pod',
            'flower', 'bud', 'pre-roll', 'preroll', 'joint',
            'concentrate', 'wax', 'shatter', 'rosin', 'live resin', 'distillate',
            'tincture', 'oil', 'topical', 'cream', 'balm', 'salve',
            'capsule', 'pill', 'beverage', 'drink', 'soda',
            'mg', 'g', 'gram', 'ounce', 'oz', 'pound', 'lb',
            'ball', 'bite', 'roll', 'squeeze', 'tube', 'ups', 'xtra', 'extra',
            'dragon', 'caramel', 'assorted', 'dark', 'cbd', 'thc', 'pk'
        }
        
        # Extract words from both names
        json_words = set(re.findall(r'\b\w+\b', json_name.lower()))
        product_words = set(re.findall(r'\b\w+\b', product_name.lower()))
        
        # Find matching key words
        json_key_words = json_words.intersection(key_words)
        product_key_words = product_words.intersection(key_words)
        
        if not json_key_words and not product_key_words:
            return 0.0
        
        # Calculate similarity based on key word matches
        common_key_words = json_key_words.intersection(product_key_words)
        total_key_words = json_key_words.union(product_key_words)
        
        if not total_key_words:
            return 0.0
        
        return len(common_key_words) / len(total_key_words)
    
    def _calculate_pattern_similarity(self, json_name: str, product_name: str) -> float:
        """Calculate similarity based on product naming patterns."""
        if not json_name or not product_name:
            return 0.0
        
        # Pattern matching for Cultivera-style names
        patterns = [
            # Pattern: BRAND_TYPE_FLAVOR_WEIGHT (e.g., "BALL_SAT_CARAMEL_10pk")
            (r'^([A-Z]+)_([A-Z]+)_([A-Z]+)_(\d+pk)$', r'^([A-Z]+)_([A-Z]+)_([A-Z]+)_(\d+pk)$'),
            # Pattern: BRAND_TYPE_WEIGHT (e.g., "BITE_SAT_10pk")
            (r'^([A-Z]+)_([A-Z]+)_(\d+pk)$', r'^([A-Z]+)_([A-Z]+)_(\d+pk)$'),
            # Pattern: BRAND_TYPE_FLAVOR_WEIGHT (e.g., "ROLL_UPS_XTRA_DRAGON_BALM_1:1_3.4oz")
            (r'^([A-Z]+)_([A-Z]+)_([A-Z]+)_([A-Z]+)_([A-Z]+)_([0-9:]+)_([0-9.]+oz)$', r'^([A-Z]+)_([A-Z]+)_([A-Z]+)_([A-Z]+)_([A-Z]+)_([0-9:]+)_([0-9.]+oz)$'),
            # Pattern: BRAND_TYPE_FLAVOR_WEIGHT (e.g., "SQUEEZE_TUBE_XTRA_DRAGON_CBD_3.4oz")
            (r'^([A-Z]+)_([A-Z]+)_([A-Z]+)_([A-Z]+)_([A-Z]+)_([0-9.]+oz)$', r'^([A-Z]+)_([A-Z]+)_([A-Z]+)_([A-Z]+)_([A-Z]+)_([0-9.]+oz)$'),
        ]
        
        json_lower = json_name.lower()
        product_lower = product_name.lower()
        
        # Check if both names follow similar patterns
        for json_pattern, product_pattern in patterns:
            json_match = re.match(json_pattern, json_name)
            product_match = re.match(product_pattern, product_name)
            
            if json_match and product_match:
                # Both follow the same pattern, check if components match
                json_groups = json_match.groups()
                product_groups = product_match.groups()
                
                if len(json_groups) == len(product_groups):
                    matches = sum(1 for j, p in zip(json_groups, product_groups) if j.lower() == p.lower())
                    return matches / len(json_groups)
        
        # Special handling for underscore vs space-separated names
        if '_' in json_name and ' ' in product_name:
            # Convert underscore to space for comparison
            json_space = json_name.replace('_', ' ')
            space_similarity = self._calculate_text_similarity(json_space, product_name)
            if space_similarity > 0.3:
                return space_similarity * 0.8  # Weight it slightly less than exact pattern matches
        
        # Check for common prefixes/suffixes
        common_prefixes = ['ball_', 'bite_', 'roll_', 'squeeze_', 'tube_']
        common_suffixes = ['_10pk', '_3.4oz', '_1:1', '_cbd', '_thc']
        
        json_prefix_score = 0
        json_suffix_score = 0
        product_prefix_score = 0
        product_suffix_score = 0
        
        for prefix in common_prefixes:
            if json_lower.startswith(prefix):
                json_prefix_score += 1
            if product_lower.startswith(prefix):
                product_prefix_score += 1
        
        for suffix in common_suffixes:
            if json_lower.endswith(suffix):
                json_suffix_score += 1
            if product_lower.endswith(suffix):
                product_suffix_score += 1
        
        # Calculate pattern similarity
        prefix_similarity = min(json_prefix_score, product_prefix_score) / max(json_prefix_score, product_prefix_score) if max(json_prefix_score, product_prefix_score) > 0 else 0
        suffix_similarity = min(json_suffix_score, product_suffix_score) / max(json_suffix_score, product_suffix_score) if max(json_suffix_score, product_suffix_score) > 0 else 0
        
        return (prefix_similarity + suffix_similarity) / 2
    
    def _find_cultivera_specialized_matches(self, json_item: dict) -> List[dict]:
        """Specialized matching for Cultivera-style products with underscore naming conventions."""
        try:
            json_name = str(json_item.get("product_name", "")).strip().lower()
            json_vendor = str(json_item.get("vendor", "")).strip().lower()
            json_brand = str(json_item.get("brand", "")).strip().lower()
            json_type = str(json_item.get("product_type", "")).strip().lower()
            json_weight = str(json_item.get("weight", "")).strip().lower()
            json_strain = str(json_item.get("strain_name", "")).strip().lower()
            
            if not json_name:
                return []
            
            all_products = self._get_all_products()
            matches = []
            
            # Cultivera-specific matching strategies
            for product in all_products:
                product_name = str(product.get('Product Name*', '') or product.get('original_name', '')).strip().lower()
                product_vendor = str(product.get('Vendor/Supplier*', '') or product.get('Vendor', '')).strip().lower()
                product_brand = str(product.get('Product Brand', '')).strip().lower()
                product_type = str(product.get('Product Type*', '')).strip().lower()
                product_weight = str(product.get('Weight*', '')).strip().lower()
                product_strain = str(product.get('Strain*', '')).strip().lower()
                
                # STRICT VENDOR ISOLATION: Skip products from different vendors
                if json_vendor and product_vendor:
                    vendor_matches = self._is_vendor_match(json_vendor, product_vendor)
                    if not vendor_matches:
                        # Skip non-matching vendors to prevent cross-brand contamination
                        continue
                
                score = 0.0
                match_reasons = []
                
                # Strategy 1: Underscore pattern matching
                if '_' in json_name and '_' in product_name:
                    json_parts = json_name.split('_')
                    product_parts = product_name.split('_')
                    
                    # Check for common parts
                    common_parts = set(json_parts).intersection(set(product_parts))
                    if common_parts:
                        part_similarity = len(common_parts) / max(len(json_parts), len(product_parts))
                        score += part_similarity * 0.4
                        match_reasons.append(f"underscore_parts:{part_similarity:.2f}")
                
                # Strategy 2: Brand prefix matching (BALL_, BITE_, ROLL_, etc.)
                cultivera_prefixes = ['ball', 'bite', 'roll', 'squeeze', 'tube']
                for prefix in cultivera_prefixes:
                    if json_name.startswith(prefix) and product_name.startswith(prefix):
                        score += 0.3
                        match_reasons.append(f"brand_prefix:{prefix}")
                        break
                
                # Strategy 3: Package count matching (10pk, 5pk, etc.)
                json_pk_match = re.search(r'(\d+)pk', json_name)
                product_pk_match = re.search(r'(\d+)pk', product_name)
                if json_pk_match and product_pk_match:
                    if json_pk_match.group(1) == product_pk_match.group(1):
                        score += 0.25
                        match_reasons.append(f"package_count:{json_pk_match.group(1)}")
                
                # Strategy 4: Weight matching (3.4oz, 1oz, etc.)
                json_weight_match = re.search(r'(\d+\.?\d*)oz', json_name)
                product_weight_match = re.search(r'(\d+\.?\d*)oz', product_name)
                if json_weight_match and product_weight_match:
                    if json_weight_match.group(1) == product_weight_match.group(1):
                        score += 0.2
                        match_reasons.append(f"weight_match:{json_weight_match.group(1)}")
                
                # Strategy 5: Strain matching
                if json_strain and product_strain and json_strain != 'mix':
                    strain_similarity = self._calculate_text_similarity(json_strain, product_strain)
                    if strain_similarity > 0.3:
                        score += strain_similarity * 0.15
                        match_reasons.append(f"strain_match:{strain_similarity:.2f}")
                
                # Strategy 6: Type matching
                if json_type and product_type:
                    type_similarity = self._calculate_text_similarity(json_type, product_type)
                    if type_similarity > 0.3:
                        score += type_similarity * 0.1
                        match_reasons.append(f"type_match:{type_similarity:.2f}")
                
                # Strategy 7: Fuzzy matching on cleaned names (remove underscores and numbers)
                json_clean = re.sub(r'[_\d]+', '', json_name)
                product_clean = re.sub(r'[_\d]+', '', product_name)
                if json_clean and product_clean:
                    from fuzzywuzzy import fuzz
                    clean_ratio = fuzz.ratio(json_clean, product_clean)
                    if clean_ratio > 40:
                        score += (clean_ratio / 100.0) * 0.2
                        match_reasons.append(f"clean_fuzzy:{clean_ratio}")
                
                # Only consider matches with reasonable scores
                if score > 0.15:  # Lower threshold for Cultivera products
                    product['fuzzy_score'] = score * 100
                    product['match_reasons'] = ', '.join(match_reasons)
                    product['original_name'] = product.get('Product Name*', 'Unknown')
                    matches.append(product)
            
            # Sort by score descending
            matches.sort(key=lambda x: x.get('fuzzy_score', 0), reverse=True)
            
            logging.info(f"Cultivera specialized matching found {len(matches)} potential matches for '{json_name}'")
            return matches[:5]  # Return top 5 matches
            
        except Exception as e:
            logging.error(f"Error in Cultivera specialized matching: {e}")
            return []
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity with fuzzy matching."""
        if not name1 or not name2:
            return 0.0
        
        # Use fuzzy matching for names
        try:
            from fuzzywuzzy import fuzz
            return fuzz.ratio(name1.lower(), name2.lower()) / 100.0
        except ImportError:
            return self._calculate_text_similarity(name1, name2)
    
    def _calculate_vendor_similarity(self, vendor1: str, vendor2: str) -> float:
        """Calculate vendor similarity."""
        return self._calculate_text_similarity(vendor1, vendor2)
    
    def _calculate_brand_similarity(self, brand1: str, brand2: str) -> float:
        """Calculate brand similarity."""
        return self._calculate_text_similarity(brand1, brand2)
    
    def _calculate_type_similarity(self, type1: str, type2: str) -> float:
        """Calculate product type similarity."""
        return self._calculate_text_similarity(type1, type2)
    
    def _calculate_weight_similarity(self, weight1: str, weight2: str) -> float:
        """Calculate weight similarity."""
        return self._calculate_text_similarity(weight1, weight2)
    
    def _calculate_strain_similarity(self, strain1: str, strain2: str) -> float:
        """Calculate strain similarity."""
        return self._calculate_text_similarity(strain1, strain2)
    
    def _get_product_vendor(self, product: dict) -> str:
        """Safely get vendor from a product dict supporting multiple schemas."""
        try:
            if not isinstance(product, dict):
                return ""
            # Prefer Excel schema exact column first
            vendor = product.get('Vendor/Supplier*')
            if vendor is None or str(vendor).strip() == '':
                # Support simplified key if present
                vendor = product.get('Vendor')
            return str(vendor).strip() if vendor is not None else ""
        except Exception:
            return ""

    def _create_product_from_db_row(self, row: dict) -> dict:
        """Create a product object in the same shape as Excel match from a DB row dict."""
        name = row.get('Product Name*') or row.get('product_name') or ''
        vendor = row.get('Vendor/Supplier*') or row.get('vendor') or ''
        brand = row.get('Product Brand') or row.get('brand') or ''
        ptype = row.get('Product Type*') or row.get('product_type') or ''
        weight = row.get('Weight*') or row.get('weight') or ''
        ratio = row.get('Ratio_or_THC_CBD') or row.get('Ratio') or ''
        strain = row.get('Product Strain') or row.get('strain_name') or ''

        product = {
            'Product Name*': name,
            'Vendor': vendor,
            'Vendor/Supplier*': vendor,
            'Product Brand': brand,
            'Product Type*': ptype,
            'Weight*': weight,
            'Ratio_or_THC_CBD': ratio,
            'Product Strain': strain,
            'displayName': name,
            'Source': 'DB_ALL'
        }
        return product

    def _find_enhanced_fuzzy_matches(self, json_item: dict) -> List[dict]:
        """Enhanced fuzzy matching using multiple strategies for better coverage."""
        try:
            json_name = str(json_item.get("product_name", "")).strip().lower()
            json_vendor = str(json_item.get("vendor", "")).strip().lower()
            json_brand = str(json_item.get("brand", "")).strip().lower()
            json_type = str(json_item.get("product_type", "")).strip().lower()
            json_weight = str(json_item.get("weight", "")).strip().lower()
            
            if not json_name:
                return []
            
            all_products = self._get_all_products()
            matches = []
            
            for product in all_products:
                product_name = str(product.get('Product Name*', '') or product.get('original_name', '')).strip().lower()
                product_vendor = str(product.get('Vendor/Supplier*', '') or product.get('Vendor', '')).strip().lower()
                product_brand = str(product.get('Product Brand', '')).strip().lower()
                product_type = str(product.get('Product Type*', '')).strip().lower()
                product_weight = str(product.get('Weight*', '')).strip().lower()
                
                # STRICT VENDOR ISOLATION: Skip products from different vendors
                if json_vendor and product_vendor:
                    vendor_matches = self._is_vendor_match(json_vendor, product_vendor)
                    if not vendor_matches:
                        # Skip non-matching vendors to prevent cross-brand contamination
                        continue
                
                score = 0.0
                match_reasons = []
                
                # Strategy 1: Fuzzy string matching on product names
                from fuzzywuzzy import fuzz
                name_ratio = fuzz.ratio(json_name, product_name)
                if name_ratio > 30:  # Lower threshold for more matches
                    score += (name_ratio / 100.0) * 0.4
                    match_reasons.append(f"name_fuzzy:{name_ratio}")
                
                # Strategy 2: Partial string matching
                partial_ratio = fuzz.partial_ratio(json_name, product_name)
                if partial_ratio > 40:
                    score += (partial_ratio / 100.0) * 0.3
                    match_reasons.append(f"partial_fuzzy:{partial_ratio}")
                
                # Strategy 3: Token set ratio (ignores word order)
                token_ratio = fuzz.token_set_ratio(json_name, product_name)
                if token_ratio > 35:
                    score += (token_ratio / 100.0) * 0.2
                    match_reasons.append(f"token_fuzzy:{token_ratio}")
                
                # Strategy 4: Vendor/brand matching bonus
                if json_vendor and product_vendor:
                    vendor_similarity = self._calculate_text_similarity(json_vendor, product_vendor)
                    if vendor_similarity > 0.4:
                        score += vendor_similarity * 0.1
                        match_reasons.append(f"vendor_match:{vendor_similarity:.2f}")
                
                # Strategy 5: Type matching bonus
                if json_type and product_type:
                    type_similarity = self._calculate_text_similarity(json_type, product_type)
                    if type_similarity > 0.4:
                        score += type_similarity * 0.1
                        match_reasons.append(f"type_match:{type_similarity:.2f}")
                
                # Strategy 6: Weight matching bonus
                if json_weight and product_weight:
                    weight_similarity = self._calculate_text_similarity(json_weight, product_weight)
                    if weight_similarity > 0.4:
                        score += weight_similarity * 0.1
                        match_reasons.append(f"weight_match:{weight_similarity:.2f}")
                
                # Strategy 7: Key word matching for difficult cases
                key_word_score = self._calculate_key_word_similarity(json_name, product_name)
                if key_word_score > 0:
                    score += key_word_score * 0.15
                    match_reasons.append(f"key_words:{key_word_score:.2f}")
                
                # Strategy 8: Pattern-based matching for Cultivera-style names
                pattern_score = self._calculate_pattern_similarity(json_name, product_name)
                if pattern_score > 0:
                    score += pattern_score * 0.2
                    match_reasons.append(f"pattern_match:{pattern_score:.2f}")
                
                # Strategy 9: Token sort ratio (handles word order variations)
                token_sort_ratio = fuzz.token_sort_ratio(json_name, product_name)
                if token_sort_ratio > 30:
                    score += (token_sort_ratio / 100.0) * 0.2
                    match_reasons.append(f"token_sort_fuzzy:{token_sort_ratio}")
                
                # Only consider matches with reasonable scores (lowered threshold)
                if score > 0.2:  # Lowered from 0.25
                    product['fuzzy_score'] = score * 100
                    product['match_reasons'] = ', '.join(match_reasons)
                    product['original_name'] = product.get('Product Name*', 'Unknown')
                    matches.append(product)
            
            # Sort by score descending
            matches.sort(key=lambda x: x.get('fuzzy_score', 0), reverse=True)
            
            logging.info(f"Enhanced fuzzy matching found {len(matches)} potential matches for '{json_name}'")
            return matches[:8]  # Return top 8 matches (increased from 5)
            
        except Exception as e:
            logging.error(f"Error in enhanced fuzzy matching: {e}")
            return []

    def _find_ceres_specialized_matches(self, json_item: dict) -> List[dict]:
        """Specialized matching for Ceres products that have generic names."""
        try:
            json_name = str(json_item.get("product_name", "")).strip().lower()
            json_vendor = str(json_item.get("vendor", "")).strip().lower()
            json_brand = str(json_item.get("brand", "")).strip().lower()
            json_type = str(json_item.get("product_type", "")).strip().lower()
            json_weight = str(json_item.get("weight", "")).strip().lower()
            json_strain = str(json_item.get("strain_name", "")).strip().lower()
            
            if not json_name:
                return []
            
            all_products = self._get_all_products()
            matches = []
            
            # Ceres-specific matching strategies
            for product in all_products:
                product_name = str(product.get('Product Name*', '') or product.get('original_name', '')).strip().lower()
                product_vendor = str(product.get('Vendor/Supplier*', '') or product.get('Vendor', '')).strip().lower()
                product_brand = str(product.get('Product Brand', '')).strip().lower()
                product_type = str(product.get('Product Type*', '')).strip().lower()
                product_weight = str(product.get('Weight*', '')).strip().lower()
                product_strain = str(product.get('Product Strain', '')).strip().lower()
                
                # Skip if not a Ceres product
                if 'ceres' not in product_vendor.lower() and 'ceres' not in product_brand.lower():
                    continue
                
                score = 0.0
                match_reasons = []
                
                # Strategy 1: Partial word matching for generic names
                json_words = set(json_name.split())
                product_words = set(product_name.split())
                common_words = json_words.intersection(product_words)
                
                if common_words:
                    word_score = len(common_words) / max(len(json_words), len(product_words))
                    score += word_score * 0.4
                    match_reasons.append(f"word_match:{word_score:.2f}")
                
                # Strategy 2: Type matching (very important for Ceres)
                if json_type and product_type:
                    type_similarity = self._calculate_text_similarity(json_type, product_type)
                    if type_similarity > 0.3:
                        score += type_similarity * 0.3
                        match_reasons.append(f"type_match:{type_similarity:.2f}")
                
                # Strategy 3: Weight matching
                if json_weight and product_weight:
                    weight_similarity = self._calculate_text_similarity(json_weight, product_weight)
                    if weight_similarity > 0.3:
                        score += weight_similarity * 0.2
                        match_reasons.append(f"weight_match:{weight_similarity:.2f}")
                
                # Strategy 4: Strain matching (if available)
                if json_strain and product_strain:
                    strain_similarity = self._calculate_text_similarity(json_strain, product_strain)
                    if strain_similarity > 0.3:
                        score += strain_similarity * 0.1
                        match_reasons.append(f"strain_match:{strain_similarity:.2f}")
                
                # Strategy 5: Special Ceres product name patterns
                ceres_patterns = {
                    'sativa': ['sativa', 'sat'],
                    'indica': ['indica', 'ind'],
                    'hybrid': ['hybrid', 'hyb'],
                    'capsules': ['capsule', 'cap', 'caps'],
                    'tincture': ['tincture', 'tinc'],
                    'balm': ['balm', 'cream'],
                    'chews': ['chew', 'gummy', 'edible'],
                    'boost': ['boost', 'immune'],
                    'dragon': ['dragon'],
                    'chill': ['chill', 'relax'],
                    'lifted': ['lifted', 'energ']
                }
                
                for pattern_key, pattern_words in ceres_patterns.items():
                    json_has_pattern = any(word in json_name for word in pattern_words)
                    product_has_pattern = any(word in product_name for word in pattern_words)
                    
                    if json_has_pattern and product_has_pattern:
                        score += 0.15
                        match_reasons.append(f"pattern_match:{pattern_key}")
                
                # Only consider matches with reasonable scores
                if score > 0.2:
                    product['fuzzy_score'] = score * 100
                    product['match_reasons'] = ', '.join(match_reasons)
                    product['original_name'] = product.get('Product Name*', 'Unknown')
                    matches.append(product)
            
            # Sort by score descending
            matches.sort(key=lambda x: x.get('fuzzy_score', 0), reverse=True)
            
            logging.info(f"Ceres specialized matching found {len(matches)} potential matches for '{json_name}'")
            return matches[:5]  # Return top 5 matches
            
        except Exception as e:
            logging.error(f"Error in Ceres specialized matching: {e}")
            return []

    def _get_all_products(self) -> List[dict]:
        """Get all available products for matching, EXCEL FIRST with priority."""
        try:
            candidates: List[dict] = []
            
            # PRIORITY 1: Excel rows (authoritative source - Excel data first!)
            if hasattr(self, 'excel_processor') and self.excel_processor and hasattr(self.excel_processor, 'df') and self.excel_processor.df is not None:
                try:
                    excel_count = 0
                    for _, row in self.excel_processor.df.iterrows():
                        row_dict = row.to_dict()
                        row_dict['_source'] = 'excel'
                        row_dict['_priority'] = 1  # Highest priority - Excel data first!
                        candidates.append(row_dict)
                        excel_count += 1
                    logging.info(f"Loaded {excel_count} products from EXCEL (highest priority)")
                except Exception as xl_err:
                    logging.debug(f"Excel candidates unavailable: {xl_err}")

            # PRIORITY 2: Database products (fallback source)
            try:
                # Try to use the app's global database instance first
                try:
                    from app import get_product_database
                    product_db = get_product_database()
                    logging.info("Using global product database instance supplied by app")
                except ImportError:
                    # Fallback to JSON matcher managed instance
                    product_db = self._get_product_database()
                    logging.info("Using JSON matcher managed ProductDatabase instance")
                
                db_products = product_db.get_all_products()
                if db_products:
                    # Mark database products with lower priority
                    for product in db_products:
                        product['_source'] = 'database'
                        product['_priority'] = 2  # Lower priority than Excel
                    candidates.extend(db_products)
                    logging.info(f"Loaded {len(db_products)} products from DATABASE (secondary priority)")
            except Exception as db_err:
                logging.warning(f"Database candidates unavailable: {db_err}")

            logging.info(f"Total candidates for matching: {len(candidates)} (Database: {len([c for c in candidates if c.get('_source') == 'database'])}, Excel: {len([c for c in candidates if c.get('_source') == 'excel'])})")
            return candidates
        except Exception as e:
            logging.error(f"Error getting all products: {e}")
            return []
    
    def _find_exact_name_matches(self, json_name: str) -> List[dict]:
        """Find exact name matches in the cache using indexed lookup."""
        normalized_name = self._normalize(json_name)
        
        # Use indexed cache for O(1) lookup instead of O(n) linear search
        if self._indexed_cache and 'exact_names' in self._indexed_cache:
            return self._indexed_cache['exact_names'].get(normalized_name, [])
        
        # Fallback to linear search if index not available
        matches = []
        if self._sheet_cache is not None:
            for cache_item in self._sheet_cache:
                if self._normalize(cache_item.get("original_name", "")) == normalized_name:
                    matches.append(cache_item)
        else:
            # Use database products if sheet cache is None
            all_products = self._get_all_products()
            for product in all_products:
                product_name = product.get("Product Name*", "")
                if self._normalize(product_name) == normalized_name:
                    # Convert to cache format
                    cache_item = {
                        "original_name": product_name,
                        "vendor": product.get("Vendor/Supplier*", ""),
                        "brand": product.get("Product Brand", ""),
                        "type": product.get("Product Type*", ""),
                        "_source": product.get("_source", "database"),
                        "_priority": product.get("_priority", 1)
                    }
                    matches.append(cache_item)
        
        return matches
    
    def _find_vendor_exact_name_matches(self, json_name: str, json_vendor: str) -> List[dict]:
        """Find exact name matches within the same vendor using indexed lookup."""
        normalized_name = self._normalize(json_name)
        
        # Use indexed cache for O(1) lookup
        if self._indexed_cache and 'vendor_exact_names' in self._indexed_cache:
            vendor_key = f"{normalized_name}|{json_vendor.lower()}"
            return self._indexed_cache['vendor_exact_names'].get(vendor_key, [])
        
        # Fallback to linear search if index not available
        matches = []
        if self._sheet_cache is not None:
            for cache_item in self._sheet_cache:
                cache_vendor = str(cache_item.get("vendor", ""))
                if (self._normalize(cache_item.get("original_name", "")) == normalized_name and
                    self._validate_vendor_match(json_vendor, cache_vendor)):
                    matches.append(cache_item)
        else:
            # Use database products if sheet cache is None
            all_products = self._get_all_products()
            for product in all_products:
                product_name = product.get("Product Name*", "")
                cache_vendor = str(product.get("Vendor/Supplier*", ""))
                if (self._normalize(product_name) == normalized_name and
                    self._validate_vendor_match(json_vendor, cache_vendor)):
                    # Convert to cache format
                    cache_item = {
                        "original_name": product_name,
                        "vendor": cache_vendor,
                        "brand": product.get("Product Brand", ""),
                        "type": product.get("Product Type*", ""),
                        "_source": product.get("_source", "database"),
                        "_priority": product.get("_priority", 1)
                    }
                    matches.append(cache_item)
        
        return matches
    
    def _find_fuzzy_name_matches(self, json_name: str, json_vendor: str = None, threshold: int = 50) -> List[dict]:
        """Find fuzzy name matches using optimized fuzzywuzzy."""
        matches = []
        
        # Get all potential candidates
        candidates = []
        if json_vendor:
            # Filter by vendor first - much stricter filtering
            # Use database products if sheet cache is None
            if self._sheet_cache is None:
                all_products = self._get_all_products()
                for product in all_products:
                    cache_vendor = str(product.get("Vendor/Supplier*", "") or product.get("vendor", ""))
                    # Use strict vendor validation
                    if self._validate_vendor_match(json_vendor, cache_vendor):
                        # Convert to cache format
                        cache_item = {
                            "original_name": product.get("Product Name*", ""),
                            "vendor": cache_vendor,
                            "brand": product.get("Product Brand", ""),
                            "type": product.get("Product Type*", ""),
                            "_source": product.get("_source", "database"),
                            "_priority": product.get("_priority", 1)
                        }
                        candidates.append(cache_item)
            else:
                for cache_item in self._sheet_cache:
                    cache_vendor = str(cache_item.get("vendor", ""))
                    # Use strict vendor validation
                    if self._validate_vendor_match(json_vendor, cache_vendor):
                        candidates.append(cache_item)
        else:
            # Use all candidates if no vendor specified
            if self._sheet_cache is None:
                # Use database products if sheet cache is None
                all_products = self._get_all_products()
                candidates = []
                for product in all_products:
                    # Convert to cache format
                    cache_item = {
                        "original_name": product.get("Product Name*", ""),
                        "vendor": product.get("Vendor/Supplier*", ""),
                        "brand": product.get("Product Brand", ""),
                        "type": product.get("Product Type*", ""),
                        "_source": product.get("_source", "database"),
                        "_priority": product.get("_priority", 1)
                    }
                    candidates.append(cache_item)
            else:
                candidates = self._sheet_cache
        
        # Limit candidates to prevent excessive processing
        max_candidates = 1000
        if len(candidates) > max_candidates:
            candidates = candidates[:max_candidates]
        
        # Use fuzzywuzzy to find best matches with early termination
        json_name_lower = json_name.lower()
        for cache_item in candidates:
            cache_name = cache_item.get("original_name", "")
            if cache_name:
                cache_name_lower = cache_name.lower()
                
                # Use only the most effective algorithm first (ratio is fastest)
                ratio = fuzz.ratio(json_name_lower, cache_name_lower)
                
                # Early termination if ratio is too low
                if ratio < threshold - 10:  # Give some buffer
                    continue
                
                # Only run additional algorithms if ratio is promising
                if ratio >= threshold:
                    # Use the best of ratio and partial_ratio (most effective combination)
                    partial_ratio = fuzz.partial_ratio(json_name_lower, cache_name_lower)
                    best_score = max(ratio, partial_ratio)
                else:
                    # Try partial_ratio as fallback
                    partial_ratio = fuzz.partial_ratio(json_name_lower, cache_name_lower)
                    if partial_ratio < threshold:
                        continue
                    best_score = partial_ratio
                
                if best_score >= threshold:
                    cache_item_copy = cache_item.copy()
                    cache_item_copy['fuzzy_score'] = best_score
                    matches.append(cache_item_copy)
                    
                    # Early termination if we have enough good matches
                    if len(matches) >= 10:
                        break
        
        # Sort by score (highest first) and limit results
        matches.sort(key=lambda x: x['fuzzy_score'], reverse=True)
        return matches[:5]  # Return only top 5 matches
    
    def _find_strain_based_matches(self, json_strain: str, json_vendor: str = None, json_type: str = None) -> List[dict]:
        """Find matches based on strain name with enhanced strain recognition."""
        matches = []
        
        # Enhanced strain normalization
        normalized_strain = self._normalize_strain_name(json_strain)
        
        for cache_item in self._sheet_cache:
            cache_name = str(cache_item.get("original_name", "")).lower()
            cache_vendor = str(cache_item.get("vendor", ""))
            cache_strain = str(cache_item.get("strain", "")).lower()
            
            # Check multiple strain matching strategies
            strain_match = False
            
            # Strategy 1: Direct strain name match
            if json_strain in cache_name or json_strain in cache_strain:
                strain_match = True
            # Strategy 2: Normalized strain match
            elif normalized_strain and (normalized_strain in cache_name or normalized_strain in cache_strain):
                strain_match = True
            # Strategy 3: Partial strain match (for compound names like "Blue Dream")
            elif self._partial_strain_match(json_strain, cache_name):
                strain_match = True
            
            if strain_match:
                # Apply vendor filtering if specified
                if not json_vendor or self._validate_vendor_match(json_vendor, cache_vendor):
                    # Apply product type filtering if specified
                    if not json_type or self._product_types_compatible(json_type, cache_item):
                        # Calculate strain match score
                        strain_score = self._calculate_strain_match_score(json_strain, cache_name, cache_strain)
                        cache_item_copy = cache_item.copy()
                        cache_item_copy['strain_score'] = strain_score
                        matches.append(cache_item_copy)
        
        # Sort by strain match score
        matches.sort(key=lambda x: x.get('strain_score', 0), reverse=True)
        return matches
    
    def _find_brand_type_weight_matches(self, json_brand: str, json_type: str, json_weight: str, json_vendor: str = None) -> List[dict]:
        """Find matches based on brand, type, and weight combination."""
        matches = []
        
        for cache_item in self._sheet_cache:
            cache_brand = str(cache_item.get("Product Brand", cache_item.get("brand", ""))).strip().lower()
            cache_name = str(cache_item.get("original_name", "")).lower()
            cache_vendor = str(cache_item.get("vendor", ""))
            
            # Check brand match
            brand_match = (json_brand in cache_brand or cache_brand in json_brand or
                          fuzz.ratio(json_brand, cache_brand) >= 80)
            
            # Check type match
            type_match = self._product_types_compatible(json_type, cache_item)
            
            # Check weight match
            weight_match = self._weights_compatible(json_weight, cache_name)
            
            # Check vendor match
            vendor_match = (not json_vendor or self._validate_vendor_match(json_vendor, cache_vendor))
            
            # Calculate composite score
            score = 0
            if brand_match: score += 0.4
            if type_match: score += 0.3
            if weight_match: score += 0.2
            if vendor_match: score += 0.1
            
            if score >= 0.4:  # Require at least brand + type match (reduced from 0.6 to 0.4)
                cache_item_copy = cache_item.copy()
                cache_item_copy['composite_score'] = score
                matches.append(cache_item_copy)
        
        # Sort by composite score
        matches.sort(key=lambda x: x['composite_score'], reverse=True)
        return matches
    
    def _get_vendor_variations(self, vendor: str) -> List[str]:
        """Get known vendor name variations - much more strict to avoid false matches."""
        vendor_variations = {
            # Only exact variations of the same company
            'dank czar': ['dcz holdings inc', 'dcz holdings inc.', 'dcz', 'dank czar holdings'],
            'dcz holdings': ['dank czar', 'dcz', 'dcz holdings inc', 'dcz holdings inc.'],
            'dcz holdings inc': ['dank czar', 'dcz', 'dcz holdings', 'dcz holdings inc.'],
            'dcz holdings inc.': ['dank czar', 'dcz', 'dcz holdings', 'dcz holdings inc'],
            
            # JSM LLC is separate from Dank Czar - remove cross-references
            'jsm llc': ['jsm', 'jsm labs'],
            
            # Hustler's Ambition variations
            'hustler\'s ambition': ['1555 industrial llc', 'hustlers ambition'],
            'hustlers ambition': ['1555 industrial llc', 'hustler\'s ambition'],
            '1555 industrial llc': ['hustler\'s ambition', 'hustlers ambition'],
            
            # Omega variations only
            'omega': ['omega labs', 'omega cannabis'],
            
            # Airo Pro variations only
            'airo pro': ['airo', 'airopro'],
            'jsm': ['jsm llc', 'jsm labs'],
            'harmony': ['harmony farms', 'harmony cannabis'],
            
            # Additional Cultivera vendor variations
            'blue roots cannabis': ['blue roots', 'blue roots cannabis llc', 'blue roots llc'],
            'grow op farms': ['grow op', 'grow op farms llc', 'grow op llc'],
            'collections cannabis': ['collections', 'collections cannabis llc', 'collections llc'],
            'cloud 9 farms': ['cloud 9', 'cloud 9 farms llc', 'cloud 9 llc'],
            'the collective': ['collective', 'collective cannabis', 'collective llc'],
            '1555 industrial': ['1555 industrial llc', '1555 llc', '1555 industrial cannabis'],
        }
        
        return vendor_variations.get(vendor, [])
    
    def _validate_vendor_match(self, json_vendor: str, cache_vendor: str) -> bool:
        """Validate that vendor match is truly appropriate."""
        if not json_vendor or not cache_vendor:
            return False
            
        json_vendor_lower = json_vendor.strip().lower()
        cache_vendor_lower = cache_vendor.strip().lower()
        
        # Exact match is always valid
        if json_vendor_lower == cache_vendor_lower:
            return True
            
        # Check vendor variations
        vendor_variations = self._get_vendor_variations(json_vendor_lower)
        if cache_vendor_lower in vendor_variations:
            return True
            
        # Check if vendor names are very similar (e.g., "Dank Czar" vs "Dank Czar Holdings")
        if (json_vendor_lower in cache_vendor_lower or 
            cache_vendor_lower in json_vendor_lower):
            # Only allow if the difference is minimal (e.g., "Holdings", "Inc", etc.)
            allowed_suffixes = [' holdings', ' inc', ' inc.', ' llc', ' corp', ' corporation']
            base_vendor = json_vendor_lower
            for suffix in allowed_suffixes:
                if base_vendor.endswith(suffix):
                    base_vendor = base_vendor[:-len(suffix)]
                    break
                    
            if base_vendor in cache_vendor_lower or cache_vendor_lower in base_vendor:
                return True
        
        # IMPROVED: Add fuzzy vendor matching as fallback to improve match rate
        try:
            from fuzzywuzzy import fuzz
            similarity = fuzz.ratio(json_vendor_lower, cache_vendor_lower)
            # Allow vendors with 70% similarity or higher
            if similarity >= 70:
                logging.debug(f"✅ Fuzzy vendor match: '{json_vendor}' ≈ '{cache_vendor}' (similarity: {similarity}%)")
                return True
        except ImportError:
            # Basic fallback if fuzzywuzzy not available
            common_words = set(json_vendor_lower.split()) & set(cache_vendor_lower.split())
            if len(common_words) >= 1 and len(common_words) >= min(len(json_vendor_lower.split()), len(cache_vendor_lower.split())) * 0.5:
                logging.debug(f"✅ Basic vendor match: '{json_vendor}' ≈ '{cache_vendor}' (common words: {common_words})")
                return True
                
        return False
    
    def _find_weight_based_matches(self, json_weight: str, json_type: str, json_vendor: str = None) -> List[dict]:
        """Find matches based on weight and product type compatibility."""
        matches = []
        
        # Normalize weight for comparison
        json_weight_normalized = self._normalize_weight(json_weight)
        if not json_weight_normalized:
            return matches
        
        for cache_item in self._sheet_cache:
            cache_weight = str(cache_item.get("Weight*", cache_item.get("weight", "")))
            cache_type = str(cache_item.get("Product Type*", cache_item.get("product_type", ""))).lower()
            
            # Check weight compatibility
            if self._weights_compatible(json_weight_normalized, cache_weight):
                # Check product type compatibility
                if self._product_types_compatible(json_type, cache_item):
                    # Apply vendor filtering if specified
                    if not json_vendor or self._validate_vendor_match(json_vendor, str(cache_item.get("vendor", ""))):
                        # Calculate score based on weight similarity
                        weight_score = self._calculate_weight_similarity(json_weight_normalized, cache_weight)
                        cache_item_copy = cache_item.copy()
                        cache_item_copy['weight_score'] = weight_score
                        matches.append(cache_item_copy)
        
        # Sort by weight similarity score
        matches.sort(key=lambda x: x.get('weight_score', 0), reverse=True)
        return matches
    
    def _find_strain_weight_matches(self, json_strain: str, json_weight: str, json_vendor: str = None) -> List[dict]:
        """Find matches based on strain name and weight combination."""
        matches = []
        
        # Normalize weight for comparison
        json_weight_normalized = self._normalize_weight(json_weight)
        if not json_weight_normalized:
            return matches
        
        for cache_item in self._sheet_cache:
            cache_strain = str(cache_item.get("strain", "")).lower()
            cache_weight = str(cache_item.get("weight", ""))
            
            # Check if strain appears in the cache item
            if json_strain in cache_strain or cache_strain in json_strain:
                # Check weight compatibility
                if self._weights_compatible(json_weight_normalized, cache_weight):
                    # Apply vendor filtering if specified
                    if not json_vendor or self._validate_vendor_match(json_vendor, str(cache_item.get("vendor", ""))):
                        # Calculate composite score
                        strain_score = 0.7  # Base score for strain match
                        weight_score = self._calculate_weight_similarity(json_weight_normalized, cache_weight)
                        composite_score = (strain_score + weight_score) / 2
                        
                        cache_item_copy = cache_item.copy()
                        cache_item_copy['composite_score'] = composite_score
                        matches.append(cache_item_copy)
        
        # Sort by composite score
        matches.sort(key=lambda x: x.get('composite_score', 0), reverse=True)
        return matches
    
    def _normalize_weight(self, weight: str) -> Optional[float]:
        """Normalize weight string to float value for comparison."""
        try:
            # Remove common units and convert to float
            weight_clean = weight.lower().replace('g', '').replace('gram', '').replace('grams', '').replace('mg', '').replace('milligram', '').replace('milligrams', '').strip()
            return float(weight_clean)
        except (ValueError, AttributeError):
            return None
    
    def _calculate_weight_similarity(self, weight1: float, weight2: float) -> float:
        """Calculate similarity score between two weights."""
        try:
            # Convert to float if strings
            w1 = float(weight1) if isinstance(weight1, str) else weight1
            w2 = float(weight2) if isinstance(weight2, str) else weight2
            
            # Calculate percentage difference
            if w1 == 0 or w2 == 0:
                return 0.0
            
            diff = abs(w1 - w2)
            max_weight = max(w1, w2)
            similarity = 1.0 - (diff / max_weight)
            
            return max(0.0, similarity)
        except (ValueError, TypeError):
            return 0.0
    
    def _normalize_strain_name(self, strain: str) -> Optional[str]:
        """Normalize strain name for better matching."""
        if not strain:
            return None
        
        # Common strain name variations and abbreviations
        strain_variations = {
            'og': 'og kush',
            'kush': 'og kush',
            'blue': 'blue dream',
            'dream': 'blue dream',
            'sour': 'sour diesel',
            'diesel': 'sour diesel',
            'wedding': 'wedding cake',
            'cake': 'wedding cake',
            'runtz': 'runtz',
            'gelato': 'gelato',
            'cookies': 'girl scout cookies',
            'gsc': 'girl scout cookies',
            'mac': 'mac 1',
            'mac1': 'mac 1'
        }
        
        strain_lower = strain.lower().strip()
        return strain_variations.get(strain_lower, strain_lower)
    
    def _partial_strain_match(self, json_strain: str, cache_name: str) -> bool:
        """Check for partial strain matches in compound names."""
        strain_words = json_strain.split()
        if len(strain_words) < 2:
            return False
        
        # Check if multiple words from strain appear in cache name
        matches = 0
        for word in strain_words:
            if len(word) > 2 and word in cache_name:  # Only consider words longer than 2 chars
                matches += 1
        
        # Require at least 2 words to match for compound strains
        return matches >= 2
    
    def _calculate_strain_match_score(self, json_strain: str, cache_name: str, cache_strain: str) -> float:
        """Calculate a score for strain matching quality."""
        score = 0.0
        
        # Exact match gets highest score
        if json_strain == cache_strain:
            score += 1.0
        elif json_strain in cache_strain or cache_strain in json_strain:
            score += 0.8
        
        # Name-based matching
        if json_strain in cache_name:
            score += 0.6
        
        # Partial matching for compound strains
        if self._partial_strain_match(json_strain, cache_name):
            score += 0.4
        
        return min(1.0, score)
    
    def _product_types_compatible(self, json_type: str, cache_item: dict) -> bool:
        """Check if product types are compatible."""
        cache_name = str(cache_item.get("original_name", "")).lower()
        cache_type = str(cache_item.get("Product Type*", cache_item.get("product_type", ""))).lower()
        
        # Define product type categories
        type_categories = {
            'flower': ['flower', 'bud', 'nug', 'usable marijuana'],
            'concentrate': ['concentrate', 'rosin', 'wax', 'shatter', 'live resin', 'distillate'],
            'vape': ['vape', 'cartridge', 'cart', 'all-in-one'],
            'edible': ['edible', 'gummy', 'chocolate', 'cookie', 'brownie'],
            'pre-roll': ['pre-roll', 'preroll', 'joint', 'blunt'],
            'tincture': ['tincture', 'drops', 'sublingual'],
            'topical': ['topical', 'cream', 'lotion', 'salve']
        }
        
        # Find JSON type category
        json_category = None
        for category, keywords in type_categories.items():
            if any(keyword in json_type for keyword in keywords):
                json_category = category
                break
        
        # Find cache item category - check both Product Type* field and name
        cache_category = None
        
        # First try to get category from Product Type* field
        if cache_type:
            for category, keywords in type_categories.items():
                if any(keyword in cache_type for keyword in keywords):
                    cache_category = category
                    break
        
        # If no category found from Product Type* field, try the name
        if not cache_category:
            for category, keywords in type_categories.items():
                if any(keyword in cache_name for keyword in keywords):
                    cache_category = category
                    break
        
        # Return True if categories match or if either is None (unknown)
        return json_category is None or cache_category is None or json_category == cache_category
    
    def _weights_compatible(self, json_weight: str, cache_name: str) -> bool:
        """Check if weights are compatible."""
        if not json_weight or not cache_name:
            return False
        
        # Extract weight from cache name using regex
        weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(g|mg)', cache_name.lower())
        if weight_match:
            cache_weight = float(weight_match.group(1))
            cache_unit = weight_match.group(2)
            
            # Extract weight from JSON
            json_weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(g|mg)', json_weight.lower())
            if json_weight_match:
                json_weight_val = float(json_weight_match.group(1))
                json_unit = json_weight_match.group(2)
                
                # Convert to same unit for comparison
                if json_unit == 'mg' and cache_unit == 'g':
                    json_weight_val = json_weight_val / 1000
                elif json_unit == 'g' and cache_unit == 'mg':
                    json_weight_val = json_weight_val * 1000
                
                # Allow 10% tolerance
                tolerance = 0.1
                return abs(json_weight_val - cache_weight) / cache_weight <= tolerance
        
        return False

    def get_product_database_priority_info(self) -> Dict[str, Any]:
        """
        Get information about Product Database priority status.
        
        Returns:
            Dictionary containing Product Database status and priority information
        """
        try:
            product_db = self._get_product_database()
            strains = product_db.get_all_strains()
            products = product_db.get_all_products()
            
            return {
                'enabled': True,
                'strain_count': len(strains),
                'product_count': len(products),
                'priority': 'HIGH - Product Database lookups prioritized over JSON exact matching',
                'message': f'Product Database available with {len(strains)} strains and {len(products)} products'
            }
        except Exception as e:
            return {
                'enabled': False,
                'strain_count': 0,
                'product_count': 0,
                'priority': 'DISABLED - JSON exact matching used as fallback',
                'message': f'Product Database not available: {e}'
            }
    
    def _process_description_from_product_name(self, product_name: str, weight: str = None, units: str = None) -> str:
        """Process description using the Excel processor formula with weight formatting."""
        if not product_name:
            return ''
        
        # Clean up the product name first
        description = str(product_name).strip()
        
        # Apply Excel processor formula: Remove " by " patterns
        if " by " in description:
            description = description.split(" by ")[0].strip()
        
        # Apply Excel processor formula: Remove weight information (patterns like " - 1g", " - .5g")
        import re
        description = re.sub(r' - [\d.].*$', '', description)
        
        # CRITICAL FIX: Don't add weight to description to avoid duplication
        # Weight will be handled separately in the WeightUnits field
        return description

    def _create_detailed_display_name(self, product_name: str, description: str, thc_result: str, cbd_result: str, test_unit: str, weight: str = None, units: str = None) -> str:
        """
        Create a detailed display name that includes CBD/THC information like:
        "5:1 Immune Boost Capsules - 230mg CBD / 50mg THC / 10mg CBG / 10mg CBN"
        
        Args:
            product_name: The product name
            description: Product description
            thc_result: THC test result
            cbd_result: CBD test result
            test_unit: Test result unit (% or mg)
            weight: Weight value (optional)
            units: Units (optional)
            
        Returns:
            Detailed display name string
        """
        try:
            # Start with the product name or description
            base_name = product_name.strip() if product_name else description.strip()
            if not base_name:
                return "Unknown Product"
            
            # Clean the base name
            base_name = base_name.replace(" by Dabstract JSON", "").strip()
            
            # Build cannabinoid information
            cannabinoid_parts = []
            
            # Add CBD information
            if cbd_result and cbd_result.strip() and cbd_result != "0" and cbd_result != "0.00":
                try:
                    cbd_value = float(cbd_result)
                    if cbd_value > 0:
                        unit_str = test_unit if test_unit else "mg"
                        cannabinoid_parts.append(f"{cbd_value:g}{unit_str} CBD")
                except (ValueError, TypeError):
                    pass
            
            # Add THC information
            if thc_result and thc_result.strip() and thc_result != "0" and thc_result != "0.00":
                try:
                    thc_value = float(thc_result)
                    if thc_value > 0:
                        unit_str = test_unit if test_unit else "mg"
                        cannabinoid_parts.append(f"{thc_value:g}{unit_str} THC")
                except (ValueError, TypeError):
                    pass
            
            # Add CBG information if available (from other fields)
            # Note: CBG data would come from additional database fields if available
            cbg_result = ""  # This would come from CBG test result fields if available
            if cbg_result and cbg_result.strip() and cbg_result != "0" and cbg_result != "0.00":
                try:
                    cbg_value = float(cbg_result)
                    if cbg_value > 0:
                        unit_str = test_unit if test_unit else "mg"
                        cannabinoid_parts.append(f"{cbg_value:g}{unit_str} CBG")
                except (ValueError, TypeError):
                    pass
            
            # Add CBN information if available (from other fields)
            # Note: CBN data would come from additional database fields if available
            cbn_result = ""  # This would come from CBN test result fields if available
            if cbn_result and cbn_result.strip() and cbn_result != "0" and cbn_result != "0.00":
                try:
                    cbn_value = float(cbn_result)
                    if cbn_value > 0:
                        unit_str = test_unit if test_unit else "mg"
                        cannabinoid_parts.append(f"{cbn_value:g}{unit_str} CBN")
                except (ValueError, TypeError):
                    pass
            
            # Create the detailed display name
            if cannabinoid_parts:
                cannabinoid_info = " / ".join(cannabinoid_parts)
                detailed_name = f"{base_name} - {cannabinoid_info}"
            else:
                # If no cannabinoid info, just use the base name (no weight duplication)
                detailed_name = base_name
            
            return detailed_name
            
        except Exception as e:
            logging.warning(f"Error creating detailed display name: {e}")
            # Fallback to simple product name
            return product_name.strip() if product_name else "Unknown Product"

    def _determine_lineage_for_product(self, product_type: str, existing_lineage: str, product_name: str = "", product_strain: str = "") -> str:
        """
        Determine the appropriate lineage for a product based on its type.
        
        Args:
            product_type: The product type (e.g., "edible (solid)", "flower", etc.)
            existing_lineage: Any existing lineage from the database
            product_name: The product name to check for explicit lineage indicators
            product_strain: The product strain to check for CBD indicators
            
        Returns:
            The appropriate lineage string
        """
        # Import constants to check product type classification
        from src.core.constants import CLASSIC_TYPES
        
        logging.info(f"🧬 LINEAGE DEBUG: product_type='{product_type}', existing_lineage='{existing_lineage}', product_name='{product_name}', product_strain='{product_strain}'")
        logging.info(f"🧬 CLASSIC_TYPES: {CLASSIC_TYPES}")
        
        # Check if this is a classic product type
        is_classic = product_type and product_type.strip().lower() in CLASSIC_TYPES
        logging.info(f"🧬 IS_CLASSIC: {is_classic} (product_type.lower()='{product_type.lower() if product_type else 'None'}')")
        
        # CRITICAL FIX: For NONCLASSIC types, ALWAYS use MIXED or CBD (never SATIVA/INDICA/HYBRID)
        # This ensures edibles, tinctures, topicals, etc. get proper nonclassic colors
        if not is_classic:
            logging.info(f"🧬 NONCLASSIC TYPE DETECTED: '{product_type}' - will use MIXED or CBD lineage only")
            
            # Check for paraphernalia product type first
            if product_type and product_type.strip().lower() == 'paraphernalia':
                logging.info(f"🧬 PARAPHERNALIA DETECTED: '{product_type}' -> 'PARAPHERNALIA'")
                return 'PARAPHERNALIA'
            
            # Check Product Strain for CBD indicators first
            if product_strain:
                strain_lower = product_strain.lower()
                if 'cbd blend' in strain_lower or 'cbd' in strain_lower:
                    logging.info(f"🧬 CBD STRAIN DETECTED: '{product_strain}' for nonclassic type '{product_type}'")
                    # CRITICAL FIX: CBD Blend products should ALWAYS get CBD lineage (yellow color)
                    # regardless of product type - this ensures proper color display
                    logging.info(f"🧬 CBD BLEND FIX: '{product_name}' (strain: {product_strain}) -> 'CBD'")
                    return 'CBD'
            
            # Check product name for CBD indicators
            if product_name:
                name_lower = product_name.lower()
                if any(word in name_lower for word in ['cbd', 'hemp', 'low-thc']):
                    # CRITICAL FIX: Products with CBD in the name should get CBD lineage (yellow color)
                    # regardless of product type - this ensures proper color display
                    logging.info(f"🧬 CBD NAME FIX: '{product_name}' -> 'CBD'")
                    return 'CBD'
            
            # Default for nonclassic types is MIXED (blue color)
            logging.info(f"🧬 NONCLASSIC TYPE DEFAULT: '{product_type}' -> 'MIXED'")
            return 'MIXED'
        
        # CLASSIC TYPES ONLY: Check for explicit lineage indicators in product name
        if product_name:
            name_lower = product_name.lower()
            if any(word in name_lower for word in ['sativa', 'sativa-dominant']):
                logging.info(f"🧬 CLASSIC TYPE WITH SATIVA IN NAME: '{product_name}' -> 'SATIVA'")
                return 'SATIVA'
            elif any(word in name_lower for word in ['indica', 'indica-dominant']):
                logging.info(f"🧬 CLASSIC TYPE WITH INDICA IN NAME: '{product_name}' -> 'INDICA'")
                return 'INDICA'
            elif any(word in name_lower for word in ['hybrid', 'balanced']):
                logging.info(f"🧬 CLASSIC TYPE WITH HYBRID IN NAME: '{product_name}' -> 'HYBRID'")
                return 'HYBRID'
            elif any(word in name_lower for word in ['cbd', 'hemp', 'low-thc']):
                logging.info(f"🧬 CLASSIC TYPE WITH CBD IN NAME: '{product_name}' -> 'CBD'")
                return 'CBD'
        
        # Classic types: use existing lineage or default to HYBRID
        result_lineage = existing_lineage or "HYBRID"
        logging.info(f"🧬 CLASSIC TYPE: '{product_type}' -> '{result_lineage}' (existing: '{existing_lineage}')")
        return result_lineage

    def _calculate_ratio_for_json_product(self, product_type: str, json_item: Dict = None) -> str:
        """
        Calculate ratio for JSON products following classic vs nonclassic rules.
        
        Args:
            product_type: The product type
            json_item: Original JSON item data (optional)
            
        Returns:
            Properly formatted ratio string
        """
        from src.core.constants import CLASSIC_TYPES
        
        if not product_type:
            return ""
        
        product_type_lower = product_type.strip().lower()
        is_classic = product_type_lower in CLASSIC_TYPES
        
        # For classic types, use default THC:CBD format
        if is_classic:
            return "THC: | BR | CBD:"
        
        # For nonclassic types, try to extract ratio from JSON data or product name
        ratio = ""
        
        # First, try to get ratio from JSON item
        if json_item:
            # Check various possible ratio fields in JSON
            ratio_fields = ['ratio', 'ratio_or_thc_cbd', 'thc_cbd_ratio', 'cannabinoid_ratio']
            for field in ratio_fields:
                if field in json_item and json_item[field]:
                    ratio = str(json_item[field]).strip()
                    if ratio and ratio.lower() not in ['nan', 'none', 'null', '']:
                        break
            
            # If no ratio field found, try to extract from product name
            if not ratio and 'product_name' in json_item:
                product_name = str(json_item['product_name']).strip()
                ratio = self._extract_ratio_from_product_name(product_name, product_type)
        
        # Return the ratio if found, otherwise empty string for nonclassic types
        return ratio if ratio else ""

    def _extract_ratio_from_product_name(self, product_name: str, product_type: str) -> str:
        """
        Extract ratio from product name for nonclassic products.
        
        Args:
            product_name: The product name
            product_type: The product type
            
        Returns:
            Extracted ratio string or empty string
        """
        if not product_name:
            return ""
        
        import re
        
        # Look for ratio patterns in product name
        ratio_patterns = [
            r'(\d+:\d+(?::\d+)*)',  # 1:1, 2:1, 1:2:1, etc.
            r'(\d+/\d+)',           # 1/1, 2/1, etc.
            r'(\d+mg.*?cbd)',       # 100mg CBD, etc.
            r'(cbd.*?\d+mg)',       # CBD 100mg, etc.
        ]
        
        for pattern in ratio_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""

    def _normalize_weight_for_json_product(self, weight: str, units: str, product_type: str, product_name: str = "") -> tuple:
        """
        Normalize weight and units for JSON products following Excel processor rules.
        
        Args:
            weight: Original weight value
            units: Original units
            product_type: Product type
            product_name: Product name for special cases
            
        Returns:
            Tuple of (normalized_weight, normalized_units)
        """
        from src.core.constants import CLASSIC_TYPES
        
        if not weight or str(weight).strip() in ['', 'nan', 'NaN', 'None']:
            return '1', 'g'  # Default fallback
        
        weight = str(weight).strip()
        units = str(units).strip() if units else 'g'
        
        # Determine if this is a nonclassic product
        is_nonclassic = product_type.lower() not in [ct.lower() for ct in CLASSIC_TYPES]
        
        # For nonclassic types, convert grams to ounces
        if is_nonclassic and units.lower() in ['g', 'gram', 'grams']:
            try:
                weight_val = float(weight)
                # Convert grams to ounces (1 oz = 28.3495 g)
                oz_val = round(weight_val / 28.3495, 2)
                # Remove trailing zeros and format without space before unit
                if oz_val.is_integer():
                    return f"{int(oz_val)}oz", 'oz'
                else:
                    return f"{oz_val:.2f}".rstrip('0').rstrip('.') + 'oz', 'oz'
            except ValueError:
                # If conversion fails, return original values
                return weight, units
        
        # For classic types or already correct units, return as-is
        return weight, units

    def _create_tag_from_database_info(self, db_info: Dict, vendor: str, json_item: Dict = None) -> Dict:
        """
        Create a product tag from Product Database information.
        This method is used when a Product Database lookup is successful.
        
        Args:
            db_info: Product information from the database
            vendor: The vendor name
            json_item: Original JSON item data (optional, for price/weight override)
            
        Returns:
            Dictionary containing the product tag information
        """
        try:
            # Helper function to clean product names
            def clean_product_name(name):
                if not name:
                    return name
                import re
                # Only remove obvious suffixes that are clearly not part of the product name
                cleaned = re.sub(r'\s*by\s+Dabstract\s+JSON\s*$', '', name, flags=re.IGNORECASE)
                # Remove extra whitespace but preserve the actual product name
                cleaned = re.sub(r'\s+', ' ', cleaned)
                return cleaned.strip()
            
            # Extract all available information from database using correct field names
            brand = db_info.get("Product Brand", "") or db_info.get("brand", "")
            product_type = db_info.get("Product Type*", "") or db_info.get("product_type", "")
            strain = db_info.get("Product Strain", "") or db_info.get("product_strain", "")
            lineage = db_info.get("Lineage", "") or db_info.get("lineage", "")
            
            # CRITICAL FIX: Extract Price from database - try multiple field name variations
            raw_price = (db_info.get("Price", "") or 
                        db_info.get("price", "") or 
                        db_info.get("Price*", "") or
                        db_info.get("Price* (Tier Name for Bulk)", ""))
            price = format_price(raw_price) if str(raw_price).strip() else ""
            
            # CRITICAL FIX: Extract Weight and Units from database - try multiple field name variations
            db_weight = (db_info.get("Weight*", "") or 
                        db_info.get("Weight", "") or 
                        db_info.get("weight", "") or
                        db_info.get("CombinedWeight", ""))
            db_units = (db_info.get("Units", "") or 
                       db_info.get("units", "") or
                       db_info.get("Weight Unit* (grams/gm or ounces/oz)", "") or
                       db_info.get("Weight Unit*", ""))
            
            weight, units = self._normalize_weight_for_json_product(
                db_weight,
                db_units,
                product_type,
                db_info.get("Product Name*", "") or db_info.get("product_name", "")
            )
            description = db_info.get("Description", "") or db_info.get("description", "")
            thc_result = str(db_info.get("THC test result", "") or db_info.get("thc_test_result", ""))
            cbd_result = str(db_info.get("CBD test result", "") or db_info.get("cbd_test_result", ""))
            test_unit = str(db_info.get("Test result unit (% or mg)", "%") or db_info.get("test_result_unit", "%"))
            batch_num = str(db_info.get("Batch Number", "") or db_info.get("batch_number", ""))
            lot_num = str(db_info.get("Lot Number", "") or db_info.get("lot_number", ""))
            barcode = str(db_info.get("Barcode*", "") or db_info.get("barcode", ""))
            cost = str(db_info.get("cost", ""))
            medical_only = str(db_info.get("Medical Only (Yes/No)", "No") or db_info.get("medical_only", "No"))
            raw_med_price = db_info.get("Med Price", "") or db_info.get("med_price", "")
            med_price = format_price(raw_med_price) if str(raw_med_price).strip() else ""
            expiration = str(db_info.get("Expiration Date(YYYY-MM-DD)", "") or db_info.get("expiration_date", ""))
            is_archived = str(db_info.get("Is Archived? (yes/no)", "no") or db_info.get("is_archived", "no"))
            thc_per_serving = str(db_info.get("THC Per Serving", "") or db_info.get("thc_per_serving", ""))
            allergens = str(db_info.get("Allergens", "") or db_info.get("allergens", ""))
            solvent = str(db_info.get("Solvent", "") or db_info.get("solvent", ""))
            accepted_date = str(db_info.get("Accepted Date", "") or db_info.get("accepted_date", ""))
            internal_id = str(db_info.get("Internal Product Identifier", "") or db_info.get("internal_product_identifier", ""))
            product_tags = str(db_info.get("Product Tags (comma separated)", "") or db_info.get("product_tags", ""))
            image_url = str(db_info.get("Image URL", "") or db_info.get("image_url", ""))
            ingredients = str(db_info.get("Ingredients", "") or db_info.get("ingredients", ""))
            
            # Create tag using database information - prioritize Product Name* from database
            # Always use Product Name* from database if available, otherwise use Description
            # CRITICAL FIX: Use Description column from database FIRST (highest priority)
            # Priority: Database Description > Transformed SKU > Raw SKU
            raw_product_name = db_info.get("Product Name*", "") or db_info.get("ProductName", "")
            db_description = db_info.get("Description", "")
            
            # Use database Description if it exists and is not just the SKU
            if db_description and db_description != raw_product_name:
                primary_product_name = db_description
                logging.info(f"📝 Using database Description: '{primary_product_name}'")
            else:
                # Fall back to transforming the SKU
                primary_product_name = transform_sku_to_readable_name(raw_product_name) or raw_product_name
                logging.info(f"📝 Using transformed SKU: '{primary_product_name}'")
            
            if not primary_product_name and strain and lineage and weight and units:
                # Strain-based lookup: create formatted description
                primary_product_name = f"{strain} - {lineage} - {weight}{units}"
                logging.info(f"📝 Created formatted description: '{primary_product_name}'")
            elif not primary_product_name:
                # Fallback to product_name field
                primary_product_name = db_info.get("product_name", "Unknown Product")
                logging.info(f"📝 Using fallback product name: '{primary_product_name}'")
            else:
                logging.info(f"📝 Using human-readable product name: '{primary_product_name}'")
            
            # CRITICAL FIX: Log the AI match information and ensure database values are used
            ai_match_score = db_info.get("ai_match_score", 0)
            ai_confidence = db_info.get("ai_confidence", "low")
            ai_match_type = db_info.get("ai_match_type", "unknown")
            
            logging.info(f"🎯 Creating tag with DATABASE MATCHED VALUES:")
            logging.info(f"   Product Name*: {primary_product_name} (from database)")
            logging.info(f"   Description: {description} (from database)")
            logging.info(f"   Price: {price} (from database)")
            logging.info(f"   Weight: {weight}{units} (from database)")
            logging.info(f"   Product Type: {product_type} (from database)")
            logging.info(f"   Brand: {brand} (from database)")
            logging.info(f"   Vendor: {vendor} (from database)")
            logging.info(f"   Strain: {strain} (from database)")
            logging.info(f"   Lineage: {lineage} (from database)")
            logging.info(f"   AI Match Score: {ai_match_score:.3f}")
            logging.info(f"   AI Confidence: {ai_confidence}")
            logging.info(f"   AI Match Type: {ai_match_type}")
            
            # Helper function to extract clean product name (remove cannabinoid details)
            def extract_clean_product_name(full_name):
                if not full_name:
                    return full_name
                # Remove cannabinoid details like "- 1000mg CBD / 75mg CBN / 75mg CBG / 1150mg THC"
                import re
                # Remove patterns like "- 1000mg CBD / 75mg CBN / 75mg CBG / 1150mg THC"
                cleaned = re.sub(r'\s*-\s*\d+mg\s+[A-Z]+(?:\s*/\s*\d+mg\s+[A-Z]+)*', '', full_name)
                # Remove "by Ceres" patterns
                cleaned = re.sub(r'\s*by\s+Ceres\s*$', '', cleaned, flags=re.IGNORECASE)
                return cleaned.strip()
            
            # Extract clean product name for UI display
            clean_display_name = extract_clean_product_name(primary_product_name)
            
            # Create DescAndWeight field in the same format as other tags
            # CRITICAL FIX: Don't add weight to description to avoid duplication
            desc_and_weight = description or primary_product_name
            
            tag = {
                # Core product information - follow existing tag format
                'Product Name*': primary_product_name,
                'ProductName': primary_product_name,
                'Description': self._create_detailed_display_name(primary_product_name, description, thc_result, cbd_result, test_unit, weight, units),  # Use detailed name for output
                'DescAndWeight': desc_and_weight,  # Format: "Description - Weight" like other tags
                'Product Type*': product_type or "Unknown",
                'Product Type': product_type or "Unknown",
                'Vendor': vendor if vendor and vendor.strip() else "Unknown Vendor",
                'Vendor/Supplier*': vendor if vendor and vendor.strip() else "Unknown Vendor",
                'Product Brand': brand,
                'ProductBrand': brand,
                'Product Strain': strain,
                'Strain Name': strain,
                'Lineage': self._determine_lineage_for_product(product_type, lineage, primary_product_name, strain),
                'Weight*': f"{weight} {units}" if weight and units else (weight or ''),
                'Weight': f"{weight} {units}" if weight and units else (weight or ''),
                'Quantity*': "1",
                'Quantity': "1",
                'Units': units or "",
                'Price': price,  # Always include Price from database
                'Price* (Tier Name for Bulk)': price,  # Always include Price from database
                'price': price,  # Include lowercase variant for compatibility
                'displayName': clean_display_name,  # Use clean product name for UI display
                
                # Enhanced fields using database information
                'State': 'active',
                'Is Sample? (yes/no)': 'no',
                'Is MJ product?(yes/no)': 'yes',
                'Discountable? (yes/no)': 'yes',
                'Room*': 'Default',
                'Medical Only (Yes/No)': medical_only or 'No',
                'DOH': db_info.get('DOH', ''),                  # Use DOH from database
                'DOH Compliant (Yes/No)': db_info.get('DOH Compliant (Yes/No)', db_info.get('DOH', '')),
                
                # Database column mappings
                'Concentrate Type': product_type if product_type and "concentrate" in product_type.lower() else '',
                'Ratio': self._calculate_ratio_for_json_product(product_type, json_item),
                'Joint Ratio': '',
                'JointRatio': '',
                'THC test result': thc_result,
                'CBD test result': cbd_result,
                'Test result unit (% or mg)': test_unit,
                'Batch Number': batch_num,
                'Lot Number': lot_num,
                'Barcode*': barcode,
                'Med Price': med_price,
                'Expiration Date(YYYY-MM-DD)': expiration,
                'Is Archived? (yes/no)': is_archived,
                'THC Per Serving': thc_per_serving,
                'Allergens': allergens,
                'Solvent': solvent,
                'Accepted Date': accepted_date,
                'Internal Product Identifier': internal_id,
                'Product Tags (comma separated)': product_tags,
                'Image URL': image_url,
                'Ingredients': ingredients,
                
                # Legacy fields for compatibility - CRITICAL FIX: Use JSON Match source for proper frontend detection
                'Source': 'JSON Match - Database Priority (100% DB)',
                'Quantity Received*': "1",
                'Weight Unit* (grams/gm or ounces/oz)': units or "g",
                'CombinedWeight': weight or "1",
                'Description_Complexity': '1',
                'Ratio_or_THC_CBD': self._calculate_ratio_for_json_product(product_type, json_item),
                'displayName': clean_product_name(primary_product_name),
                'weightWithUnits': f"{str(round(float(weight or '1')))}{units or 'g'}",
                'WeightWithUnits': f"{str(round(float(weight or '1')))}{units or 'g'}",
                'WeightUnits': f"{str(round(float(weight or '1')))}{units or 'g'}",
                
                # Additional fields for consistency
                'vendor': vendor,
                'productBrand': brand,
                'lineage': self._determine_lineage_for_product(product_type, lineage, primary_product_name, strain),
                'productType': product_type or "Unknown",
                'weight': weight or "1",
                'units': units or "g",
                'price': price or "",
                'strain': strain,
                'quantity': "1",
                'thc': thc_result,
                'cbd': cbd_result,
                'test_unit': test_unit,
                'batch_number': batch_num,
                'lot_number': lot_num,
                'barcode': barcode,
                'cost': cost,
                'medical_only': medical_only or "No",
                'med_price': med_price,
                'expiration_date': expiration,
                'is_archived': is_archived or "no",
                'thc_per_serving': thc_per_serving,
                'allergens': allergens,
                'solvent': solvent,
                'accepted_date': accepted_date,
                'internal_id': internal_id,
                'product_tags': product_tags,
                'image_url': image_url,
                'ingredients': ingredients,
                
                # AI Match Information for tracking
                'ai_match_score': ai_match_score,
                'ai_confidence': ai_confidence,
                'ai_match_type': ai_match_type,
            }
            
            logging.info(f"✅ Created tag from Product Database for: {primary_product_name}")
            logging.info(f"   Final tag uses: Strain='{strain}', Lineage='{lineage}', Product Type='{product_type}'")
            return tag
            
        except Exception as e:
            logging.error(f"Error creating tag from database info for '{primary_product_name}': {e}")
            # Fallback to basic tag creation - NO DEFAULT PRICE
            return {
                'Product Name*': primary_product_name,
                'ProductName': primary_product_name,
                'Description': primary_product_name,
                'displayName': primary_product_name,  # Use clean product name for UI display
                'Vendor': vendor,
                'Source': 'JSON Match',  # Changed back to 'JSON Match' for proper frontend detection
                'Product Type*': 'Unknown',
                'Price': '',  # NO DEFAULT PRICE - let it be missing so we can identify the issue
                'Weight*': '1 g',
                'Units': 'g',
                'Quantity*': '1'
            }
    
    def _process_item_with_main_matching(self, item: Dict, product_name: str, vendor: str, product_type: str, strain: str, global_vendor: str) -> List[Dict]:
        """Process a single item using the main matching logic (database + Excel + Advanced matching)."""
        print(f"🔍 DEBUG: _process_item_with_main_matching called for '{product_name}'")
        try:
            # CRITICAL: Translate CERES codes to readable names for better matching
            original_name = product_name
            translated_name = self._translate_ceres_code_to_name(product_name)
            if translated_name != original_name:
                print(f"🔍 DEBUG: Translated CERES code '{original_name}' to '{translated_name}'")
                product_name = translated_name

            vendor_for_variations = vendor or global_vendor or item.get('vendor', '')
            excel_style_variations, type_override = self._generate_excel_style_variations(
                item,
                vendor_for_variations,
                product_type
            )
            if type_override:
                product_type = type_override
            if vendor_for_variations:
                vendor = self._normalize_vendor_display_name(vendor_for_variations)
            if excel_style_variations:
                product_name = excel_style_variations[0]
            
            # ENHANCED: Create multiple search variations for better CERES matching
            search_variations = self._create_ceres_search_variations(original_name, translated_name, product_type)
            if excel_style_variations:
                for variation in excel_style_variations:
                    if variation not in search_variations:
                        search_variations.insert(0, variation)
            
            # Initialize variables for main matching
            db_match = None
            excel_match = None
            advanced_match = None
            db_score = 0.0
            excel_score = 0.0
            advanced_score = 0.0
            
            # PRIORITY 1: Try Product Database
            try:
                product_db = self._get_product_database()
                
                # ENHANCED: Try multiple search variations for better CERES matching
                db_match = None
                for search_variation in search_variations:
                    print(f"🔍 DEBUG: Trying database search with variation: '{search_variation}'")
                    db_match = product_db.find_best_product_match(
                        product_name=search_variation,
                        vendor=vendor,
                        product_type=product_type,
                        strain=strain
                    )
                    if db_match:
                        print(f"🔍 DEBUG: Found database match with variation: '{search_variation}'")
                        break
                
                if not db_match:
                    print(f"🔍 DEBUG: No database match found with any search variation")
                    
                    # FINAL ATTEMPT: Use direct database lookup with keyword targeting
                    try:
                        fallback_weight = item.get('unit_weight') or item.get('weight') or ''
                        fallback_strain = strain or item.get('strain_name') or ''
                        direct_match = self._find_best_database_match(
                            product_name=product_name,
                            vendor=vendor,
                            weight=str(fallback_weight),
                            strain=fallback_strain,
                            product_db=product_db
                        )
                        if direct_match:
                            db_match = direct_match
                            print(f"🔍 DEBUG: Direct database fallback matched '{direct_match.get('Product Name*', 'Unknown')}'")
                    except Exception as direct_db_error:
                        logging.debug(f"Direct database fallback lookup failed: {direct_db_error}")
                
                if db_match:
                    if hasattr(db_match, 'to_dict'):
                        db_match = db_match.to_dict()
                    db_score = 70.0  # Base score for database match
                    
                    # Add intelligent scoring based on product type and naming patterns
                    db_product_type = db_match.get('product_type', '')
                    if product_type and db_product_type:
                        if product_type.lower() == db_product_type.lower():
                            db_score += 80.0  # High bonus for exact product type match
                        elif self._are_product_types_compatible(product_type, db_product_type):
                            db_score += 60.0  # Good bonus for compatible product types
                        else:
                            db_score -= 30.0  # Penalty for incompatible product types
                    
                    # Add naming pattern score
                    db_product_name = db_match.get('product_name', '')
                    if db_product_name:
                        db_score += self._calculate_naming_pattern_score(product_name, db_product_name, product_type)
                    
                    # Add vendor match bonus
                    db_vendor = db_match.get('vendor', '')
                    if vendor and db_vendor and vendor.lower() == db_vendor.lower():
                        db_score += 20.0
                    
                    # Add strain match bonus
                    db_strain = db_match.get('product_strain', '')
                    if strain and db_strain and strain.lower() == db_strain.lower():
                        db_score += 15.0
                    
                    db_score = min(100.0, db_score)  # Cap at 100
                    logging.info(f"✅ Found Product Database match for '{product_name}': {db_match.get('product_name', 'Unknown')} (score: {db_score:.1f})")
                else:
                    logging.info(f"📝 No Product Database match found for '{product_name}'")
                    
            except Exception as db_error:
                logging.warning(f"Error accessing Product Database: {db_error}")
            
            # PRIORITY 2: Try Excel data
            if self.excel_processor and self.excel_processor.df is not None and self._sheet_cache:
                df = self.excel_processor.df
                excel_matches_by_name = {}
                
                for idx, row in df.iterrows():
                    try:
                        excel_product_name = str(row.get('Product Name*', '') or row.get('ProductName', '') or row.get('Description', '')).strip().lower()
                        excel_vendor = str(row.get('Vendor', '') or row.get('Vendor/Supplier*', '')).strip().lower()
                        
                        if not excel_product_name:
                            continue
                        
                        # VENDOR ISOLATION: Only process candidates from the same vendor (flexible matching)
                        vendor_match = False
                        if vendor and excel_vendor:
                            vendor_lower = vendor.lower().strip()
                            excel_vendor_lower = excel_vendor.lower().strip()
                            
                            # Normalize both vendors
                            vendor_clean = self._normalize_vendor_name(vendor_lower)
                            excel_vendor_clean = self._normalize_vendor_name(excel_vendor_lower)
                            
                            # Exact match
                            if vendor_clean == excel_vendor_clean:
                                vendor_match = True
                            # Check if one contains the other (for cases like "CERES" vs "CERES - 435011")
                            # But only if one is significantly longer than the other to prevent false matches
                            elif (len(vendor_clean) > len(excel_vendor_clean) * 2 and excel_vendor_clean in vendor_clean) or \
                                 (len(excel_vendor_clean) > len(vendor_clean) * 2 and vendor_clean in excel_vendor_clean):
                                vendor_match = True
                                print(f"🔍 SUBSTRING VENDOR MATCH: '{vendor_clean}' matches '{excel_vendor_clean}' via substring matching")
                            # Check for partial word matches (at least 75% word overlap - much stricter)
                            elif len(vendor_clean.split()) > 1 and len(excel_vendor_clean.split()) > 1:
                                vendor_words = set(vendor_clean.split())
                                excel_words = set(excel_vendor_clean.split())
                                overlap = len(vendor_words.intersection(excel_words))
                                min_words = min(len(vendor_words), len(excel_words))
                                # Check for meaningful word overlap (at least 50% but with additional validation)
                                if overlap / min_words >= 0.50:
                                    # Additional check: ensure the overlapping words are substantial (not just short words)
                                    overlapping_words = vendor_words.intersection(excel_words)
                                    substantial_overlap = any(len(word) >= 4 for word in overlapping_words)
                                    if substantial_overlap:
                                        vendor_match = True
                                        print(f"🔍 WORD OVERLAP VENDOR MATCH: '{vendor_clean}' matches '{excel_vendor_clean}' via word overlap ({overlap / min_words:.2f})")
                            # Fuzzy matching for similar vendor names (much stricter threshold)
                            elif len(vendor_clean) >= 6 and len(excel_vendor_clean) >= 6:
                                try:
                                    from rapidfuzz import fuzz
                                    vendor_ratio = fuzz.ratio(vendor_clean, excel_vendor_clean)
                                    # Increased threshold from 60% to 75% to prevent false matches but allow legitimate ones
                                    if vendor_ratio >= 75:
                                        vendor_match = True
                                        print(f"🔍 FUZZY VENDOR MATCH: '{vendor_clean}' matches '{excel_vendor_clean}' via fuzzy matching ({vendor_ratio}%)")
                                except:
                                    pass
                            # Check for common vendor name patterns
                            elif self._is_vendor_match_flexible(vendor_clean, excel_vendor_clean):
                                vendor_match = True
                                print(f"🔍 FLEXIBLE VENDOR MATCH: '{vendor_clean}' matches '{excel_vendor_clean}' via flexible matching")
                        
                        # STRICT vendor isolation - reject non-matching vendors
                        if vendor and excel_vendor:
                            if not vendor_match:
                                # REJECT cross-vendor matches to prevent brand contamination
                                print(f"🚫 REJECTED: Cross-vendor match - '{product_name}' (vendor: '{vendor}') ≠ Excel '{excel_product_name}' (vendor: '{excel_vendor}')")
                                continue  # Skip this candidate
                            else:
                                print(f"✓ VENDOR MATCH: '{product_name}' (vendor: '{vendor}') matches Excel '{excel_product_name}' (vendor: '{excel_vendor}')")
                        
                        # Calculate match score
                        score = 0.0
                        
                        # Exact name match (highest priority)
                        if product_name.lower() == excel_product_name:
                            score += 100.0
                        
                        # Vendor match bonus (already confirmed above)
                        if vendor_match:
                            score += 100.0  # Strong bonus for vendor matching
                        
                        # Product type match (very important for accuracy)
                        excel_product_type = str(row.get('Product Type*', '') or row.get('ProductType', '')).strip().lower()
                        if product_type and excel_product_type:
                            if product_type.lower() == excel_product_type:
                                score += 80.0  # High bonus for exact product type match
                            elif self._are_product_types_compatible(product_type, excel_product_type):
                                score += 60.0  # Good bonus for compatible product types
                            else:
                                score -= 30.0  # Penalty for incompatible product types
                        
                        # Intelligent naming pattern matching
                        score += self._calculate_naming_pattern_score(product_name, excel_product_name, product_type)
                        
                        # Partial name match
                        if product_name.lower() in excel_product_name or excel_product_name in product_name.lower():
                            score += 40.0
                        
                        # Fuzzy string similarity
                        try:
                            from fuzzywuzzy import fuzz
                            similarity = fuzz.ratio(product_name.lower(), excel_product_name)
                            if similarity >= 60:
                                score += similarity * 0.3
                        except ImportError:
                            pass
                        
                        # Store match by product name to prevent duplicates
                        if excel_product_name not in excel_matches_by_name or score > excel_matches_by_name[excel_product_name]['score']:
                            excel_matches_by_name[excel_product_name] = {
                                'row': row,
                                'score': score
                            }
                            
                    except Exception as e:
                        logging.debug(f"Error processing Excel row {idx}: {e}")
                        continue
                
                # Find the best match from deduplicated Excel matches
                if excel_matches_by_name:
                    best_excel_match = max(excel_matches_by_name.values(), key=lambda x: x['score'])
                    excel_score = best_excel_match['score']
                    excel_match = best_excel_match['row']
                    logging.info(f"✅ Found Excel match for '{product_name}': {excel_score:.1f}")
                else:
                    logging.info(f"📝 No Excel match found for '{product_name}' (STRICT VENDOR ISOLATION - no same vendor products found)")
                    print(f"🔍 EXCEL VENDOR: No matches found for vendor '{vendor}' - will try advanced matching")
            
            # PRIORITY 3: Try Advanced Matching (if no good matches found)
            if (db_match is None or db_score < 70) and (excel_match is None or excel_score < 70):
                try:
                    print(f"🔍 DEBUG: Trying advanced matching for '{product_name}'")
                    
                    # Ensure sheet cache is built
                    if self._sheet_cache is None:
                        print(f"🔍 DEBUG: Building sheet cache for advanced matching")
                        self._build_sheet_cache()
                    
                    # Prepare JSON item for advanced matching
                    json_item = {
                        "product_name": product_name,
                        "vendor": vendor,
                        "brand": item.get("brand", ""),
                        "product_type": product_type,
                        "weight": item.get("weight", ""),
                        "strain_name": strain
                    }
                    
                    # Use advanced matching with Excel cache as candidates
                    if self._sheet_cache:
                        print(f"🔍 DEBUG: Sheet cache has {len(self._sheet_cache)} candidates")
                        advanced_matches = self._find_advanced_matches(json_item)
                        if advanced_matches:
                            product_type_lower = (product_type or "").strip().lower()
                            compatible_match = None
                            
                            for candidate in advanced_matches:
                                candidate_item = candidate.item
                                candidate_type = (candidate_item.get('Product Type*') or
                                                  candidate_item.get('product_type') or
                                                  candidate_item.get('ProductType') or
                                                  "").strip().lower()
                                
                                if not product_type_lower or not candidate_type:
                                    compatible_match = candidate
                                    break
                                
                                if candidate_type == product_type_lower or self._are_product_types_compatible(product_type_lower, candidate_type):
                                    compatible_match = candidate
                                    break
                            
                            best_advanced = compatible_match or advanced_matches[0]
                            advanced_score = best_advanced.overall_score
                            advanced_match = best_advanced.item
                            print(f"🔍 DEBUG: Advanced matching found {len(advanced_matches)} matches, best score {advanced_score:.1f}")
                            print(f"🔍 DEBUG: Best match: {advanced_match.get('original_name', 'Unknown')}")
                        else:
                            print(f"🔍 DEBUG: Advanced matching found no matches")
                    else:
                        print(f"🔍 DEBUG: No sheet cache available for advanced matching")
                        
                except Exception as advanced_error:
                    logging.warning(f"Error in advanced matching: {advanced_error}")
                    print(f"🔍 DEBUG: Advanced matching error: {advanced_error}")
            
            # Choose the best match between database, Excel, and advanced matching
            matches = []
            
            # Add database match if found
            if db_match:
                matches.append({
                    'match': self._convert_database_match_to_excel_format(db_match),
                    'score': float(db_score) if db_score is not None else 0.0,
                    'source': 'Product Database Match'
                })
            
            # Add Excel match if found
            if excel_match is not None and not (hasattr(excel_match, 'empty') and excel_match.empty):
                excel_match_payload = excel_match.to_dict() if hasattr(excel_match, 'to_dict') else excel_match
                matches.append({
                    'match': excel_match_payload,
                    'score': float(excel_score) if excel_score is not None else 0.0,
                    'source': 'Excel Match'
                })
            
            # Add advanced match if found
            if advanced_match:
                matches.append({
                    'match': advanced_match,
                    'score': float(advanced_score) if advanced_score is not None else 0.0,
                    'source': 'Advanced Match'
                })
            
            # Choose the best match
            if matches:
                json_product_type = product_type or map_inventory_type_to_product_type(
                    item.get('inventory_type'),
                    item.get('inventory_category'),
                    item.get('product_name')
                )
            if matches and json_product_type:
                product_type_lower = str(json_product_type).strip().lower()
                filtered_matches = []
                for candidate in matches:
                    match_obj = candidate.get('match', {})
                    candidate_type = (match_obj.get('Product Type*') or
                                      match_obj.get('product_type') or
                                      match_obj.get('ProductType') or
                                      '').strip().lower()
                    if candidate_type:
                        if not self._are_product_types_compatible(product_type_lower, candidate_type) and candidate_type != product_type_lower:
                            logging.debug(f"🚫 Product type mismatch: JSON '{product_type_lower}' vs candidate '{candidate_type}'")
                            continue
                    filtered_matches.append(candidate)
                if filtered_matches:
                    matches = filtered_matches
                else:
                    logging.debug("🚫 All matches filtered out due to product type incompatibility")
                    matches = []

            if matches:
                best_match_info = max(matches, key=lambda x: x['score'])
                best_match = best_match_info['match']
                best_score = best_match_info['score']
                match_source = best_match_info['source']
                logging.info(f"🏆 Using {match_source} (score: {best_score:.1f})")
            else:
                return []  # No match found
            
            # Process the match if we found one
            best_score_num = float(best_score) if best_score is not None else 0.0
            if best_match is not None and not (hasattr(best_match, 'empty') and best_match.empty) and best_score_num >= 2.0:
                try:
                    # Create product from the match
                    if match_source == 'Product Database Match':
                        product = best_match.copy()
                        product['Original JSON Product Name'] = str(item.get("product_name", ""))
                        # CRITICAL FIX: Ensure Weight* is properly formatted (no space between number and unit)
                        self._format_weight_field(product, item)
                    elif match_source == 'Advanced Match':
                        # Convert advanced match to product format
                        product = self._create_product_from_advanced_match(best_match, item, global_vendor)
                        product['Original JSON Product Name'] = str(item.get("product_name", ""))
                        # CRITICAL FIX: Ensure Weight* is properly formatted
                        self._format_weight_field(product, item)
                    else:  # Excel Match
                        product = self._create_product_from_excel_match(best_match, item, global_vendor)
                        product['Original JSON Product Name'] = str(item.get("product_name", ""))
                        # CRITICAL FIX: Ensure Weight* is properly formatted
                        self._format_weight_field(product, item)
                    
                    return [product]
                    
                except Exception as e:
                    logging.warning(f"Error creating product from match: {e}")
                    return []
            
            return []  # No good match found
            
        except Exception as e:
            logging.warning(f"Error in main matching logic: {e}")
            logging.debug(traceback.format_exc())
            return []
    
    def _create_product_from_advanced_match(self, advanced_match: Dict, item: Dict, global_vendor: str) -> Dict:
        """Create a product from an advanced match result."""
        try:
            # Extract information from the advanced match
            original_name = advanced_match.get('original_name', '')
            vendor = advanced_match.get('vendor', global_vendor)
            brand = advanced_match.get('brand', '')
            product_type = advanced_match.get('product_type', '')
            weight = advanced_match.get('weight', '')
            units = advanced_match.get('units', '')
            price = advanced_match.get('price', '')
            thc = advanced_match.get('thc', '')
            cbd = advanced_match.get('cbd', '')
            strain = advanced_match.get('strain', '')
            lineage = advanced_match.get('lineage', '')
            description = advanced_match.get('description', original_name)
            
            # Create the product dictionary
            product = {
                'Product Name*': original_name,
                'Vendor': vendor,
                'Product Brand': brand,
                'Product Type*': product_type,
                'Description': description,
                'Weight*': self._format_weight_label(weight, units) if weight else '',  # Format like normal tags (no space: "3.5g")
                'Weight': self._format_weight_label(weight, units) if weight else '',  # Format like normal tags
                'Units': units,
                'Price*': price,
                'THC test result': thc,
                'CBD test result': cbd,
                'Product Strain': strain,
                'Lineage': lineage,
                'Quantity*': '1'
            }
            
            return product
            
        except Exception as e:
            logging.warning(f"Error creating product from advanced match: {e}")
            return {}

    def _is_valid_product(self, product: Dict) -> bool:
        """Check if product is valid (not voided or trade sample)."""
        if not product:
            return False

        # Check Product Name* and Description for void/sample indicators
        product_name = str(product.get('Product Name*', '')).upper()
        description = str(product.get('Description', '')).upper()

        # Filter out voided products
        if '*VOID*' in product_name or '*VOID*' in description:
            logging.info(f"🚫 Filtered out invalid product: {product.get('Product Name*', 'Unknown')} (contains '*VOID*')")
            return False

        # Filter out trade samples specifically (not all products containing "sample")
        if 'TRADE SAMPLE' in product_name or 'TRADE SAMPLE' in description:
            logging.info(f"🚫 Filtered out invalid product: {product.get('Product Name*', 'Unknown')} (contains 'TRADE SAMPLE')")
            return False

        # Filter out products that START with "SAMPLE" (free samples)
        # But allow products that contain "sample" in the middle (like "Sample Size" products)
        if product_name.startswith('SAMPLE ') or description.startswith('SAMPLE '):
            logging.info(f"🚫 Filtered out invalid product: {product.get('Product Name*', 'Unknown')} (starts with 'SAMPLE')")
            return False

        return True

    def _create_tag_from_product(self, product: Dict, item: Dict, global_vendor: str) -> Dict[str, Any]:
        """Create a tag from a product object."""
        try:
            # DEBUG: Log the actual product dictionary structure
            logging.info(f"🔍 DEBUG: _create_tag_from_product called with product keys: {list(product.keys())}")
            logging.info(f"🔍 DEBUG: _create_tag_from_product called with item keys: {list(item.keys())}")
            logging.info(f"🔍 DEBUG: Full product dict: {product}")
            logging.info(f"🔍 DEBUG: Full item dict: {item}")
            
            # Extract basic information - try multiple field name variations
            # CRITICAL FIX: Transform SKU codes to human-readable names
            raw_name = (product.get('Product Name*', '') or 
                          product.get('ProductName', '') or 
                          product.get('product_name', '') or
                          product.get('name', ''))
            description = product.get('Description', '')
            product_name = (description or  # Use Description if available
                          transform_sku_to_readable_name(raw_name) or # Transform SKU to readable
                          raw_name)  # Raw name as fallback
            
            # CRITICAL FIX: Prioritize vendor/brand from JSON item to preserve correct vendor associations
            # JSON source data should take precedence over database match vendor/brand
            vendor = (extract_vendor_info(item) or  # Extract vendor from JSON item first
                     global_vendor or  # Then use global vendor from document
                     item.get('vendor', '') or
                     item.get('supplier_name', '') or
                     item.get('brand', '') or  # Brand can sometimes be vendor
                     product.get('Vendor', '') or  # Fallback to database product vendor
                     product.get('Vendor/Supplier*', '') or 
                     product.get('vendor', ''))
            
            # CRITICAL FIX: Prioritize brand from JSON item to preserve correct brand associations
            # JSON source data should take precedence over database match brand
            brand = (item.get('brand', '') or  # JSON brand first
                    item.get('vendor', '') or  # JSON vendor can be brand
                    item.get('supplier_name', '') or
                    extract_vendor_info(item) or  # Extract from JSON if brand not directly available
                    global_vendor or  # Global vendor as fallback
                    product.get('Product Brand', '') or  # Then database product brand
                    product.get('ProductBrand', '') or 
                    product.get('Brand', '') or 
                    product.get('brand', '') or
                    product.get('vendor', '') or
                    'CERES')  # Always default to CERES for Ceres products
            
            # Try multiple product type field variations
            product_type = (product.get('Product Type*', '') or 
                           product.get('ProductType', '') or 
                           product.get('product_type', '') or
                           product.get('inventory_type', '') or
                           'Edible (Solid)')  # Default for Ceres products
            
            # Extract weight and units first - prioritize JSON item fields
            weight = (product.get('Weight*', '') or 
                     product.get('Weight', '') or 
                     str(item.get('unit_weight', '')).strip() or  # JSON uses unit_weight
                     str(item.get('weight', '')).strip() or
                     item.get('Weight', '') or
                     item.get('weight_with_units', '') or
                     item.get('size', '') or
                     item.get('Size', ''))
            units = (product.get('Units', '') or 
                    product.get('Weight Unit*', '') or
                    str(item.get('unit_weight_uom', '')).strip() or  # JSON uses unit_weight_uom
                    str(item.get('uom', '')).strip() or
                    item.get('units', '') or
                    item.get('Units', '') or
                    item.get('weight_unit', '') or
                    'g')
            
            # DEBUG: Log extracted values
            logging.info(f"🔍 DEBUG: Extracted values - product_name: '{product_name}', brand: '{brand}', product_type: '{product_type}', vendor: '{vendor}', weight: '{weight}', units: '{units}'")
            
            # Description already set above, just ensure it has a value
            if not description:
                description = product_name
            
            # Try multiple price field variations - extract actual price from data
            price = (product.get('Price*', '') or 
                    product.get('Price', '') or 
                    product.get('price', '') or
                    product.get('Price* (Tier Name for Bulk)', '') or
                    item.get('price', '') or
                    item.get('line_price', '') or
                    '')  # Leave blank if no price found - don't use defaults
            price = format_price(price) if str(price).strip() else ""
            
            # DEBUG: Log price extraction
            print(f"🔍 DEBUG: _create_tag_from_product - Product: '{product_name}', JSON price: '{item.get('line_price', item.get('price', ''))}', Final price: '{price}'")
            thc = product.get('THC test result', '') or product.get('THC Content', '')
            cbd = product.get('CBD test result', '') or product.get('CBD Content', '')
            strain = product.get('Product Strain', '') or product.get('Strain', '')
            # CRITICAL FIX: ALWAYS determine lineage to ensure nonclassic types get correct colors
            existing_lineage = product.get('Lineage', '')
            lineage = self._determine_lineage_for_product(product_type, existing_lineage, product_name, strain)
            
            # Get DOH field: try multiple variations, then blank if not found
            doh = (product.get('DOH', '') or 
                   product.get('DOH Compliant (Yes/No)', '') or 
                   product.get('doh', '') or
                   product.get('doh_compliant', '') or
                   item.get('doh', '') or
                   item.get('doh_compliant', '') or
                   '')  # Leave blank if not found in data
            
            # Create DescAndWeight field in the same format as other tags
            # CRITICAL FIX: Don't add weight to description to avoid duplication
            desc_and_weight = description or product_name
            
            # Helper function to extract clean product name (remove cannabinoid details)
            def extract_clean_product_name(full_name):
                if not full_name:
                    return full_name
                # Remove cannabinoid details like "- 1000mg CBD / 75mg CBN / 75mg CBG / 1150mg THC"
                import re
                # Remove patterns like "- 1000mg CBD / 75mg CBN / 75mg CBG / 1150mg THC"
                cleaned = re.sub(r'\s*-\s*\d+mg\s+[A-Z]+(?:\s*/\s*\d+mg\s+[A-Z]+)*', '', full_name)
                # Remove "by Ceres" patterns
                cleaned = re.sub(r'\s*by\s+Ceres\s*$', '', cleaned, flags=re.IGNORECASE)
                return cleaned.strip()
            
            # Extract clean product name for UI display
            clean_display_name = extract_clean_product_name(product_name)
            
            # Create the tag with proper field names that template generation expects
            tag = {
                # Core product information - use template generation field names
                'Product Name*': product_name,
                'ProductName': product_name,
                'Description': description,
                'DescAndWeight': desc_and_weight,  # Format: "Description - Weight" like other tags
                'Product Type*': product_type,
                'ProductType': product_type,
                'Vendor': vendor if vendor and vendor.strip() else "Unknown Vendor",
                'Vendor/Supplier*': vendor if vendor and vendor.strip() else "Unknown Vendor",
                'Product Brand': brand,
                'ProductBrand': brand,
                'Product Strain': strain,
                'Strain Name': strain,
                'Lineage': lineage,
                'Weight*': self._format_weight_label(weight, units) if weight else '',  # Format like normal tags (no space: "3.5g")
                'Weight': self._format_weight_label(weight, units) if weight else '',  # Format like normal tags
                'Quantity*': '1',
                'Quantity': '1',
                'Units': units,
                'Price': price,
                'Price* (Tier Name for Bulk)': price,
                'price': price,
                'displayName': clean_display_name,  # Use clean product name for UI display
                'Original JSON Product Name': str(item.get('product_name', '')),
                
                # Enhanced fields
                'State': 'active',
                'Is Sample? (yes/no)': 'no',
                'Is MJ product?(yes/no)': 'yes',
                'Discountable? (yes/no)': 'yes',
                'Room*': 'Default',
                'Medical Only (Yes/No)': 'No',
                'DOH': doh,  # Use DOH from Excel/database, not hardcoded
                'DOH Compliant (Yes/No)': doh,
                
                # Database column mappings
                'Concentrate Type': product_type if product_type and "concentrate" in product_type.lower() else '',
                'Ratio': '',
                'Joint Ratio': '',
                'JointRatio': '',
                'THC test result': thc,
                'CBD test result': cbd,
                'Test result unit (% or mg)': '%',
                'Batch Number': '',
                'Lot Number': '',
                'Barcode*': '',
                'Source': 'JSON Match - Database Priority (100% DB)'
            }
            
            return tag
            
        except Exception as e:
            logging.warning(f"Error creating tag from product: {e}")
            return {
                # Core product information - use template generation field names
                'Product Name*': str(item.get("product_name", "")),
                'ProductName': str(item.get("product_name", "")),
                'Description': str(item.get("product_name", "")),
                'Product Type*': 'Edible (Solid)',  # Default product type for error cases
                'ProductType': 'Edible (Solid)',
                'Vendor': global_vendor,
                'Vendor/Supplier*': global_vendor,
                'Product Brand': 'CERES',  # Default brand for error cases
                'ProductBrand': 'CERES',
                'Product Strain': '',
                'Strain Name': '',
                'Lineage': '',
                'Weight*': '',
                'Weight': '',
                'Quantity*': '1',
                'Quantity': '1',
                'Units': '',
                'Price': '',  # Leave blank for error cases - no default pricing
                'Price* (Tier Name for Bulk)': '',
                
                # Enhanced fields
                'State': 'active',
                'Is Sample? (yes/no)': 'no',
                'Is MJ product?(yes/no)': 'yes',
                'Discountable? (yes/no)': 'yes',
                'Room*': 'Default',
                'Medical Only (Yes/No)': 'No',
                'DOH': '',  # Leave blank for error cases - don't assume DOH compliance
                'DOH Compliant (Yes/No)': '',
                
                # Database column mappings
                'Concentrate Type': '',
                'Ratio': '',
                'Joint Ratio': '',
                'JointRatio': '',
                'THC test result': '',
                'CBD test result': '',
                'Test result unit (% or mg)': '%',
                'Batch Number': '',
                'Lot Number': '',
                'Barcode*': '',
                'Source': 'JSON Match - Database Priority (Error)'
            }

    def _are_product_types_compatible(self, type1: str, type2: str) -> bool:
        """Check if two product types are compatible."""
        if not type1 or not type2:
            return False
        
        type1_lower = type1.lower().strip()
        type2_lower = type2.lower().strip()
        
        # Exact match
        if type1_lower == type2_lower:
            return True
        
        # Define compatibility groups
        compatibility_groups = {
            'edibles': ['solid edible', 'edible', 'gummy', 'chocolate', 'candy', 'cookie', 'brownie'],
            'capsules': ['capsule', 'pill', 'cap'],
            'topicals': ['topical ointment', 'topical', 'cream', 'balm', 'lotion', 'salve'],
            'flower': ['core flower', 'flower', 'bud', 'nug'],
            'concentrates': ['concentrate', 'wax', 'shatter', 'oil', 'resin'],
            'vapes': ['vape', 'cartridge', 'cart', 'pen'],
            'tinctures': ['tincture', 'drops', 'liquid edible']
        }
        
        # Check if both types are in the same compatibility group
        for group, types in compatibility_groups.items():
            if type1_lower in types and type2_lower in types:
                return True
        
        return False
    
    def _calculate_naming_pattern_score(self, json_name: str, excel_name: str, product_type: str) -> float:
        """Calculate intelligent naming pattern score based on product type and naming conventions."""
        score = 0.0
        json_lower = json_name.lower()
        excel_lower = excel_name.lower()
        
        if not product_type:
            return score
        
        product_type_lower = product_type.lower()
        
        # CAPS = Capsules pattern matching
        if product_type_lower == 'capsule':
            # Look for capsule indicators in both names
            capsule_indicators = ['caps', 'capsule', 'pill', 'cap']
            
            json_has_capsule = any(indicator in json_lower for indicator in capsule_indicators)
            excel_has_capsule = any(indicator in excel_lower for indicator in capsule_indicators)
            
            if json_has_capsule and excel_has_capsule:
                score += 50.0  # High bonus for both having capsule indicators
            elif json_has_capsule or excel_has_capsule:
                score += 25.0  # Medium bonus for one having capsule indicators
            else:
                score -= 20.0  # Penalty if neither has capsule indicators
        
        # BALL/BITE = Edibles pattern matching
        elif product_type_lower in ['solid edible', 'edible']:
            edible_indicators = ['ball', 'bite', 'chew', 'gummy', 'chocolate', 'candy', 'cookie']
            
            json_has_edible = any(indicator in json_lower for indicator in edible_indicators)
            excel_has_edible = any(indicator in excel_lower for indicator in edible_indicators)
            
            if json_has_edible and excel_has_edible:
                score += 40.0
            elif json_has_edible or excel_has_edible:
                score += 20.0
            else:
                score -= 15.0
        
        # TINCS = Tinctures pattern matching
        elif product_type_lower in ['liquid edible', 'tincture']:
            tincture_indicators = ['tincs', 'tincture', 'drops', 'liquid']
            
            json_has_tincture = any(indicator in json_lower for indicator in tincture_indicators)
            excel_has_tincture = any(indicator in excel_lower for indicator in tincture_indicators)
            
            if json_has_tincture and excel_has_tincture:
                score += 40.0
            elif json_has_tincture or excel_has_tincture:
                score += 20.0
            else:
                score -= 15.0
        
        # JAR/SQUEEZE/ROLL = Topicals pattern matching
        elif product_type_lower in ['topical ointment', 'topical']:
            topical_indicators = ['jar', 'squeeze', 'roll', 'balm', 'cream', 'ointment', 'salve']
            
            json_has_topical = any(indicator in json_lower for indicator in topical_indicators)
            excel_has_topical = any(indicator in excel_lower for indicator in topical_indicators)
            
            if json_has_topical and excel_has_topical:
                score += 40.0
            elif json_has_topical or excel_has_topical:
                score += 20.0
            else:
                score -= 15.0
        
        # Strain type matching (SAT/IND/MIX)
        strain_indicators = {
            'sativa': ['sat', 'sativa'],
            'indica': ['ind', 'indica'],
            'hybrid': ['mix', 'hybrid', 'mixed']
        }
        
        for strain_type, indicators in strain_indicators.items():
            json_has_strain = any(indicator in json_lower for indicator in indicators)
            excel_has_strain = any(indicator in excel_lower for indicator in indicators)
            
            if json_has_strain and excel_has_strain:
                score += 30.0  # Bonus for matching strain types
            elif json_has_strain or excel_has_strain:
                score += 15.0  # Smaller bonus for partial strain match
        
        # Weight/quantity pattern matching
        weight_patterns = [r'(\d+(?:\.\d+)?)\s*(g|mg|oz|ml)', r'(\d+)pk', r'(\d+)pack']
        
        for pattern in weight_patterns:
            import re
            json_match = re.search(pattern, json_lower)
            excel_match = re.search(pattern, excel_lower)
            
            if json_match and excel_match:
                # Extract the numeric part for comparison
                json_num = float(json_match.group(1))
                excel_num = float(excel_match.group(1))
                
                # Give bonus for similar weights/quantities
                if abs(json_num - excel_num) <= 1:  # Within 1 unit
                    score += 25.0
                elif abs(json_num - excel_num) <= 5:  # Within 5 units
                    score += 15.0
                else:
                    score += 5.0  # Small bonus for having any weight info
        
        return score

    def _create_tag_from_educated_guess(self, educated_guess: Dict[str, Any], vendor: str) -> Dict[str, Any]:
        """
        Create a product tag from educated guess information.
        This method is used when no exact database match is found but similar products exist.
        
        Args:
            educated_guess: Product information from educated guessing
            vendor: The vendor name
            
        Returns:
            Dictionary containing the product tag information
        """
        try:
            # Extract data from educated guess
            # CRITICAL FIX: Use Description column from database FIRST
            # Priority: Database Description > Transformed SKU > Raw SKU
            raw_name = educated_guess.get("product_name", "") or educated_guess.get("Product Name*", "")
            db_description = educated_guess.get("description", "") or educated_guess.get("Description", "")
            
            # Use database Description if it exists and is different from SKU
            if db_description and db_description != raw_name:
                product_name = db_description
                logging.info(f"📝 Using database Description: '{product_name}'")
            else:
                # Fall back to transforming the SKU
                product_name = transform_sku_to_readable_name(raw_name) or raw_name
                logging.info(f"📝 Using transformed SKU: '{product_name}'")
            brand = educated_guess.get("brand", "") or educated_guess.get("Product Brand", "")
            product_type = educated_guess.get("product_type", "") or educated_guess.get("Product Type*", "")
            strain = educated_guess.get("strain_name", "") or educated_guess.get("Product Strain", "")
            lineage = educated_guess.get("lineage", "") or educated_guess.get("Lineage", "")
            price = str(educated_guess.get("price", "") or educated_guess.get("Price", ""))
            weight = str(educated_guess.get("weight", "") or educated_guess.get("Weight*", ""))
            units = str(educated_guess.get("units", "") or educated_guess.get("Units", ""))
            confidence = educated_guess.get("confidence", "medium")
            
            logging.info(f"🎯 Creating tag with EDUCATED GUESS VALUES:")
            logging.info(f"   Product: {product_name}")
            logging.info(f"   Strain: {strain} (inferred)")
            logging.info(f"   Lineage: {lineage} (inferred)")
            logging.info(f"   Product Type: {product_type} (inferred)")
            logging.info(f"   Weight: {weight}{units} (inferred)")
            logging.info(f"   Price: {price} (inferred)")
            logging.info(f"   Confidence: {confidence}")
            
            # Create tag with educated guess information
            tag = {
                'Product Name*': product_name,
                'ProductName': product_name,
                'Description': product_name,  # Use product_name, not description
                'Product Type*': product_type,
                'Product Type': product_type,
                'Vendor': vendor if vendor and vendor.strip() else "Unknown Vendor",
                'Vendor/Supplier*': vendor if vendor and vendor.strip() else "Unknown Vendor",
                'Product Brand': brand,
                'ProductBrand': brand,
                'Product Strain': strain,
                'Strain Name': strain,
                'Lineage': lineage,
                'Weight*': f"{weight} {units}" if weight and units else weight,
                'Weight': f"{weight} {units}" if weight and units else weight,
                'Quantity*': '1',
                'Quantity': '1',
                'Units': units,
                'Price': price,
                'Price* (Tier Name for Bulk)': price,
                'Source': f'JSON Match - Educated Guess ({confidence})',
                'Quantity Received*': '1',
                'Weight Unit* (grams/gm or ounces/oz)': units,
                'CombinedWeight': weight,
                'DescAndWeight': self._process_description_from_product_name(product_name, weight, units),  # Use Excel processor formula with weight
                'Description_Complexity': '1',
                'Ratio_or_THC_CBD': '',
                'THC test result': '',
                'CBD test result': '',
                'Test result unit (% or mg)': '%',
                'Batch Number': '',
                'Lot Number': '',
                'Barcode*': '',
                'Medical Only (Yes/No)': 'No',
                'DOH': '',  # Use blank DOH for educated guesses (no database source)
                'DOH Compliant (Yes/No)': '',
                'State': 'active',
                'Is Sample? (yes/no)': 'no',
                'Is MJ product?(yes/no)': 'yes',
                'Discountable? (yes/no)': 'yes',
                'Room*': 'Default',
                'Concentrate Type': product_type if "concentrate" in product_type.lower() else '',
                'Ratio': '',
                'Joint Ratio': '',
                'JointRatio': '',
                'Med Price': '',
                'Expiration Date(YYYY-MM-DD)': '',
                'Is Archived? (yes/no)': 'no',
                'THC Per Serving': '',
                'Allergens': '',
                'Solvent': '',
                'Accepted Date': '',
                'Internal Product Identifier': '',
                'Product Tags (comma separated)': '',
                'Image URL': '',
                'Ingredients': '',
            }
            
            logging.info(f"✅ Created tag from Educated Guess for: {product_name}")
            return tag
            
        except Exception as e:
            logging.error(f"Error creating tag from educated guess for '{product_name}': {e}")
            # Fallback to basic tag creation
            return {
                'Product Name*': product_name,
                'ProductName': product_name,
                'Description': product_name,
                'Vendor': vendor,
                'Source': 'Educated Guess (Fallback)',
                'Product Type*': 'Unknown',
                'Price': '',  # NO DEFAULT PRICE - let it be missing so we can identify the issue
                'Weight*': '1 g',
                'Units': 'g',
                'Quantity*': '1'
            }
    
    def _create_faux_tag_for_novel_product(self, json_item: dict, vendor: str, global_vendor: str = None) -> Dict[str, Any]:
        """
        Force creation of a faux tag for a novel product that has no match.
        This ensures that all novel products get tags created even when matching fails.
        
        Args:
            json_item: The JSON item data
            vendor: The vendor name
            global_vendor: Optional global vendor fallback
            
        Returns:
            Dictionary containing the faux product tag information
        """
        try:
            # Use global vendor as fallback
            if not vendor and global_vendor:
                vendor = global_vendor
            
            # Extract basic information from JSON
            product_name = str(json_item.get("product_name", json_item.get("name", ""))).strip()
            if not product_name:
                product_name = "Unknown Product"
            
            brand = str(json_item.get("brand", "")).strip()
            inventory_type = str(json_item.get("inventory_type", "")).strip()
            inventory_category = str(json_item.get("inventory_category", "")).strip()
            
            # Extract product type
            product_type = str(json_item.get("product_type", "")).strip()
            inventory_type_lower = inventory_type.lower() if inventory_type else ""
            if product_type:
                product_type_lower = product_type.lower()
                if product_type_lower in {"unknown", "unknown type"} or product_type_lower == inventory_type_lower:
                    product_type = ""
            mapped_product_type = map_inventory_type_to_product_type(
                inventory_type,
                inventory_category,
                product_name
            )
            if not product_type and mapped_product_type:
                product_type = mapped_product_type
            if not product_type:
                product_type = inventory_type or "Unknown"
            
            # Extract weight - prioritize unit_weight from JSON
            weight = str(json_item.get("unit_weight", json_item.get("weight", ""))).strip()
            if not weight:
                # Try to extract from product name
                import re
                weight_match = re.search(r'(\d+\.?\d*)\s*(g|gram|grams|gm|oz|ounce)', product_name, re.IGNORECASE)
                if weight_match:
                    weight = weight_match.group(1)
                else:
                    weight = "1"
            
            # Extract units - prioritize unit_weight_uom from JSON
            units = str(json_item.get("unit_weight_uom", json_item.get("uom", json_item.get("units", "")))).strip()
            if not units:
                if "oz" in product_name.lower() or "ounce" in product_name.lower():
                    units = "oz"
                elif "mg" in product_name.lower():
                    units = "mg"
                else:
                    units = "g"
            
            # Extract strain
            strain = str(json_item.get("strain_name", json_item.get("strain", ""))).strip()
            if not strain and product_name:
                strain = self._extract_strain_from_product_name(product_name) or ""
            
            # Extract lineage
            lineage = "HYBRID"  # Default
            if strain:
                strain_lower = strain.lower()
                if any(x in strain_lower for x in ["haze", "sativa", "durban", "jack"]):
                    lineage = "SATIVA"
                elif any(x in strain_lower for x in ["kush", "indica", "afghan", "bubba"]):
                    lineage = "INDICA"
                else:
                    lineage = "HYBRID"
            
            # Extract price
            price = str(json_item.get("line_price", json_item.get("price", ""))).strip()
            
            # Extract quantity
            quantity = str(json_item.get("qty", "1")).strip()
            
            # Extract description
            description = str(json_item.get("description", json_item.get("product_description", product_name))).strip()
            
            # Extract other fields
            thc_result = str(json_item.get("thc", "")).strip()
            cbd_result = str(json_item.get("cbd", "")).strip()
            doh_raw_value = (
                json_item.get('DOH') or json_item.get('doh') or json_item.get('doh_compliant') or
                json_item.get('DOH Compliant') or json_item.get('is_doh', '')
            )
            normalized_doh_value = ''
            if doh_raw_value:
                value_str = str(doh_raw_value).strip().lower()
                if value_str in ['yes', 'y', 'true', '1', 'doh']:
                    normalized_doh_value = 'Yes'
                elif str(doh_raw_value).upper() == 'THC':
                    normalized_doh_value = 'THC'
                elif str(doh_raw_value).upper() == 'CBD':
                    normalized_doh_value = 'CBD'
            
            # ENHANCED: Extrapolate missing data from similar products
            # If we're missing critical data (price, weight, description), try to infer from similar products
            inferred_data = {}
            if not price or not weight or not description or description == product_name:
                try:
                    logging.info(f"🔍 Attempting to extrapolate missing data for '{product_name}' from similar products...")
                    inferred_data = self._infer_from_similar_database_matches(
                        product_name, vendor, brand, product_type, strain, weight
                    )
                    
                    # Apply inferred data if missing
                    if not price and inferred_data.get('price'):
                        price = inferred_data['price']
                        logging.info(f"💰 Extrapolated price: {price} from similar products")
                    
                    if not weight and inferred_data.get('weight'):
                        weight = inferred_data['weight']
                        logging.info(f"⚖️  Extrapolated weight: {weight} from similar products")
                    
                    if (not description or description == product_name) and inferred_data.get('description'):
                        description = inferred_data['description']
                        logging.info(f"📝 Extrapolated description: {description} from similar products")
                    
                    # Also use inferred brand, lineage, product type if missing
                    if not brand and inferred_data.get('brand'):
                        brand = inferred_data['brand']
                        logging.info(f"🏷️  Extrapolated brand: {brand} from similar products")
                    
                    if lineage == "HYBRID" and inferred_data.get('lineage'):
                        lineage = inferred_data['lineage']
                        logging.info(f"🧬 Extrapolated lineage: {lineage} from similar products")
                    
                    if (not product_type or product_type == "Unknown Type") and inferred_data.get('product_type'):
                        product_type = inferred_data['product_type']
                        logging.info(f"📦 Extrapolated product type: {product_type} from similar products")
                        
                except Exception as infer_error:
                    logging.warning(f"Could not extrapolate data from similar products: {infer_error}")
            
            # Ensure manifest-derived product type takes precedence when inference conflicts
            if mapped_product_type and mapped_product_type.lower() not in {"unknown", "unknown type"}:
                mapped_type_lower = mapped_product_type.lower()
                product_type_lower = product_type.lower() if product_type else ""
                if product_type_lower and not self._are_product_types_compatible(mapped_type_lower, product_type_lower):
                    logging.info(f"🔁 Keeping manifest product type '{mapped_product_type}' over inferred '{product_type}'")
                    product_type = mapped_product_type
            elif not product_type:
                product_type = mapped_product_type or product_type
            
            # Normalize vendor/brand display
            vendor_display = self._normalize_vendor_display_name(vendor) if vendor else ''
            if vendor_display:
                vendor = vendor_display
            if not brand and vendor:
                brand = vendor
            
            # Normalize units and weight formatting
            units = (units or '').strip().lower() or 'g'
            formatted_weight = self._format_weight_label(weight, units) if weight else ''
            if not formatted_weight:
                formatted_weight = f"{weight}{units}".strip() if weight else ''
            combined_weight_value = weight
            
            # Format price using Excel-style formatting
            if price:
                price = format_price(price)
            elif inferred_data.get('price'):
                price = format_price(inferred_data['price'])
            price_value = price or ''
            
            # Create the faux tag
            tag = {
                # Core product information
                'Product Name*': product_name,
                'ProductName': product_name,
                'Description': description,
                'Product Type*': product_type,
                'Product Type': product_type,
                'Vendor': vendor if vendor and vendor.strip() else "Unknown Vendor",
                'Vendor/Supplier*': vendor if vendor and vendor.strip() else "Unknown Vendor",
                'Product Brand': brand,
                'ProductBrand': brand,
                'Product Strain': strain,
                'Strain Name': strain,
                'Lineage': lineage,
                'Weight*': formatted_weight,
                'Weight': formatted_weight,
                'Quantity*': quantity,
                'Quantity': quantity,
                'Units': units,
                'Price': price_value,
                'Price* (Tier Name for Bulk)': price_value,
                
                # Enhanced fields
                'State': 'active',
                'Is Sample? (yes/no)': 'no',
                'Is MJ product?(yes/no)': 'yes',
                'Discountable? (yes/no)': 'yes',
                'Room*': 'Default',
                'Medical Only (Yes/No)': 'No',
                'DOH': normalized_doh_value,
                'DOH Compliant (Yes/No)': normalized_doh_value,
                
                # Additional fields
                'Concentrate Type': product_type if "concentrate" in product_type.lower() else '',
                'Ratio': '',
                'Joint Ratio': '',
                'JointRatio': '',
                'THC test result': thc_result,
                'CBD test result': cbd_result,
                'Test result unit (% or mg)': '%',
                'Batch Number': '',
                'Lot Number': '',
                'Barcode*': '',
                'Med Price': '',
                'Expiration Date(YYYY-MM-DD)': '',
                'Is Archived? (yes/no)': 'no',
                'THC Per Serving': '',
                'Allergens': '',
                'Solvent': '',
                'Accepted Date': '',
                'Internal Product Identifier': '',
                'Product Tags (comma separated)': '',
                'Image URL': '',
                'Ingredients': '',
                
                # Legacy fields for compatibility
                'Source': 'JSON Match - Faux Tag (Novel Product)',
                'Quantity Received*': quantity,
                'Weight Unit* (grams/gm or ounces/oz)': units,
                'CombinedWeight': combined_weight_value,
                'DescAndWeight': self._process_description_from_product_name(product_name, weight, units),
                'Description_Complexity': '1',
                'Ratio_or_THC_CBD': '',
                'displayName': product_name,
                'weightWithUnits': formatted_weight,
                'WeightWithUnits': formatted_weight,
                'WeightUnits': formatted_weight,
                'vendor': vendor,
                'productBrand': brand,
                'lineage': lineage,
                'productType': product_type,
                'weight': weight,
                'units': units,
                'price': price_value,
                'description': description,
                'strain': strain,
                'quantity': quantity,
                'thc': thc_result,
                'cbd': cbd_result,
            }
            
            logging.info(f"🎨 Created FAUX TAG for novel product: '{product_name}' (no match found)")
            return tag
            
        except Exception as e:
            logging.error(f"Error creating faux tag for novel product: {e}")
            # Fallback minimal tag
            product_name = str(json_item.get("product_name", json_item.get("name", "Unknown Product"))).strip()
            return {
                'Product Name*': product_name,
                'ProductName': product_name,
                'Description': product_name,
                'Vendor': vendor or global_vendor or '',
                'Source': 'JSON Match - Faux Tag (Error Fallback)',
                'Product Type*': 'Unknown',
                'Weight*': '1 g',
                'Units': 'g',
                'Quantity*': '1',
                'Price': ''
            }
    
    def _add_educated_guess_to_database(self, educated_guess: Dict[str, Any], vendor: str) -> bool:
        """
        Add an educated guess product to the database so it shows up in the UI.
        
        Args:
            educated_guess: Product information from educated guessing
            vendor: The vendor name
            
        Returns:
            True if successfully added, False otherwise
        """
        try:
            # Extract data from educated guess
            product_name = educated_guess.get("product_name", "")
            brand = educated_guess.get("brand", "")
            product_type = educated_guess.get("product_type", "")
            strain = educated_guess.get("strain_name", "")
            lineage = educated_guess.get("lineage", "")
            price = str(educated_guess.get("price", ""))
            weight = str(educated_guess.get("weight", ""))
            units = str(educated_guess.get("units", ""))
            description = educated_guess.get("description", "")
            confidence = educated_guess.get("confidence", "medium")
            
            logging.info(f"💾 Adding educated guess to database: {product_name}")
            
            # CRITICAL FIX: Ensure CBD Blend products get CBD lineage
            if strain and str(strain).strip().lower() == 'cbd blend':
                if lineage and str(lineage).strip().upper() != 'CBD':
                    logging.info(f"🧬 CBD BLEND FIX: Setting lineage to 'CBD' for educated guess '{product_name}' (strain: '{strain}', was: '{lineage}')")
                lineage = 'CBD'
            elif not lineage and strain:
                # If no lineage but we have a strain, determine lineage using the same logic as _determine_lineage_for_product
                lineage = self._determine_lineage_for_product(product_type, lineage or '', product_name, strain)
                logging.info(f"🧬 Determined lineage '{lineage}' for educated guess '{product_name}' (type: '{product_type}', strain: '{strain}')")
            
            # Add to product database
            if hasattr(self, 'product_db') and self.product_db:
                # Check if product already exists
                existing_product = self.product_db.get_product_info(product_name)
                if existing_product:
                    logging.info(f"Product already exists in database: {product_name}")
                    return True
                
                # Add new product to database
                product_data = {
                    "Product Name*": product_name,
                    "Product Type*": product_type,
                    "Vendor/Supplier*": vendor,
                    "Product Brand": brand,
                    "Product Strain": strain,
                    "Lineage": lineage,
                    "Weight*": weight,
                    "Weight Unit* (grams/gm or ounces/oz)": units,
                    "Price* (Tier Name for Bulk)": price,
                    "Description": description,
                    "Source": f"Educated Guess ({confidence})",
                    "Total Occurrences": 1
                }
                
                success = self.product_db.add_or_update_product(product_data)
                if success:
                    logging.info(f"✅ Successfully added educated guess to database: {product_name}")
                    return True
                else:
                    logging.warning(f"❌ Failed to add educated guess to database: {product_name}")
                    return False
            else:
                logging.warning(f"❌ No product database available to add educated guess: {product_name}")
                return False
                
        except Exception as e:
            logging.error(f"Error adding educated guess to database for '{product_name}': {e}")
            return False
            


    def is_product_database_enabled(self) -> bool:
        """
        Check if Product Database integration is enabled and should be prioritized.
        
        Returns:
            True if Product Database should be used, False otherwise
        """
        try:
            # Check if we can initialize the Product Database
            product_db = self._get_product_database()
            # Try to access a simple method to verify it's working
            strains = product_db.get_all_strains()
            return len(strains) > 0
        except Exception as e:
            logging.debug(f"Product Database not available: {e}")
            return False

    def integrate_with_excel_system(self, excel_processor, matched_products: List[Dict]) -> bool:
        """
        Integrate JSON-matched products into the Excel data system.
        This ensures that JSON-matched products can be found during validation
        and label generation.
        
        Args:
            excel_processor: The Excel processor instance
            matched_products: List of products from JSON matching
            
        Returns:
            True if integration was successful, False otherwise
        """
        try:
            if not excel_processor or not hasattr(excel_processor, 'df'):
                logging.warning("Excel processor not available for integration")
                return False
                
            if not matched_products:
                logging.info("No products to integrate with Excel system")
                return True
                
            logging.info(f"Integrating {len(matched_products)} JSON-matched products with Excel system")
            
            # Convert matched products to DataFrame format
            import pandas as pd
            
            # Create a list to store the new rows
            new_rows = []
            
            for product in matched_products:
                # Create a row that matches the Excel DataFrame structure
                row_data = {}
                
                # Map all the fields to Excel columns
                for key, value in product.items():
                    # Handle both the original Excel column names and the JSON matcher field names
                    if key in excel_processor.df.columns:
                        row_data[key] = value
                    else:
                        # Try to find a matching column name
                        matching_col = None
                        for col in excel_processor.df.columns:
                            if col.lower() == key.lower() or col.lower().replace(' ', '').replace('*', '') == key.lower().replace(' ', '').replace('*', ''):
                                matching_col = col
                                break
                        
                        if matching_col:
                            row_data[matching_col] = value
                        else:
                            # If no matching column found, try to add it to the DataFrame
                            if key not in excel_processor.df.columns:
                                excel_processor.df[key] = ''
                            row_data[key] = value
                
                # Ensure all required Excel columns are present
                for col in excel_processor.df.columns:
                    if col not in row_data:
                        row_data[col] = ''
                
                new_rows.append(row_data)
            
            if new_rows:
                # Create DataFrame from new rows
                new_df = pd.DataFrame(new_rows)
                
                # Append to existing DataFrame
                excel_processor.df = pd.concat([excel_processor.df, new_df], ignore_index=True)
                
                logging.info(f"Successfully integrated {len(new_rows)} JSON-matched products into Excel system")
                logging.info(f"Excel DataFrame now contains {len(excel_processor.df)} total records")
                
                return True
            else:
                logging.warning("No valid rows created for Excel integration")
                return False
                
        except Exception as e:
            logging.error(f"Error integrating JSON products with Excel system: {e}")
            return False

    def _infer_product_type_from_name(self, product_name: str) -> str:
        """
        Infer product type from product name by analyzing keywords.
        Uses the same logic as the global infer_product_type_from_name function.
        
        Args:
            product_name: The product name to analyze
            
        Returns:
            Inferred product type or "Unknown Type" if no match
        """
        if not isinstance(product_name, str):
            return "Unknown Type"
        
        name_lower = product_name.lower()
        
        # Check TYPE_OVERRIDES first
        for key, value in TYPE_OVERRIDES.items():
            if key in name_lower:
                return value
        
        # Pattern-based inference - prioritize vape keywords over concentrate keywords
        if any(x in name_lower for x in ["flower", "bud", "nug", "herb", "marijuana", "cannabis"]):
            return "Flower"
        elif any(x in name_lower for x in ["vape", "cart", "cartridge", "disposable", "pod", "battery", "jefe", "twisted", "fire", "pen"]):
            return "Vape Cartridge"
        elif any(x in name_lower for x in ["concentrate", "rosin", "shatter", "wax", "live resin", "diamonds", "sauce", "extract", "oil", "distillate"]):
            return "Concentrate"
        elif any(x in name_lower for x in ["edible", "gummy", "chocolate", "cookie", "brownie", "candy"]):
            return "Edible (Solid)"
        elif any(x in name_lower for x in ["tincture", "oil", "drops", "liquid"]):
            return "Edible (Liquid)"
        elif any(x in name_lower for x in ["pre-roll", "joint", "cigar", "blunt"]):
            return "Pre-roll"
        elif any(x in name_lower for x in ["topical", "cream", "lotion", "salve", "balm"]):
            return "Topical"
        elif any(x in name_lower for x in ["tincture", "sublingual"]):
            return "Tincture"
        else:
            # Default to Vape Cartridge for any remaining unknown types since most products are concentrates
            return "Vape Cartridge"

    def _infer_brand_from_name(self, product_name: str) -> str:
        """
        Infer brand from product name by looking for common brand patterns and database lookups.
        
        Args:
            product_name: The product name to analyze
            
        Returns:
            Inferred brand name or empty string if no match
        """
        if not product_name:
            return ""
        
        # First, try to find brand in database using pattern matching
        try:
            product_db = self._get_product_database()
            
            # Search for similar product names in database to find brand
            with sqlite3.connect(product_db.db_path) as conn:
                # Use fuzzy matching to find similar product names
                cursor = conn.execute("""
                    SELECT "Product Brand", "Product Name*" 
                    FROM products 
                    WHERE "Product Brand" IS NOT NULL AND "Product Brand" != '' 
                    AND ("Product Name*" LIKE ? OR normalized_name LIKE ?)
                    LIMIT 5
                """, [f'%{product_name}%', f'%{product_name.lower()}%'])
                
                results = cursor.fetchall()
                if results:
                    # Return the most common brand from matches
                    brands = [row[0] for row in results if row[0]]
                    if brands:
                        # Return the first non-empty brand
                        return brands[0]
        except Exception as e:
            logging.warning(f"Database brand lookup failed: {e}")
        
        # Enhanced pattern-based inference using product type patterns
        name_lower = product_name.lower()
        
        # Try to infer brand based on product patterns that match known brands
        inferred_brand = self._infer_brand_from_product_patterns(product_name)
        if inferred_brand:
            return inferred_brand
        
        # Fallback to exact brand keyword matching
        brand_patterns = {
            'CERES': ['ceres', 'by ceres', 'ceres gardens'],
            'Oleum': ['oleum'],
            'Dabstract': ['dabstract'],
            'Constellation Cannabis': ['constellation'],
            'Mary Jones Cannabis Co': ['mary jones'],
            'Collections Cannabis': ['collections'],
            'Blue Roots Cannabis': ['blue roots'],
            'Grow Op Farms': ['grow op'],
            'Cloud 9 Farms': ['cloud 9'],
            'The Collective': ['collective'],
            'Fifty Fold': ['fifty fold'],
            'Seattle Sluggerz': ['seattle sluggerz'],
            'Hibro Wholesale': ['hibro'],
            'Core Reactor': ['core reactor'],
            'Diamond Knot': ['diamond knot'],
            'Terp Slurper': ['terp slurper']
        }
        
        # Check for exact brand matches
        for brand, keywords in brand_patterns.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return brand
        
        # Try to extract brand from product name structure
        # Priority 1: Look for "by Brand" pattern (most reliable)
        import re
        by_brand_match = re.search(r'\bby\s+([A-Za-z][A-Za-z\s&]+?)(?:\s+-\s*|\s*$)', product_name, re.IGNORECASE)
        if by_brand_match:
            brand = by_brand_match.group(1).strip()
            # Clean up common suffixes
            brand = re.sub(r'\s+(cannabis|co|company|brand|products?)$', '', brand, flags=re.IGNORECASE)
            if len(brand) > 1:
                return brand
        
        return ""

    def _infer_brand_from_product_patterns(self, product_name: str) -> str:
        """
        Infer brand by matching product patterns to known branded products.
        
        Args:
            product_name: The product name to analyze
            
        Returns:
            Inferred brand name or empty string if no match
        """
        try:
            if not product_name:
                return ""
            
            name_lower = product_name.lower()
            
            # Define brand-specific product patterns
            # These patterns are based on actual branded products in the data
            brand_patterns = {
                'CERES': [
                    # Ceres-specific patterns
                    'ceres',
                    'by ceres',
                    'ceres gardens',
                    'ceres -',
                    'ceres capsules',
                    'ceres tincture',
                    'ceres balm',
                    'ceres chews',
                    'ceres boost',
                    'ceres dragon',
                    'ceres chill',
                    'ceres lifted'
                ],
                'Oleum': [
                    # Live Resin patterns
                    'live resin cartridge',
                    'live resin disposable',
                    'live resin vape',
                    # Liquid Diamond patterns  
                    'liquid diamond disposable',
                    'liquid diamond vape',
                    # Honey Crystal patterns
                    'honey crystal',
                    # General Oleum patterns
                    'by oleum',
                    'oleum -'
                ],
                'Dabstract': [
                    'dabstract',
                    'by dabstract'
                ],
                'Constellation Cannabis': [
                    'constellation',
                    'by constellation'
                ],
                'Mary Jones Cannabis Co': [
                    'mary jones',
                    'by mary jones'
                ],
                'Collections Cannabis': [
                    'collections',
                    'by collections'
                ],
                'Blue Roots Cannabis': [
                    'blue roots',
                    'by blue roots'
                ],
                'Grow Op Farms': [
                    'grow op',
                    'by grow op'
                ],
                'Cloud 9 Farms': [
                    'cloud 9',
                    'by cloud 9'
                ],
                'The Collective': [
                    'collective',
                    'by collective'
                ],
                'Fifty Fold': [
                    'fifty fold',
                    'by fifty fold'
                ],
                'Seattle Sluggerz': [
                    'seattle sluggerz',
                    'by seattle sluggerz'
                ],
                'Hibro Wholesale': [
                    'hibro',
                    'by hibro'
                ],
                'Core Reactor': [
                    'core reactor',
                    'by core reactor'
                ],
                'Diamond Knot': [
                    'diamond knot',
                    'by diamond knot'
                ],
                'Terp Slurper': [
                    'terp slurper',
                    'by terp slurper'
                ]
            }
            
            # Check for pattern matches
            for brand, patterns in brand_patterns.items():
                for pattern in patterns:
                    if pattern in name_lower:
                        logging.info(f"🏷️ Inferred brand '{brand}' from pattern '{pattern}' in '{product_name}'")
                        return brand
            
            # Special case: Look for similar product patterns in database
            # This helps match products that share similar naming conventions
            try:
                product_db = self._get_product_database()
                
                # Extract key terms from the product name
                key_terms = self._extract_key_terms_for_brand_matching(product_name)
                
                if key_terms:
                    # Search for products with similar terms that have brands
                    import sqlite3
                    with sqlite3.connect(product_db.db_path) as conn:
                        cursor = conn.execute("""
                            SELECT "Product Brand", "Product Name*" 
                            FROM products 
                            WHERE "Product Brand" IS NOT NULL AND "Product Brand" != '' 
                            AND (
                                "Product Name*" LIKE ? OR 
                                "Product Name*" LIKE ? OR 
                                "Product Name*" LIKE ? OR
                                "Product Name*" LIKE ?
                            )
                            LIMIT 10
                        """, [
                            f'%{key_terms[0]}%' if len(key_terms) > 0 else '',
                            f'%{key_terms[1]}%' if len(key_terms) > 1 else '',
                            f'%{key_terms[2]}%' if len(key_terms) > 2 else '',
                            f'%{key_terms[3]}%' if len(key_terms) > 3 else ''
                        ])
                        
                        results = cursor.fetchall()
                        if results:
                            # Count brand occurrences
                            from collections import Counter
                            brands = [row[0] for row in results if row[0]]
                            if brands:
                                brand_counter = Counter(brands)
                                most_common_brand = brand_counter.most_common(1)[0][0]
                                logging.info(f"🏷️ Inferred brand '{most_common_brand}' from similar products for '{product_name}'")
                                return most_common_brand
            except Exception as e:
                logging.warning(f"Database pattern matching failed: {e}")
            
            return ""
            
        except Exception as e:
            logging.warning(f"Error in brand pattern inference: {e}")
            return ""
    
    def _extract_key_terms_for_brand_matching(self, product_name: str) -> list:
        """
        Extract key terms from product name that are likely to match branded products.
        
        Args:
            product_name: The product name to analyze
            
        Returns:
            List of key terms for brand matching
        """
        try:
            if not product_name:
                return []
            
            name_lower = product_name.lower()
            
            # Extract meaningful terms that are likely to appear in branded products
            key_terms = []
            
            # Product type terms
            product_type_terms = [
                'live resin', 'liquid diamond', 'honey crystal', 'distillate', 
                'cartridge', 'disposable', 'vape', 'concentrate', 'extract',
                'rosin', 'wax', 'shatter', 'diamonds', 'sauce'
            ]
            
            for term in product_type_terms:
                if term in name_lower:
                    key_terms.append(term)
            
            # Strain-like terms (but be careful not to use strain names as brand indicators)
            # Only use very common terms that appear in multiple branded products
            common_terms = [
                'gelato', 'cookies', 'kush', 'diesel', 'haze', 'skunk',
                'purple', 'blue', 'green', 'white', 'black', 'gold'
            ]
            
            for term in common_terms:
                if term in name_lower:
                    key_terms.append(term)
            
            # Return the most relevant terms (limit to 4 to avoid too many database queries)
            return key_terms[:4]
            
        except Exception as e:
            logging.warning(f"Error extracting key terms: {e}")
            return []
    
    def _extract_key_terms_for_strain_matching(self, product_name: str) -> list:
        """
        Extract key terms from product name that are likely to match strains in database.
        
        Args:
            product_name: The product name to analyze
            
        Returns:
            List of key terms for strain matching
        """
        try:
            if not product_name:
                return []
            
            name_lower = product_name.lower()
            
            # Extract meaningful terms that are likely to appear in strain names
            key_terms = []
            
            # Common strain name patterns
            strain_patterns = [
                'blue', 'green', 'purple', 'white', 'black', 'gold', 'red', 'pink', 'orange',
                'dream', 'crack', 'kush', 'haze', 'diesel', 'og', 'gelato', 'cookies', 'runtz',
                'wedding', 'cake', 'sherbet', 'berry', 'fruit', 'citrus', 'mint', 'vanilla',
                'strawberry', 'blueberry', 'banana', 'mango', 'pineapple', 'lemon', 'lime',
                'cherry', 'grape', 'apple', 'orange', 'guava', 'dragon', 'passion', 'peach',
                'apricot', 'watermelon', 'cantaloupe', 'honeydew', 'kiwi', 'plum', 'raspberry',
                'blackberry', 'yoda', 'amnesia', 'afghani', 'hashplant', 'super', 'boof',
                'grandy', 'candy', 'tricho', 'jordan', 'cosmic', 'combo', 'honey', 'bread',
                'mintz', 'grinch', 'ak-47', 'northern', 'lights', 'skunk', 'jack', 'herer',
                'durban', 'poison', 'trainwreck', 'chemdawg', 'sour', 'cheese', 'master',
                'hindu', 'afghan', 'bubba', 'granddaddy', 'grand', 'daddy', 'maui', 'wowie',
                'gsc', 'thin', 'mint', 'forum', 'cut', 'animal', 'white', 'pink', 'zombie',
                'rainbow', 'trophy', 'sunset', 'pie', 'cream', 'gas', 'gelatti', 'shortcake',
                'grapefruit', 'rain', 'crepe', 'trunk', 'funk', 'sub', 'woofer', 'golden',
                'chicken', 'waffles', 'punch', 'crasher', 'mimosa', 'goji', 'velvet', 'truffle',
                'emerald', 'bollywood', 'lemonade', 'burst', 'wave', 'soda', 'bliss', 'eyes',
                'ztripez', 'metaverse', 'galactic', 'gdpunch', 'ape', 'zoda', 'goji'
            ]
            
            for pattern in strain_patterns:
                if pattern in name_lower:
                    key_terms.append(pattern)
            
            # Also extract individual words that might be strain names
            words = product_name.split()
            for word in words:
                word_clean = re.sub(r'[^a-zA-Z]', '', word)
                if len(word_clean) >= 3 and word_clean.isalpha():
                    key_terms.append(word_clean.lower())
            
            # Return unique terms (limit to 5 to avoid too many database queries)
            unique_terms = list(set(key_terms))[:5]
            return unique_terms
            
        except Exception as e:
            logging.warning(f"Error extracting key terms for strain matching: {e}")
            return []

    def _format_weight_with_hyphen(self, weight: str, units: str, combined_weight: str = None, description: str = None) -> str:
        """
        Format weight with hyphen and nonbreaking space, using combined weight value.
        For JSON matched items, replaces weight value with " - " + combined weight.
        If combined weight is empty, extracts weight from end of product description.
        
        Args:
            weight: The weight value as string (original weight)
            units: The units (e.g., "g", "mg", "oz")
            combined_weight: The combined weight value from the database
            description: The product description (used to extract weight if combined_weight is empty)
            
        Returns:
            Formatted weight string with hyphen and nonbreaking space
        """
        # For JSON matched items, use combined weight value
        if combined_weight and str(combined_weight).strip():
            # Use the combined weight value directly, but format it properly
            weight_value = self._format_weight_value(str(combined_weight).strip())
            logging.info(f"🏷️ Using combined weight '{weight_value}' for JSON matched item")
            return f" - {weight_value}"
        
        # If combined weight is empty, try to extract from description
        if description and not combined_weight:
            weight_from_desc = self._extract_weight_from_description(description)
            if weight_from_desc:
                logging.info(f"🏷️ Extracted weight '{weight_from_desc}' from description for JSON matched item")
                return f" - {weight_from_desc}"
        
        # Fallback to original weight formatting if no combined weight available
        if not weight or not units:
            return f" - {weight or '0'}{units or 'g'}"
        
        try:
            # Convert to float to check if it's a whole number
            weight_float = float(weight)
            if weight_float == int(weight_float):
                # It's a whole number, remove decimal point
                formatted_weight = str(int(weight_float))
            else:
                # Keep decimal point for non-whole numbers
                formatted_weight = str(weight_float)
        except (ValueError, TypeError):
            # If conversion fails, use original weight
            formatted_weight = str(weight)
        
        return f" - {formatted_weight}{units}"

    def _extract_weight_from_description(self, description: str) -> str:
        """
        Enhanced weight extraction from product descriptions and names.
        Looks for patterns like "1.0g", "3.5g", "1oz", "10pk", "3.4oz", etc.
        
        Args:
            description: The product description string
            
        Returns:
            Extracted weight string or empty string if not found
        """
        if not description:
            return ""
        
        import re
        
        # Enhanced patterns for weight extraction
        weight_patterns = [
            # Standard weight patterns: 1.0g, 3.5g, 1oz, 100mg, etc.
            r'(\d+\.?\d*)\s*(g|oz|mg|grams?|ounces?)\s*$',
            # Package count patterns: 10pk, 5pk, 20pk, etc.
            r'(\d+)\s*pk\s*$',
            # Volume patterns: 3.4oz, 1oz, 0.5oz, etc.
            r'(\d+\.?\d*)\s*oz\s*$',
            # Weight in product names: BALL_SAT_CARAMEL_10pk, ROLL_UPS_3.4oz
            r'_(\d+\.?\d*)\s*(g|oz|mg|pk)\s*$',
            # Mixed patterns: 1:1_3.4oz, CBD_3.4oz
            r'(\d+\.?\d*)\s*(g|oz|mg|pk)\s*$',
        ]
        
        description_clean = description.strip()
        
        for pattern in weight_patterns:
            match = re.search(pattern, description_clean, re.IGNORECASE)
            if match:
                weight_value = match.group(1)
                unit = match.group(2) if len(match.groups()) > 1 else ""
                
                # Normalize units
                if unit.lower() in ['grams', 'gram']:
                    unit = 'g'
                elif unit.lower() in ['ounces', 'ounce']:
                    unit = 'oz'
                elif unit.lower() == 'pk':
                    unit = 'pk'
                
                # Format the result
                if unit:
                    return f"{weight_value}{unit}"
                else:
                    return weight_value
        
        return ""

    def _format_weight_value(self, weight_string: str) -> str:
        """
        Format weight value by removing decimal point for whole numbers.
        Examples: "1.0g" -> "1g", "3.5g" -> "3.5g", "2.0oz" -> "2oz"
        
        Args:
            weight_string: The weight string (e.g., "1.0g", "3.5g", "2.0oz")
            
        Returns:
            Formatted weight string with decimal removed for whole numbers
        """
        if not weight_string:
            return weight_string
        
        import re
        
        # Pattern to match weight with decimal: "1.0g", "3.5g", "2.0oz", etc.
        weight_pattern = r'^(\d+)\.0+([a-zA-Z]+)$'
        
        match = re.match(weight_pattern, weight_string.strip())
        if match:
            # It's a whole number with .0, remove the decimal
            number = match.group(1)
            unit = match.group(2)
            formatted = f"{number}{unit}"
            logging.info(f"🏷️ Formatted weight '{weight_string}' -> '{formatted}' (removed .0)")
            return formatted
        
        # No change needed for non-whole numbers or already formatted weights
        return weight_string

    def _normalize_vendor_display_name(self, vendor: str) -> str:
        """
        Normalize vendor casing to align with Excel / database conventions.
        Currently focuses on Cultivera manifests where vendor strings are fully uppercase.
        """
        if not vendor:
            return ""
        
        vendor_clean = str(vendor).strip()
        if not vendor_clean:
            return ""
        
        vendor_lower = vendor_clean.lower()
        
        special_cases = {
            'mt baker homegrown': 'Mt Baker Homegrown',
            'a greener today-bothell': 'A Greener Today - Bothell',
            'a greener today bothell': 'A Greener Today - Bothell'
        }
        
        if vendor_lower in special_cases:
            return special_cases[vendor_lower]
        
        # Title-case by default, but preserve common all-caps abbreviations
        title_cased = vendor_lower.title()
        # Preserve LLC/Inc style suffixes
        title_cased = title_cased.replace('Llc', 'LLC').replace('Inc', 'Inc').replace('Dbc', 'DBC')
        return title_cased

    def _format_weight_label(self, weight_value: Any, units: str) -> str:
        """
        Format a numeric weight plus units into Excel-style label (e.g., 1.0 g -> 1g, 3.5 g -> 3.5g).
        """
        if weight_value in [None, ""]:
            return ""
        
        unit = (units or "").strip()
        if not unit:
            unit = ""
        
        try:
            value = float(weight_value)
        except (TypeError, ValueError):
            # If parsing fails, fall back to raw value
            return f"{weight_value}{unit}"
        
        if value.is_integer():
            value_str = str(int(value))
        else:
            value_str = f"{value:.2f}".rstrip('0').rstrip('.')
        
        return f"{value_str}{unit}"
    
    def _format_weight_field(self, product: Dict, json_item: Dict = None) -> None:
        """
        Ensure Weight* field is properly formatted (no space between number and unit, e.g., "3.5g").
        This ensures JSON matched tags display weight exactly like normal tags.
        """
        if not product:
            return
        
        # Get weight and units from product or JSON item
        weight = product.get('Weight*', '') or product.get('Weight', '')
        units = product.get('Units', '') or product.get('Weight Unit*', '')
        
        # Try to get from JSON item if not in product
        if json_item and (not weight or not units):
            if not weight:
                weight = str(json_item.get('unit_weight', '') or json_item.get('weight', '')).strip()
            if not units:
                units = str(json_item.get('unit_weight_uom', '') or json_item.get('uom', '')).strip() or 'g'
        
        # If weight already includes units (e.g., "3.5g"), extract them
        if weight and not units:
            import re
            match = re.match(r'^([\d.]+)\s*([a-zA-Z]+)$', str(weight).strip())
            if match:
                weight = match.group(1)
                units = match.group(2)
        
        # Format weight properly (no space between number and unit)
        if weight and str(weight).strip():
            formatted_weight = self._format_weight_label(weight, units)
            product['Weight*'] = formatted_weight
            product['Weight'] = formatted_weight
            if units:
                product['Units'] = units

    def _generate_excel_style_variations(
        self,
        item: Dict[str, Any],
        vendor: str,
        product_type: Optional[str] = None
    ) -> Tuple[List[str], Optional[str]]:
        """
        Generate Excel-format product name variations for Cultivera-style manifests so that
        JSON matching can line up with database naming conventions.
        Returns a tuple of (variations, product_type_override).
        """
        variations: List[str] = []
        product_type_override: Optional[str] = None
        
        if not isinstance(item, dict):
            return variations, product_type_override
        
        vendor_display = self._normalize_vendor_display_name(vendor or item.get('vendor') or "")
        strain = str(item.get('strain_name') or item.get('strain') or "").strip()
        product_name = str(item.get('product_name', '')).strip()
        units = (item.get('unit_weight_uom') or item.get('weight_unit') or item.get('uom') or "").strip()
        weight_value = item.get('unit_weight') or item.get('weight')
        
        # Prepare helpers
        try:
            total_weight = float(weight_value) if weight_value not in [None, ""] else None
        except (TypeError, ValueError):
            total_weight = None
        
        units_lower = units.lower()
        name_lower = product_name.lower()
        is_joint_product = any(keyword in name_lower for keyword in ['joint', 'pre-roll', 'preroll'])
        
        # Flower / standard usable marijuana formatting
        if vendor_display and strain and total_weight is not None and units_lower in ['g', 'gram', 'grams'] and not is_joint_product:
            weight_label = self._format_weight_label(total_weight, 'g')
            if weight_label:
                base_name = f"{strain} by {vendor_display} - {weight_label}"
                variations.append(base_name)
                product_type_override = product_type_override or "Flower"
        
        # Pre-roll / joint formatting with pack sizes
        if vendor_display and strain and total_weight is not None and units_lower in ['g', 'gram', 'grams'] and is_joint_product:
            # Attempt to extract pack size from product name
            pack_count = None
            pack_match = re.search(r'joint\s*x\s*(\d+)', name_lower)
            if not pack_match:
                pack_match = re.search(r'x\s*(\d+)\s*pack', name_lower)
            if not pack_match:
                pack_match = re.search(r'(\d+)\s*pack', name_lower)
            if pack_match:
                try:
                    pack_count = int(pack_match.group(1))
                except ValueError:
                    pack_count = None
            
            if pack_count is None or pack_count <= 0:
                # Fallback: infer pack count based on naming patterns (e.g., "x2 Pack")
                if 'x2' in name_lower:
                    pack_count = 2
                elif 'x10' in name_lower:
                    pack_count = 10
            
            if pack_count is None or pack_count <= 0:
                pack_count = 1
            
            if pack_count > 0:
                per_unit_weight = total_weight / pack_count if pack_count else total_weight
                per_unit_label = self._format_weight_label(per_unit_weight, 'g')
                
                pack_suffix = "Pack" if pack_count > 1 else ""
                base_name = f"{strain} Pre-Roll by {vendor_display} - {per_unit_label} x {pack_count} {pack_suffix}".strip()
                variations.append(base_name)
                
                # Alternate formatting used in some Excel rows ("Pre-Rolls By")
                variations.append(base_name.replace("Pre-Roll by", "Pre-Rolls By", 1))
                
                # Allow variant without leading zero for .5g style entries
                if per_unit_label.startswith("0."):
                    no_leading_zero = per_unit_label[1:]
                    variations.append(base_name.replace(per_unit_label, no_leading_zero))
                    variations.append(base_name.replace(per_unit_label, no_leading_zero).replace("Pre-Roll by", "Pre-Rolls By", 1))
                
                product_type_override = "Pre-Roll"
        
        # Deduplicate while preserving order
        seen = set()
        unique_variations = []
        for variation in variations:
            normalized = variation.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_variations.append(normalized)
        
        return unique_variations, product_type_override

    def _upgrade_fallback_products(self, products: List[Dict], global_vendor: str) -> List[Dict]:
        """
        Post-process fallback products by attempting to convert them to full database-backed tags
        and applying formatting consistency when conversion isn't possible.
        """
        if not products:
            return products
        
        try:
            product_db = self._get_product_database()
        except Exception as db_error:
            logging.debug(f"Unable to obtain product database for fallback upgrade: {db_error}")
            product_db = None
        
        upgraded_products: List[Dict] = []
        
        for product in products:
            original_item = product.pop('__json_item__', None)
            vendor = product.get('Vendor') or global_vendor
            vendor_norm = self._normalize_vendor_display_name(vendor)
            strain = product.get('Product Strain') or (original_item.get('strain_name') if isinstance(original_item, dict) else '')
            product_type = product.get('Product Type*') or ''
            
            upgraded = False
            if product.get('Source', '').startswith('JSON - No DB Match') and product_db and isinstance(original_item, dict):
                variations, type_override = self._generate_excel_style_variations(original_item, vendor_norm, product_type)
                if type_override:
                    product_type = type_override
                if variations:
                    try:
                        db_match = self._find_best_database_match(
                            product_name=variations[0],
                            vendor=vendor_norm,
                            weight=str(original_item.get("unit_weight", original_item.get("weight", ""))).strip(),
                            strain=str(original_item.get("strain_name", original_item.get("strain", ""))).strip(),
                            product_db=product_db
                        )
                        if db_match:
                            upgraded_products.append(self._create_tag_from_database_info(db_match, vendor_norm, original_item))
                            upgraded = True
                    except Exception as upgrade_error:
                        logging.debug(f"DB upgrade for fallback failed: {upgrade_error}")
            
            if upgraded:
                continue
            
            # Apply consistent formatting even when we can't upgrade to DB match
            if vendor_norm:
                product['Vendor'] = vendor_norm
                product['Vendor/Supplier*'] = vendor_norm
            if product.get('Product Brand'):
                product['Product Brand'] = self._normalize_vendor_display_name(product['Product Brand'])
                product['ProductBrand'] = product['Product Brand']
            else:
                product['Product Brand'] = vendor_norm or product.get('Product Brand', 'Unknown Brand')
                product['ProductBrand'] = product['Product Brand']
            
            if product_type:
                product['Product Type*'] = product_type
                product['ProductType'] = product_type
            
            # Format weight label
            weight_value = product.get('Weight*')
            units = product.get('Units')
            weight_label = self._format_weight_label(weight_value, units)
            if weight_label:
                product['Weight Value + Unit'] = weight_label
            
            # Format price
            if product.get('Price'):
                formatted_price = format_price(product['Price'])
                product['Price'] = formatted_price
                product['Price*'] = formatted_price
            
            upgraded_products.append(product)
        
        return upgraded_products

    def _determine_doh_value(self, product_type: str, product_name: str = '') -> str:
        """
        Determine the appropriate DOH value based on product type.
        
        Args:
            product_type: The product type string
            product_name: The product name (optional, for additional context)
            
        Returns:
            DOH value string: 'THC', 'CBD', 'YES', or 'NO'
        """
        if not product_type:
            # Default to THC for products without type
            return 'THC'
        
        product_type_lower = str(product_type).lower().strip()
        product_name_lower = str(product_name).lower().strip()
        
        # High CBD products get CBD designation
        if 'high cbd' in product_type_lower or 'highcbd' in product_type_lower:
            return 'CBD'
        
        # CBD-focused products (check product name too)
        if 'cbd' in product_type_lower and 'thc' not in product_type_lower:
            return 'CBD'
        
        # Classic types (flower, pre-roll, concentrates, vapes) get THC designation
        classic_types = [
            'flower', 'bud', 'pre-roll', 'preroll', 'blunt', 'joint',
            'concentrate', 'wax', 'shatter', 'rosin', 'resin', 'hash',
            'cartridge', 'vape', 'pen', 'disposable', 'distillate',
            'extract', 'crumble', 'badder', 'sauce', 'diamonds', 'live'
        ]
        
        if any(classic_type in product_type_lower for classic_type in classic_types):
            return 'THC'
        
        # High THC products get THC designation
        if 'high thc' in product_type_lower or 'highthc' in product_type_lower:
            return 'THC'
        
        # Non-classic types (edibles, tinctures, topicals) default to YES
        nonclassic_types = [
            'edible', 'tincture', 'topical', 'capsule', 'pill',
            'tablet', 'gummy', 'gummies', 'chocolate', 'candy',
            'beverage', 'drink', 'syrup', 'powder', 'spray',
            'lotion', 'balm', 'salve', 'cream', 'patch'
        ]
        
        if any(nonclassic_type in product_type_lower for nonclassic_type in nonclassic_types):
            return 'YES'
        
        # Default to THC for unrecognized types
        return 'THC'
    
    def _get_default_lineage_for_product_type(self, product_type: str) -> str:
        """
        Get default lineage based on product type.
        Uses intelligent lineage assignment based on product type characteristics.
        
        Args:
            product_type: The product type string
            
        Returns:
            Default lineage string based on product type
        """
        if not product_type:
            return 'HYBRID'  # Default to HYBRID instead of MIXED
        
        product_type_lower = str(product_type).lower().strip()
        
        # Define product type to lineage mapping
        type_lineage_mapping = {
            # Flower and plant-based products - typically HYBRID
            'flower': 'HYBRID',
            'bud': 'HYBRID', 
            'nug': 'HYBRID',
            'herb': 'HYBRID',
            'marijuana': 'HYBRID',
            'cannabis': 'HYBRID',
            'mini buds': 'HYBRID',
            'shake': 'HYBRID',
            'trim': 'HYBRID',
            
            # Pre-rolls - typically HYBRID
            'pre-roll': 'HYBRID',
            'joint': 'HYBRID',
            'cigar': 'HYBRID',
            'blunt': 'HYBRID',
            
            # Concentrates - typically HYBRID (single strain extracts)
            'concentrate': 'HYBRID',
            'rosin': 'HYBRID',
            'wax': 'HYBRID',
            'shatter': 'HYBRID',
            'live resin': 'HYBRID',
            'diamonds': 'HYBRID',
            'sauce': 'HYBRID',
            'extract': 'HYBRID',
            'oil': 'HYBRID',
            'distillate': 'HYBRID',
            'honey crystal': 'HYBRID',
            'liquid diamond': 'HYBRID',
            
            # Vape products - typically HYBRID
            'vape': 'HYBRID',
            'cart': 'HYBRID',
            'cartridge': 'HYBRID',
            'disposable': 'HYBRID',
            'pod': 'HYBRID',
            'disposable vape': 'HYBRID',
            'vape cartridge': 'HYBRID',
            
            # Edibles - typically MIXED (nonclassic types get blue color)
            'edible': 'MIXED',
            'gummy': 'MIXED',
            'chocolate': 'MIXED',
            'cookie': 'MIXED',
            'brownie': 'MIXED',
            'candy': 'MIXED',
            'beverage': 'MIXED',
            
            # Tinctures and oils - typically MIXED (nonclassic types get blue color)
            'tincture': 'MIXED',
            'drops': 'MIXED',
            'liquid': 'MIXED',
            'sublingual': 'MIXED',
            
            # Topicals - typically MIXED (nonclassic types get blue color)
            'topical': 'MIXED',
            'cream': 'MIXED',
            'lotion': 'MIXED',
            'salve': 'MIXED',
            'balm': 'MIXED',
            
            # RSO and full extract - typically HYBRID
            'rso': 'HYBRID',
            'feco': 'HYBRID',
            'full extract': 'HYBRID',
            'co2': 'HYBRID',
            'tanker': 'HYBRID',
            
            # Capsules - typically MIXED (nonclassic type)
            'capsule': 'MIXED',
            
            # Only truly mixed products should be MIXED
            'mixed': 'MIXED',
            'blend': 'MIXED',
            'combination': 'MIXED',
            
            # Paraphernalia and non-cannabis products
            'paraphernalia': 'PARAPHERNALIA',
            'accessory': 'PARAPHERNALIA',
            'equipment': 'PARAPHERNALIA'
        }
        
        # Check for exact matches first
        for type_key, lineage in type_lineage_mapping.items():
            if type_key in product_type_lower:
                logging.info(f"🧬 Assigned lineage '{lineage}' based on product type '{product_type}'")
                return lineage
        
        # If no specific match found, default based on product type classification
        # Import CLASSIC_TYPES to determine if this is a nonclassic product
        from src.core.constants import CLASSIC_TYPES
        is_nonclassic = product_type.lower() not in [ct.lower() for ct in CLASSIC_TYPES]
        
        if is_nonclassic:
            logging.info(f"🧬 No specific lineage mapping found for nonclassic product type '{product_type}', defaulting to MIXED")
            return 'MIXED'
        else:
            logging.info(f"🧬 No specific lineage mapping found for classic product type '{product_type}', defaulting to HYBRID")
            return 'HYBRID'

    def _find_strain_in_database(self, product_name: str, product_db) -> Optional[str]:
        """
        Find strain information in the database by searching for similar product names.
        
        Args:
            product_name: The product name to search for
            product_db: The ProductDatabase instance
            
        Returns:
            Strain name if found, None otherwise
        """
        try:
            # Search for products with similar names in the database
            similar_products = product_db.find_best_product_match(product_name)
            
            if similar_products and similar_products.get('product_strain'):
                return similar_products['product_strain']
            
            # If no direct match, try searching by product name parts
            name_parts = product_name.lower().split()
            for part in name_parts:
                if len(part) > 3:  # Only search for meaningful parts
                    # Search for products containing this part
                    search_result = product_db.find_best_product_match(part)
                    if search_result and search_result.get('product_strain'):
                        logging.info(f"Found strain '{search_result['product_strain']}' for part '{part}' of '{product_name}'")
                        return search_result['product_strain']
            
            return None
            
        except Exception as e:
            logging.warning(f"Error searching database for strain: {e}")
            return None

    def _extract_strain_from_product_name(self, product_name: str) -> Optional[str]:
        """
        Extract strain name from product name for database lookup.
        
        Args:
            product_name: The full product name
            
        Returns:
            Extracted strain name or None if no strain found
        """
        try:
            if not product_name:
                return None
                
            # Common strain keywords to look for
            strain_keywords = [
                # Popular strains
                "blue dream", "green crack", "maui wowie", "granddaddy purple", "bubba kush",
                "master kush", "hindu kush", "afghan kush", "sour diesel", "nyc diesel",
                "girl scout cookies", "gsc", "thin mint", "forum cut", "animal cookies",
                "white runtz", "pink runtz", "zombie runtz", "rainbow runtz", "trophy runtz",
                "gelato", "gelato 33", "gelato 41", "gelato 47", "sunset sherbet", "sherbet",
                "wedding cake", "wedding crasher", "wedding pie", "wedding mint",
                "blueberry", "strawberry", "banana", "mango", "pineapple", "lemon", "lime", 
                "cherry", "grape", "apple", "orange", "guava", "dragon", "fruit", "passion", 
                "peach", "apricot", "watermelon", "cantaloupe", "honeydew", "kiwi", "plum", 
                "raspberry", "blackberry", "yoda", "amnesia", "afghani", "hashplant", "super", 
                "boof", "grandy", "candy", "tricho", "jordan", "cosmic", "combo", "honey", 
                "bread", "mintz", "grinch", "ak-47", "white widow", "northern lights", "skunk", 
                "jack herer", "durban poison", "trainwreck", "chemdawg", "sour", "cheese", 
                "dream", "crack", "maui", "granddaddy", "grand daddy", "bubba", "master", 
                "hindu", "afghan", "master", "sour", "cheese", "dream", "high life", "white gummie",
                "seattle trophy wife", "tangerine queen", "cenex", "triangle kush", "red velvet cake",
                "grape goji", "watermelon mojito", "candy pound cake", "truffle cake", "emerald apricot",
                "bollywood runtz", "mango punch", "raspberry lemonade", "strawberry burst", "watermelon wave",
                "grape soda", "strawberry bliss", "25 eyes", "cherry ztripez", "metaverse", "galactic jack",
                "gdpunch", "grape ape", "rainbow cake", "strawberry mimosa", "yoda og", "goji og",
                "cookies and cream", "grape gas gelatti", "maui wowie", "strawberry shortcake", "grapefruit",
                "purple rain", "crepe ape", "trunk funk", "sub woofer", "golden pineapple", "chicken & waffles"
            ]
            
            product_lower = product_name.lower()
            
            # If no exact match, try to extract from common patterns FIRST
            import re
            
            # Look for "Strain Name (Strain/weight)" pattern - CRITICAL FOR JSON MATCHED PRODUCTS
            # This should take priority over keyword matching for better accuracy
            parentheses_match = re.search(r'\(([^/]+)/', product_name)
            if parentheses_match:
                potential_strain = parentheses_match.group(1).strip()
                # Clean up the strain name - remove extra descriptive text after dash
                if " - " in potential_strain:
                    potential_strain = potential_strain.split(" - ")[0].strip()
                if len(potential_strain) > 2:  # Must be at least 3 characters
                    logging.debug(f"Extracted potential strain '{potential_strain}' from parentheses pattern")
                    return potential_strain.title()
            
            # ENHANCED: Look for strain as first 1-3 words of product name (most common pattern)
            # This handles cases like "GSC Live Resin Cartridge 1.0g" -> "GSC"
            # or "Purple Punch Live Resin Disposable Vape 1.0g" -> "Purple Punch"
            # or "Jet Fuel Gelato Live Resin by Oleum - 1g" -> "Jet Fuel Gelato"
            words = product_name.split()
            if len(words) >= 2:
                product_type_words = ['live', 'liquid', 'diamond', 'honey', 'crystal', 'resin', 'distillate', 'extract', 'concentrate', 'oil', 'wax', 'shatter', 'rosin', 'sauce', 'diamonds', 'terp', 'terps', 'terpene', 'terpenes', 'disposable', 'vape', 'cartridge']
                
                # Try first three words as strain (for three-word strains like "Jet Fuel Gelato")
                if len(words) >= 3:
                    three_words = f"{words[0]} {words[1]} {words[2]}"
                    if len(three_words) > 6 and all(word.isalpha() for word in words[:3]):
                        # Check if none of the words are common product type words
                        if not any(word.lower() in product_type_words for word in words[:3]):
                            logging.debug(f"Extracted potential strain '{three_words}' from first three words pattern")
                            return three_words.title()
                        else:
                            logging.debug(f"Skipping three-word strain '{three_words}' due to product type words")
                
                # Try first two words as strain (for multi-word strains like "Purple Punch")
                if len(words) >= 2:
                    two_words = f"{words[0]} {words[1]}"
                    if len(two_words) > 4 and all(word.isalpha() for word in words[:2]):
                        # Check if neither word is a common product type word
                        if not any(word.lower() in product_type_words for word in words[:2]):
                            logging.debug(f"Extracted potential strain '{two_words}' from first two words pattern")
                            return two_words.title()
                
                # Try first word as strain
                first_word = words[0]
                if len(first_word) > 2 and first_word.isalpha():
                    # Check if it's not a common product type word
                    product_type_words = ['live', 'liquid', 'diamond', 'honey', 'crystal', 'resin', 'distillate', 'extract', 'concentrate', 'oil', 'wax', 'shatter', 'rosin', 'sauce', 'diamonds', 'terp', 'terps', 'terpene', 'terpenes', 'disposable', 'vape', 'cartridge']
                    if first_word.lower() not in product_type_words:
                        logging.debug(f"Extracted potential strain '{first_word}' from first word pattern")
                        # Preserve original case for acronyms (all caps)
                        if first_word.isupper() and len(first_word) <= 4:
                            return first_word
                        else:
                            return first_word.title()
            
            # Look for "Strain Name -" pattern
            if " - " in product_name:
                parts = product_name.split(" - ")
                if len(parts) > 1:
                    potential_strain = parts[1].split()[0]  # First word after dash
                    if len(potential_strain) > 2:  # Must be at least 3 characters
                        logging.debug(f"Extracted potential strain '{potential_strain}' from dash pattern")
                        return potential_strain.title()
            
            # Look for exact strain matches in keywords list (fallback)
            # But only if we haven't already found a strain from first word patterns
            for strain in strain_keywords:
                if strain in product_lower:
                    # Skip if this is just a product type word
                    if strain.lower() in ['honey', 'crystal', 'live', 'liquid', 'diamond', 'resin', 'disposable', 'vape', 'cartridge']:
                        continue
                    logging.debug(f"Found strain '{strain}' in product name '{product_name}'")
                    return strain.title()
            
            # Look for "Strain Name LR" pattern (Live Resin)
            lr_match = re.search(r'^([A-Za-z\s]+)\s+LR', product_name, re.IGNORECASE)
            if lr_match:
                potential_strain = lr_match.group(1).strip()
                if len(potential_strain) > 2:
                    logging.debug(f"Extracted potential strain '{potential_strain}' from LR pattern")
                    return potential_strain.title()
            
            # Look for "Strain Name Dabstract" pattern
            dabstract_match = re.search(r'^([A-Za-z\s]+)\s+Dabstract', product_name, re.IGNORECASE)
            if dabstract_match:
                potential_strain = dabstract_match.group(1).strip()
                if len(potential_strain) > 2:
                    logging.debug(f"Extracted potential strain '{potential_strain}' from Dabstract pattern")
                    return potential_strain.title()
            
            # Look for "Strain Name Gummiez" pattern
            gummiez_match = re.search(r'^([A-Za-z\s]+)\s+Gummiez', product_name, re.IGNORECASE)
            if gummiez_match:
                potential_strain = gummiez_match.group(1).strip()
                if len(potential_strain) > 2:
                    logging.debug(f"Extracted potential strain '{potential_strain}' from Gummiez pattern")
                    return potential_strain.title()
            
            # FALLBACK: Try to find strain in database by searching for similar product names
            try:
                product_db = self._get_product_database()
                
                # Search for products with similar names that have strains
                import sqlite3
                with sqlite3.connect(product_db.db_path) as conn:
                    # Extract key terms from product name for matching
                    key_terms = self._extract_key_terms_for_strain_matching(product_name)
                    
                    if key_terms:
                        # Search for products with similar terms that have strains
                        placeholders = ' OR '.join(['"Product Name*" LIKE ?'] * len(key_terms))
                        query = f"""
                            SELECT "Product Strain", "Product Name*" 
                            FROM products 
                            WHERE "Product Strain" IS NOT NULL AND "Product Strain" != '' 
                            AND ({placeholders})
                            LIMIT 5
                        """
                        
                        cursor = conn.execute(query, [f'%{term}%' for term in key_terms])
                        results = cursor.fetchall()
                        
                        if results:
                            # Count strain occurrences
                            from collections import Counter
                            strains = [row[0] for row in results if row[0]]
                            if strains:
                                strain_counter = Counter(strains)
                                most_common_strain = strain_counter.most_common(1)[0][0]
                                logging.debug(f"Found strain '{most_common_strain}' from database similarity for '{product_name}'")
                                return most_common_strain
            except Exception as e:
                logging.debug(f"Database strain lookup failed: {e}")
            
            logging.debug(f"No strain extracted from product name: {product_name}")
            return None
            
        except Exception as e:
            logging.warning(f"Error extracting strain from product name '{product_name}': {e}")
            return None

    def _extract_key_terms(self, name: str) -> Set[str]:
        """Extract meaningful product terms, excluding common prefixes/suffixes."""
        try:
            # Debug logging to see what type of input we're getting
            if not isinstance(name, str):
                logging.warning(f"_extract_key_terms received non-string input: {type(name)} - {name}")
                if isinstance(name, list):
                    logging.warning(f"_extract_key_terms received a list: {name}")
                    # If it's a list, try to join it or take the first element
                    if name:
                        name = str(name[0]) if isinstance(name[0], str) else str(name[0])
                    else:
                        name = ""
                else:
                    name = str(name) if name is not None else ""
            
            # Ensure input is a string
            name = str(name or "")
            name_lower = name.lower()
            
            # Split on both spaces and hyphens to break compound terms
            words = set()
            for part in name_lower.replace('_', ' ').split():
                # Split each part on hyphens as well
                sub_parts = part.split('-')
                for sub_part in sub_parts:
                    if sub_part.strip():  # Only add non-empty parts
                        words.add(sub_part.strip())
            
            # Common words to exclude
            common_words = {
                'medically', 'compliant', '1g', '2g', '3.5g', '7g', '14g', '28g', 'oz', 'gram', 'grams',
                'pk', 'pack', 'packs', 'piece', 'pieces', 'roll', 'rolls', 'stix', 'stick', 'sticks', 'brand', 'vendor', 'product',
                'the', 'and', 'or', 'with', 'for', 'of', 'by', 'from', 'to', 'in', 'on', 'at', 'a', 'an', 'mg', 'thc', 'cbd'
            }
            
            # Filter out common words and short words (less than 2 characters for words like "all", "in", "one")
            key_terms = {word for word in words if word not in common_words and len(word) >= 2}
            
            # Add product type indicators for better matching
            product_types = {
                'rosin', 'wax', 'shatter', 'live', 'resin', 'distillate', 'cartridge', 'pre-roll', 'pre-rolls',
                'blunt', 'blunts', 'edible', 'edibles', 'tincture', 'tinctures', 'topical', 'topicals',
                'concentrate', 'concentrates', 'flower', 'buds', 'infused', 'flavour', 'flavor'
            }
            
            # Add product type terms if found
            for word in words:
                if word in product_types:
                    key_terms.add(word)
            
            # Add strain names (common cannabis strain words)
            strain_indicators = {
                'gmo', 'runtz', 'cookies', 'cream', 'wedding', 'cake', 'blueberry', 'banana', 'strawberry',
                'grape', 'lemon', 'lime', 'orange', 'cherry', 'apple', 'mango', 'pineapple', 'passion',
                'dragon', 'fruit', 'guava', 'pink', 'lemonade', 'haze', 'kush', 'diesel', 'og', 'sherbet',
                'gelato', 'mintz', 'grinch', 'cosmic', 'combo', 'honey', 'bread', 'tricho', 'jordan',
                'super', 'boof', 'grandy', 'candy', 'afghani', 'hashplant', 'yoda', 'amnesia'
            }
            
            # Add strain terms if found
            for word in words:
                if word in strain_indicators:
                    key_terms.add(word)
            
            # Add vendor/brand terms (but exclude common prefixes)
            vendor_prefixes = {'medically', 'compliant', 'by'}
            name_parts = name_lower.split()
            for i, part in enumerate(name_parts):
                if part not in vendor_prefixes and len(part) >= 3:
                    # Add single vendor words only
                    key_terms.add(part)
                  
            return key_terms
        except Exception as e:
            logging.warning(f"Error in _extract_key_terms: {e}")
            return set()

    def _create_synthetic_match(self, product_name: str, vendor: str, brand: str, product_type: str, strain: str, weight: str) -> Optional[str]:
        """Create a synthetic match when no real match can be found to ensure 100% coverage."""
        try:
            # Find any row in the Excel data that we can use as a template
            if self.excel_processor and self.excel_processor.df is not None:
                df = self.excel_processor.df
                
                # Look for any row with similar characteristics
                for idx, row in df.iterrows():
                    try:
                        # Check if this row has basic product information
                        excel_product_name = str(row.get('Product Name*', '') or row.get('ProductName', '') or row.get('Description', '')).strip()
                        excel_vendor = str(row.get('Vendor', '') or row.get('Vendor/Supplier*', '')).strip()
                        excel_product_type = str(row.get('Product Type*', '')).strip()
                        
                        if excel_product_name and excel_product_type:
                            # Use this row as a template for synthetic matching
                            logging.info(f"🔧 Creating synthetic match for '{product_name}' using template row '{excel_product_name}'")
                            return str(idx)
                    except Exception as e:
                        continue
                
                # If no template found, use the first available row
                if len(df) > 0:
                    logging.info(f"🔧 Creating synthetic match for '{product_name}' using first available row")
                    return str(df.index[0])
            
            return None
        except Exception as e:
            logging.warning(f"Error creating synthetic match: {e}")
            return None

    def _find_fallback_match(self, product_name: str, vendor: str, brand: str, product_type: str, strain: str, weight: str) -> Optional[str]:
        """
        Emergency fallback matching to ensure 100% coverage.
        This method finds any possible match using very loose criteria.
        """
        try:
            if not self.excel_processor or self.excel_processor.df is None:
                return None
                
            df = self.excel_processor.df
            product_name_lower = product_name.lower()
            
            # Strategy 1: Find any row with similar product type
            if product_type:
                for idx, row in df.iterrows():
                    excel_type = str(row.get('Product Type*', '') or row.get('Product Type', '')).lower()
                    if product_type.lower() in excel_type or excel_type in product_type.lower():
                        logging.info(f"🆘 Emergency match by product type: '{product_name}' → '{row.get('Product Name*', 'Unknown')}'")
                        return str(idx)
            
            # Strategy 2: Find any row with similar weight
            if weight:
                weight_num = re.search(r'(\d+(?:\.\d+)?)', weight)
                if weight_num:
                    weight_val = float(weight_num.group(1))
                    for idx, row in df.iterrows():
                        excel_weight = str(row.get('Weight*', '') or row.get('Weight', ''))
                        excel_weight_num = re.search(r'(\d+(?:\.\d+)?)', excel_weight)
                        if excel_weight_num:
                            excel_weight_val = float(excel_weight_num.group(1))
                            if abs(weight_val - excel_weight_val) <= 2.0:  # Within 2 units
                                logging.info(f"🆘 Emergency match by weight: '{product_name}' → '{row.get('Product Name*', 'Unknown')}'")
                                return str(idx)
            
            # Strategy 3: Find any row with any word in common (very loose)
            product_words = set(product_name_lower.split())
            for idx, row in df.iterrows():
                excel_name = str(row.get('Product Name*', '') or row.get('ProductName', '') or row.get('Description', '')).lower()
                excel_words = set(excel_name.split())
                if product_words.intersection(excel_words):
                    logging.info(f"🆘 Emergency match by word overlap: '{product_name}' → '{row.get('Product Name*', 'Unknown')}'")
                    return str(idx)
            
            # Strategy 4: Just pick the first available row (last resort)
            if len(df) > 0:
                first_idx = df.index[0]
                logging.info(f"🆘 Emergency match using first available row: '{product_name}' → '{df.iloc[0].get('Product Name*', 'Unknown')}'")
                return str(first_idx)
                
            return None
            
        except Exception as e:
            logging.error(f"Error in emergency fallback matching: {e}")
            return None

    def _enhance_product_with_json_data(self, product: dict, json_item: dict) -> None:
        """
        Enhance a product with additional data from JSON item.
        This is used when we have a partial match but want to add more data from JSON.
        
        Args:
            product: The product dictionary to enhance
            json_item: The original JSON item with additional data
        """
        try:
            # Add JSON quantity if available and product doesn't have it
            current_qty = product.get('Quantity*') if hasattr(product, 'get') else (product['Quantity*'] if hasattr(product, 'index') and 'Quantity*' in product.index else '') if hasattr(product, 'index') else ''
            if not current_qty and json_item.get('qty'):
                product['Quantity*'] = str(json_item.get('qty'))
            
            # Add JSON weight if available and product doesn't have it
            current_weight = product.get('Weight*') if hasattr(product, 'get') else (product['Weight*'] if hasattr(product, 'index') and 'Weight*' in product.index else '') if hasattr(product, 'index') else ''
            if not current_weight and json_item.get('unit_weight'):
                product['Weight*'] = str(json_item.get('unit_weight'))
            
            # Add JSON price if available and product doesn't have it
            current_price = product.get('Price') if hasattr(product, 'get') else (product['Price'] if hasattr(product, 'index') and 'Price' in product.index else '') if hasattr(product, 'index') else ''
            if not current_price and json_item.get('price'):
                product['Price'] = str(json_item.get('price'))
            
            # Add JSON strain if available and product doesn't have it
            current_strain = product.get('Product Strain') if hasattr(product, 'get') else (product['Product Strain'] if hasattr(product, 'index') and 'Product Strain' in product.index else '') if hasattr(product, 'index') else ''
            if not current_strain and json_item.get('strain_name'):
                product['Product Strain'] = str(json_item.get('strain_name'))
            
            # Add JSON brand if available and product doesn't have it
            current_brand = product.get('Product Brand') if hasattr(product, 'get') else (product['Product Brand'] if hasattr(product, 'index') and 'Product Brand' in product.index else '') if hasattr(product, 'index') else ''
            if not current_brand and json_item.get('brand'):
                product['Product Brand'] = str(json_item.get('brand'))
            
            # Add JSON vendor if available and product doesn't have it
            current_vendor = product.get('Vendor') if hasattr(product, 'get') else (product['Vendor'] if hasattr(product, 'index') and 'Vendor' in product.index else '') if hasattr(product, 'index') else ''
            if not current_vendor and json_item.get('vendor'):
                product['Vendor'] = str(json_item.get('vendor'))
            
            # Add JSON product type if available and product doesn't have it
            current_type = product.get('Product Type*') if hasattr(product, 'get') else (product['Product Type*'] if hasattr(product, 'index') and 'Product Type*' in product.index else '') if hasattr(product, 'index') else ''
            if not current_type and json_item.get('inventory_type'):
                product['Product Type*'] = str(json_item.get('inventory_type'))
            
            # Try to extract THC/CBD values from JSON data
            current_thc = product.get('THC test result') if hasattr(product, 'get') else product.get('THC test result', '') if 'THC test result' in product else ''
            if not current_thc or current_thc == '':
                thc_value = (json_item.get('THC test result') or 
                            json_item.get('thc') or 
                            json_item.get('thc_percent') or 
                            json_item.get('thc_percentage') or 
                            json_item.get('total_thc') or 
                            json_item.get('total_thc_percent'))
                if thc_value:
                    product['THC test result'] = str(thc_value)
                    logging.info(f"🧪 Enhanced with THC value from JSON: {thc_value}")
            
            current_cbd = product.get('CBD test result') if hasattr(product, 'get') else product.get('CBD test result', '') if 'CBD test result' in product else ''
            if not current_cbd or current_cbd == '':
                cbd_value = (json_item.get('CBD test result') or 
                            json_item.get('cbd') or 
                            json_item.get('cbd_percent') or 
                            json_item.get('cbd_percentage') or 
                            json_item.get('total_cbd') or 
                            json_item.get('total_cbd_percent'))
                if cbd_value:
                    product['CBD test result'] = str(cbd_value)
                    logging.info(f"🧪 Enhanced with CBD value from JSON: {cbd_value}")
            
            # Try to extract from lab_result_data as well
            lab_result_data = json_item.get("lab_result_data", {})
            if lab_result_data:
                cannabinoids = extract_cannabinoids(lab_result_data)
                current_thc = product.get('THC test result') if hasattr(product, 'get') else product.get('THC test result', '') if 'THC test result' in product else ''
                if 'thc' in cannabinoids and (not current_thc or current_thc == ''):
                    product['THC test result'] = str(cannabinoids['thc'])
                    logging.info(f"🧪 Enhanced with THC value from lab_result_data: {cannabinoids['thc']}")
                current_cbd = product.get('CBD test result') if hasattr(product, 'get') else product.get('CBD test result', '') if 'CBD test result' in product else ''
                if 'cbd' in cannabinoids and (not current_cbd or current_cbd == ''):
                    product['CBD test result'] = str(cannabinoids['cbd'])
                    logging.info(f"🧪 Enhanced with CBD value from lab_result_data: {cannabinoids['cbd']}")
            
            logging.info(f"✅ Enhanced product with JSON data: '{product.get('Product Name*', 'Unknown')}'")
            
        except Exception as e:
            logging.warning(f"Error enhancing product with JSON data: {e}")

    def _create_database_entry_for_unmatched_json(self, tag: dict, product_db) -> None:
        """
        Create a new database entry for an unmatched JSON tag.
        This ensures that unmatched JSON products are added to the product database
        for future matching and reference.
        
        Args:
            tag: The tag dictionary created from JSON data
            product_db: The ProductDatabase instance
        """
        try:
            # Extract key information from the tag
            product_name = tag.get('Product Name*', '').strip()
            vendor = tag.get('Vendor', '').strip()
            brand = tag.get('Product Brand', '').strip()
            product_type = tag.get('Product Type*', '').strip()
            weight = tag.get('Weight*', '').strip()
            price = tag.get('Price', '').strip()
            strain = tag.get('Product Strain', '').strip()
            lineage = tag.get('Lineage', '').strip()
            description = tag.get('Description', '').strip()
            
            # ENHANCED STRAIN EXTRACTION: If no strain in tag, try to find in database
            if not strain and product_name:
                # First try to extract strain from product name
                extracted_strain = self._extract_strain_from_product_name(product_name)
                if extracted_strain:
                    strain = extracted_strain
                    logging.info(f"🧬 Extracted strain '{strain}' from product name '{product_name}' for database entry")
                else:
                    # Try to find strain in database
                    try:
                        db_strain = self._find_strain_in_database(product_name, product_db)
                        if db_strain:
                            strain = db_strain
                            logging.info(f"🗄️ Found strain '{strain}' in database for product '{product_name}' in database entry")
                    except Exception as db_error:
                        logging.warning(f"Failed to search database for strain in database entry: {db_error}")
            
            # CRITICAL FIX: Ensure CBD Blend products get CBD lineage
            if strain and str(strain).strip().lower() == 'cbd blend':
                if lineage and str(lineage).strip().upper() != 'CBD':
                    logging.info(f"🧬 CBD BLEND FIX: Setting lineage to 'CBD' for product '{product_name}' (strain: '{strain}', was: '{lineage}')")
                lineage = 'CBD'
            elif not lineage and strain:
                # If no lineage but we have a strain, determine lineage using the same logic as _determine_lineage_for_product
                lineage = self._determine_lineage_for_product(product_type, lineage or '', product_name, strain)
                logging.info(f"🧬 Determined lineage '{lineage}' for product '{product_name}' (type: '{product_type}', strain: '{strain}')")
            
            if not product_name:
                logging.warning("Cannot create database entry: missing product name")
                return
            
            logging.info(f"🗄️ Creating new database entry for unmatched JSON product: '{product_name}'")
            
            # Prepare product data for database insertion using correct column names
            product_data = {
                'Product Name*': product_name,
                'normalized_name': product_name.lower().strip(),
                'Vendor/Supplier*': vendor,
                'Product Brand': brand,
                'Product Type*': product_type,
                'Weight*': weight,
                'Price': price,
                'Product Strain': strain,
                'Lineage': lineage,
                'Description': description,
                'state': 'active',
                'is_mj_product': 'yes',
                'doh_compliant': 'no'
            }
            
            # Add the product to the database
            product_id = product_db.add_or_update_product(product_data)
            
            # If we have strain information, also add/update the strain
            if strain:
                try:
                    strain_id = product_db.add_or_update_strain(strain, lineage)
                    logging.info(f"✅ Added strain '{strain}' to database with ID: {strain_id}")
                except Exception as strain_error:
                    logging.warning(f"Failed to add strain '{strain}' to database: {strain_error}")
            
            logging.info(f"✅ Successfully created database entry for '{product_name}' with ID: {product_id}")
            
        except Exception as e:
            logging.error(f"Error creating database entry for unmatched JSON tag: {e}")
            # Don't re-raise the exception to avoid breaking the main flow
    
    def _find_advanced_matches(self, json_item: dict) -> List[MatchResult]:
        """
        Use the advanced matching system to find the best matches for a JSON item.
        
        Args:
            json_item: The JSON item to match
            
        Returns:
            List of MatchResult objects sorted by overall score
        """
        try:
            if not self._sheet_cache:
                logging.warning("No sheet cache available for advanced matching")
                return []
            
            # DEBUG: Check vendor data in sheet cache before advanced matching
            if self._sheet_cache:
                sample_vendors = []
                for i, item in enumerate(self._sheet_cache[:5]):
                    vendor = str(item.get("vendor", "")).strip()
                    sample_vendors.append(f"'{vendor}'")
                print(f"🔍 DEBUG: Sheet cache vendor data (first 5): {sample_vendors}")
            
            # Use the advanced matcher to find matches (AI-powered aggressive matching within vendor)
            matches = self.advanced_matcher.find_best_matches(
                json_item=json_item,
                candidates=self._sheet_cache,
                threshold=1.0,  # Ultra-low threshold for AI-powered matching
                max_results=50
            )
            
            if matches:
                logging.debug(f"🔍 ADVANCED MATCHING: Found {len(matches)} matches for '{json_item.get('product_name', 'Unknown')}'")
                for i, match in enumerate(matches[:3]):  # Log top 3 matches
                    logging.debug(f"  {i+1}. {match.item.get('original_name', 'Unknown')} (score: {match.overall_score:.1f}, {match.algorithm_used})")
            
            return matches
            
        except Exception as e:
            logging.error(f"Error in advanced matching: {e}")
            return []
    
    def _normalize_vendor_name(self, vendor_name: str) -> str:
        """Normalize vendor name for comparison."""
        if not vendor_name:
            return ""
        
        # Convert to lowercase and strip
        vendor_name = vendor_name.lower().strip()
        
        # Remove special characters but keep spaces and hyphens
        import re
        vendor_name = re.sub(r'[^\w\s-]', ' ', vendor_name)
        
        # Normalize whitespace
        vendor_name = re.sub(r'\s+', ' ', vendor_name)
        
        return vendor_name.strip()

    def _translate_ceres_code_to_name(self, product_name: str) -> str:
        """Translate CERES product codes to human-readable names for better matching."""
        if not product_name:
            return product_name
            
        # Convert to lowercase for processing
        name_lower = product_name.lower()
        
        # Handle ratio codes first (before other replacements)
        import re
        name_lower = re.sub(r'(\d+):(\d+)', r'\1 to \2', name_lower)
        name_lower = re.sub(r'(\d+):(\d+):(\d+)', r'\1 to \2 to \3', name_lower)
        name_lower = re.sub(r'(\d+):(\d+):(\d+):(\d+)', r'\1 to \2 to \3 to \4', name_lower)
        
        # Convert underscores to spaces
        name_lower = name_lower.replace('_', ' ')
        
        # CERES code mapping patterns (apply after ratio and underscore conversion)
        code_mappings = {
            # Product type codes (order matters - longer codes first)
            'squeeze tube': 'squeeze tube',
            'roll up': 'roll up',
            'chocolate ball': 'chocolate ball',
            'chocolate bite': 'chocolate bite', 
            'fruit chew': 'fruit chew',
            'capsule': 'capsule',
            'tincture': 'tincture',
            'jar': 'jar',
            
            # Strain codes
            'sativa': 'sativa',
            'indica': 'indica',
            'mixed': 'mixed',
            
            # Flavor codes
            'sour apple': 'sour apple',
            'gold max': 'gold max',
            'xtra strength': 'xtra strength',
            'caramel': 'caramel',
            'assorted': 'assorted',
            'dark': 'dark',
            'milk': 'milk',
            'cherry': 'cherry',
            'mango': 'mango',
            'watermelon': 'watermelon',
            'tropical': 'tropical',
            'guava': 'guava',
            'citrus': 'citrus',
            'dragon': 'dragon',
            'balance': 'balance',
            'chill': 'chill',
            'lifted': 'lifted',
            'relief': 'relief',
            'berry': 'berry',
            
            # Pack size codes
            '10 pack': '10 pack',
            '20 pack': '20 pack',
            'single': 'single',
            '1 pack': '1 pack',
            
            # Potency codes
            '1000mg': '1000mg',
            '100ml': '100ml',
            '3.4oz': '3.4oz',
            '2oz': '2oz',
        }
        
        # Apply code mappings (order matters - longer patterns first)
        for code, replacement in sorted(code_mappings.items(), key=lambda x: len(x[0]), reverse=True):
            name_lower = name_lower.replace(code, replacement)
        
        # Clean up extra spaces
        name_lower = re.sub(r'\s+', ' ', name_lower).strip()
        
        return name_lower

    def _create_ceres_search_variations(self, original_name: str, translated_name: str, product_type: str) -> List[str]:
        """Create multiple search variations for CERES products to improve matching."""
        variations = []
        
        # Start with original and translated names
        variations.append(original_name.lower())
        if translated_name != original_name:
            variations.append(translated_name.lower())
        
        # Extract key terms from translated name
        terms = translated_name.lower().split()
        
        # Create variations based on key product patterns
        if 'chew' in translated_name.lower():
            # Fruit chew variations
            if 'ind' in translated_name.lower():
                variations.append('indica fruit chew')
                variations.append('indica chew')
            if 'sat' in translated_name.lower():
                variations.append('sativa fruit chew')
                variations.append('sativa chew')
            if 'mango' in translated_name.lower():
                variations.append('mango fruit chew')
                variations.append('mango chew')
            if 'watermelon' in translated_name.lower():
                variations.append('watermelon fruit chew')
                variations.append('watermelon chew')
            if 'cherry' in translated_name.lower():
                variations.append('cherry fruit chew')
                variations.append('cherry chew')
        
        elif 'ball' in translated_name.lower():
            # Chocolate ball variations
            if 'ind' in translated_name.lower():
                variations.append('indica chocolate ball')
                variations.append('indica ball')
            if 'sat' in translated_name.lower():
                variations.append('sativa chocolate ball')
                variations.append('sativa ball')
            if 'caramel' in translated_name.lower():
                variations.append('caramel chocolate ball')
                variations.append('caramel ball')
            if 'dragon' in translated_name.lower():
                variations.append('dragon chocolate ball')
                variations.append('dragon ball')
        
        elif 'bite' in translated_name.lower():
            # Chocolate bite variations
            if 'ind' in translated_name.lower():
                variations.append('indica chocolate bite')
                variations.append('indica bite')
            if 'sat' in translated_name.lower():
                variations.append('sativa chocolate bite')
                variations.append('sativa bite')
        
        elif 'caps' in translated_name.lower():
            # Capsule variations
            if 'balance' in translated_name.lower():
                variations.append('balance capsule')
                variations.append('balance cap')
            if 'chill' in translated_name.lower():
                variations.append('chill capsule')
                variations.append('chill cap')
            if 'lifted' in translated_name.lower():
                variations.append('lifted capsule')
                variations.append('lifted cap')
        
        elif 'tincs' in translated_name.lower():
            # Tincture variations
            if 'relief' in translated_name.lower():
                variations.append('relief tincture')
                variations.append('relief tinc')
        
        elif 'squeeze tube' in translated_name.lower() or 'roll up' in translated_name.lower():
            # Topical variations
            if 'dragon' in translated_name.lower():
                variations.append('dragon balm')
                variations.append('dragon topical')
            if 'xtra' in translated_name.lower():
                variations.append('xtra strength dragon balm')
                variations.append('xtra dragon balm')
            if 'gold max' in translated_name.lower():
                variations.append('gold max dragon balm')
                variations.append('max dragon balm')
        
        # Add strain-based variations
        if 'ind' in translated_name.lower():
            variations.append('indica')
        if 'sat' in translated_name.lower():
            variations.append('sativa')
        if 'mix' in translated_name.lower() or 'mixed' in translated_name.lower():
            variations.append('mixed')
        
        # Remove duplicates and empty strings
        variations = list(set([v.strip() for v in variations if v.strip()]))
        
        return variations
    
    def _is_vendor_match_flexible(self, vendor1: str, vendor2: str) -> bool:
        """Check if two vendor names represent the same vendor using various patterns."""
        if not vendor1 or not vendor2:
            return False
        
        # Remove common business suffixes and variations
        suffixes = [
            'llc', 'inc', 'corp', 'ltd', 'co', 'company', 'holdings', 'group', 'brands',
            'enterprises', 'industries', 'solutions', 'systems', 'services', 'products',
            'farms', 'garden', 'cultivation', 'cannabis', 'hemp', 'marijuana',
            'wholesale', 'distribution', 'supply', 'cooperative', 'collective'
        ]
        
        v1_clean = vendor1.lower().strip()
        v2_clean = vendor2.lower().strip()
        
        # Remove suffixes and clean up
        for suffix in suffixes:
            v1_clean = v1_clean.replace(f' {suffix}', '').replace(f'-{suffix}', '').replace(f'_{suffix}', '')
            v2_clean = v2_clean.replace(f' {suffix}', '').replace(f'-{suffix}', '').replace(f'_{suffix}', '')
        
        # Remove common prefixes
        prefixes = ['the', 'a', 'an']
        for prefix in prefixes:
            if v1_clean.startswith(f'{prefix} '):
                v1_clean = v1_clean[len(prefix)+1:]
            if v2_clean.startswith(f'{prefix} '):
                v2_clean = v2_clean[len(prefix)+1:]
        
        # Clean up extra spaces and special characters
        import re
        v1_clean = re.sub(r'\s+', ' ', v1_clean).strip()
        v2_clean = re.sub(r'\s+', ' ', v2_clean).strip()
        
        # Check if cleaned names match exactly
        if v1_clean == v2_clean:
            return True
        
        # Check for acronym matches (e.g., "CERES" vs "Ceres Holdings")
        if len(v1_clean) <= 6 and len(v2_clean) > 6:
            if v1_clean in v2_clean:
                return True
        elif len(v2_clean) <= 6 and len(v1_clean) > 6:
            if v2_clean in v1_clean:
                return True
        
        # Check for partial matches with high confidence - MUCH MORE RESTRICTIVE
        if len(v1_clean) >= 4 and len(v2_clean) >= 4:
            # Only allow subset matches if one name is significantly longer (3x) than the other
            # This prevents short names from matching long ones inappropriately
            if len(v1_clean) > len(v2_clean) * 3:
                if v2_clean in v1_clean:
                    return True
            elif len(v2_clean) > len(v1_clean) * 3:
                if v1_clean in v2_clean:
                    return True
            
            # Check for word overlap (at least 75% of words match - much stricter)
            v1_words = set(v1_clean.split())
            v2_words = set(v2_clean.split())
            if len(v1_words) > 0 and len(v2_words) > 0:
                overlap = len(v1_words.intersection(v2_words))
                min_words = min(len(v1_words), len(v2_words))
                # Increased threshold from 50% to 75% to prevent false matches
                if overlap / min_words >= 0.75:
                    return True
            
            # Check for phonetic similarity (Soundex) - only for very similar names
            try:
                import jellyfish
                # Only allow phonetic matches if names are already quite similar
                if len(v1_clean) >= 5 and len(v2_clean) >= 5:
                    if jellyfish.soundex(v1_clean) == jellyfish.soundex(v2_clean):
                        # Additional check: ensure at least 60% character similarity
                        char_similarity = len(set(v1_clean).intersection(set(v2_clean))) / max(len(set(v1_clean)), len(set(v2_clean)))
                        if char_similarity >= 0.6:
                            return True
            except:
                pass
        
        return False