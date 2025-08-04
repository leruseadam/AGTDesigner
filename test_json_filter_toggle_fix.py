#!/usr/bin/env python3
"""
Test script to verify that JSON filter toggle functionality works correctly after the count fix.
This test ensures that the available list properly switches between JSON matched items and full Excel list.
"""

import requests
import json
import time

def test_json_filter_toggle_fix():
    """Test that JSON filter toggle works correctly after JSON matching."""
    
    base_url = 'http://localhost:5000'
    
    print("🧪 Testing JSON Filter Toggle Fix...\n")
    
    # Step 1: Check initial state
    print("1. Checking initial state...")
    try:
        response = requests.get(f'{base_url}/api/get-filter-status')
        if response.status_code == 200:
            initial_status = response.json()
            print(f"   ✅ Initial filter status: {initial_status.get('current_mode', 'unknown')}")
            print(f"   - Can toggle: {initial_status.get('can_toggle', False)}")
            print(f"   - Has full Excel: {initial_status.get('has_full_excel', False)}")
            print(f"   - Has JSON matched: {initial_status.get('has_json_matched', False)}")
        else:
            print(f"   ❌ Failed to get initial filter status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error getting initial filter status: {e}")
        return False
    
    # Step 2: Perform JSON matching to set up the toggle functionality
    print("\n2. Performing JSON matching to set up toggle functionality...")
    
    # Create mock JSON data with test items
    mock_json_data = {
        "inventory_transfer": {
            "items": [
                {
                    "product_name": "Test Product 1",
                    "vendor": "Test Vendor 1",
                    "product_type": "flower",
                    "weight": "3.5g",
                    "price": "$25.00",
                    "strain_name": "Test Strain 1",
                    "lineage": "HYBRID",
                    "thc_percentage": "18.5%",
                    "cbd_percentage": "0.8%"
                },
                {
                    "product_name": "Test Product 2",
                    "vendor": "Test Vendor 2",
                    "product_type": "concentrate",
                    "weight": "1g",
                    "price": "$45.00",
                    "strain_name": "Test Strain 2",
                    "lineage": "INDICA",
                    "thc_percentage": "85.2%",
                    "cbd_percentage": "0.1%"
                }
            ]
        }
    }
    
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
            
            # Wait a moment for backend processing
            time.sleep(1)
            
        else:
            print(f"   ❌ JSON matching failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during JSON matching: {e}")
        return False
    
    # Step 3: Check filter status after JSON matching
    print("\n3. Checking filter status after JSON matching...")
    try:
        response = requests.get(f'{base_url}/api/get-filter-status')
        if response.status_code == 200:
            post_match_status = response.json()
            print(f"   ✅ Post-match filter status: {post_match_status.get('current_mode', 'unknown')}")
            print(f"   - Can toggle: {post_match_status.get('can_toggle', False)}")
            print(f"   - Has full Excel: {post_match_status.get('has_full_excel', False)}")
            print(f"   - Has JSON matched: {post_match_status.get('has_json_matched', False)}")
            print(f"   - JSON matched count: {post_match_status.get('json_matched_count', 0)}")
            print(f"   - Full Excel count: {post_match_status.get('full_excel_count', 0)}")
            
            if not post_match_status.get('can_toggle', False):
                print("   ❌ Cannot toggle after JSON matching")
                return False
                
        else:
            print(f"   ❌ Failed to get post-match filter status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error getting post-match filter status: {e}")
        return False
    
    # Step 4: Test toggle to full Excel list
    print("\n4. Testing toggle to full Excel list...")
    try:
        response = requests.post(f'{base_url}/api/toggle-json-filter',
                               json={'filter_mode': 'toggle'},
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            toggle_result = response.json()
            print(f"   ✅ Toggle successful")
            print(f"   - New mode: {toggle_result.get('filter_mode', 'unknown')}")
            print(f"   - Mode name: {toggle_result.get('mode_name', 'unknown')}")
            print(f"   - Available count: {toggle_result.get('available_count', 0)}")
            
            if toggle_result.get('filter_mode') == 'full_excel':
                print("   ✅ Successfully switched to full Excel list")
            else:
                print(f"   ❌ Expected 'full_excel' mode, got '{toggle_result.get('filter_mode')}'")
                return False
                
        else:
            print(f"   ❌ Toggle failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during toggle: {e}")
        return False
    
    # Step 5: Test toggle back to JSON matched items
    print("\n5. Testing toggle back to JSON matched items...")
    try:
        response = requests.post(f'{base_url}/api/toggle-json-filter',
                               json={'filter_mode': 'toggle'},
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            toggle_result = response.json()
            print(f"   ✅ Toggle back successful")
            print(f"   - New mode: {toggle_result.get('filter_mode', 'unknown')}")
            print(f"   - Mode name: {toggle_result.get('mode_name', 'unknown')}")
            print(f"   - Available count: {toggle_result.get('available_count', 0)}")
            
            if toggle_result.get('filter_mode') == 'json_matched':
                print("   ✅ Successfully switched back to JSON matched items")
            else:
                print(f"   ❌ Expected 'json_matched' mode, got '{toggle_result.get('filter_mode')}'")
                return False
                
        else:
            print(f"   ❌ Toggle back failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during toggle back: {e}")
        return False
    
    # Step 6: Verify available tags count changes correctly
    print("\n6. Verifying available tags count changes...")
    try:
        # Get available tags in JSON matched mode
        response = requests.get(f'{base_url}/api/available-tags')
        if response.status_code == 200:
            json_matched_tags = response.json()
            json_matched_count = len(json_matched_tags)
            print(f"   - JSON matched mode: {json_matched_count} tags")
            
            # Toggle to full Excel
            response = requests.post(f'{base_url}/api/toggle-json-filter',
                                   json={'filter_mode': 'toggle'},
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                # Get available tags in full Excel mode
                response = requests.get(f'{base_url}/api/available-tags')
                if response.status_code == 200:
                    full_excel_tags = response.json()
                    full_excel_count = len(full_excel_tags)
                    print(f"   - Full Excel mode: {full_excel_count} tags")
                    
                    # Verify the counts are different
                    if full_excel_count != json_matched_count:
                        print(f"   ✅ Available tags count changes correctly between modes")
                        print(f"   - Difference: {abs(full_excel_count - json_matched_count)} tags")
                    else:
                        print(f"   ❌ Available tags count is the same in both modes")
                        return False
                        
                else:
                    print(f"   ❌ Failed to get full Excel tags: {response.status_code}")
                    return False
            else:
                print(f"   ❌ Failed to toggle to full Excel: {response.status_code}")
                return False
                
        else:
            print(f"   ❌ Failed to get JSON matched tags: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verifying tag counts: {e}")
        return False
    
    print("\n✅ JSON Filter Toggle Fix Test Completed Successfully!")
    print("🎉 The available list properly switches between JSON matched items and full Excel list.")
    
    return True

def test_clear_functionality():
    """Test that clearing JSON matches works correctly."""
    
    base_url = 'http://localhost:5000'
    
    print("\n🧹 Testing Clear Functionality...\n")
    
    # Step 1: Check current state before clear
    print("1. Checking current state before clear...")
    try:
        response = requests.get(f'{base_url}/api/get-filter-status')
        if response.status_code == 200:
            before_clear = response.json()
            print(f"   - Current mode: {before_clear.get('current_mode', 'unknown')}")
            print(f"   - Can toggle: {before_clear.get('can_toggle', False)}")
            print(f"   - JSON matched count: {before_clear.get('json_matched_count', 0)}")
        else:
            print(f"   ❌ Failed to get status before clear: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error getting status before clear: {e}")
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
        response = requests.get(f'{base_url}/api/get-filter-status')
        if response.status_code == 200:
            after_clear = response.json()
            print(f"   - Current mode: {after_clear.get('current_mode', 'unknown')}")
            print(f"   - Can toggle: {after_clear.get('can_toggle', False)}")
            print(f"   - JSON matched count: {after_clear.get('json_matched_count', 0)}")
            
            if after_clear.get('json_matched_count', 0) == 0:
                print("   ✅ All JSON matched items were cleared")
            else:
                print(f"   ❌ {after_clear.get('json_matched_count', 0)} JSON matched items remain after clear")
                return False
                
        else:
            print(f"   ❌ Failed to get status after clear: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error getting status after clear: {e}")
        return False
    
    print("\n✅ Clear Functionality Test Completed Successfully!")
    return True

def main():
    """Run all tests."""
    print("🧪 JSON Filter Toggle Fix Test Suite")
    print("="*60)
    
    # Run the main test
    main_test_passed = test_json_filter_toggle_fix()
    
    # Run the clear test
    clear_test_passed = test_clear_functionality()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    if main_test_passed and clear_test_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ JSON filter toggle functionality is working correctly")
        print("✅ Available list properly switches between modes")
        print("✅ Clear functionality works correctly")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        if not main_test_passed:
            print("❌ Main JSON filter toggle test failed")
        if not clear_test_passed:
            print("❌ Clear functionality test failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main()) 