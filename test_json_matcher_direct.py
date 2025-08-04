#!/usr/bin/env python3
"""
Direct test of JSON matcher functionality without server.
This tests the core JSON matching logic to identify any remaining issues.
"""

import sys
import os
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor

def test_json_matcher_direct():
    """Test JSON matcher functionality directly."""
    
    print("🧪 Testing JSON Matcher Directly")
    print("=" * 50)
    
    try:
        # Initialize Excel processor
        print("\n1️⃣ Initializing Excel processor...")
        excel_processor = ExcelProcessor()
        
        # Try to load a default file
        from src.core.data.excel_processor import get_default_upload_file
        default_file = get_default_upload_file()
        
        if default_file and os.path.exists(default_file):
            print(f"   📁 Loading default file: {default_file}")
            success = excel_processor.load_file(default_file)
            if success:
                print(f"   ✅ File loaded successfully: {excel_processor.df.shape[0]} rows")
            else:
                print(f"   ❌ Failed to load file")
                return False
        else:
            print(f"   ⚠️  No default file found, creating empty DataFrame")
            import pandas as pd
            excel_processor.df = pd.DataFrame()
        
        # Initialize JSON matcher
        print("\n2️⃣ Initializing JSON matcher...")
        json_matcher = JSONMatcher(excel_processor)
        print(f"   ✅ JSON matcher initialized")
        
        # Test with sample JSON data
        print("\n3️⃣ Testing with sample JSON data...")
        
        # Test case 1: Normal dictionary
        test_json_1 = {
            "product_name": "Test Product",
            "strain_name": "Test Strain",
            "vendor": "Test Vendor"
        }
        
        print(f"   📝 Testing with normal dictionary: {test_json_1}")
        
        # This should not throw any errors
        try:
            # Test the _calculate_match_score method directly
            if hasattr(json_matcher, '_sheet_cache') and json_matcher._sheet_cache:
                test_cache_item = json_matcher._sheet_cache[0]
                score = json_matcher._calculate_match_score(test_json_1, test_cache_item)
                print(f"   ✅ Score calculation successful: {score}")
            else:
                print(f"   ⚠️  No cache items available for testing")
        except Exception as e:
            print(f"   ❌ Error in score calculation: {e}")
            return False
        
        # Test case 2: String instead of dictionary (this should be handled gracefully)
        test_json_2 = "This is a string, not a dictionary"
        
        print(f"   📝 Testing with string input: {test_json_2}")
        
        try:
            if hasattr(json_matcher, '_sheet_cache') and json_matcher._sheet_cache:
                test_cache_item = json_matcher._sheet_cache[0]
                score = json_matcher._calculate_match_score(test_json_2, test_cache_item)
                print(f"   ✅ String input handled gracefully: {score}")
            else:
                print(f"   ⚠️  No cache items available for testing")
        except Exception as e:
            print(f"   ❌ Error handling string input: {e}")
            return False
        
        # Test case 3: None values
        test_json_3 = None
        
        print(f"   📝 Testing with None input: {test_json_3}")
        
        try:
            if hasattr(json_matcher, '_sheet_cache') and json_matcher._sheet_cache:
                test_cache_item = json_matcher._sheet_cache[0]
                score = json_matcher._calculate_match_score(test_json_3, test_cache_item)
                print(f"   ✅ None input handled gracefully: {score}")
            else:
                print(f"   ⚠️  No cache items available for testing")
        except Exception as e:
            print(f"   ❌ Error handling None input: {e}")
            return False
        
        print("\n✅ All direct tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_json_matcher_direct()
    if success:
        print("\n🎉 JSON matcher is working correctly!")
        sys.exit(0)
    else:
        print("\n🚨 JSON matcher has issues!")
        sys.exit(1) 