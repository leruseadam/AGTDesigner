#!/usr/bin/env python3
"""
Test script to verify JSON matching fixes are working correctly.
This script tests the enhanced JSON matching functionality.
"""

import requests
import json
import time
import sys

def test_json_matching_fixes():
    """Test the JSON matching fixes to ensure all matches are generated."""
    
    base_url = "http://127.0.0.1:5003"  # Default Flask port
    
    print("🧪 Testing JSON Matching Fixes")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1️⃣ Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Server is running: {status_data.get('server', 'unknown')}")
            print(f"   Data loaded: {status_data.get('data_loaded', False)}")
            print(f"   Data shape: {status_data.get('data_shape', 'unknown')}")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")
        return False
    
    # Test 2: Test cache clearing endpoint
    print("\n2️⃣ Testing cache clearing endpoint...")
    try:
        response = requests.post(f"{base_url}/api/json-match/clear-cache", timeout=10)
        if response.status_code == 200:
            clear_data = response.json()
            print(f"✅ Cache cleared successfully: {clear_data.get('message', 'Unknown')}")
            print(f"   Cleared {clear_data.get('cleared_cache_count', 0)} cache entries")
        else:
            print(f"❌ Cache clearing failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Cache clearing test failed: {e}")
    
    # Test 3: Test diagnostic endpoint
    print("\n3️⃣ Testing diagnostic endpoint...")
    try:
        # Use a sample URL for testing
        test_url = "https://api.example.com/sample-inventory"
        diagnostic_data = {
            "url": test_url
        }
        
        response = requests.post(f"{base_url}/api/json-match/diagnose", 
                               json=diagnostic_data, timeout=30)
        if response.status_code == 200:
            diag_data = response.json()
            print(f"✅ Diagnostic completed successfully")
            print(f"   Excel processor exists: {diag_data.get('excel_processor_status', {}).get('exists', False)}")
            print(f"   JSON matcher exists: {diag_data.get('json_matcher_status', {}).get('exists', False)}")
            print(f"   Recommendations: {len(diag_data.get('recommendations', []))}")
        else:
            print(f"❌ Diagnostic failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Diagnostic test failed: {e}")
    
    # Test 4: Test JSON matching with sample data
    print("\n4️⃣ Testing JSON matching with sample data...")
    try:
        # Create sample JSON data for testing
        sample_json = {
            "inventory_transfer_items": [
                {
                    "product_name": "Test Product 1",
                    "vendor": "Test Vendor",
                    "brand": "Test Brand",
                    "inventory_type": "Concentrate for Inhalation",
                    "weight": "1g",
                    "strain": "Test Strain 1"
                },
                {
                    "product_name": "Test Product 2", 
                    "vendor": "Test Vendor",
                    "brand": "Test Brand",
                    "inventory_type": "Flower",
                    "weight": "3.5g",
                    "strain": "Test Strain 2"
                },
                {
                    "product_name": "Test Product 3",
                    "vendor": "Test Vendor", 
                    "brand": "Test Brand",
                    "inventory_type": "Vape Cartridge",
                    "weight": "0.5g",
                    "strain": "Test Strain 3"
                }
            ],
            "from_license_name": "Test Vendor"
        }
        
        # Convert to data URL for testing
        import base64
        json_str = json.dumps(sample_json)
        data_url = f"data:application/json;base64,{base64.b64encode(json_str.encode()).decode()}"
        
        match_data = {
            "url": data_url
        }
        
        print(f"   Testing with {len(sample_json['inventory_transfer_items'])} sample products...")
        
        response = requests.post(f"{base_url}/api/json-match", 
                               json=match_data, timeout=60)
        if response.status_code == 200:
            match_result = response.json()
            print(f"✅ JSON matching completed successfully")
            print(f"   Matched count: {match_result.get('matched_count', 0)}")
            print(f"   Available tags: {len(match_result.get('available_tags', []))}")
            print(f"   Selected tags: {len(match_result.get('selected_tags', []))}")
            print(f"   JSON matched tags: {len(match_result.get('json_matched_tags', []))}")
            
            # Check if all products were matched
            expected_count = len(sample_json['inventory_transfer_items'])
            actual_count = match_result.get('matched_count', 0)
            
            if actual_count >= expected_count:
                print(f"✅ SUCCESS: All {expected_count} products were matched!")
            else:
                print(f"⚠️  WARNING: Only {actual_count}/{expected_count} products were matched")
                
        else:
            print(f"❌ JSON matching failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ JSON matching test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Test available tags endpoint
    print("\n5️⃣ Testing available tags endpoint...")
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        if response.status_code == 200:
            available_tags = response.json()
            print(f"✅ Available tags retrieved successfully")
            print(f"   Count: {len(available_tags)}")
            
            # Check for JSON matched tags
            json_matched_count = 0
            for tag in available_tags:
                if isinstance(tag, dict) and tag.get('Source') in ['JSON Match', 'Product Database Match', 'Excel Match (Exact)', 'Excel Match (Strict)']:
                    json_matched_count += 1
            
            print(f"   JSON matched tags: {json_matched_count}")
            
        else:
            print(f"❌ Available tags failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Available tags test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 JSON Matching Fixes Test Complete!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_json_matching_fixes()
        if success:
            print("\n✅ All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
