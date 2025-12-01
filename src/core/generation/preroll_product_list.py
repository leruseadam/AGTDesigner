"""
Preroll Product List Generator

This module handles the generation of product list documents for preroll templates.
It creates a separate document listing all preroll items grouped by category.
"""

import logging
from typing import List, Dict, Any, Optional
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from flask import session
from flask_caching import Cache
from src.core.constants import PREROLL_ALLOWED_BRANDS


def generate_preroll_product_list(records: List[Dict[str, Any]], cache: Cache) -> Optional[Document]:
    """
    Generate a separate product list document for preroll templates.
    
    Args:
        records: List of product records (used to extract group IDs if needed)
        cache: Flask cache instance for retrieving stored group data
        
    Returns:
        A separate Document containing the product list (or None if no groups found)
    """
    try:
        # Create a new document for the preroll list
        list_doc = Document()
        
        # Add title
        title = list_doc.add_heading('Preroll Product Lists', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Get session ID and group IDs to retrieve stored preroll groups
        session_id = session.get('preroll_session_id', session.get('session_id', 'default'))
        group_ids = session.get('preroll_group_ids', [])
        
        # Retrieve all preroll groups from cache using stored group IDs
        preroll_groups = {}
        for group_id in group_ids:
            group_items = cache.get(f"preroll_group_{session_id}_{group_id}")
            group_info = cache.get(f"preroll_group_info_{session_id}_{group_id}")
            if group_items and group_info:
                preroll_groups[group_id] = {
                    'items': group_items,
                    'info': group_info
                }
                logging.info(f"PREROLL LIST: Loaded group '{group_info.get('display_name', group_id)}' with {len(group_items)} items from cache")
            else:
                logging.warning(f"PREROLL LIST: Group '{group_id}' not found in cache (items: {group_items is not None}, info: {group_info is not None})")
        
        if not preroll_groups:
            logging.warning("PREROLL LIST: No preroll groups found in cache")
            # Try fallback: check records for group IDs
            for record in records:
                group_id = record.get('_group_id')
                if group_id and group_id not in preroll_groups:
                    group_items = cache.get(f"preroll_group_{session_id}_{group_id}")
                    group_info = cache.get(f"preroll_group_info_{session_id}_{group_id}")
                    if group_items and group_info:
                        preroll_groups[group_id] = {
                            'items': group_items,
                            'info': group_info
                        }
        
        # Only create list document if we have groups
        if preroll_groups:
            # Create a section for each preroll group
            for group_id, group_data in preroll_groups.items():
                group_info = group_data['info']
                group_items = group_data['items']
                display_name = group_info.get('display_name', f'Group {group_id}')
                
                # Add group heading
                heading = list_doc.add_heading(display_name, level=1)
                heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                # Create a table for the items (6 columns: add DOH status)
                table = list_doc.add_table(rows=1, cols=6)
                table.style = 'Light Grid Accent 1'
                
                # Header row
                header_cells = table.rows[0].cells
                header_cells[0].text = 'Product Name'
                header_cells[1].text = 'Brand'
                header_cells[2].text = 'Price'
                header_cells[3].text = 'Weight'
                header_cells[4].text = 'Lineage'
                header_cells[5].text = 'DOH'
                
                # Make header row bold
                for cell in header_cells:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.bold = True
                            run.font.size = Pt(11)
                
                # Filter items by allowed brands if configured
                filtered_items = group_items
                if PREROLL_ALLOWED_BRANDS and len(PREROLL_ALLOWED_BRANDS) > 0:
                    allowed_brands_lower = {brand.lower().strip() for brand in PREROLL_ALLOWED_BRANDS if brand and str(brand).strip()}
                    original_item_count = len(filtered_items)
                    filtered_items = [
                        item for item in group_items
                        if str(item.get('brand', '')).strip().lower() in allowed_brands_lower
                    ]
                    if len(filtered_items) < original_item_count:
                        logging.info(f"PREROLL LIST: Filtered {original_item_count} items to {len(filtered_items)} items for group '{display_name}' based on allowed brands")
                
                # Add items to table
                for item in filtered_items:
                    row_cells = table.add_row().cells
                    row_cells[0].text = item.get('product_name', '')
                    row_cells[1].text = item.get('brand', '')
                    row_cells[2].text = item.get('price', '')
                    row_cells[3].text = item.get('weight', '')
                    row_cells[4].text = item.get('lineage', '')
                    row_cells[5].text = item.get('doh', '')
                
                # Add spacing after each group
                list_doc.add_paragraph('')
            
            # Log summary of items in list
            total_items_in_list = sum(len(group_data['items']) for group_data in preroll_groups.values())
            logging.info(f"PREROLL LIST: Generated separate product list document with {len(preroll_groups)} groups containing {total_items_in_list} total items")
            
            # Log which groups and their item counts
            for group_id, group_data in preroll_groups.items():
                group_name = group_data['info'].get('display_name', group_id)
                item_count = len(group_data['items'])
                logging.info(f"PREROLL LIST GROUP: '{group_name}' ({group_id}) - {item_count} items")
            
            return list_doc
        else:
            logging.warning("PREROLL LIST: No preroll groups found, skipping list creation")
            return None
        
    except Exception as e:
        logging.warning(f"PREROLL LIST: Failed to create preroll list document: {e}")
        return None
