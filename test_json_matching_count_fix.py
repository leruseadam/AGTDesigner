#!/usr/bin/env python3
"""
Test script to verify that JSON matching properly handles available tags count.
This test ensures that when 99 items match, all 99 are properly added to the available tags list.
"""

import requests
import json
import time

def test_json_matching_count_fix():
    """Test that JSON matching properly adds all matched items to available tags."""
    
    base_url = 'http://localhost:5000'
    
    print("🧪 Testing JSON Matching Count Fix...\n")
    
    # Step 1: Check initial state
    print("1. Checking initial state...")
    try:
        response = requests.get(f'{base_url}/api/available-tags')
        if response.status_code == 200:
            initial_tags = response.json()
            print(f"   ✅ Initial available tags: {len(initial_tags)}")
        else:
            print(f"   ❌ Failed to get initial tags: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error getting initial tags: {e}")
        return False
    
    # Step 2: Perform JSON matching with test data
    print("\n2. Performing JSON matching...")
    
    # Create mock JSON data with 99 items
    mock_json_data = {
        "inventory_transfer": {
            "items": []
        }
    }
    
    # Generate 99 test items
    for i in range(1, 100):
        item = {
            "product_name": f"Test Product {i:03d}",
            "vendor": f"Test Vendor {(i % 5) + 1}",
            "product_type": "flower",
            "weight": "3.5g",
            "price": f"${25 + (i % 10)}.00",
            "strain_name": f"Test Strain {i % 10}",
            "lineage": ["hybrid", "indica", "sativa"][i % 3].upper(),
            "thc_percentage": f"{15 + (i % 10)}.5%",
            "cbd_percentage": f"{0.5 + (i % 5)}%"
        }
        mock_json_data["inventory_transfer"]["items"].append(item)
    
    print(f"   Created mock JSON with {len(mock_json_data['inventory_transfer']['items'])} items")
    
    # Step 3: Test JSON matching
    try:
        # Use a mock URL that returns our test data
        test_url = "https://example.com/test-inventory.json"
        
        # Mock the JSON matching by directly calling the endpoint with our data
        response = requests.post(f'{base_url}/api/json-match', 
                               json={'url': test_url, 'mock_data': mock_json_data},
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ JSON matching successful")
            print(f"   - Matched count: {result.get('matched_count', 0)}")
            print(f"   - Available tags in response: {len(result.get('available_tags', []))}")
            print(f"   - JSON matched tags: {len(result.get('json_matched_tags', []))}")
            
            # Verify the counts
            matched_count = result.get('matched_count', 0)
            available_tags_count = len(result.get('available_tags', []))
            json_matched_tags_count = len(result.get('json_matched_tags', []))
            
            if matched_count == 99:
                print(f"   ✅ Correctly matched 99 items")
            else:
                print(f"   ❌ Expected 99 matches, got {matched_count}")
                return False
            
            if json_matched_tags_count == 99:
                print(f"   ✅ Correctly created 99 JSON matched tags")
            else:
                print(f"   ❌ Expected 99 JSON matched tags, got {json_matched_tags_count}")
                return False
                
        else:
            print(f"   ❌ JSON matching failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during JSON matching: {e}")
        return False
    
    # Step 4: Check final available tags count
    print("\n3. Checking final available tags count...")
    try:
        response = requests.get(f'{base_url}/api/available-tags')
        if response.status_code == 200:
            final_tags = response.json()
            print(f"   ✅ Final available tags: {len(final_tags)}")
            
            # Count JSON matched tags
            json_matched_count = sum(1 for tag in final_tags if tag.get('Source') == 'JSON Match')
            print(f"   - JSON matched tags in final list: {json_matched_count}")
            
            # Verify the fix worked
            expected_total = len(initial_tags) + 99  # Initial + new JSON matched
            if len(final_tags) >= expected_total:
                print(f"   ✅ Available tags count is correct (expected >= {expected_total}, got {len(final_tags)})")
            else:
                print(f"   ❌ Available tags count is wrong (expected >= {expected_total}, got {len(final_tags)})")
                return False
            
            if json_matched_count == 99:
                print(f"   ✅ All 99 JSON matched tags are in the available list")
            else:
                print(f"   ❌ Expected 99 JSON matched tags, found {json_matched_count}")
                return False
                
        else:
            print(f"   ❌ Failed to get final tags: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error getting final tags: {e}")
        return False
    
    # Step 5: Test the frontend behavior simulation
    print("\n4. Testing frontend behavior simulation...")
    
    # Simulate what the frontend should do
    try:
        # Get the current available tags
        response = requests.get(f'{base_url}/api/available-tags')
        if response.status_code == 200:
            current_tags = response.json()
            
            # Simulate the frontend logic
            existing_tags = [tag for tag in current_tags if tag.get('Source') != 'JSON Match']
            json_matched_tags = [tag for tag in current_tags if tag.get('Source') == 'JSON Match']
            
            print(f"   - Existing tags (non-JSON): {len(existing_tags)}")
            print(f"   - JSON matched tags: {len(json_matched_tags)}")
            print(f"   - Total available tags: {len(current_tags)}")
            
            # Verify the counts make sense
            if len(current_tags) == len(existing_tags) + len(json_matched_tags):
                print(f"   ✅ Tag counts are consistent")
            else:
                print(f"   ❌ Tag counts are inconsistent")
                return False
                
            # Check for duplicates
            product_names = [tag.get('Product Name*', '') for tag in current_tags]
            unique_names = set(product_names)
            if len(product_names) == len(unique_names):
                print(f"   ✅ No duplicate product names found")
            else:
                print(f"   ❌ Found {len(product_names) - len(unique_names)} duplicate product names")
                return False
                
        else:
            print(f"   ❌ Failed to get current tags: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error in frontend simulation: {e}")
        return False
    
    print("\n✅ JSON Matching Count Fix Test Completed Successfully!")
    print("🎉 The fix ensures that all 99 matched items are properly added to the available tags list.")
    
    return True

def test_clear_functionality():
    """Test that clearing JSON matches works correctly."""
    
    base_url = 'http://localhost:5000'
    
    print("\n🧹 Testing Clear Functionality...\n")
    
    # Step 1: Check current state
    print("1. Checking current state before clear...")
    try:
        response = requests.get(f'{base_url}/api/available-tags')
        if response.status_code == 200:
            before_clear = response.json()
            json_matched_before = sum(1 for tag in before_clear if tag.get('Source') == 'JSON Match')
            print(f"   - Total tags before clear: {len(before_clear)}")
            print(f"   - JSON matched tags before clear: {json_matched_before}")
        else:
            print(f"   ❌ Failed to get tags before clear: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error getting tags before clear: {e}")
        return False
    
    # Step 2: Clear JSON matches
    print("\n2. Clearing JSON matches...")
    try:
        response = requests.post(f'{base_url}/api/json-clear', 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Clear successful: {result.get('message', 'Unknown')}")
        else:
            print(f"   ❌ Clear failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error during clear: {e}")
        return False
    
    # Step 3: Check state after clear
    print("\n3. Checking state after clear...")
    try:
        response = requests.get(f'{base_url}/api/available-tags')
        if response.status_code == 200:
            after_clear = response.json()
            json_matched_after = sum(1 for tag in after_clear if tag.get('Source') == 'JSON Match')
            print(f"   - Total tags after clear: {len(after_clear)}")
            print(f"   - JSON matched tags after clear: {json_matched_after}")
            
            if json_matched_after == 0:
                print(f"   ✅ All JSON matched tags were cleared")
            else:
                print(f"   ❌ {json_matched_after} JSON matched tags remain after clear")
                return False
                
        else:
            print(f"   ❌ Failed to get tags after clear: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error getting tags after clear: {e}")
        return False
    
    print("\n✅ Clear Functionality Test Completed Successfully!")
    return True

def main():
    """Run all tests."""
    print("🧪 JSON Matching Count Fix Test Suite")
    print("="*60)
    
    # Run the main test
    main_test_passed = test_json_matching_count_fix()
    
    # Run the clear test
    clear_test_passed = test_clear_functionality()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    if main_test_passed and clear_test_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ JSON matching count fix is working correctly")
        print("✅ All 99 matched items are properly added to available tags")
        print("✅ Clear functionality works correctly")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        if not main_test_passed:
            print("❌ Main JSON matching count test failed")
        if not clear_test_passed:
            print("❌ Clear functionality test failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main()) 