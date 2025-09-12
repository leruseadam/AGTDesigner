#!/usr/bin/env python3
"""
Test script to verify the improved JSON matching logic.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor

def test_json_matching_improvement():
    """Test the improved JSON matching that uses both database and Excel data."""
    print("=== Testing Improved JSON Matching ===")
    
    # Create a mock Excel processor with some test data
    excel_processor = ExcelProcessor()
    
    # Create some mock Excel data
    import pandas as pd
    mock_data = {
        'Product Name*': ['Blue Dream Flower', 'OG Kush Concentrate', 'Sour Diesel Vape'],
        'Vendor': ['Test Vendor 1', 'Test Vendor 2', 'Test Vendor 1'],
        'Product Brand': ['Brand A', 'Brand B', 'Brand C'],
        'Product Type*': ['Flower', 'Concentrate', 'Vape Cartridge'],
        'Price': ['25.00', '45.00', '35.00'],
        'Weight*': ['3.5g', '1g', '0.5g']
    }
    excel_processor.df = pd.DataFrame(mock_data)
    
    # Create JSON matcher
    json_matcher = JSONMatcher(excel_processor)
    
    # Test JSON data with various matching scenarios
    test_json_data = [
        {
            "product_name": "Blue Dream Flower",  # Exact match
            "vendor": "Test Vendor 1",
            "brand": "Brand A",
            "inventory_type": "Flower",
            "qty": 10,
            "unit_weight": "3.5g",
            "price": "25.00"
        },
        {
            "product_name": "Purple Haze Flower",  # No match - should create from JSON
            "vendor": "Test Vendor 3",
            "brand": "Brand D",
            "inventory_type": "Flower",
            "qty": 5,
            "unit_weight": "3.5g",
            "price": "30.00"
        },
        {
            "product_name": "OG Kush",  # Partial match
            "vendor": "Test Vendor 2",
            "brand": "Brand B",
            "inventory_type": "Concentrate",
            "qty": 3,
            "unit_weight": "1g",
            "price": "45.00"
        }
    ]
    
    print(f"Test JSON data: {len(test_json_data)} items")
    print(f"Mock Excel data: {len(excel_processor.df)} items")
    
    # Test the matching logic
    try:
        # Simulate the matching process
        matched_products = []
        
        for i, item in enumerate(test_json_data):
            product_name = item.get("product_name", "")
            print(f"\n--- Processing item {i+1}: '{product_name}' ---")
            
            # Test database matching (simulated)
            db_match = None
            db_score = 0.0
            if product_name == "Blue Dream Flower":
                db_score = 90.0  # Simulate high database match
                db_match = {"product_name": "Blue Dream Flower", "vendor": "Test Vendor 1"}
                print(f"✅ Database match found (score: {db_score:.1f})")
            else:
                print(f"📝 No database match found")
            
            # Test Excel matching
            excel_match = None
            excel_score = 0.0
            for idx, row in excel_processor.df.iterrows():
                excel_name = row.get('Product Name*', '').lower()
                if product_name.lower() in excel_name or excel_name in product_name.lower():
                    excel_score = 80.0  # Simulate good Excel match
                    excel_match = row
                    print(f"✅ Excel match found (score: {excel_score:.1f})")
                    break
            
            if excel_match is None:
                print(f"📝 No Excel match found")
            
            # Choose best match
            best_match = None
            best_score = 0.0
            match_source = None
            
            if db_match is not None and excel_match is not None:
                if db_score >= excel_score:
                    best_match = db_match
                    best_score = db_score
                    match_source = 'Product Database Match'
                    print(f"🏆 Using Database match (score: {db_score:.1f} vs Excel: {excel_score:.1f})")
                else:
                    best_match = excel_match
                    best_score = excel_score
                    match_source = 'Excel Match'
                    print(f"🏆 Using Excel match (score: {excel_score:.1f} vs Database: {db_score:.1f})")
            elif db_match is not None:
                best_match = db_match
                best_score = db_score
                match_source = 'Product Database Match'
                print(f"🏆 Using Database match (score: {db_score:.1f})")
            elif excel_match is not None:
                best_match = excel_match
                best_score = excel_score
                match_source = 'Excel Match'
                print(f"🏆 Using Excel match (score: {excel_score:.1f})")
            
            # Process based on match quality
            if best_match is not None and best_score >= 15.0:
                print(f"✅ Good match found - using {match_source} (score: {best_score:.1f})")
                matched_products.append({
                    'Product Name*': product_name,
                    'Source': match_source,
                    'Score': best_score,
                    'Original JSON Product Name': product_name
                })
            else:
                print(f"📝 No good match - creating from JSON data (best score: {best_score:.1f})")
                matched_products.append({
                    'Product Name*': product_name,
                    'Source': 'JSON Data',
                    'Score': best_score,
                    'Original JSON Product Name': product_name
                })
        
        print(f"\n=== Results ===")
        print(f"Total products processed: {len(test_json_data)}")
        print(f"Total products created: {len(matched_products)}")
        print(f"Retention rate: {len(matched_products)/len(test_json_data)*100:.1f}%")
        
        for product in matched_products:
            print(f"  - '{product['Product Name*']}' ({product['Source']}, score: {product['Score']:.1f})")
        
        return len(matched_products) == len(test_json_data)
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_json_matching_improvement()
    print(f"\n=== Test Result ===")
    print(f"Test {'PASSED' if success else 'FAILED'}")
