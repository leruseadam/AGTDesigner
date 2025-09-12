#!/usr/bin/env python3
"""
Debug script to test Vape Cartridge lineage alignment with actual data flow.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.constants import CLASSIC_TYPES

def test_actual_data_flow():
    """Test the actual data flow as it happens in the template processor."""
    print("=== Testing Actual Data Flow ===")
    
    # Simulate the record data as it would come from Excel
    record = {
        'ProductType': 'Vape Cartridge',
        'Product Type*': 'Vape Cartridge'
    }
    
    # Simulate the current_product_type assignment (lines 973-974)
    current_product_type = (record.get('ProductType', '').lower() or 
                          record.get('Product Type*', '').lower())
    
    print(f"Original ProductType: '{record.get('ProductType', '')}'")
    print(f"Original Product Type*: '{record.get('Product Type*', '')}'")
    print(f"current_product_type after .lower(): '{current_product_type}'")
    print(f"CLASSIC_TYPES: {CLASSIC_TYPES}")
    
    # Test the lineage alignment logic (lines 2483-2484)
    product_type = current_product_type
    is_classic_product = product_type and product_type.lower() in CLASSIC_TYPES
    
    print(f"\nLineage alignment check:")
    print(f"  product_type: '{product_type}'")
    print(f"  product_type.lower(): '{product_type.lower()}'")
    print(f"  product_type.lower() in CLASSIC_TYPES: {product_type.lower() in CLASSIC_TYPES}")
    print(f"  is_classic_product: {is_classic_product}")
    
    # Test the fallback logic (lines 2750-2751)
    if product_type:
        is_classic_product_fallback = product_type.lower() in CLASSIC_TYPES
        print(f"\nFallback check:")
        print(f"  product_type: '{product_type}'")
        print(f"  product_type.lower() in CLASSIC_TYPES: {product_type.lower() in CLASSIC_TYPES}")
        print(f"  is_classic_product_fallback: {is_classic_product_fallback}")
    
    # Test with different variations
    print(f"\n=== Testing Different Variations ===")
    test_variations = [
        "Vape Cartridge",
        "vape cartridge", 
        "VAPE CARTRIDGE",
        "Vape cartridge",
        "vape Cartridge"
    ]
    
    for variation in test_variations:
        # Simulate the .lower() conversion
        lower_variation = variation.lower()
        is_classic = lower_variation in CLASSIC_TYPES
        print(f"  '{variation}' -> '{lower_variation}' -> is_classic: {is_classic}")

def test_classic_types_content():
    """Test the actual content of CLASSIC_TYPES."""
    print(f"\n=== CLASSIC_TYPES Content Analysis ===")
    print(f"CLASSIC_TYPES type: {type(CLASSIC_TYPES)}")
    print(f"CLASSIC_TYPES content: {CLASSIC_TYPES}")
    
    for classic_type in CLASSIC_TYPES:
        print(f"  '{classic_type}' (type: {type(classic_type)})")
        if classic_type == "vape cartridge":
            print(f"    -> This should match 'vape cartridge'")
        elif classic_type.lower() == "vape cartridge":
            print(f"    -> This should match 'vape cartridge' (case insensitive)")

if __name__ == "__main__":
    test_actual_data_flow()
    test_classic_types_content()
