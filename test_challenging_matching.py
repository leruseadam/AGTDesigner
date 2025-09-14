#!/usr/bin/env python3
"""
Test script to check JSON matching with challenging product names
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor

def test_challenging_matching():
    """Test the matching logic with challenging product names"""
    print("🔍 Testing JSON matching with challenging product names...")
    
    try:
        # Initialize components
        excel_processor = ExcelProcessor()
        json_matcher = JSONMatcher(excel_processor)
        
        # Load challenging test data
        with open('test_challenging_data.json', 'r') as f:
            test_data = json.load(f)
        
        print(f"📋 Loaded {len(test_data['inventory_transfer_items'])} challenging test products")
        
        # Test the matching by processing the JSON data directly
        matched_products = []
        failed_products = []
        
        for item in test_data['inventory_transfer_items']:
            try:
                # Create a product tag from the JSON item
                product_tag = json_matcher._create_product_from_json(item, "Test Vendor")
                if product_tag:
                    matched_products.append(product_tag)
                    print(f"  ✅ Matched: {product_tag.get('Product Name*', 'Unknown')}")
                else:
                    failed_products.append(item.get('product_name', 'Unknown'))
                    print(f"  ❌ Failed to match: {item.get('product_name', 'Unknown')}")
            except Exception as e:
                failed_products.append(item.get('product_name', 'Unknown'))
                print(f"  ❌ Error processing {item.get('product_name', 'Unknown')}: {e}")
        
        print(f"\n🎯 Total matches: {len(matched_products)}")
        print(f"❌ Failed matches: {len(failed_products)}")
        
        if failed_products:
            print(f"\n📋 Failed products:")
            for i, product in enumerate(failed_products):
                print(f"  {i+1}. {product}")
        
        if matched_products:
            print(f"\n📋 Matched products:")
            for i, product in enumerate(matched_products):
                product_name = product.get('Product Name*', 'Unknown')
                vendor = product.get('Product Vendor', 'Unknown')
                weight = product.get('Weight*', 'Unknown')
                print(f"  {i+1}. {product_name} (Vendor: {vendor}, Weight: {weight})")
        
        return len(matched_products), len(failed_products)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0

if __name__ == "__main__":
    matched_count, failed_count = test_challenging_matching()
    print(f"\n🎯 Total matches: {matched_count}")
    print(f"❌ Total failures: {failed_count}")
    
    success_rate = (matched_count / (matched_count + failed_count)) * 100 if (matched_count + failed_count) > 0 else 0
    print(f"📊 Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT: High success rate! The matching system is working well.")
    elif success_rate >= 60:
        print("✅ GOOD: Decent success rate, but some products still not matching.")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Low success rate. May need further threshold adjustments.")
