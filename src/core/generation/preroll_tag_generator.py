"""
Preroll Tag Generator

This module handles the generation and grouping of preroll tags.
It groups preroll products by category and creates representative records for label generation.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from flask import session
from flask_caching import Cache


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
    pack_match = re.search(r'(\d+(?:\.\d+)?)\s*g\s*x\s*(\d+)\s*pack', combined, re.IGNORECASE)
    if pack_match:
        weight = pack_match.group(1)
        count = pack_match.group(2)
        # Normalize weight display (remove leading zeros in decimals)
        weight_display = weight.lstrip('0').lstrip('.') if '.' in weight else weight
        if weight_display.startswith('.'):
            weight_display = '0' + weight_display
        # Include the word "Pre-Roll" in the display name so grouped
        # pack labels clearly indicate they are prerolls.
        return {
            'group_id': f'{weight}g-{count}pack',
            'display_name': f'Assorted Pre-Roll {weight_display}g x {count} Packs',
            'category': f'{weight_display}g x {count} Packs'
        }
    
    # Check specifically for 1g x 5 packs (more specific, should be caught by above but keeping for safety)
    if re.search(r'1g\s*x\s*5\s*pack', combined, re.IGNORECASE) or '1g x 5 pack' in combined.lower() or '1 g x 5 pack' in combined.lower():
        # Ensure the specific 1g x 5 pack group also includes "Pre-Roll"
        return {
            'group_id': '5packs',
            'display_name': 'Assorted Pre-Roll 1g x 5 Packs',
            'category': '1g x 5 Packs'
        }
    
    # Check for infused prerolls with weight
    if 'infused' in combined and 'pre' in combined and 'roll' in combined:
        weight_match = re.search(r'(\d+(?:\.\d+)?)\s*g', combined)
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
        weight_match = re.search(r'(\d+(?:\.\d+)?)\s*g', combined)
        if weight_match:
            weight = weight_match.group(1)
            return {
                'group_id': f'preroll-{weight}g',
                'display_name': f'Pre-Roll - {weight}g',
                'category': f'Pre-Roll - {weight}g'
            }
    
    # Default: use truncated description pattern
    preroll_patterns = [
        r'(.+?)(Infused\s+Pre[-‑ ]?Roll.*)',
        r'(.+?)(Pre[-‑ ]?Roll.*)',
    ]
    for pattern in preroll_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            universal_desc = match.group(2).strip().lower()
            # Create a safe group ID from the description
            group_id = re.sub(r'[^a-z0-9-]+', '-', universal_desc).strip('-')
            display_name = universal_desc.replace('pre-roll', 'Pre-Roll').replace('pre roll', 'Pre-Roll')
            display_name = display_name.replace('infused', 'Infused').title()
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
    # Save original records for QR page (before grouping)
    original_records_for_qr = [r.copy() for r in records]
    
    # Store original records in session so they can be used in the product list document
    session['preroll_original_records'] = original_records_for_qr
    session.modified = True
    
    # Step 1: Identify product groups and group records
    grouped_records = {}
    for record in records:
        description = record.get('Description', '')
        product_name = record.get('Product Name*', record.get('ProductName', ''))
        
        # Identify the product group
        group_info = identify_preroll_product_group(description, product_name)
        group_id = group_info['group_id']
        logging.info(f"PREROLL GROUP: Product '{product_name}' -> Group: '{group_info['display_name']}' (group_id: {group_id})")
        
        # Extract vendor to include in grouping key
        vendor = (
            record.get('Vendor/Supplier*', '') or
            record.get('Vendor', '') or
            record.get('Vendor/Supplier', '') or
            ''
        )
        vendor_clean = str(vendor).strip()
        
        # Extract price and normalize it
        price = record.get('Price', '')
        try:
            if isinstance(price, str):
                price_clean = price.replace('$', '').replace(',', '').strip()
                try:
                    price_float = float(price_clean)
                    if price_float.is_integer():
                        price_tier = str(int(price_float))
                    else:
                        price_tier = f"{price_float:.2f}".rstrip('0').rstrip('.')
                except ValueError:
                    price_tier = price_clean
            else:
                price_tier = str(price).strip()
        except Exception:
            price_tier = str(price).strip() if price else 'N/A'
        
        # CRITICAL FIX: Group by category AND vendor to preserve all vendors
        # This creates one label per vendor per product category
        # Each vendor gets their own label even if they have the same product category
        group_key = f"{group_id}|{vendor_clean}" if vendor_clean else group_id
        
        if group_key not in grouped_records:
            grouped_records[group_key] = {
                'records': [],
                'group_info': group_info
            }
        grouped_records[group_key]['records'].append(record)
    
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
        
        # CRITICAL FIX: Preserve vendor information in the representative record
        # This ensures each vendor's label shows their vendor name
        vendor = (
            representative.get('Vendor/Supplier*', '') or
            representative.get('Vendor', '') or
            representative.get('Vendor/Supplier', '') or
            ''
        )
        if vendor:
            logging.info(f"PREROLL GROUP REP: Updated representative record for vendor '{vendor}' with group '{group_display_name}' (was: '{group_records_list[0].get('ProductName', '')}')")
        else:
            logging.info(f"PREROLL GROUP REP: Updated representative record fields to '{group_display_name}' (was: '{group_records_list[0].get('ProductName', '')}')")
        
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
        
        unique_records.append(representative)
        
        # Store items for this group in cache (for QR code page) - use ALL original records
        group_items = []
        for record in group_records_list:
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
        logging.info(f"PREROLL: Stored {len(group_items)} items for group '{group_info.get('display_name', original_group_id)}' (group_key: {group_key}, group_id: {original_group_id}) with session-independent key")
    
    original_count = len(records)
    
    # Verify all records were grouped (every record should be in a group)
    total_grouped = sum(len(group_data['records']) for group_data in grouped_records.values())
    if total_grouped != original_count:
        logging.warning(f"PREROLL GROUPING WARNING: {original_count} original records but only {total_grouped} were grouped. Some products may be missing!")
    else:
        logging.info(f"PREROLL GROUPING: All {original_count} records successfully grouped")
    
    grouped_records_list = unique_records
    logging.info(f"PREROLL GROUPING: Grouped {original_count} records into {len(grouped_records_list)} product groups (one label per vendor per category)")
    
    # Store group IDs in session for later retrieval when creating list document
    # Store both group_keys (with vendor) and original group_ids for compatibility
    group_keys = list(grouped_records.keys())
    group_ids = [group_info['group_id'] for group_info in [g['group_info'] for g in grouped_records.values()]]
    session['preroll_group_ids'] = group_ids  # Store original group_ids for backward compatibility
    session['preroll_group_keys'] = group_keys  # Store full group_keys (with vendor) for new functionality
    session['preroll_session_id'] = session_id
    session.modified = True
    
    # Note: Group items are already stored in cache above during grouping
    logging.info(f"PREROLL: Generated {len(grouped_records_list)} grouped labels (one per vendor per product category)")
    
    return grouped_records_list
