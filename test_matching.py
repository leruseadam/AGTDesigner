#!/usr/bin/env python3
"""
Test script to check JSON matching with lowered thresholds
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor
from src.core.data.ai_product_matcher import AIProductMatcher

def test_matching():
    """Test the matching logic with sample data"""
    print("🔍 Testing JSON matching with lowered thresholds...")
    
    try:
        # Initialize components
        excel_processor = ExcelProcessor()
        json_matcher = JSONMatcher(excel_processor)
        
        # Test with a sample URL (you can replace this with your actual JSON URL)
        test_url = "https://example.com/test.json"
        
        print(f"📡 Testing with URL: {test_url}")
        
        # Test the matching
        matched_products = json_matcher.fetch_and_match_with_product_db(test_url)
        
        print(f"✅ Found {len(matched_products)} matched products")
        
        if matched_products:
            print("\n📋 Sample matched products:")
            for i, product in enumerate(matched_products[:5]):  # Show first 5
                product_name = product.get('Product Name*', product.get('ProductName', 'Unknown'))
                vendor = product.get('Product Vendor', product.get('vendor', 'Unknown'))
                print(f"  {i+1}. {product_name} (Vendor: {vendor})")
        
        return len(matched_products)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    match_count = test_matching()
    print(f"\n🎯 Total matches: {match_count}")
    
    if match_count > 4:
        print("🎉 SUCCESS: More than 4 products matched! The lowered thresholds are working.")
    else:
        print("⚠️  Still only 4 or fewer matches. May need further threshold adjustments.")
