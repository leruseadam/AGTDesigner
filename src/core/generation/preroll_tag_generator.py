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
# Precompiled regexes to improve performance (avoid repeated compilation in loops)
# Matches pack patterns like "0.5g x 7 Pack", "1g x 5 Pack", etc.
PACK_RE = re.compile(r"(\d+(?:\.\d+)?)\s*g\s*x\s*(\d+)\s*pack", re.IGNORECASE)
# Matches "by BrandName -" pattern used to extract brand
BY_PATTERN = re.compile(r"\sby\s+([^-]+?)(?:\s+-|$)", re.IGNORECASE)
# Matches weight like "1g" or "0.5g"
WEIGHT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*g", re.IGNORECASE)
# Preroll universal patterns (compiled)
PREROLL_PATTERN_COMPILED = [
    re.compile(r'(.+?)(Infused\s+Pre[-‑ ]?Roll.*)', re.IGNORECASE),
    re.compile(r'(.+?)(Pre[-‑ ]?Roll.*)', re.IGNORECASE),
]
# Non-alphanumeric for normalization
NON_ALNUM_RE = re.compile(r'[^a-z0-9-]+')
import threading
import os
import time


def _store_preroll_groups_batch(groups_data: List[tuple]):
    """Store multiple preroll groups in database in a single batch operation.
    
    Args:
        groups_data: List of tuples (group_key, group_id, group_items, group_info)
    """
    if not groups_data:
        return
    
    try:
        from app import get_product_database, get_current_store_name
        store_name = get_current_store_name()
        product_db = get_product_database(store_name)
        
        if not product_db:
            return  # Silently skip if DB not available
        
        conn = product_db._get_connection()
        if not conn:
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
        
        # Prepare batch data
        from datetime import datetime
        updated_at = datetime.now().isoformat()
        batch_values = []
        for group_key, group_id, group_items, group_info in groups_data:
            items_json = json.dumps(group_items)
            info_json = json.dumps(group_info)
            batch_values.append((group_key, group_id, items_json, info_json, updated_at))
        
        # Batch insert/update (much faster than individual writes)
        cursor.executemany("""
            INSERT OR REPLACE INTO preroll_groups 
            (group_key, group_id, group_items, group_info, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, batch_values)
        
        conn.commit()
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug(f"PREROLL DB: Stored {len(batch_values)} groups")
        
    except Exception as e:
        logging.warning(f"PREROLL DB: Error batch storing groups: {e}")
        # Don't raise - allow cache to work as fallback


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
    
    # Check for flavored blunts
    if 'flavored blunt' in combined or 'flavoured blunt' in combined:
        return {
            'group_id': 'blunts',
            'display_name': 'Assorted Blunts',
            'category': 'Flavored Blunts'
        }
    
    # Check for pack sizes (general pattern - check this BEFORE specific 1g x 5 check)
    # Pattern: "0.5g x 7 Pack", "1g x 5 Pack", ".5g x 2 Pack", etc.
    pack_match = PACK_RE.search(combined)
    if pack_match:
        weight = pack_match.group(1)
        count = pack_match.group(2)
        # Normalize weight display (handle .5g -> 0.5g, but keep 0.5g as 0.5g)
        if weight.startswith('.'):
            # ".5" -> "0.5"
            weight_display = '0' + weight
        else:
            # "0.5" stays "0.5", "1" stays "1"
            weight_display = weight
        # Include the word "Pre-Roll" in the display name so grouped
        # pack labels clearly indicate they are prerolls.
        return {
            'group_id': f'{weight}g-{count}pack',
            'display_name': f'Assorted Pre-Roll - {weight_display}g x {count} Packs',
            'category': f'{weight_display}g x {count} Packs'
        }
    
    # Check specifically for 1g x 5 packs (more specific, should be caught by above but keeping for safety)
    if re.search(r'1g\s*x\s*5\s*pack', combined, re.IGNORECASE) or '1g x 5 pack' in combined.lower() or '1 g x 5 pack' in combined.lower():
        # Ensure the specific 1g x 5 pack group also includes "Pre-Roll"
        return {
            'group_id': '5packs',
            'display_name': 'Assorted Pre-Roll - 1g x 5 Packs',
            'category': '1g x 5 Packs'
        }
    
    # Check for infused prerolls with weight
    if 'infused' in combined and 'pre' in combined and 'roll' in combined:
        weight_match = WEIGHT_RE.search(combined)
        if weight_match:
            weight = weight_match.group(1)
            return {
                'group_id': f'infused-preroll-{weight}g',
                'display_name': f'Infused Pre-Roll - {weight}g',
                'category': f'Infused Pre-Roll - {weight}g'
            }
        else:
            return {
                'group_id': 'infused-preroll',
                'display_name': 'Infused Pre-Roll',
                'category': 'Infused Pre-Roll'
            }
    
    # Check for regular prerolls with weight
    if ('pre' in combined and 'roll' in combined) and 'infused' not in combined:
        weight_match = WEIGHT_RE.search(combined)
        if weight_match:
            weight = weight_match.group(1)
            return {
                'group_id': f'preroll-{weight}g',
                'display_name': f'Pre-Roll - {weight}g',
                'category': f'Pre-Roll - {weight}g'
            }
        # If no weight found but it's still a preroll, continue to pattern matching below
        # This ensures prerolls without weights still get grouped
    
    # Default: use truncated description pattern
    # CRITICAL FIX: Check for infused prerolls FIRST before regular prerolls
    for pattern in PREROLL_PATTERN_COMPILED:
        match = pattern.search(description)
        if match:
            universal_desc = match.group(2).strip().lower()
            # Create a safe group ID from the description
            group_id = NON_ALNUM_RE.sub('-', universal_desc).strip('-')
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
    start_t = time.time()

    # CRITICAL: Track original count BEFORE any filtering
    original_input_count = len(records)
    # ALWAYS log input count at INFO level for debugging
    logging.info(f"PREROLL INPUT: Received {original_input_count} records for grouping")
    
    # Log sample product names and vendors to verify input
    if records:
        sample_names = [r.get('Product Name*', r.get('ProductName', 'N/A')) for r in records[:5]]
        sample_vendors = [r.get('Vendor/Supplier*', r.get('Vendor', 'N/A')) for r in records[:5]]
        logging.info(f"PREROLL INPUT SAMPLE: First 5 products - Names: {sample_names}")
        logging.info(f"PREROLL INPUT SAMPLE: First 5 products - Vendors: {sample_vendors}")
    # DEBUG: Log PREROLL_ALLOWED_BRANDS status (only if filtering is active)
    if PREROLL_ALLOWED_BRANDS is not None and len(PREROLL_ALLOWED_BRANDS) > 0:
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug(f"PREROLL BRAND FILTER: PREROLL_ALLOWED_BRANDS is set to: {PREROLL_ALLOWED_BRANDS}")

    # If environment requests preserve-all, skip grouping and return records unchanged
    if os.getenv('PREROLL_PRESERVE_ALL', '').lower() in ['1', 'true', 'yes']:
        logging.info(f"PREROLL: PREROLL_PRESERVE_ALL set - skipping grouping and returning all {len(records)} records")
        return records

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
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug(f"PREROLL: BRAND FILTER skipped (no valid brands)")
        else:
            filtered_records = []
            for record in records:
                # CRITICAL FIX: Use same brand extraction logic as grouping
                # This ensures products with brands in product names are included
                # even if Product Brand field is empty
                brand = ''
                product_name = record.get('Product Name*', record.get('ProductName', ''))
                
                # PRIORITY 1: Extract brand from product name using "by BrandName -" pattern
                if product_name:
                    product_name_str = str(product_name).strip()
                    by_match = BY_PATTERN.search(product_name_str)
                    if by_match:
                        brand = by_match.group(1).strip()
                
                # PRIORITY 2: Fall back to explicit Product Brand fields
                if not brand:
                    brand = (
                        record.get('Product Brand', '') or
                        record.get('ProductBrand', '') or
                        record.get('Brand', '') or
                        ''
                    )
                    brand = str(brand).strip()
                
                # PRIORITY 3: Fall back to vendor if still no brand
                if not brand:
                    vendor = (
                        record.get('Vendor/Supplier*', '') or
                        record.get('Vendor', '') or
                        record.get('Vendor/Supplier', '') or
                        ''
                    )
                    brand = str(vendor).strip()
                
                brand_lower = brand.lower() if brand else ''
                
                # Check if brand is in allowed list
                if brand_lower in allowed_brands_lower:
                    filtered_records.append(record)
                elif logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug(f"PREROLL BRAND FILTER: Excluding product '{product_name}' with brand '{brand}'")
            
            records = filtered_records
            excluded = original_count - len(records)
            sample_kept = [r.get('Product Name*', r.get('ProductName', '')) for r in records[:5]]
            logging.info(f"PREROLL BRAND FILTER: Filtered {original_count} -> {len(records)} records (excluded {excluded})")
    # Skip logging when no filter is applied (common case)
    
    # NOTE: We'll populate session['preroll_original_records'] after grouping
    # so that the QR page references the full cached group items (not just
    # the possibly filtered input records). This prevents QR pages from
    # showing incomplete item lists when the incoming `records` were
    # pre-filtered by Product Type or other UI filters.
    
    # Step 1: Identify product groups and group records
    grouped_records = {}
    skipped_count = 0
    for record in records:
        description = record.get('Description', '')
        product_name = record.get('Product Name*', record.get('ProductName', ''))
        
        # CRITICAL: Ensure we have at least a product name to work with
        if not product_name or not str(product_name).strip():
            skipped_count += 1
            continue
        
        # Identify the product group
        group_info = identify_preroll_product_group(description, product_name)
        group_id = group_info['group_id']
        
        # Extract brand from product name using "by BrandName -" pattern
        # This is used for grouping to avoid duplicates
        brand_for_grouping = ''
        product_name_str = str(product_name).strip()
        by_match = BY_PATTERN.search(product_name_str)
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

        # Group by category AND brand/vendor - each brand/vendor gets their own group
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
        
        # REVERT TO ORIGINAL: group_id|brand_key only (one per category per vendor = ~56 groups)
        # This is how it "used to work fine" - product hash caused 322 groups and downstream issues
        key_parts = [group_id]
        if brand_key:
            key_parts.append(brand_key)
        else:
            vendor = (
                record.get('Vendor/Supplier*', '') or
                record.get('Vendor', '') or
                record.get('Vendor/Supplier', '') or
                ''
            )
            if vendor:
                vendor_key = re.sub(r'[^a-z0-9]+', '', str(vendor).strip().lower())
                if vendor_key:
                    key_parts.append(vendor_key)
        
        group_key = '|'.join(key_parts)
        if '|' not in group_key:
            group_key = f"{group_id}|unknown_{len(grouped_records)}"
        
        if group_key not in grouped_records:
            grouped_records[group_key] = {
                'records': [],
                'group_info': group_info
            }
        grouped_records[group_key]['records'].append(record)
        
        # DEBUG: Log group keys to verify grouping logic (log first 30 groups)
        # PERFORMANCE: Skip verbose logging during grouping (only log at debug level)
        if logging.getLogger().isEnabledFor(logging.DEBUG) and len(grouped_records) <= 5:
            logging.debug(f"PREROLL GROUPING DEBUG: Added record to group_key '{group_key}' (group_id: {group_id}, brand_key: {brand_key})")
    
    if skipped_count > 0:
        logging.warning(f"PREROLL GROUP: Skipped {skipped_count} records with no product name")

    # CRITICAL: Log grouping results
    logging.info(f"PREROLL GROUPING COMPLETE: {original_input_count} input records -> {len(grouped_records)} unique groups")
    
    # Log unique vendors/brands found in groups for debugging
    vendors_in_groups = set()
    brands_in_groups = set()
    for group_key, group_data in grouped_records.items():
        for record in group_data['records']:
            vendor = record.get('Vendor/Supplier*', '') or record.get('Vendor', '') or ''
            brand = record.get('Product Brand', '') or record.get('ProductBrand', '') or ''
            if vendor:
                vendors_in_groups.add(str(vendor).strip())
            if brand:
                brands_in_groups.add(str(brand).strip())
    logging.info(f"PREROLL GROUPING: Found {len(vendors_in_groups)} unique vendors in groups: {sorted(list(vendors_in_groups))[:10]}")
    if len(vendors_in_groups) > 10:
        logging.info(f"PREROLL GROUPING: ... and {len(vendors_in_groups) - 10} more vendors")

    # Step 2: Create representative records with group display names
    unique_records = []
    session_id = session.get('session_id', 'default')
    groups_processed = 0
    groups_failed = 0
    
    logging.info(f"PREROLL GROUPING: Processing {len(grouped_records)} groups to create representatives...")
    # DEBUG: Log all group keys to see what groups were created
    if len(grouped_records) <= 30:  # Only log if reasonable number of groups
        group_keys_list = list(grouped_records.keys())
        logging.info(f"PREROLL GROUPING DEBUG: Created {len(group_keys_list)} groups with keys: {group_keys_list}")
    # Group keys logging removed (too verbose)
    
    # CRITICAL: Track which groups are processed to ensure none are lost
    processed_group_keys_set = set()
    
    # PERFORMANCE: Collect groups for batch database write
    groups_for_db_batch = []
    
    for group_key, group_data in grouped_records.items():
        try:
            group_info = group_data['group_info']
            group_records_list = group_data['records']
            
            if not group_records_list or len(group_records_list) == 0:
                logging.warning(f"PREROLL GROUP: Skipping empty group '{group_key}'")
                continue
            
            original_group_id = group_info['group_id']
            group_display_name = group_info['display_name']
            
            representative = group_records_list[0].copy()
            
            # Use group display name (e.g. "Pre-Roll - 1g", "Assorted Pre-Roll - 0.5g x 14 Packs")
            # Make Product Name* unique per group_key (append brand) so downstream never deduplicates
            # different vendors' same-category groups (e.g. "Pre-Roll - 1g" from Phat Panda vs Hustler's)
            brand_suffix = group_key.split('|')[-1] if '|' in group_key else ''
            unique_display = f"{group_display_name} ({brand_suffix})" if brand_suffix else group_display_name
            representative['Description'] = group_display_name
            representative['Product Name*'] = unique_display
            representative['ProductName'] = unique_display
            representative['DescAndWeight'] = group_display_name
            
            # CRITICAL FIX: Preserve Product Type* for infused prerolls to ensure filtering works correctly
            # Check if this is an infused preroll group and set Product Type* accordingly
            if 'infused' in group_display_name.lower() or original_group_id.startswith('infused-preroll'):
                representative['Product Type*'] = 'Infused Pre-Roll'
                representative['ProductType'] = 'infused pre-roll'
            else:
                # For regular prerolls, ensure Product Type* is set correctly
                if 'pre' in group_display_name.lower() and 'roll' in group_display_name.lower():
                    representative['Product Type*'] = 'Pre-Roll'
                    representative['ProductType'] = 'pre-roll'
            
            # CRITICAL FIX: Preserve vendor information in the representative record
            # This ensures each vendor's label shows their vendor name
            # First try to get vendor from the representative record
            vendor = (
                representative.get('Vendor/Supplier*', '') or
                representative.get('Vendor', '') or
                representative.get('Vendor/Supplier', '') or
                ''
            )
            if not vendor and '|' in group_key:
                vendor = group_key.split('|', 1)[1]
            if not vendor:
                for r in group_records_list:
                    v = (r.get('Vendor/Supplier*', '') or r.get('Vendor', '') or r.get('Vendor/Supplier', '') or '')
                    if v and str(v).strip():
                        vendor = str(v).strip()
                        break
            if vendor:
                representative['Vendor/Supplier*'] = vendor
                representative['Vendor'] = vendor
                representative['ProductVendor'] = vendor
            
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
            rep_lineage = ''
            rep_sovereign = None
            rep_canonical = None
            for r in group_records_list:
                # Check sovereign_lineage first (user edits - highest priority)
                candidate_sovereign = r.get('sovereign_lineage')
                if candidate_sovereign and str(candidate_sovereign).strip() and str(candidate_sovereign).strip().lower() not in ['none', 'nan', '']:
                    rep_sovereign = str(candidate_sovereign).strip()
                    rep_lineage = rep_sovereign
                    break
                
                # Check canonical_lineage (from strains table)
                candidate_canonical = r.get('canonical_lineage')
                if candidate_canonical and str(candidate_canonical).strip() and str(candidate_canonical).strip().lower() not in ['none', 'nan', '']:
                    rep_canonical = str(candidate_canonical).strip()
                    if not rep_lineage:
                        rep_lineage = rep_canonical
                
                # Fall back to other lineage fields
                if not rep_lineage:
                    candidate = (
                        r.get('proprietary_lineage') or
                        r.get('proprietaryLineage') or
                        r.get('currentLineage') or
                        r.get('Lineage') or
                        r.get('lineage')
                    )
                    if candidate and str(candidate).strip() and str(candidate).strip().lower() not in ['none', 'nan', '']:
                        rep_lineage = str(candidate).strip()
                        break
            
            # CRITICAL FIX: Normalize lineage for classic product types (MIXED -> HYBRID)
            # Prerolls are classic types and should never have MIXED lineage
            if rep_lineage:
                rep_lineage_upper = str(rep_lineage).strip().upper()
                # Check if this is a classic product type (prerolls are always classic)
                product_type = representative.get('Product Type*', '').lower()
                from src.core.constants import CLASSIC_TYPES
                is_classic_type = product_type in [ct.lower() for ct in CLASSIC_TYPES] if product_type else True  # Default to True for prerolls
                
                if is_classic_type and (rep_lineage_upper == 'MIXED' or rep_lineage_upper == 'THC'):
                    logging.debug(f"PREROLL: Normalizing MIXED/THC lineage to HYBRID for classic type '{product_type}'")
                    rep_lineage = 'HYBRID'
                    rep_lineage_upper = 'HYBRID'
            
            # CRITICAL FIX: Set ALL lineage fields for consistency (matching DOCX generation priority)
            # This ensures the representative has all lineage fields populated correctly
            if rep_lineage:
                rep_lineage_upper = str(rep_lineage).strip().upper()
                representative['Lineage'] = rep_lineage_upper
                representative['Lineage*'] = rep_lineage_upper
                representative['lineage'] = rep_lineage_upper.lower()
                representative['currentLineage'] = rep_lineage_upper
                
                # Preserve source fields if they exist
                if rep_sovereign:
                    representative['sovereign_lineage'] = rep_sovereign.upper()
                    representative['canonical_lineage'] = rep_sovereign.upper()  # Also set canonical for consistency
                elif rep_canonical:
                    representative['canonical_lineage'] = rep_canonical.upper()
                    # Don't set sovereign_lineage if it wasn't in source
                else:
                    # Excel lineage only - set canonical_lineage to match
                    representative['canonical_lineage'] = rep_lineage_upper

            # Ensure representative preserves a sensible Brand value
            # PRIORITY 1: Extract brand from product name using "by BrandName -" pattern
            # This is the most reliable source since product names follow the pattern:
            # "Product Description by BrandName - Size"
            rep_brand = ''
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
                            break

            # PRIORITY 2: Fall back to Product Brand field if extraction failed
            # Note: The Product Brand field often contains vendor names, so extraction is preferred
            if not rep_brand:
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
                    if any(suffix in cand_str.upper() for suffix in ['LLC', ' INC', ' CO', 'CORP', 'COMPANY']):
                        continue
                    rep_brand = cand_str
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

            if rep_brand:
                representative['Product Brand'] = rep_brand
                representative['ProductBrand'] = rep_brand
                representative['Brand'] = rep_brand

            unique_records.append(representative)
            processed_group_keys_set.add(group_key)
            groups_processed += 1
            
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

                item = {
                    'product_name': record.get('Product Name*', record.get('ProductName', '')),
                    'description': record.get('Description', ''),
                    'price': record.get('Price', ''),
                    'weight': record.get('CombinedWeight', record.get('WeightUnits', '')),
                    'vendor': record.get('Vendor', record.get('Vendor/Supplier*', '')),
                    'brand': record.get('Product Brand', record.get('ProductBrand', '')),
                    'strain': record.get('Product Strain', ''),
                    'lineage': record.get('Lineage', ''),
                    'doh': doh_display,
                }
                group_items.append(item)
            
            # PERFORMANCE: Collect for batch database and cache writes at the end
            # Store group info for batch write (much faster than 322 individual writes)
            groups_for_db_batch.append((group_key, original_group_id, group_items, group_info))
        
        except Exception as group_error:
            groups_failed += 1
            logging.error(f"PREROLL GROUP ERROR: Failed to process group '{group_key}': {group_error}")
            import traceback
            logging.error(f"PREROLL GROUP ERROR: Traceback: {traceback.format_exc()}")
            # Still try to create a minimal representative to avoid losing the group
            try:
                group_data = grouped_records.get(group_key)
                if group_data:
                    group_records_list = group_data.get('records', [])
                    group_info = group_data.get('group_info', {})
                    if group_records_list and len(group_records_list) > 0:
                        minimal_rep = group_records_list[0].copy()
                        group_display_name = group_info.get('display_name', 'Pre-Roll')
                        original_group_id = group_info.get('group_id', group_key)
                        minimal_rep['Product Name*'] = group_display_name
                        minimal_rep['ProductName'] = minimal_rep['Product Name*']
                        minimal_rep['Description'] = minimal_rep['Product Name*']
                        minimal_rep['_group_id'] = original_group_id
                        minimal_rep['_group_key'] = group_key
                        unique_records.append(minimal_rep)
                        processed_group_keys_set.add(group_key)
                        groups_processed += 1
                        logging.warning(f"PREROLL GROUP: Created minimal representative for group '{group_key}' after error")
                    else:
                        logging.error(f"PREROLL GROUP ERROR: Group '{group_key}' has no records to create representative from")
                else:
                    logging.error(f"PREROLL GROUP ERROR: Group '{group_key}' not found in grouped_records")
            except Exception as fallback_error:
                logging.error(f"PREROLL GROUP: Failed to create even minimal representative for '{group_key}': {fallback_error}")
                # Last resort: create a completely minimal record to ensure the group isn't lost
                try:
                    minimal_rep = {
                        'Product Name*': f'Pre-Roll Group {group_key}',
                        'ProductName': f'Pre-Roll Group {group_key}',
                        'Description': f'Pre-Roll Group {group_key}',
                        '_group_id': group_key.split('|')[0] if '|' in group_key else group_key,
                        '_group_key': group_key
                    }
                    unique_records.append(minimal_rep)
                    groups_processed += 1
                    logging.warning(f"PREROLL GROUP: Created absolute minimal representative for group '{group_key}' as last resort")
                except Exception as last_resort_error:
                    logging.error(f"PREROLL GROUP: Complete failure for group '{group_key}': {last_resort_error}")
    
    if groups_failed > 0:
        logging.warning(f"PREROLL GROUPING: {groups_failed} groups failed during processing, {groups_processed} groups successfully processed")
    else:
        logging.info(f"PREROLL GROUPING: All {groups_processed} groups successfully processed")
    
    # CRITICAL DEBUG: Log the actual count of unique_records vs grouped_records
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        logging.debug(f"PREROLL: {len(unique_records)} unique records, {len(grouped_records)} groups, {groups_processed} processed")
    
    # Check if any groups were not processed in the loop
    unprocessed_groups = set(grouped_records.keys()) - processed_group_keys_set
    if unprocessed_groups:
        logging.error(f"PREROLL GROUPING ERROR: {len(unprocessed_groups)} groups were NOT processed in the loop! Unprocessed keys (first 20): {list(unprocessed_groups)[:20]}")
    
    # Track count after brand filtering (if any)
    records_after_brand_filter = len(records)
    
    # Verify all records were grouped (every record should be in a group)
    total_grouped = sum(len(group_data['records']) for group_data in grouped_records.values())
    if total_grouped != records_after_brand_filter:
        logging.error(f"PREROLL GROUPING ERROR: {records_after_brand_filter} records after brand filter but only {total_grouped} were grouped. {records_after_brand_filter - total_grouped} products are MISSING!")
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
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug(f"PREROLL: All {records_after_brand_filter} records grouped into {len(grouped_records)} groups")
    
    # Log summary of grouping
    logging.info(f"PREROLL GROUPING SUMMARY: Input={original_input_count}, After brand filter={records_after_brand_filter}, Grouped={total_grouped}, Groups created={len(grouped_records)}")
    
    # CRITICAL: Rebuild grouped_records_list directly from grouped_records in key order.
    # This guarantees every group_key has exactly one representative and preserves order.
    rep_by_key = {r.get('_group_key'): r for r in unique_records if r.get('_group_key')}
    final_grouped_records_list = []
    for group_key in grouped_records.keys():
        rep = rep_by_key.get(group_key)
        if rep:
            final_grouped_records_list.append(rep)
            continue
        try:
            group_data = grouped_records[group_key]
            group_records_list = group_data.get('records', [])
            group_info = group_data.get('group_info', {})
            if group_records_list:
                new_rep = group_records_list[0].copy()
            else:
                new_rep = {}
            group_display_name = group_info.get('display_name', 'Pre-Roll')
            brand_suffix = group_key.split('|')[-1] if '|' in group_key else ''
            unique_display = f"{group_display_name} ({brand_suffix})" if brand_suffix else group_display_name
            new_rep['Product Name*'] = unique_display
            new_rep['ProductName'] = unique_display
            new_rep['Description'] = group_display_name
            new_rep['DescAndWeight'] = group_display_name
            new_rep['_group_id'] = group_info.get('group_id', group_key)
            new_rep['_group_key'] = group_key
            final_grouped_records_list.append(new_rep)
            logging.warning(f"PREROLL GROUPING: Added missing representative for group '{group_key}'")
        except Exception as add_error:
            logging.error(f"PREROLL GROUPING: Failed to add representative for '{group_key}': {add_error}")
    grouped_records_list = final_grouped_records_list
    
    # Verify all groups were processed
    if len(grouped_records_list) != len(grouped_records):
        logging.error(f"PREROLL GROUPING ERROR: Created {len(grouped_records)} groups but only {len(grouped_records_list)} representatives!")
        processed_keys = {r.get('_group_key', '') for r in grouped_records_list if r.get('_group_key')}
        missing_keys = set(grouped_records.keys()) - processed_keys
        if missing_keys:
            logging.error(f"PREROLL GROUPING ERROR: Missing group_keys: {list(missing_keys)[:20]}")
    else:
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug(f"PREROLL: All {len(grouped_records)} groups have representatives")
    
    # PERFORMANCE: Batch write all groups to database and cache in background (much faster)
    if groups_for_db_batch:
        try:
            # Batch database write in background
            threading.Thread(
                target=_store_preroll_groups_batch,
                args=(groups_for_db_batch,),
                daemon=True
            ).start()
            
            # Batch cache writes (much faster than individual writes)
            try:
                session_id = session.get('preroll_session_id', 'default')
                for group_key, original_group_id, group_items, group_info in groups_for_db_batch:
                    # Store with session-independent key for persistence
                    cache.set(f"preroll_group_latest_{group_key}", group_items, timeout=86400)
                    cache.set(f"preroll_group_info_latest_{group_key}", group_info, timeout=86400)
                    # Store with session-specific key for backward compatibility
                    cache.set(f"preroll_group_{session_id}_{group_key}", group_items, timeout=86400)
                    cache.set(f"preroll_group_info_{session_id}_{group_key}", group_info, timeout=86400)
                    # Store with original group_id for backward compatibility (only if different)
                    if original_group_id != group_key:
                        cache.set(f"preroll_group_latest_{original_group_id}", group_items, timeout=86400)
                        cache.set(f"preroll_group_info_latest_{original_group_id}", group_info, timeout=86400)
            except Exception as cache_error:
                logging.warning(f"PREROLL: Batch cache error (non-fatal): {cache_error}")
        except Exception as db_error:
            logging.warning(f"PREROLL: Failed to start background batch DB store: {db_error}")
    
    logging.info(f"PREROLL GROUPING FINAL: {original_input_count} input records -> {len(grouped_records)} unique groups -> {len(grouped_records_list)} product groups")
    # PERFORMANCE: Only log detailed debug info at debug level
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        if len(grouped_records) <= 50:
            group_keys_sample = list(grouped_records.keys())[:50]
            logging.debug(f"PREROLL GROUPING FINAL DEBUG: All {len(grouped_records)} group keys created: {group_keys_sample}")
        else:
            group_keys_sample = list(grouped_records.keys())[:50]
            logging.debug(f"PREROLL GROUPING FINAL DEBUG: First 50 group keys: {group_keys_sample} (total: {len(grouped_records)})")
    
    # Only log warnings/errors (not info for normal cases)
    if len(grouped_records_list) < len(grouped_records):
        logging.warning(f"PREROLL: Lost {len(grouped_records) - len(grouped_records_list)} groups during processing!")
    elif len(grouped_records_list) > len(grouped_records):
        logging.warning(f"PREROLL: Created {len(grouped_records_list) - len(grouped_records)} extra groups (unexpected)!")
    
    # PERFORMANCE: Skip stats logging unless at debug level
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        pack_groups = sum(1 for k in grouped_records.keys() if 'pack' in k.lower())
        non_pack_groups = len(grouped_records) - pack_groups
        logging.debug(f"PREROLL GROUPING STATS: {pack_groups} pack groups, {non_pack_groups} non-pack groups (total: {len(grouped_records)})")
    
    # Log summary only (reduce logging overhead)
    if grouped_records_list and logging.getLogger().isEnabledFor(logging.DEBUG):
        sample_groups = grouped_records_list[:3]
        for i, rep in enumerate(sample_groups):
            pname = rep.get('Product Name*', rep.get('ProductName', 'N/A'))
            vendor = rep.get('Vendor/Supplier*', rep.get('Vendor', 'N/A'))
            logging.debug(f"PREROLL GROUP [{i+1}]: '{pname}' | Vendor: '{vendor}'")
    
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
    elapsed = time.time() - start_t
    # CRITICAL: Final verification before returning
    final_count = len(grouped_records_list)
    expected_count = len(grouped_records)
    if final_count != expected_count:
        logging.error(f"PREROLL CRITICAL ERROR: Returning {final_count} groups but {expected_count} were created! Missing {expected_count - final_count} groups!")
        # Log missing group_keys
        returned_keys = {r.get('_group_key', '') for r in grouped_records_list if r.get('_group_key')}
        all_keys = set(grouped_records.keys())
        missing = all_keys - returned_keys
        if missing:
            logging.error(f"PREROLL CRITICAL ERROR: Missing group_keys (first 30): {list(missing)[:30]}")
    else:
        logging.info(f"PREROLL SUCCESS: Returning all {final_count} groups as expected")
    
    logging.info(f"PREROLL: Generated {final_count} grouped labels from {original_input_count} originals in {elapsed:.3f}s")

    return grouped_records_list
