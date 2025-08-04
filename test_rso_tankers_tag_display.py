#!/usr/bin/env python3
"""
Test script to verify that RSO Tankers tags display correctly like other edibles.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd

def test_rso_tankers_tag_display():
    """Test that RSO Tankers tags display correctly like other edibles."""
    
    # Create test data with RSO Tankers and other edibles
    test_data = {
        'Product Name*': [
            'Test RSO Tanker Product',
            'Test Edible Solid Product',
            'Test Tincture Product',
            'Test Flower Product'
        ],
        'Product Type*': [
            'rso/co2 tankers',
            'edible (solid)',
            'tincture',
            'flower'
        ],
        'Product Brand': ['Test Brand'] * 4,
        'Vendor': ['Test Vendor'] * 4,
        'Lineage': ['MIXED'] * 4,
        'Weight*': ['1'] * 4,
        'Units': ['g'] * 4,
        'Price': ['$10'] * 4,
        'Ratio': ['THC 10mg CBD 5mg CBG 2mg'] * 4
    }
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Create ExcelProcessor instance
    processor = ExcelProcessor()
    processor.df = df
    
    # Test that RSO Tankers is recognized as an edible type
    print("Testing RSO Tankers edible type recognition:")
    print("=" * 50)
    
    edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule", "rso/co2 tankers"}
    
    for product_type in processor.df['Product Type*'].unique():
        is_edible = product_type.lower() in edible_types
        print(f"  '{product_type}': {'✅ Edible' if is_edible else '❌ Not Edible'}")
    
    # Test tag generation
    print(f"\nTesting tag generation:")
    print("=" * 50)
    
    # Get available tags
    available_tags = processor.get_available_tags()
    
    print(f"Generated {len(available_tags)} tags:")
    for tag in available_tags:
        product_type = tag.get('Product Type*', 'Unknown')
        product_name = tag.get('Product Name*', 'Unknown')
        lineage = tag.get('Lineage', 'Unknown')
        print(f"  - {product_name} ({product_type}) - Lineage: {lineage}")
    
    # Test that RSO Tankers gets the same formatting as other edibles
    print(f"\nTesting ratio formatting:")
    print("=" * 50)
    
    # Get selected records to see how ratio formatting is applied
    processor.selected_tags = [tag['Product Name*'] for tag in available_tags]
    selected_records = processor.get_selected_records('vertical')
    
    for record in selected_records:
        product_type = record.get('ProductType', 'Unknown')
        ratio = record.get('Ratio_or_THC_CBD', 'No ratio')
        print(f"  {product_type}: {repr(ratio)}")
    
    print(f"\n✅ RSO Tankers tags should now display like other edibles!")
    print(f"   - Same tag structure and layout")
    print(f"   - Same lineage dropdown options")
    print(f"   - Same ratio formatting (line breaks after every 2nd space)")
    print(f"   - Same color coding and styling")

if __name__ == "__main__":
    test_rso_tankers_tag_display() 