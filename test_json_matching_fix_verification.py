#!/usr/bin/env python3
"""
Test script to verify JSON matching fix.
This test verifies that JSON matched items properly replace the available tags list
and that fetchAndUpdateAvailableTags doesn't override them.
"""
import requests
import json
import time

def test_json_matching_fix_verification():
    """Test the complete JSON matching functionality."""
    base_url = 'http://127.0.0.1:5001'
    print("🧪 Testing JSON Matching Fix Verification")
    
    # Test 1: Basic JSON matching
    print("\n📋 Test 1: Basic JSON Matching")
    try:
        # Use a test JSON URL
        test_url = f"{base_url}/test_products.json"
        
        response = requests.post(f"{base_url}/api/json-match", 
                               json={"url": test_url},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON matching successful: {result.get('matched_count', 0)} items matched")
            
            # Check if available_tags contains JSON matched items
            available_tags = result.get('available_tags', [])
            json_matched_count = sum(1 for tag in available_tags if tag.get('Source') == 'JSON Match')
            print(f"📊 Available tags: {len(available_tags)} total, {json_matched_count} JSON matched")
            
            if json_matched_count > 0:
                print("✅ JSON matched items found in available_tags")
            else:
                print("❌ No JSON matched items found in available_tags")
                return False
                
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in basic JSON matching test: {e}")
        return False
    
    # Test 2: Check that available tags endpoint returns JSON matched items
    print("\n📋 Test 2: Available Tags Endpoint")
    try:
        response = requests.get(f"{base_url}/api/available-tags")
        
        if response.status_code == 200:
            available_tags = response.json()
            json_matched_count = sum(1 for tag in available_tags if tag.get('Source') == 'JSON Match')
            print(f"📊 Available tags endpoint: {len(available_tags)} total, {json_matched_count} JSON matched")
            
            if json_matched_count > 0:
                print("✅ Available tags endpoint returns JSON matched items")
            else:
                print("❌ Available tags endpoint does not return JSON matched items")
                return False
                
        else:
            print(f"❌ Available tags endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in available tags endpoint test: {e}")
        return False
    
    # Test 3: Check backend state directly
    print("\n📋 Test 3: Backend State Check")
    try:
        # Check cache status
        response = requests.get(f"{base_url}/api/cache-status")
        
        if response.status_code == 200:
            cache_status = response.json()
            print(f"📊 Cache status: {cache_status}")
            
            # Check if filter mode is set to json_matched
            response = requests.get(f"{base_url}/api/get-filter-status")
            
            if response.status_code == 200:
                filter_status = response.json()
                current_mode = filter_status.get('current_filter_mode', 'unknown')
                print(f"📊 Filter mode: {current_mode}")
                
                if current_mode == 'json_matched':
                    print("✅ Filter mode correctly set to json_matched")
                else:
                    print(f"❌ Filter mode not set correctly: {current_mode}")
                    return False
            else:
                print(f"❌ Filter status endpoint failed: {response.status_code}")
                return False
                
        else:
            print(f"❌ Cache status endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in backend state check: {e}")
        return False
    
    print("\n🎉 All tests passed! JSON matching fix is working correctly.")
    return True

def test_json_matcher_attributes():
    """Test that the JSON matcher correctly stores and retrieves matched data."""
    print("\n🧪 Testing JSON Matcher Attribute Fix")
    
    try:
        # Import the JSONMatcher class
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        from core.data.json_matcher import JSONMatcher
        from core.data.excel_processor import ExcelProcessor
        
        # Create a mock Excel processor
        excel_processor = ExcelProcessor()
        
        # Create JSON matcher
        json_matcher = JSONMatcher(excel_processor)
        
        # Test that attributes are accessible
        print("📋 Testing attribute accessibility")
        
        # Initially should be None
        names = json_matcher.get_matched_names()
        tags = json_matcher.get_matched_tags()
        
        print(f"📊 Initial state - names: {names}, tags: {tags}")
        
        # Set some test data
        test_names = ["Test Product 1", "Test Product 2"]
        test_tags = [{"Product Name*": "Test Product 1", "Source": "JSON Match"}, 
                    {"Product Name*": "Test Product 2", "Source": "JSON Match"}]
        
        json_matcher.json_matched_names = test_names
        json_matcher.json_matched_tags = test_tags
        
        # Retrieve the data
        retrieved_names = json_matcher.get_matched_names()
        retrieved_tags = json_matcher.get_matched_tags()
        
        print(f"📊 After setting data - names: {retrieved_names}, tags: {retrieved_tags}")
        
        if retrieved_names == test_names and retrieved_tags == test_tags:
            print("✅ JSON matcher attributes working correctly")
            return True
        else:
            print("❌ JSON matcher attributes not working correctly")
            return False
            
    except Exception as e:
        print(f"❌ Error in JSON matcher attribute test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting JSON Matching Fix Verification Tests")
    
    # Test the attribute fix first
    attribute_test_passed = test_json_matcher_attributes()
    
    if attribute_test_passed:
        # Test the full functionality
        main_test_passed = test_json_matching_fix_verification()
        
        if main_test_passed:
            print("\n🎉 All tests passed! The JSON matching fix is working correctly.")
        else:
            print("\n❌ Main functionality tests failed.")
    else:
        print("\n❌ Attribute fix test failed.")
    
    print("\n📝 Test Summary:")
    print("- JSON matcher attribute fix: ✅" if attribute_test_passed else "- JSON matcher attribute fix: ❌")
    print("- Full functionality test: ✅" if attribute_test_passed and 'main_test_passed' in locals() and main_test_passed else "- Full functionality test: ❌") 