"""
Preroll Tag Generator

This module handles the generation and grouping of preroll tags.
It groups preroll products by category and creates representative records for label generation.
"""

import re
import logging
import json
from typing import List, Dict, Any, Optional
from flask import session
from flask_caching import Cache
from src.core.constants import PREROLL_ALLOWED_BRANDS
import threading
import re

# Known preroll subbrands to surface as brands when present in product names
PREROLL_SUBBRAND_MAP = {
    'honey stixx': 'Honey Stixx',
    'honey stix': 'Honey Stixx',
    'sugar stix': 'Sugar Stix',
    'sugar stixx': 'Sugar Stixx',
    'flavour stix': 'Flavour Stix',
    'flavour stixx': 'Flavour Stix',
    'rosin rolls': 'Rosin Rolls',
    'bang stix': 'Bang Stix',
    'bloomers': 'Bloomers',
    'rose infused': 'Rose Infused',
    'sugar cone': 'Sugar Cone',
    'snickerdoobie': 'SnickerDoobie',
    'hash holes': 'Hash Holes',
    'hash infused': 'Hash Infused',
    'sparklers': 'Sparklers',
    'melt stix': 'Melt Stix',
    'blunts': 'Blunts',
    'bubble hash': 'Bubble Hash'
}


def _store_preroll_group_in_database(group_key: str, group_id: str, group_items: List[Dict], group_info: Dict):
    """Store preroll group data in database for persistence across site refreshes."""
    try:
        from app import get_product_database, get_current_store_name
        store_name = get_current_store_name()
        product_db = get_product_database(store_name)
        
        if not product_db:
            logging.warning("PREROLL DB: Product database not available")
            return
        
        conn = product_db._get_connection()
        if not conn:
            logging.warning("PREROLL DB: Could not get database connection")
            return
        
        cursor = conn.cursor()
        
        # Create preroll_groups table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preroll_groups (
                group_key TEXT PRIMARY KEY,
                group_id TEXT NOT NULL,
                group_items TEXT NOT NULL,
                group_info TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Store group data as JSON
        items_json = json.dumps(group_items)
        info_json = json.dumps(group_info)
        from datetime import datetime
        updated_at = datetime.now().isoformat()
        
        # Insert or replace (upsert)
        cursor.execute("""
            INSERT OR REPLACE INTO preroll_groups 
            (group_key, group_id, group_items, group_info, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (group_key, group_id, items_json, info_json, updated_at))
        
        conn.commit()
        logging.info(f"PREROLL DB: Stored group '{group_key}' in database")
        
    except Exception as e:
        logging.error(f"PREROLL DB: Error storing group in database: {e}")
        # Don't raise - allow cache to work as fallback


def _normalize_weight_display(weight: str) -> str:
    """Normalize a weight string to a canonical display form.

    Examples:
      '.5' -> '0.5'
      '0.6' -> '0.6'
      '1.0' -> '1'
      '5' -> '5'
    Preserves minimal decimals (up to 3) and removes trailing zeros.
    """
    if weight is None:
        return ''
    w = str(weight).strip()
    if not w:
        return ''
    # Remove commas and stray spaces
    w = w.replace(',', '').strip()
    # If it starts with a dot, add leading zero
    if w.startswith('.'):
        w = '0' + w
    try:
        wf = float(w)
    except Exception:
        # If parsing fails, return trimmed original (best-effort)
        return w
    # If it's an integer like 1.0 -> '1'
    if wf.is_integer():
        return str(int(wf))
    # Keep up to 3 decimal places, but strip trailing zeros
    s = ('{:.3f}'.format(wf)).rstrip('0').rstrip('.')
    # Ensure leading zero is present (edge-case)
    if s.startswith('.'):
        s = '0' + s
    return s


def _build_assorted_preroll_group(weight_display: str, count: str, is_infused: bool) -> Dict[str, str]:
    """Build group metadata for assorted preroll packs in a single place."""
    group_prefix = 'infused-' if is_infused else ''
    display_prefix = 'Assorted Infused Pre-Roll' if is_infused else 'Assorted Pre-Roll'
    return {
        'group_id': f'{group_prefix}{weight_display}g-{count}pack',
        'display_name': f'{display_prefix} - {weight_display}g x {count} Packs',
        'category': f'{display_prefix} - {weight_display}g x {count} Packs'
    }


def _get_preroll_group_from_database(group_key: str = None, group_id: str = None) -> tuple:
    """Retrieve preroll group data from database. Returns (group_items, group_info) or (None, None)."""
    try:
        from app import get_product_database, get_current_store_name
        store_name = get_current_store_name()
        product_db = get_product_database(store_name)
        
        if not product_db:
            return None, None
        
        conn = product_db._get_connection()
        if not conn:
            return None, None
        
        cursor = conn.cursor()
        
        # Try group_key first, then group_id
        if group_key:
            cursor.execute("SELECT group_items, group_info FROM preroll_groups WHERE group_key = ?", (group_key,))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0]), json.loads(result[1])
        
        if group_id:
            cursor.execute("SELECT group_items, group_info FROM preroll_groups WHERE group_id = ? LIMIT 1", (group_id,))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0]), json.loads(result[1])
        
        return None, None
        
    except Exception as e:
        logging.warning(f"PREROLL DB: Error retrieving group from database: {e}")
        return None, None


def identify_preroll_product_group(description: str, product_name: str = '') -> Dict[str, str]:
    """Identify product group category for preroll products (reusable function).
    
    Returns dict with 'group_id', 'display_name', 'category'
    """
    if not description:
        description = product_name
    
    desc_lower = str(description).lower()
    name_lower = str(product_name).lower()
    combined = f"{desc_lower} {name_lower}"
    is_infused = 'infused' in combined
    
    # Check for flavored blunts
    if 'flavored blunt' in combined or 'flavoured blunt' in combined:
        return {
            'group_id': 'blunts',
            'display_name': 'Assorted Blunts',
            'category': 'Flavored Blunts'
        }
    
    # Check for pack sizes (general pattern - check this BEFORE specific 1g x 5 check)
    # Pattern: "0.5g x 7 Pack", "1g x 5 Pack", ".5g x 2 Pack", etc.
    pack_match = re.search(r'(\d*\.?\d+)\s*g\s*x\s*(\d+)\s*pack', combined, re.IGNORECASE)
    if pack_match:
        weight = pack_match.group(1)
        count = pack_match.group(2)
        # Normalize weight display (handle .5g -> 0.5g, preserve leading zero)
        weight_display = _normalize_weight_display(weight)
        # Keep infused assorted packs explicitly labeled as infused and
        # grouped separately from non-infused assorted packs.
        return _build_assorted_preroll_group(weight_display, count, is_infused)
    
    # Check specifically for 1g x 5 packs (more specific, should be caught by above but keeping for safety)
    if re.search(r'1g\s*x\s*5\s*pack', combined, re.IGNORECASE) or '1g x 5 pack' in combined.lower() or '1 g x 5 pack' in combined.lower():
        # Ensure infused 1g x 5 assorted packs stay explicitly infused.
        return _build_assorted_preroll_group('1', '5', is_infused)
    
    # Check for infused prerolls with weight
    if 'infused' in combined and 'pre' in combined and 'roll' in combined:
        weight_match = re.search(r'(\d*\.?\d+)\s*g', combined)
        if weight_match:
            weight = weight_match.group(1)
            weight_display = _normalize_weight_display(weight)
            return {
                'group_id': f'infused-preroll-{weight_display}g',
                'display_name': f'Infused Pre-Roll - {weight_display}g',
                'category': f'Infused Pre-Roll - {weight_display}g'
            }
        else:
            return {
                'group_id': 'infused-preroll',
                'display_name': 'Infused Pre-Roll',
                'category': 'Infused Pre-Roll'
            }
    
    # Check for regular prerolls with weight
    if ('pre' in combined and 'roll' in combined) and 'infused' not in combined:
        weight_match = re.search(r'(\d*\.?\d+)\s*g', combined)
        if weight_match:
            weight = weight_match.group(1)
            weight_display = _normalize_weight_display(weight)
            return {
                'group_id': f'preroll-{weight_display}g',
                'display_name': f'Pre-Roll - {weight_display}g',
                'category': f'Pre-Roll - {weight_display}g'
            }
        # If no weight found but it's still a preroll, continue to pattern matching below
        # This ensures prerolls without weights still get grouped
    
    # Default: use truncated description pattern
    # CRITICAL FIX: Check for infused prerolls FIRST before regular prerolls
    preroll_patterns = [
        r'(.+?)(Infused\s+Pre[-‑ ]?Roll.*)',  # Infused prerolls first
        r'(.+?)(Pre[-‑ ]?Roll.*)',  # Regular prerolls second
    ]
    for pattern in preroll_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            universal_desc = match.group(2).strip().lower()
            # Create a safe group ID from the description
            group_id = re.sub(r'[^a-z0-9-]+', '-', universal_desc).strip('-')
            display_name = universal_desc.replace('pre-roll', 'Pre-Roll').replace('pre roll', 'Pre-Roll')
            # CRITICAL FIX: Ensure "infused" is capitalized and preserved in display name
            if 'infused' in universal_desc:
                display_name = display_name.replace('infused', 'Infused').title()
                # Ensure "Infused" appears before "Pre-Roll" in the display name
                if 'infused' in display_name.lower() and 'pre-roll' not in display_name:
                    display_name = display_name.replace('Infused', 'Infused Pre-Roll')
            else:
                display_name = display_name.title()
            return {
                'group_id': group_id[:50],  # Limit length
                'display_name': display_name,
                'category': universal_desc
            }
    
    # Fallback
    if is_infused:
        return {
            'group_id': 'infused-other',
            'display_name': 'Assorted Infused Pre-Rolls',
            'category': 'Infused Other'
        }

    return {
        'group_id': 'other',
        'display_name': 'Assorted Pre-Rolls',
        'category': 'Other'
    }


def generate_preroll_tags(records: List[Dict[str, Any]], cache: Cache) -> List[Dict[str, Any]]:
    """
    Generate preroll tags by grouping products by category.

    Args:
        records: List of product records to group
        cache: Flask cache instance for storing group data

    Returns:
        List of grouped representative records (one per category)
    """
    # DEBUG: Log brand values in input records
    if records:
        # Log all keys from first record to understand data structure
        logging.info(f"PREROLL INPUT DEBUG: First record keys ({len(records[0].keys())} total): {list(records[0].keys())}")
        for i, r in enumerate(records[:5]):
            brand_val = r.get('Product Brand', '') or r.get('ProductBrand', '') or r.get('Brand', '')
            vendor_val = r.get('Vendor/Supplier*', '') or r.get('Vendor', '')
            logging.info(f"PREROLL INPUT DEBUG [{i+1}]: Name='{r.get('Product Name*', 'N/A')}', Brand='{brand_val}', Vendor='{vendor_val}', ALL_BRAND_FIELDS: Product Brand={repr(r.get('Product Brand'))}, ProductBrand={repr(r.get('ProductBrand'))}, Brand={repr(r.get('Brand'))}")

    # Filter records by allowed brands if configured
    # CRITICAL FIX: Only filter if PREROLL_ALLOWED_BRANDS is not None and not empty
    # Prepare normalized allowed brand set once to avoid repeated work
    allowed_brands_lower = None
    if PREROLL_ALLOWED_BRANDS is not None and len(PREROLL_ALLOWED_BRANDS) > 0:
        original_count = len(records)
        # Normalize allowed brands to lowercase for case-insensitive matching
        allowed_brands_lower = {brand.lower().strip() for brand in PREROLL_ALLOWED_BRANDS if brand and str(brand).strip()}
        
        if not allowed_brands_lower:
            # If after normalization we have no valid brands, skip filtering
            logging.info(f"PREROLL BRAND FILTER: PREROLL_ALLOWED_BRANDS is set but contains no valid brands, skipping filter (allowing all brands)")
        else:
            filtered_records = []
            for record in records:
                # Get brand from various possible fields
                brand = (
                    record.get('Product Brand', '') or
                    record.get('ProductBrand', '') or
                    record.get('Brand', '') or
                    ''
                )
                brand_lower = str(brand).strip().lower()
                
                # Check if brand is in allowed list
                if brand_lower in allowed_brands_lower:
                    filtered_records.append(record)
                else:
                    logging.info(f"PREROLL BRAND FILTER: Excluding product '{record.get('Product Name*', 'Unknown')}' with brand '{brand}' (not in allowed brands: {PREROLL_ALLOWED_BRANDS})")
            
            records = filtered_records
            logging.info(f"PREROLL BRAND FILTER: Filtered {original_count} records to {len(records)} records matching allowed brands: {PREROLL_ALLOWED_BRANDS}")
    else:
        logging.info(f"PREROLL BRAND FILTER: PREROLL_ALLOWED_BRANDS is empty or None, allowing all brands (no filtering applied)")
    
    # NOTE: We'll populate session['preroll_original_records'] after grouping
    # so that the QR page references the full cached group items (not just
    # the possibly filtered input records). This prevents QR pages from
    # showing incomplete item lists when the incoming `records` were
    # pre-filtered by Product Type or other UI filters.
    
    # Step 1: Identify product groups and group records
    grouped_records = {}
    for record in records:
        description = record.get('Description', '')
        product_name = record.get('Product Name*', record.get('ProductName', ''))
        
        # CRITICAL: Ensure we have at least a product name to work with
        if not product_name or not str(product_name).strip():
            logging.warning(f"PREROLL GROUP: Skipping record with no product name: {record}")
            continue
        
        # Identify the product group
        group_info = identify_preroll_product_group(description, product_name)
        group_id = group_info['group_id']
        logging.debug(f"PREROLL GROUP: Product '{product_name}' -> Group: '{group_info['display_name']}' (group_id: {group_id})")
        
        # Extract brand from product name using "by BrandName -" pattern
        # This is used for grouping to avoid duplicates
        brand_for_grouping = ''
        product_name_str = str(product_name).strip()
        by_match = re.search(r'\sby\s+([^-]+?)(?:\s+-|$)', product_name_str, re.IGNORECASE)
        if by_match:
            brand_for_grouping = by_match.group(1).strip()

        # Fallback: prefer explicit Product Brand fields, then vendor as last resort
        if not brand_for_grouping:
            brand_field = (
                record.get('Product Brand', '') or
                record.get('ProductBrand', '') or
                record.get('Brand', '') or
                ''
            )
            if brand_field and str(brand_field).strip():
                brand_for_grouping = str(brand_field).strip()
            else:
                # Fall back to vendor for grouping purposes
                vendor = (
                    record.get('Vendor/Supplier*', '') or
                    record.get('Vendor', '') or
                    record.get('Vendor/Supplier', '') or
                    ''
                )
                brand_for_grouping = str(vendor).strip()

        # Group by category AND brand - each brand gets their own group
        # Normalize brand into a compact key to avoid duplicate groups caused
        # by minor whitespace/punctuation/casing differences.
        # We'll keep the original `brand_for_grouping` for display, but use
        # a normalized `brand_key` inside the group_key to ensure consistent grouping.
        brand_key = ''
        if brand_for_grouping:
            brand_for_grouping = str(brand_for_grouping).strip()
            # Normalize: lowercase, remove non-alphanumeric characters
            brand_key = re.sub(r'[^a-z0-9]+', '', brand_for_grouping.lower())
            if not brand_key:
                # Fallback to underscored short form
                brand_key = brand_for_grouping.lower().replace(' ', '_')

        if brand_key:
            group_key = f"{group_id}|{brand_key}"
        else:
            group_key = group_id
        
        if group_key not in grouped_records:
            grouped_records[group_key] = {
                'records': [],
                'group_info': group_info
            }
        grouped_records[group_key]['records'].append(record)
        logging.debug(f"PREROLL GROUP: Added product '{product_name}' to group '{group_key}' (brand/vendor: '{brand_for_grouping}', total in group: {len(grouped_records[group_key]['records'])})")
    
    # Log all groups created in Step 1 for debugging
    logging.info(f"PREROLL STEP 1 COMPLETE: Created {len(grouped_records)} groups from {len(records)} records")
    for gk, gd in grouped_records.items():
        logging.info(f"  GROUP: '{gk}' -> {len(gd['records'])} records, display_name='{gd['group_info'].get('display_name', 'N/A')}'")

    # Step 2: Create representative records with group display names
    unique_records = []
    session_id = session.get('session_id', 'default')

    for group_key, group_data in grouped_records.items():
        group_info = group_data['group_info']
        group_records_list = group_data['records']
        
        # Extract the original group_id from group_key (group_key may include vendor)
        # group_key format: "group_id" or "group_id|vendor"
        original_group_id = group_info['group_id']
        
        # Use the first record as representative
        representative = group_records_list[0].copy()
        
        # Update ALL fields that might be displayed on the label to show group display name
        group_display_name = group_info['display_name']
        representative['Description'] = group_display_name
        representative['Product Name*'] = group_display_name
        representative['ProductName'] = group_display_name
        # Also update DescAndWeight - use group name only (no individual product details)
        representative['DescAndWeight'] = group_display_name
        
        # CRITICAL FIX: Preserve Product Type* for infused prerolls to ensure filtering works correctly
        # Check if this is an infused preroll group and set Product Type* accordingly
        if 'infused' in group_display_name.lower() or original_group_id.startswith('infused-preroll'):
            representative['Product Type*'] = 'Infused Pre-Roll'
            representative['ProductType'] = 'infused pre-roll'
            logging.debug(f"PREROLL GROUP REP: Set Product Type* to 'Infused Pre-Roll' for infused preroll group '{group_display_name}'")
        else:
            # For regular prerolls, ensure Product Type* is set correctly
            if 'pre' in group_display_name.lower() and 'roll' in group_display_name.lower():
                representative['Product Type*'] = 'Pre-Roll'
                representative['ProductType'] = 'pre-roll'
                logging.debug(f"PREROLL GROUP REP: Set Product Type* to 'Pre-Roll' for regular preroll group '{group_display_name}'")
        
        # CRITICAL FIX: Preserve vendor information in the representative record
        # This ensures each vendor's label shows their vendor name
        # First try to get vendor from the representative record
        vendor = (
            representative.get('Vendor/Supplier*', '') or
            representative.get('Vendor', '') or
            representative.get('Vendor/Supplier', '') or
            ''
        )
        # If no vendor found in representative, extract from group_key (format: "group_id|vendor")
        if not vendor and '|' in group_key:
            vendor = group_key.split('|', 1)[1]
            logging.info(f"PREROLL GROUP REP: Extracted vendor '{vendor}' from group_key for '{group_display_name}'")
        # If still no vendor, search through all records in the group
        if not vendor:
            for r in group_records_list:
                v = (r.get('Vendor/Supplier*', '') or r.get('Vendor', '') or r.get('Vendor/Supplier', '') or '')
                if v and str(v).strip():
                    vendor = str(v).strip()
                    logging.info(f"PREROLL GROUP REP: Found vendor '{vendor}' from group record for '{group_display_name}'")
                    break
        # Set vendor on representative record to ensure it's passed to template processor
        if vendor:
            representative['Vendor/Supplier*'] = vendor
            representative['Vendor'] = vendor
            representative['ProductVendor'] = vendor
            logging.debug(f"PREROLL GROUP REP: Set vendor '{vendor}' on representative for '{group_display_name}'")
        else:
            logging.warning(f"PREROLL GROUP REP: No vendor found for group '{group_display_name}' (group_key: {group_key})")
        
        # Keep the price from the first record (or could average/use min/max - using first for now)
        original_price = representative.get('Price', '')
        # Ensure price is formatted correctly
        if original_price and str(original_price).strip():
            if not str(original_price).startswith('$'):
                try:
                    price_val = float(str(original_price).replace('$', '').replace(',', '').strip())
                    if price_val.is_integer():
                        representative['Price'] = f"${int(price_val)}"
                    else:
                        representative['Price'] = f"${price_val:.2f}".rstrip('0').rstrip('.')
                except:
                    representative['Price'] = f"${original_price}" if not str(original_price).startswith('$') else str(original_price)
        
        # Store group_id and group_info for QR code generation
        # Use the original group_id (without vendor) for cache keys to maintain compatibility
        representative['_group_id'] = original_group_id
        representative['_group_info'] = group_info
        # Store the full group_key (with vendor) for reference
        representative['_group_key'] = group_key

        # Ensure representative preserves a sensible Lineage value
        # Prefer proprietary/sovereign lineage fields first (owner-managed),
        # then fall back to canonical or generic Lineage fields.
        def _clean_lineage(val):
            if val is None:
                return ''
            # Remove soft-hyphen and non-breaking spaces which may be injected
            s = str(val)
            s = s.replace('\u00AD', '')
            s = s.replace('\u00A0', ' ')
            # Collapse multiple whitespace into single spaces and trim
            return ' '.join(s.split()).strip()

        rep_lineage = ''
        for r in group_records_list:
            candidate = (
                r.get('sovereign_lineage') or
                r.get('proprietary_lineage') or
                r.get('proprietaryLineage') or
                r.get('canonical_lineage') or
                r.get('Lineage') or
                r.get('lineage')
            )
            if candidate and str(candidate).strip() and str(candidate).strip().lower() not in ['none', 'nan', '']:
                rep_lineage = _clean_lineage(candidate)
                logging.info(f"PREROLL GROUP REP: Using lineage '{rep_lineage}' for group representative of '{group_display_name}'")
                break
        representative['Lineage'] = rep_lineage

        # Ensure representative preserves a sensible Brand value
        # PRIORITY 1: Extract brand from product name using "by BrandName -" pattern
        # This is the most reliable source since product names follow the pattern:
        # "Product Description by BrandName - Size"
        rep_brand = ''
        # PRIORITY 0: If the product name contains a known preroll subbrand, use that as the brand
        try:
            pn_check = (group_records_list[0].get('Product Name*') or group_records_list[0].get('ProductName') or '').lower()
            for sub, canonical in PREROLL_SUBBRAND_MAP.items():
                if sub in pn_check:
                    rep_brand = canonical
                    logging.info(f"PREROLL GROUP REP: Detected subbrand '{rep_brand}' in product name '{pn_check}', using as brand")
                    break
        except Exception:
            pass
        for r in group_records_list:
            product_name = r.get('Product Name*', '') or r.get('ProductName', '') or r.get('Description', '')
            if product_name:
                product_name_str = str(product_name).strip()
                # Pattern: "... by BrandName - ..." or "... by BrandName" (case insensitive)
                by_match = re.search(r'\sby\s+([^-]+?)(?:\s+-|$)', product_name_str, re.IGNORECASE)
                if by_match:
                    potential_brand = by_match.group(1).strip()
                    if potential_brand and potential_brand.lower() not in ['', 'none', 'nan']:
                        rep_brand = potential_brand
                        logging.info(f"PREROLL GROUP REP: Extracted brand '{rep_brand}' from product name '{product_name_str}' (by X - pattern)")
                        break

        # PRIORITY 2: Fall back to Product Brand field if extraction failed
        # Note: The Product Brand field often contains vendor names, so extraction is preferred
        if not rep_brand:
            default_brand = 'PREMIUM CANNABIS'
            for r in group_records_list:
                candidate = (
                    r.get('Product Brand') or
                    r.get('ProductBrand') or
                    r.get('Brand') or
                    r.get('brand')
                )
                if not candidate:
                    continue
                cand_str = str(candidate).strip()
                if not cand_str or cand_str.lower() in ['none', 'nan', 'premium cannabis']:
                    continue
                # Skip if it looks like a vendor (contains LLC, Inc, Co, etc.)
                if any(suffix in cand_str.upper() for suffix in ['LLC', ' INC', ' CO', 'CORP', 'COMPANY']):
                    logging.debug(f"PREROLL GROUP REP: Skipping vendor-like brand '{cand_str}' for '{group_display_name}'")
                    continue
                rep_brand = cand_str
                logging.info(f"PREROLL GROUP REP: Using Product Brand field '{rep_brand}' for '{group_display_name}'")
                break

        # PRIORITY 3: Final fallback - use vendor as brand if still nothing
        if not rep_brand:
            vendor_fallback = (
                representative.get('Vendor/Supplier*', '') or
                representative.get('Vendor', '') or
                representative.get('ProductVendor', '')
            )
            if vendor_fallback and str(vendor_fallback).strip():
                rep_brand = str(vendor_fallback).strip()
                logging.info(f"PREROLL GROUP REP: Using vendor '{rep_brand}' as brand fallback for '{group_display_name}'")

        if rep_brand:
            representative['Product Brand'] = rep_brand
            representative['ProductBrand'] = rep_brand
            representative['Brand'] = rep_brand
            logging.info(f"PREROLL GROUP REP: ✅ Set brand '{rep_brand}' on representative for '{group_display_name}'")
        else:
            # Log warning with details about what brands were found in records
            all_brands = []
            for i, r in enumerate(group_records_list[:5]):
                brand_val = r.get('Product Brand', '') or r.get('ProductBrand', '') or r.get('Brand', '') or r.get('brand', '')
                all_brands.append(f"[{i}]={repr(brand_val)}")
            logging.warning(f"PREROLL GROUP REP: ⚠️ NO BRAND found for '{group_display_name}'. Sample brand values: {', '.join(all_brands)}")
            logging.warning(f"PREROLL GROUP REP: ⚠️ Record keys available: {list(group_records_list[0].keys())[:20] if group_records_list else 'N/A'}")

        # Log final representative record summary for debugging
        final_brand = representative.get('Product Brand', '') or representative.get('ProductBrand', '')
        final_vendor = representative.get('Vendor/Supplier*', '') or representative.get('Vendor', '')
        logging.info(f"PREROLL GROUP REP FINAL: '{group_display_name}' -> Brand='{final_brand}', Vendor='{final_vendor}'")

        unique_records.append(representative)
        
        # Store items for this group in cache (for QR code page) - use ALL original records
        # But filter by allowed brands if configured
        group_items = []
        for record in group_records_list:
            # Filter by allowed brands if configured
            # CRITICAL FIX: Only filter if PREROLL_ALLOWED_BRANDS is not None and not empty
            if allowed_brands_lower:
                brand = (
                    record.get('Product Brand', '') or
                    record.get('ProductBrand', '') or
                    record.get('Brand', '') or
                    ''
                )
                brand_lower = str(brand).strip().lower()
                
                if brand_lower not in allowed_brands_lower:
                    logging.debug(f"PREROLL GROUP CACHE: Excluding product '{record.get('Product Name*', 'Unknown')}' with brand '{brand}' from cache (not in allowed brands)")
                    continue
            
            # Normalize DOH/DOH-compliant field so lists and QR views can display
            # a clean YES/NO status.
            doh_raw = record.get('DOH') or record.get('DOH Compliant (Yes/No)', '')
            doh_str = str(doh_raw).strip() if doh_raw is not None else ''
            doh_display = ''
            if doh_str:
                upper = doh_str.upper()
                if upper in ['YES', 'Y', 'TRUE', '1']:
                    doh_display = 'YES'
                elif upper in ['NO', 'N', 'FALSE', '0']:
                    doh_display = 'NO'
                else:
                    doh_display = doh_str

            # Clean lineage field for cached group items as well
            raw_lineage = record.get('Lineage', '')
            item = {
                'product_name': record.get('Product Name*', record.get('ProductName', '')),
                'description': record.get('Description', ''),
                'price': record.get('Price', ''),
                'weight': record.get('CombinedWeight', record.get('WeightUnits', '')),
                'vendor': record.get('Vendor', record.get('Vendor/Supplier*', '')),
                # Ensure brand is inferred if missing: prefer Product Brand, then parse product name, then vendor
                'brand': (
                    (record.get('Product Brand') or record.get('ProductBrand') or record.get('Brand') or '')
                    or (lambda pn: (re.search(r'\sby\s+([^-\n]+?)(?:\s+-|$)', pn, re.IGNORECASE).group(1).strip() if re.search(r'\sby\s+([^-\n]+?)(?:\s+-|$)', pn, re.IGNORECASE) else '') )(str(record.get('Product Name*', record.get('ProductName', ''))))
                    or (record.get('Vendor') or record.get('Vendor/Supplier*') or '')
                ),
                'strain': record.get('Product Strain', ''),
                'lineage': _clean_lineage(raw_lineage),
                'doh': doh_display,
            }
            group_items.append(item)
        logging.info(f"PREROLL GROUP: Storing {len(group_items)} items for group '{group_info.get('display_name', original_group_id)}' (group_id: {original_group_id}, vendor: {vendor})")
        
        # Store group items in cache using the full group_key (includes vendor) to avoid collisions
        # This ensures each vendor's products are stored separately even if they have the same category
        cache.set(f"preroll_group_{session_id}_{group_key}", group_items, timeout=86400)
        # CRITICAL FIX: Also store with session-independent key so QR codes work across sessions
        # Use group_key (with vendor) to ensure vendor-specific QR codes work correctly
        cache.set(f"preroll_group_latest_{group_key}", group_items, timeout=86400)
        # Also store with original group_id for backward compatibility (may overwrite, but that's OK for QR codes)
        cache.set(f"preroll_group_latest_{original_group_id}", group_items, timeout=86400)
        # Also store group info for display purposes
        cache.set(f"preroll_group_info_{session_id}_{group_key}", group_info, timeout=86400)
        cache.set(f"preroll_group_info_latest_{group_key}", group_info, timeout=86400)
        cache.set(f"preroll_group_info_latest_{original_group_id}", group_info, timeout=86400)
        
        # CRITICAL FIX: Store in database for persistence across site refreshes
        # Persist group to DB in background so web request isn't blocked by I/O
        try:
            threading.Thread(
                target=_store_preroll_group_in_database,
                args=(group_key, original_group_id, group_items, group_info),
                daemon=True
            ).start()
        except Exception as db_error:
            logging.warning(f"PREROLL: Failed to start background DB store (using cache only): {db_error}")
        
        logging.info(f"PREROLL: Stored {len(group_items)} items for group '{group_info.get('display_name', original_group_id)}' (group_key: {group_key}, group_id: {original_group_id}) with session-independent key and database")
    
    original_count = len(records)
    
    # Verify all records were grouped (every record should be in a group)
    total_grouped = sum(len(group_data['records']) for group_data in grouped_records.values())
    if total_grouped != original_count:
        logging.error(f"PREROLL GROUPING ERROR: {original_count} original records but only {total_grouped} were grouped. {original_count - total_grouped} products are MISSING!")
        # Log details about which records might be missing
        grouped_product_names = set()
        for group_data in grouped_records.values():
            for record in group_data['records']:
                product_name = record.get('Product Name*', record.get('ProductName', ''))
                if product_name:
                    grouped_product_names.add(str(product_name).strip())
        
        all_product_names = {record.get('Product Name*', record.get('ProductName', '')) for record in records if record.get('Product Name*') or record.get('ProductName')}
        missing_names = all_product_names - grouped_product_names
        if missing_names:
            logging.error(f"PREROLL GROUPING ERROR: Missing products: {list(missing_names)[:10]}")  # Log first 10 missing
    else:
        logging.info(f"PREROLL GROUPING: All {original_count} records successfully grouped into {len(grouped_records)} groups")
    
    # Deduplicate final grouped representatives by normalized display name AND vendor/group_key
    # CRITICAL FIX: Include _group_key in dedup key to preserve vendor-specific groups
    # Without this, "Assorted Pre-Roll - 0.5g x 7 Packs" from different vendors would collapse to just one
    deduped = []
    seen_keys = set()
    for rep in unique_records:
        pname = (rep.get('ProductName') or rep.get('Product Name*') or rep.get('Description') or '').strip()
        pname_key = re.sub(r'[^a-z0-9]+', '', pname.lower()) if pname else ''
        # CRITICAL: Include group_key (which contains vendor) in the dedup key
        group_key = rep.get('_group_key', '')
        dedup_key = f"{pname_key}|{group_key}"
        if dedup_key in seen_keys:
            logging.debug(f"PREROLL DEDUP: Skipping duplicate representative '{pname}' (group_key: {group_key})")
            continue
        seen_keys.add(dedup_key)
        deduped.append(rep)

    grouped_records_list = deduped
    logging.info(f"PREROLL DEDUP: {len(unique_records)} unique records -> {len(deduped)} after deduplication (by name+vendor)")
    logging.info(f"PREROLL GROUPING: Grouped {original_count} records into {len(grouped_records_list)} product groups (one label per vendor per category)")
    
    # Store group IDs in session for later retrieval when creating list document
    # Store both group_keys (with vendor) and original group_ids for compatibility
    group_keys = list(grouped_records.keys())
    group_ids = [group_info['group_id'] for group_info in [g['group_info'] for g in grouped_records.values()]]
    session['preroll_group_ids'] = group_ids  # Store original group_ids for backward compatibility
    session['preroll_group_keys'] = group_keys  # Store full group_keys (with vendor) for new functionality
    session['preroll_session_id'] = session_id
    session.modified = True
    
    # Build a merged, cache-backed original records list for the QR product list
    merged_originals = []
    seen = set()
    for group_key in group_keys:
        candidates = []
        # Prefer session-independent latest vendor-inclusive key
        ck = cache.get(f"preroll_group_latest_{group_key}")
        if ck:
            candidates = ck
        else:
            # Fallback to group_id-only latest key
            base_id = group_key.split('|')[0]
            ck2 = cache.get(f"preroll_group_latest_{base_id}")
            if ck2:
                candidates = ck2
            else:
                # Last fallback: session-scoped key
                ck3 = cache.get(f"preroll_group_{session_id}_{group_key}")
                if ck3:
                    candidates = ck3

        for item in candidates:
            name = (item.get('product_name') or '').strip()
            if not name:
                continue
            if name in seen:
                continue
            seen.add(name)
            merged_originals.append(item)

    # Persist merged originals for QR / product list generation
    session['preroll_original_records'] = merged_originals
    session.modified = True

    # Note: Group items are already stored in cache above during grouping
    logging.info(f"PREROLL: Generated {len(grouped_records_list)} grouped labels (one per vendor per product category)")

    return grouped_records_list
