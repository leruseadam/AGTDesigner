#!/usr/bin/env python3
"""
Test script to verify that JSON matching now processes ALL items without any loss.
This script tests the critical fixes applied to ensure no items are filtered out.
"""

import requests
import json
import time
import sys

def test_json_matching_all_items():
    """Test that JSON matching processes ALL items without any loss."""
    
    base_url = "http://127.0.0.1:5003"  # Default Flask port
    
    print("🧪 Testing JSON Matching - ALL Items Must Be Processed")
    print("=" * 60)
    
    # Test 1: Check if server is running
    print("\n1️⃣ Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Test JSON matching with sample data
    print("\n2️⃣ Testing JSON matching with sample data...")
    
    # Create sample JSON data with multiple items
    sample_json_data = {
        "inventory_transfer_items": [
            {
                "product_name": "Test Product 1",
                "vendor": "Test Vendor",
                "brand": "Test Brand",
                "inventory_type": "flower",
                "weight": "3.5g",
                "strain": "Test Strain 1"
            },
            {
                "product_name": "Test Product 2", 
                "vendor": "Test Vendor",
                "brand": "Test Brand",
                "inventory_type": "concentrate",
                "weight": "1g",
                "strain": "Test Strain 2"
            },
            {
                "product_name": "Test Product 3",
                "vendor": "Test Vendor", 
                "brand": "Test Brand",
                "inventory_type": "edible",
                "weight": "100mg",
                "strain": "Test Strain 3"
            },
            {
                "product_name": "Test Product 4",
                "vendor": "Test Vendor",
                "brand": "Test Brand", 
                "inventory_type": "vape",
                "weight": "0.5g",
                "strain": "Test Strain 4"
            },
            {
                "product_name": "Test Product 5",
                "vendor": "Test Vendor",
                "brand": "Test Brand",
                "inventory_type": "topical",
                "weight": "30ml",
                "strain": "Test Strain 5"
            }
        ],
        "from_license_name": "Test Vendor"
    }
    
    # Convert to data URL
    import base64
    json_str = json.dumps(sample_json_data)
    data_url = f"data:application/json;base64,{base64.b64encode(json_str.encode()).decode()}"
    
    print(f"📊 Sample data contains {len(sample_json_data['inventory_transfer_items'])} items")
    
    # Test JSON matching
    try:
        response = requests.post(f"{base_url}/api/json-match", 
                               json={'url': data_url}, 
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ JSON matching request successful")
            
            # Check the response data
            matched_count = result.get('matched_count', 0)
            available_tags = result.get('available_tags', [])
            json_matched_tags = result.get('json_matched_tags', [])
            
            print(f"📊 Response data:")
            print(f"   - matched_count: {matched_count}")
            print(f"   - available_tags length: {len(available_tags)}")
            print(f"   - json_matched_tags length: {len(json_matched_tags)}")
            
            # CRITICAL TEST: Verify ALL items were processed
            expected_count = len(sample_json_data['inventory_transfer_items'])
            if matched_count == expected_count:
                print(f"✅ SUCCESS: All {expected_count} items were processed!")
            else:
                print(f"❌ FAILURE: Only {matched_count}/{expected_count} items were processed")
                return False
                
            if len(available_tags) == expected_count:
                print(f"✅ SUCCESS: All {expected_count} items are in available_tags!")
            else:
                print(f"❌ FAILURE: Only {len(available_tags)}/{expected_count} items in available_tags")
                return False
                
            if len(json_matched_tags) == expected_count:
                print(f"✅ SUCCESS: All {expected_count} items are in json_matched_tags!")
            else:
                print(f"❌ FAILURE: Only {len(json_matched_tags)}/{expected_count} items in json_matched_tags")
                return False
            
            # Test 3: Verify available tags endpoint returns all items
            print("\n3️⃣ Testing available tags endpoint...")
            try:
                response = requests.get(f"{base_url}/api/available-tags", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    # Handle different response formats
                    if isinstance(result, dict):
                        available_count = len(result.get('tags', []))
                    elif isinstance(result, list):
                        available_count = len(result)
                    else:
                        available_count = 0
                        
                    print(f"📊 Available tags endpoint returned {available_count} tags")
                    
                    if available_count >= expected_count:
                        print(f"✅ SUCCESS: Available tags endpoint has all {expected_count} items!")
                    else:
                        print(f"❌ FAILURE: Available tags endpoint missing items ({available_count}/{expected_count})")
                        return False
                else:
                    print(f"❌ Available tags endpoint failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Error testing available tags endpoint: {e}")
                return False
                
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during JSON matching test: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED! JSON matching now processes ALL items correctly.")
    return True

def main():
    """Main test function."""
    print("Starting JSON Matching All Items Test...")
    
    # Wait a moment for server to start
    time.sleep(2)
    
    success = test_json_matching_all_items()
    
    if success:
        print("\n✅ TEST SUMMARY: JSON matching fixes are working correctly!")
        print("   - All items are processed without loss")
        print("   - No deduplication is removing legitimate items")
        print("   - All matched products appear in available tags")
        sys.exit(0)
    else:
        print("\n❌ TEST SUMMARY: JSON matching still has issues!")
        print("   - Some items are being lost during processing")
        print("   - Additional fixes may be needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
