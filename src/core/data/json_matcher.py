import logging
import os
import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .product_database import ProductDatabase

try:
    from fuzzywuzzy import fuzz
except Exception:  # pragma: no cover - fuzzywuzzy is optional
    fuzz = None


# ---------------------------------------------------------------------------
# Helper utilities that are used elsewhere in the project/tests
# ---------------------------------------------------------------------------

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
    lineage_map = {'SAT': 'sativa', 'IND': 'indica', 'HYB': 'hybrid'}
    product_map = {
        'BALL': 'ball',
        'BITE': 'bite',
        'CHEW': 'chew',
        'CAPS': 'capsule',
        'TINCS': 'tincture',
        'JAR': 'jar',
        'SQUEEZE': 'squeeze',
        'ROLL': 'roll',
    }
    
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
        'UPS': 'Roll Up',
    }
    
    # Lineage mapping
    lineage_map = {
        'SAT': 'Sativa',
        'IND': 'Indica',
        'HYB': 'Hybrid',
    }
    
    # Extract components
    product_type = parts[0]
    lineage = parts[1] if len(parts) > 1 else ''
    
    # Get human-readable product type
    readable_type = product_type_map.get(product_type, product_type.title())
    readable_lineage = lineage_map.get(lineage, lineage.title())
    
    # Get flavor/description parts (everything except last part which is usually size)
    flavor_parts: List[str] = []
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
    readable_parts: List[str] = []
    
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


# Type override lookup maintained for compatibility
TYPE_OVERRIDES = {
    "all-in-one": "Vape Cartridge",
    "rosin": "Solventless Concentrate",
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
    "battery": "Paraphernalia",
    "honey crystal": "Concentrate",
    "hash rosin": "Solventless Concentrate",
    "hash": "Solventless Concentrate",
    "diamonds": "Concentrate",
    "diamond": "Concentrate",
    "diamond caviar": "Concentrate",
    "tincture": "Tincture)",
    "capsules": "Capsule)",
}


CANNABINOID_TYPES = [
    "thc",
    "thca",
    "cbd",
    "cbda",
    "cbg",
    "cbga",
    "cbn",
    "cbna",
    "total-cannabinoids",
]


def map_inventory_type_to_product_type(
    inventory_type: Any,
    inventory_category: Optional[Any] = None,
    product_name: Optional[Any] = None,
) -> str:
    """
    Map JSON inventory types to product types.

    Kept largely compatible with the previous implementation so existing
    callers (including tests) continue to behave as expected.
    """
    if not inventory_type:
        return "Unknown"
    
    inventory_type_lower = str(inventory_type).lower().strip()
    inventory_category_lower = str(inventory_category).lower().strip() if inventory_category else ""
    product_name_lower = str(product_name).lower().strip() if product_name else ""
    
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
        "eye drops": "Eye Drops",
    }
    
    if inventory_type_lower in type_mappings:
        return type_mappings[inventory_type_lower]
    
    if "intermediate" in inventory_category_lower:
        if "concentrate" in inventory_type_lower or "extract" in inventory_type_lower:
            return "Vape Cartridge"
        if "flower" in inventory_type_lower:
            return "Flower"

    if inventory_type_lower.startswith("usable"):
        if product_name_lower:
            joint_keywords = ["pre-roll", "pre roll", "joint", "blunt", "cone"]
            if any(k in product_name_lower for k in joint_keywords):
                return "Pre-Roll"
            if any(k in product_name_lower for k in ["shake", "trim"]):
                return "Flower"
        return "Flower"
    
    # Product-name-based heuristics (kept simple but compatible)
    if product_name_lower:
        if any(k in product_name_lower for k in ["pre-roll", "pre roll", "joint", "blunt", "cone"]):
            return "Pre-Roll"
        if any(k in product_name_lower for k in ["cartridge", "cart", "vape", "510", "all-in-one", "aio", "disposable"]):
            return "Vape Cartridge"
        if any(k in product_name_lower for k in ["rosin", "resin", "wax", "shatter", "crumble", "sauce", "badder", "diamonds", "hash", "solventless", "distillate"]):
            return "Concentrate"
        if any(k in product_name_lower for k in ["gummy", "chew", "cookie", "brownie", "chocolate", "edible", "candy", "lozenge"]):
            return "Edible"
        if any(k in product_name_lower for k in ["tincture", "drops", "sublingual", "dropper"]):
            return "Tincture"
        if any(k in product_name_lower for k in ["topical", "lotion", "salve", "balm", "cream", "ointment"]):
            return "Topical"

    if any(k in inventory_type_lower for k in ["cartridge", "pen", "vape"]):
        return "Vape Cartridge"
    if any(k in inventory_type_lower for k in ["flower", "bud", "nug"]):
        return "Flower"
    if any(k in inventory_type_lower for k in ["edible", "gummy", "chocolate", "brownie", "cookie"]):
        return "Edible"
    if any(k in inventory_type_lower for k in ["tincture", "oil", "drops"]):
        return "Tincture"
    if any(k in inventory_type_lower for k in ["topical", "cream", "lotion", "salve"]):
        return "Topical"
    if any(k in inventory_type_lower for k in ["pre-roll", "joint", "cigar"]):
        return "Pre-Roll"
    
        return "Flower"


def extract_cannabinoids(lab_result_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced cannabinoid extraction with better parsing and validation."""
    result: Dict[str, Any] = {}
    if not lab_result_data:
        return result
    
    potency = lab_result_data.get("potency", [])
    if not isinstance(potency, list):
        potency = []
    
    cannabinoid_field_map = {
        "thc": "THC test result",
        "thca": "THCA test result",
        "cbd": "CBD test result",
        "cbda": "CBDA test result",
        "total-cannabinoids": "Total Cannabinoids",
        "cbg": "CBG",
        "cbn": "CBN",
        "cbga": "CBGA",
        "cbna": "CBNA",
    }
    
    for c in potency:
        if not isinstance(c, dict):
            continue
            
        ctype = str(c.get("type", "")).lower().strip()
        value = c.get("value")
        unit = str(c.get("unit", "")).lower().strip()
        
        if ctype in CANNABINOID_TYPES and value is not None:
            try:
                float_value = float(value)
                
                # Handle common per-mille and mg encodings
                if unit == "pct":
                    if float_value > 100:
                        float_value = float_value / 10.0
                elif unit in {"mg", "mille"} and float_value > 1000:
                        float_value = float_value / 10.0
                
                db_field_name = cannabinoid_field_map.get(ctype, ctype)
                rounded = round(float_value, 1)
                result[db_field_name] = rounded
                result[ctype] = rounded
            except (ValueError, TypeError):
                logging.warning(f"Invalid cannabinoid value: {value} for type {ctype}")
                continue
    
    # Pass through selected metadata fields
    for meta_key in [
        "coa",
        "lab_result_status",
        "lab_result_id",
        "coa_release_date",
        "coa_expire_date",
    ]:
        if meta_key in lab_result_data:
            result[meta_key] = lab_result_data[meta_key]
    
    return result


# ---------------------------------------------------------------------------
# New, simplified description-based JSON matcher
# ---------------------------------------------------------------------------

class JSONMatcher:
    """
    Simplified JSON matcher.

    New behavior:
      - Fetch JSON from the given URL.
      - For each JSON item, extract a description string.
      - Build a candidate index from the product database and current Excel sheet.
      - Use fuzzy text similarity between the JSON description and candidate
        product name/vendor text to find the closest match.
      - Return product dicts that are compatible with the existing tag
        generation pipeline (keys like 'Product Name*', 'Vendor/Supplier*', etc.).
    """
    
    def __init__(self, excel_processor):
        self.excel_processor = excel_processor
        self._candidate_index: Optional[List[Dict[str, Any]]] = None
        self.json_matched_names: Optional[List[str]] = None
        self.json_matched_tags: Optional[List[Dict[str, Any]]] = None

    # ---- Candidate index -------------------------------------------------

    def _get_product_database(self) -> Optional[ProductDatabase]:
        """
        Lightweight ProductDatabase initializer.

        We keep this intentionally simple: prefer an explicit DEFAULT_STORE_NAME
        if provided, otherwise fall back to 'AGT_Bothell'.
        """
        try:
            store_name = (
                os.environ.get("DEFAULT_JSON_MATCH_STORE")
                or os.environ.get("DEFAULT_STORE_NAME")
                or os.environ.get("DEFAULT_STORE")
                or "AGT_Bothell"
            )
            db = ProductDatabase(store_name=store_name)
            db.init_database()
            return db
        except Exception as e:
            logging.warning(
                f"Unable to initialize ProductDatabase for JSON matching: {e}"
            )
            return None

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = str(text or "").lower()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _normalize_vendor(text: str) -> str:
        """
        Normalize vendor strings so JSON vendor hints can be matched against
        Excel/DB vendors. This is intentionally simple but consistent.
        """
        if not text:
            return ""
        # Lowercase, strip punctuation, and drop common business suffixes
        t = JSONMatcher._normalize_text(text)
        for suffix in [" llc", " inc", " incorporated", " ltd", " co", " company"]:
            if t.endswith(suffix):
                t = t[: -len(suffix)]
        return t.strip()

    def _build_candidate_index(self) -> None:
        """
        Build an in-memory list of candidate products from Excel + database.
        """
        if self._candidate_index is not None:
            return

        candidates: List[Dict[str, Any]] = []

        # Excel candidates
        try:
            df: Optional[pd.DataFrame] = getattr(self.excel_processor, "df", None)
        except Exception:
            df = None

        if df is not None is not False and isinstance(df, pd.DataFrame) and not df.empty:
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                name = (
                    row_dict.get("Product Name*")
                    or row_dict.get("ProductName")
                    or row_dict.get("Description")
                    or ""
                )
                if not name:
                    continue
                vendor = row_dict.get("Vendor/Supplier*") or row_dict.get("Vendor") or ""
                vendor_norm = self._normalize_vendor(vendor)
                text = self._normalize_text(f"{name} {vendor}")
                candidates.append(
                    {
                        "source": "excel",
                        "text": text,
                        "row": row_dict,
                        "vendor_norm": vendor_norm,
                    }
                )

        # Database candidates (skip on PythonAnywhere for performance)
        is_pythonanywhere = bool(
            os.environ.get("PYTHONANYWHERE_DOMAIN") or os.environ.get("PYTHONANYWHERE_SITE")
        )
        if not is_pythonanywhere:
            product_db = self._get_product_database()
            if product_db is not None:
                try:
                    conn = product_db._get_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM products')
                    columns = [c[0] for c in cursor.description]
                    for row in cursor.fetchall():
                        row_dict = dict(zip(columns, row))
                        name = (
                            row_dict.get("Product Name*")
                            or row_dict.get("ProductName")
                            or row_dict.get("product_name")
                            or ""
                        )
                        if not name:
                            continue
                        vendor = row_dict.get("Vendor/Supplier*") or row_dict.get("Vendor") or ""
                        vendor_norm = self._normalize_vendor(vendor)
                        text = self._normalize_text(f"{name} {vendor}")
                        candidates.append(
                            {
                                "source": "database",
                                "text": text,
                                "row": row_dict,
                                "vendor_norm": vendor_norm,
                            }
                        )
                except Exception as e:
                    logging.warning(f"Failed to build database candidate index: {e}")

        self._candidate_index = candidates
        logging.info(f"JSONMatcher candidate index built with {len(candidates)} products")

    # ---- Matching core ---------------------------------------------------

    def _similarity(self, a: str, b: str) -> int:
        if fuzz is not None:
            return int(fuzz.token_set_ratio(a, b))
        return int(SequenceMatcher(None, a, b).ratio() * 100)

    def _match_description(self, description: str, vendor_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not description:
            return None
        if self._candidate_index is None:
            self._build_candidate_index()
        if not self._candidate_index:
            return None

        desc_norm = self._normalize_text(description)
        if not desc_norm:
            return None

        # If we have a vendor hint from the JSON, restrict candidates to that vendor
        vendor_norm_hint = self._normalize_vendor(vendor_hint) if vendor_hint else ""
        candidates = self._candidate_index
        if vendor_norm_hint:
            restricted = [
                c
                for c in self._candidate_index
                if c.get("vendor_norm")
                and (
                    vendor_norm_hint in c["vendor_norm"]
                    or c["vendor_norm"] in vendor_norm_hint
                )
            ]
            # If we found any vendor-aligned candidates, only search within those
            if restricted:
                candidates = restricted

        best: Optional[Dict[str, Any]] = None
        best_score = 0
        for cand in candidates:
            score = self._similarity(desc_norm, cand["text"])
            if score > best_score:
                best_score = score
                best = cand

        # Require at least a modest similarity
        if not best or best_score < 50:
            return None

        matched = dict(best["row"])
        matched.setdefault("Source", "JSON Match")
        matched["json_match_score"] = best_score
        return matched

    @staticmethod
    def _extract_description_from_item(item: Dict[str, Any]) -> str:
        for key in [
            "description",
            "Description",
            "product_name",
            "ProductName",
            "displayName",
            "name",
        ]:
            value = item.get(key)
            if value:
                return str(value)
        # If none of the known keys are present, return empty string
        return ""
            
    @staticmethod
    def _extract_vendor_from_item(item: Dict[str, Any]) -> str:
        """Best-effort vendor extraction from a JSON inventory item."""
        for key in [
            "vendor",
            "Vendor",
            "vendor_name",
            "supplier",
            "supplier_name",
            "from_license_name",
            "license_name",
            "brand",
        ]:
            value = item.get(key)
            if value:
                return str(value)
        # If none of the known keys are present, return empty string
        return ""
    
    @staticmethod
    def _extract_field_from_json_item(item: Dict[str, Any], canonical_field: str) -> Optional[Any]:
        """Extract a field value from JSON item using comprehensive field mapping."""
        # Field mapping from JSON keys to canonical field names
        field_map = {
            "Product Name*": ["product_name", "ProductName", "name", "displayName", "description", "Description"],
            "Vendor/Supplier*": ["vendor", "Vendor", "vendor_name", "supplier", "supplier_name", "from_license_name", "license_name"],
            "Product Brand": ["brand", "Brand", "brand_name"],
            "Price": ["price", "Price", "line_price", "unit_price", "retail_price"],
            "Weight*": ["weight", "Weight", "unit_weight", "net_weight", "package_weight"],
            "Units": ["units", "Units", "unit_weight_uom", "uom", "weight_unit"],
            "Product Strain": ["strain", "Strain", "strain_name", "strain_type"],
            "Product Type*": ["product_type", "ProductType", "inventory_type", "type"],
            "Lineage": ["lineage", "Lineage", "strain_lineage"],
            "Quantity*": ["quantity", "Quantity", "qty", "Qty"],
            "THC test result": ["thc_percentage", "thc", "THC", "thc_pct"],
            "CBD test result": ["cbd_percentage", "cbd", "CBD", "cbd_pct"],
        }
        
        # Get list of JSON keys to check for this canonical field
        json_keys = field_map.get(canonical_field, [])
        
        # Try each JSON key
        for json_key in json_keys:
            value = item.get(json_key)
            if value is not None and value != "":
                return value
        
        return None
    
    @staticmethod
    def _enrich_matched_product(matched: Dict[str, Any], json_item: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich matched product with missing fields from JSON item."""
        # Fields to enrich if missing from matched product
        fields_to_enrich = [
            "Price",
            "Weight*",
            "Units",
            "Product Brand",
            "Product Strain",
            "Lineage",
            "Quantity*",
            "THC test result",
            "CBD test result",
        ]
        
        enriched = dict(matched)  # Copy matched product
        
        for field in fields_to_enrich:
            # Only enrich if field is missing or empty in matched product
            current_value = enriched.get(field)
            if not current_value or (isinstance(current_value, str) and current_value.strip() == ""):
                json_value = JSONMatcher._extract_field_from_json_item(json_item, field)
                if json_value is not None:
                    # Format weight properly (combine weight and units)
                    if field == "Weight*":
                        units = JSONMatcher._extract_field_from_json_item(json_item, "Units")
                        if units:
                            # Format as "weightunits" (no space per user preference)
                            weight_str = str(json_value).strip()
                            # Remove .0 from whole numbers (e.g., 1.0 -> 1)
                            if weight_str.endswith('.0'):
                                weight_str = weight_str[:-2]
                            enriched[field] = f"{weight_str}{units}"
                            if "Units" not in enriched or not enriched.get("Units"):
                                enriched["Units"] = str(units).strip()
                        else:
                            weight_str = str(json_value).strip()
                            if weight_str.endswith('.0'):
                                weight_str = weight_str[:-2]
                            enriched[field] = weight_str
                    elif field in ["THC test result", "CBD test result"]:
                        # Handle percentage values - round to 1 decimal place
                        try:
                            pct_value = float(json_value)
                            enriched[field] = round(pct_value, 1)
                        except (ValueError, TypeError):
                            enriched[field] = str(json_value)
                    elif field == "Price":
                        # Format price - remove .00 for whole numbers
                        try:
                            price_value = float(json_value)
                            if price_value == int(price_value):
                                enriched[field] = str(int(price_value))
                            else:
                                enriched[field] = f"{price_value:.2f}"
                        except (ValueError, TypeError):
                            enriched[field] = str(json_value)
                    else:
                        enriched[field] = str(json_value)
                    logging.debug(f"Enriched {field} from JSON: {enriched[field]}")
        
        # Also check for lab result data in JSON item
        lab_result_data = json_item.get("lab_result_data") or json_item.get("lab_results") or json_item.get("potency")
        if lab_result_data:
            cannabinoids = extract_cannabinoids(lab_result_data)
            for key, value in cannabinoids.items():
                # Only add if not already present or empty
                if key not in enriched or not enriched.get(key):
                    enriched[key] = value
                    logging.debug(f"Enriched {key} from JSON lab results: {value}")
        
        return enriched
    
    # ---- Public API used by Flask app ------------------------------------

    def _fetch_items_from_url(self, url: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        import requests
        
        if not url.lower().startswith("http"):
            raise ValueError("Please provide a valid HTTP URL")
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }

        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            payload = response.json()
        except Exception as e:
            logging.error(f"Failed to fetch JSON from {url}: {e}")
            return [], None

        global_vendor: Optional[str] = None
        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            # Common Cultivera-style payload
            items = payload.get("inventory_transfer_items") or payload.get("items") or []
            # Many vendor-specific JSON feeds include a top-level license/vendor name
            global_vendor = (
                payload.get("from_license_name")
                or payload.get("vendor")
                or payload.get("license_name")
            )
        else:
            items = []

        clean_items = [i for i in items if isinstance(i, dict)]
        return clean_items, global_vendor

    def fetch_and_match_with_product_db(
        self,
        url: str,
        force_simplified: bool = False,
        deduplicate: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Main entrypoint used by the Flask app.

        The previous implementation had multiple strategies and AI layers; this
        new version focuses solely on description-based fuzzy matching against
        Excel + database products.
        """
        items, global_vendor = self._fetch_items_from_url(url)
        if not items:
            return []
            
        matched_products: List[Dict[str, Any]] = []
        matched_names: List[str] = []

        for item in items:
            description = self._extract_description_from_item(item)
            # Prefer per-item vendor, fall back to any global vendor from the payload
            vendor_hint = self._extract_vendor_from_item(item) or global_vendor
            matched = self._match_description(description, vendor_hint=vendor_hint)
            if not matched:
                continue
            
            # Enrich matched product with missing fields from JSON item
            matched = self._enrich_matched_product(matched, item)
            
            # Attach raw JSON context for debugging only; do not overwrite database/Excel
            # description fields so the final tags use canonical names/descriptions.
            matched.setdefault("json_raw", item)

            name = str(
                matched.get("Product Name*")
                or matched.get("ProductName")
                or matched.get("Description")
                or matched.get("product_name")
                or ""
            ).strip()

            matched_products.append(matched)
            if name:
                matched_names.append(name)

        # Optionally deduplicate by (Product Name*, Vendor/Supplier*)
        if deduplicate and matched_products:
            seen_keys = set()
            unique_products: List[Dict[str, Any]] = []
            for p in matched_products:
                key = (
                    str(p.get("Product Name*") or p.get("ProductName") or "").strip().lower(),
                    str(p.get("Vendor/Supplier*") or p.get("Vendor") or "").strip().lower(),
                )
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                unique_products.append(p)
            matched_products = unique_products

        self.json_matched_tags = matched_products
        self.json_matched_names = matched_names

        return matched_products

    # Legacy compatibility: simplified matcher just calls the same logic
    def fetch_and_match(self, url: str, deduplicate: bool = False) -> List[Dict[str, Any]]:
        return self.fetch_and_match_with_product_db(url, force_simplified=True, deduplicate=deduplicate)

    def process_json_inventory(self, url: str):
        """
        Legacy endpoint helper: just return the raw JSON as a DataFrame if possible.
        """
        items, _ = self._fetch_items_from_url(url)
        if not items:
            return pd.DataFrame()
        try:
            return pd.DataFrame(items)
        except Exception:
            return items

    def get_sheet_cache_status(self) -> Dict[str, Any]:
        """
        Kept for compatibility with debug endpoints.
        """
        count = len(self._candidate_index) if self._candidate_index is not None else 0
        return {
            "candidate_index_built": self._candidate_index is not None,
            "candidate_count": count,
        }

    def get_matched_names(self) -> Optional[List[str]]:
        return self.json_matched_names

    def get_matched_tags(self) -> Optional[List[Dict[str, Any]]]:
        return self.json_matched_tags

    def clear_matches(self) -> None:
        self.json_matched_names = None
        self.json_matched_tags = None

    # The old implementation had a complex upgrade step; for now this is a no-op
    def _upgrade_fallback_products(
        self,
        products: Optional[List[Dict[str, Any]]],
        *_,
        **__,
    ) -> List[Dict[str, Any]]:
        return products or []


