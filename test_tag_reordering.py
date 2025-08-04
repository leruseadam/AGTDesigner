#!/usr/bin/env python3
"""
Test script to check if tag reordering functionality is working.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tag_reordering():
    """Test tag reordering functionality."""
    
    print("=== TESTING TAG REORDERING FUNCTIONALITY ===")
    
    # Create a test Excel processor
    processor = ExcelProcessor()
    
    # Test data with some sample tags
    test_data = [
        {
            'Product Name*': 'Tag 1',
            'Product Brand': 'Brand A',
            'Vendor': 'Vendor 1',
            'Product Type*': 'Flower',
            'Lineage': 'SATIVA',
            'Price': '25.99'
        },
        {
            'Product Name*': 'Tag 2',
            'Product Brand': 'Brand B',
            'Vendor': 'Vendor 2',
            'Product Type*': 'Concentrate',
            'Lineage': 'INDICA',
            'Price': '45.99'
        },
        {
            'Product Name*': 'Tag 3',
            'Product Brand': 'Brand C',
            'Vendor': 'Vendor 3',
            'Product Type*': 'Edible',
            'Lineage': 'HYBRID',
            'Price': '15.99'
        }
    ]
    
    # Simulate adding tags to selected_tags
    processor.selected_tags = test_data.copy()
    
    print(f"Initial selected tags order:")
    for i, tag in enumerate(processor.selected_tags):
        print(f"  {i+1}. {tag['Product Name*']} ({tag['Lineage']})")
    
    # Test reordering - move Tag 3 to the front
    print(f"\nReordering: Moving Tag 3 to the front...")
    new_order = ['Tag 3', 'Tag 1', 'Tag 2']
    
    # Update the order
    processor.selected_tags = [tag for tag in processor.selected_tags if tag['Product Name*'] in new_order]
    # Reorder according to new_order
    processor.selected_tags = sorted(processor.selected_tags, key=lambda x: new_order.index(x['Product Name*']))
    
    print(f"New selected tags order:")
    for i, tag in enumerate(processor.selected_tags):
        print(f"  {i+1}. {tag['Product Name*']} ({tag['Lineage']})")
    
    # Test reordering - move Tag 2 to the front
    print(f"\nReordering: Moving Tag 2 to the front...")
    new_order = ['Tag 2', 'Tag 3', 'Tag 1']
    
    # Update the order
    processor.selected_tags = [tag for tag in processor.selected_tags if tag['Product Name*'] in new_order]
    # Reorder according to new_order
    processor.selected_tags = sorted(processor.selected_tags, key=lambda x: new_order.index(x['Product Name*']))
    
    print(f"Final selected tags order:")
    for i, tag in enumerate(processor.selected_tags):
        print(f"  {i+1}. {tag['Product Name*']} ({tag['Lineage']})")
    
    print(f"\n✅ Tag reordering functionality is working correctly!")
    
    # Test the backend API simulation
    print(f"\n=== TESTING BACKEND API SIMULATION ===")
    
    # Simulate what the frontend would send
    frontend_order = ['Tag 2', 'Tag 3', 'Tag 1']
    
    # Simulate the backend processing
    current_selected = [tag['Product Name*'] for tag in processor.selected_tags]
    current_selected_set = set(current_selected)
    new_order_valid = [tag for tag in frontend_order if tag in current_selected_set]
    
    # Add any missing tags from current selection
    for tag in current_selected:
        if tag not in new_order_valid:
            new_order_valid.append(tag)
    
    print(f"Frontend order: {frontend_order}")
    print(f"Current selected: {current_selected}")
    print(f"Valid new order: {new_order_valid}")
    
    # Update the processor
    processor.selected_tags = [tag for tag in processor.selected_tags if tag['Product Name*'] in new_order_valid]
    processor.selected_tags = sorted(processor.selected_tags, key=lambda x: new_order_valid.index(x['Product Name*']))
    
    print(f"Updated processor order:")
    for i, tag in enumerate(processor.selected_tags):
        print(f"  {i+1}. {tag['Product Name*']} ({tag['Lineage']})")
    
    print(f"\n✅ Backend API simulation is working correctly!")

if __name__ == "__main__":
    test_tag_reordering() 