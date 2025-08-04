#!/usr/bin/env python3
"""
Test script to check for tag duplication issues in drag and drop functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_drag_drop_duplication():
    """Test for tag duplication issues in drag and drop."""
    
    print("=== TESTING DRAG AND DROP DUPLICATION ISSUES ===")
    
    base_url = "http://127.0.0.1:9090"
    
    try:
        # Test 1: Check if server is running
        print("\n1. Testing server connectivity...")
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding properly")
            return False
        
        # Test 2: Get initial selected tags
        print("\n2. Getting initial selected tags...")
        response = requests.get(f"{base_url}/api/selected-tags", timeout=10)
        if response.status_code == 200:
            initial_selected = response.json()
            if isinstance(initial_selected, list):
                initial_count = len(initial_selected)
            else:
                initial_count = len(initial_selected.get('selected_tags', []))
            print(f"   - Initial selected tags: {initial_count}")
            
            # Get unique tag names
            if isinstance(initial_selected, list):
                initial_tag_names = [tag.get('Product Name*', '') if isinstance(tag, dict) else str(tag) for tag in initial_selected]
            else:
                initial_tag_names = [tag.get('Product Name*', '') if isinstance(tag, dict) else str(tag) for tag in initial_selected.get('selected_tags', [])]
            
            initial_unique = set(initial_tag_names)
            print(f"   - Initial unique tag names: {len(initial_unique)}")
            
            if len(initial_tag_names) != len(initial_unique):
                print(f"❌ DUPLICATION DETECTED: {len(initial_tag_names)} total vs {len(initial_unique)} unique")
                duplicates = [name for name in initial_tag_names if initial_tag_names.count(name) > 1]
                print(f"   - Duplicate tags: {duplicates}")
                return False
            else:
                print("✅ No initial duplication detected")
        else:
            print("❌ Could not get initial selected tags")
            return False
        
        # Test 3: Test order update API for potential duplication
        print("\n3. Testing order update API...")
        
        # Create a test order with some potential duplicates
        test_order = initial_tag_names[:3] * 2  # Duplicate the first 3 tags
        print(f"   - Test order with duplicates: {test_order}")
        
        response = requests.post(f"{base_url}/api/update-selected-order", 
                               headers={'Content-Type': 'application/json'},
                               json={'order': test_order},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                updated_tags = data.get('selected_tags', [])
                print(f"   - Updated tags count: {len(updated_tags)}")
                print(f"   - Updated tags: {updated_tags}")
                
                # Check for duplicates in the response
                unique_updated = set(updated_tags)
                if len(updated_tags) != len(unique_updated):
                    print(f"❌ DUPLICATION IN RESPONSE: {len(updated_tags)} total vs {len(unique_updated)} unique")
                    duplicates = [name for name in updated_tags if updated_tags.count(name) > 1]
                    print(f"   - Duplicate tags in response: {duplicates}")
                    return False
                else:
                    print("✅ No duplication in API response")
            else:
                print("❌ Order update failed")
                return False
        else:
            print(f"❌ Order update failed with status {response.status_code}")
            return False
        
        # Test 4: Get selected tags again to check for persistence issues
        print("\n4. Checking selected tags after order update...")
        response = requests.get(f"{base_url}/api/selected-tags", timeout=10)
        if response.status_code == 200:
            final_selected = response.json()
            if isinstance(final_selected, list):
                final_count = len(final_selected)
                final_tag_names = [tag.get('Product Name*', '') if isinstance(tag, dict) else str(tag) for tag in final_selected]
            else:
                final_count = len(final_selected.get('selected_tags', []))
                final_tag_names = [tag.get('Product Name*', '') if isinstance(tag, dict) else str(tag) for tag in final_selected.get('selected_tags', [])]
            
            print(f"   - Final selected tags: {final_count}")
            print(f"   - Final tag names: {final_tag_names}")
            
            final_unique = set(final_tag_names)
            if len(final_tag_names) != len(final_unique):
                print(f"❌ PERSISTENT DUPLICATION: {len(final_tag_names)} total vs {len(final_unique)} unique")
                duplicates = [name for name in final_tag_names if final_tag_names.count(name) > 1]
                print(f"   - Persistent duplicate tags: {duplicates}")
                return False
            else:
                print("✅ No persistent duplication detected")
        else:
            print("❌ Could not get final selected tags")
            return False
        
        # Test 5: Test clear operation to reset state
        print("\n5. Testing clear operation...")
        response = requests.post(f"{base_url}/api/clear-filters", 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                cleared_tags = data.get('selected_tags', [])
                print(f"   - Cleared tags count: {len(cleared_tags)}")
                if len(cleared_tags) == 0:
                    print("✅ Clear operation successful")
                else:
                    print(f"❌ Clear operation failed - still have {len(cleared_tags)} tags")
                    return False
            else:
                print("❌ Clear operation failed")
                return False
        else:
            print(f"❌ Clear operation failed with status {response.status_code}")
            return False
        
        print("\n=== ALL TESTS PASSED ===")
        print("✅ No tag duplication issues detected!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the application is running on port 9090.")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Server might be overloaded.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_backend_duplication_logic():
    """Test the backend logic for handling duplicates."""
    
    print("\n=== TESTING BACKEND DUPLICATION LOGIC ===")
    
    base_url = "http://127.0.0.1:9090"
    
    try:
        # Test 1: Send order with duplicates and see how backend handles it
        print("\n1. Testing backend duplicate handling...")
        
        # First, get some available tags to work with
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        if response.status_code == 200:
            available_tags = response.json()
            if len(available_tags) > 0:
                # Take first 3 tags and create a duplicate order
                test_tags = available_tags[:3]
                tag_names = [tag.get('Product Name*', '') for tag in test_tags if tag.get('Product Name*')]
                
                if len(tag_names) >= 2:
                    # Create order with duplicates
                    duplicate_order = tag_names + tag_names  # Duplicate the entire list
                    print(f"   - Test order with duplicates: {duplicate_order}")
                    
                    response = requests.post(f"{base_url}/api/update-selected-order", 
                                           headers={'Content-Type': 'application/json'},
                                           json={'order': duplicate_order},
                                           timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            result_tags = data.get('selected_tags', [])
                            print(f"   - Backend result: {result_tags}")
                            
                            # Check if backend deduplicated
                            unique_result = list(dict.fromkeys(result_tags))  # Preserve order
                            if len(result_tags) == len(unique_result):
                                print("✅ Backend properly deduplicated tags")
                            else:
                                print(f"❌ Backend did not deduplicate: {len(result_tags)} vs {len(unique_result)} unique")
                                return False
                        else:
                            print("❌ Backend order update failed")
                            return False
                    else:
                        print(f"❌ Backend order update failed with status {response.status_code}")
                        return False
                else:
                    print("❌ Not enough tags available for testing")
                    return False
            else:
                print("❌ No available tags for testing")
                return False
        else:
            print("❌ Could not get available tags")
            return False
        
        print("✅ Backend duplication logic test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing backend logic: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Drag and Drop Duplication Tests...")
    
    # Test basic duplication detection
    basic_success = test_drag_drop_duplication()
    
    # Test backend logic
    backend_success = test_backend_duplication_logic()
    
    if basic_success and backend_success:
        print("\n🎉 ALL DUPLICATION TESTS PASSED!")
        print("No tag duplication issues detected in drag and drop functionality.")
    else:
        print("\n❌ DUPLICATION ISSUES DETECTED!")
        print("There may be problems with tag duplication in the drag and drop system.")
        
        if not basic_success:
            print("- Basic duplication detection failed")
        if not backend_success:
            print("- Backend duplication logic has issues") 