#!/usr/bin/env python3
"""
Test script to check JSON matching with local test data
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor

def test_matching_with_local_data():
    """Test the matching logic with local JSON data"""
    print("🔍 Testing JSON matching with local test data...")
    
    try:
        # Initialize components
        excel_processor = ExcelProcessor()
        json_matcher = JSONMatcher(excel_processor)
        
        # Load local test data
        with open('test_data.json', 'r') as f:
            test_data = json.load(f)
        
        print(f"📋 Loaded {len(test_data['inventory_transfer_items'])} test products")
        
        # Test the matching by processing the JSON data directly
        matched_products = []
        
        for item in test_data['inventory_transfer_items']:
            try:
                # Create a product tag from the JSON item
                product_tag = json_matcher._create_product_from_json(item, "Test Vendor")
                if product_tag:
                    matched_products.append(product_tag)
                    print(f"  ✅ Matched: {product_tag.get('Product Name*', 'Unknown')}")
                else:
                    print(f"  ❌ Failed to match: {item.get('product_name', 'Unknown')}")
            except Exception as e:
                print(f"  ❌ Error processing {item.get('product_name', 'Unknown')}: {e}")
        
        print(f"\n🎯 Total matches: {len(matched_products)}")
        
        if matched_products:
            print("\n📋 Matched products:")
            for i, product in enumerate(matched_products):
                product_name = product.get('Product Name*', 'Unknown')
                vendor = product.get('Product Vendor', 'Unknown')
                weight = product.get('Weight*', 'Unknown')
                print(f"  {i+1}. {product_name} (Vendor: {vendor}, Weight: {weight})")
        
        return len(matched_products)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    match_count = test_matching_with_local_data()
    print(f"\n🎯 Total matches: {match_count}")
    
    if match_count > 4:
        print("🎉 SUCCESS: More than 4 products matched! The lowered thresholds are working.")
    else:
        print("⚠️  Still only 4 or fewer matches. May need further threshold adjustments.")
