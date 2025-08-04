#!/usr/bin/env python3
"""
Test script to debug brand name issues in label generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_brand_name_processing():
    """Test brand name processing to see why it might be missing."""
    
    print("=== Testing Brand Name Processing ===")
    
    # Simulate the data processing that happens in the excel processor
    def simulate_record_processing(record):
        """Simulate how a record is processed in the excel processor."""
        
        print(f"\nProcessing record:")
        print(f"  Raw record: {record}")
        
        # Get product brand (same logic as excel processor)
        product_brand = record.get('Product Brand', '').upper()
        print(f"  Product Brand (raw): {repr(record.get('Product Brand', ''))}")
        print(f"  Product Brand (processed): {repr(product_brand)}")
        
        # Get product type
        product_type = record.get('Product Type*', '').strip().lower()
        print(f"  Product Type: {repr(product_type)}")
        
        # Simulate template processor logic
        if product_brand:
            classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
            
            if product_type in classic_types:
                print(f"  → Using PRODUCTBRAND marker (classic type)")
                return f"PRODUCTBRAND_START{product_brand}PRODUCTBRAND_END"
            else:
                print(f"  → Using PRODUCTBRAND_CENTER marker (non-classic type)")
                return f"PRODUCTBRAND_CENTER_START{product_brand}PRODUCTBRAND_CENTER_END"
        else:
            print(f"  → No brand name found!")
            return ""
    
    # Test cases
    test_records = [
        {
            'Product Name*': 'White Widow CBG',
            'Product Brand': 'Platinum Distillate',
            'Product Type*': 'vape cartridge',
            'Price': '35',
            'Lineage': 'HYBRID',
            'DOH': 'YES'
        },
        {
            'Product Name*': 'White Widow CBG',
            'Product Brand': '',  # Empty brand
            'Product Type*': 'vape cartridge',
            'Price': '35',
            'Lineage': 'HYBRID',
            'DOH': 'YES'
        },
        {
            'Product Name*': 'White Widow CBG',
            # Missing Product Brand field
            'Product Type*': 'vape cartridge',
            'Price': '35',
            'Lineage': 'HYBRID',
            'DOH': 'YES'
        },
        {
            'Product Name*': 'White Widow CBG',
            'Product Brand': 'Platinum Distillate',
            'Product Type*': 'edible (solid)',  # Non-classic type
            'Price': '35',
            'Lineage': 'HYBRID',
            'DOH': 'YES'
        }
    ]
    
    for i, record in enumerate(test_records, 1):
        print(f"\n--- Test Case {i} ---")
        result = simulate_record_processing(record)
        print(f"  Final result: {repr(result)}")
    
    print("\n=== Analysis ===")
    print("Possible reasons why brand name might be missing:")
    print("1. 'Product Brand' field is empty in the Excel file")
    print("2. 'Product Brand' field is missing from the Excel file")
    print("3. 'Product Brand' field contains only whitespace")
    print("4. The product type is not being recognized correctly")
    print("5. The template is not displaying the brand name field")
    
    return True

if __name__ == "__main__":
    success = test_brand_name_processing()
    sys.exit(0 if success else 1) 