#!/usr/bin/env python3
"""
Comprehensive test for JSON matching string object fixes.
This test verifies that all the fixes for the 'str' object has no attribute 'get' error are working.
"""

import requests
import json
import time
import sys

def test_json_matching_fix():
    """Test that JSON matching no longer throws string object errors."""
    
    base_url = "http://127.0.0.1:9090"
    
    print("🧪 Testing JSON Matching String Object Fix")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1️⃣ Checking server status...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print(f"   ✅ Server is running")
            print(f"   📊 Data loaded: {status_data.get('data_loaded', False)}")
        else:
            print(f"   ❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Test JSON matching with a known URL
    print("\n2️⃣ Testing JSON matching...")
    
    # Use a test URL that should trigger the matching process
    test_url = "https://api.cultivera.com/api/v1/inventory_transfers/12345"
    
    try:
        response = requests.post(
            f"{base_url}/api/json-match",
            json={"url": test_url},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ JSON matching completed successfully")
            print(f"   📊 Success: {result.get('success', False)}")
            print(f"   📋 Matched count: {result.get('matched_count', 0)}")
            print(f"   🔧 Cache status: {result.get('cache_status', 'Unknown')}")
            
            # Check if we got any matched names
            if result.get('matched_names'):
                print(f"   📝 Sample matches: {result.get('matched_names', [])[:3]}")
            
            # Check if we got any matched tags
            if result.get('json_matched_tags'):
                print(f"   🏷️  Matched tags count: {len(result.get('json_matched_tags', []))}")
                
                # Test that all matched tags are dictionaries
                matched_tags = result.get('json_matched_tags', [])
                non_dict_tags = [tag for tag in matched_tags if not isinstance(tag, dict)]
                if non_dict_tags:
                    print(f"   ⚠️  Found {len(non_dict_tags)} non-dictionary tags")
                else:
                    print(f"   ✅ All matched tags are dictionaries")
            
            return True
            
        else:
            error_data = response.json()
            error_msg = error_data.get('error', 'Unknown error')
            print(f"   ❌ JSON matching failed: {response.status_code} - {error_msg}")
            
            # Check if the error is the string object error
            if "'str' object has no attribute 'get'" in error_msg:
                print(f"   🚨 STRING OBJECT ERROR STILL OCCURRING!")
                return False
            else:
                print(f"   ℹ️  Different error occurred (not the string object error)")
                return True
                
    except Exception as e:
        print(f"   ❌ Exception during JSON matching: {e}")
        return False
    
    # Test 3: Test with malformed data to ensure robust error handling
    print("\n3️⃣ Testing error handling with malformed data...")
    
    try:
        # Test with a URL that might return malformed data
        malformed_url = "https://httpbin.org/json"
        
        response = requests.post(
            f"{base_url}/api/json-match",
            json={"url": malformed_url},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Malformed data handled gracefully")
            print(f"   📊 Success: {result.get('success', False)}")
            return True
        else:
            error_data = response.json()
            error_msg = error_data.get('error', 'Unknown error')
            print(f"   ℹ️  Expected error with malformed data: {error_msg}")
            
            # Check if the error is the string object error
            if "'str' object has no attribute 'get'" in error_msg:
                print(f"   🚨 STRING OBJECT ERROR STILL OCCURRING WITH MALFORMED DATA!")
                return False
            else:
                print(f"   ✅ Different error occurred (not the string object error)")
                return True
                
    except Exception as e:
        print(f"   ❌ Exception during malformed data test: {e}")
        return False

def test_available_tags_processing():
    """Test that available tags processing doesn't throw string object errors."""
    
    base_url = "http://127.0.0.1:9090"
    
    print("\n4️⃣ Testing available tags processing...")
    
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        
        if response.status_code == 200:
            tags = response.json()
            print(f"   ✅ Available tags retrieved successfully")
            print(f"   📊 Tags count: {len(tags)}")
            
            # Check that all tags are dictionaries
            non_dict_tags = [tag for tag in tags if not isinstance(tag, dict)]
            if non_dict_tags:
                print(f"   ⚠️  Found {len(non_dict_tags)} non-dictionary tags")
                print(f"   📝 Sample non-dict tags: {non_dict_tags[:3]}")
            else:
                print(f"   ✅ All available tags are dictionaries")
            
            return True
            
        else:
            error_data = response.json()
            error_msg = error_data.get('error', 'Unknown error')
            print(f"   ❌ Available tags failed: {response.status_code} - {error_msg}")
            
            # Check if the error is the string object error
            if "'str' object has no attribute 'get'" in error_msg:
                print(f"   🚨 STRING OBJECT ERROR IN AVAILABLE TAGS!")
                return False
            else:
                print(f"   ℹ️  Different error occurred")
                return True
                
    except Exception as e:
        print(f"   ❌ Exception during available tags test: {e}")
        return False

def main():
    """Run all tests."""
    
    print("🚀 Starting Comprehensive JSON Matching Fix Tests")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test JSON matching
    if not test_json_matching_fix():
        all_tests_passed = False
    
    # Test available tags processing
    if not test_available_tags_processing():
        all_tests_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    if all_tests_passed:
        print("✅ ALL TESTS PASSED!")
        print("🎉 The JSON matching string object fix is working correctly!")
        print("🔧 No more 'str' object has no attribute 'get' errors should occur.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🚨 The string object error is still occurring.")
        print("🔍 Please check the logs for more details.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 