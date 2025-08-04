#!/usr/bin/env python3
"""
Test script to verify that drag and drop duplication issues have been fixed.
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

def test_drag_drop_fix():
    """Test that drag and drop duplication issues have been fixed."""
    
    print("=== TESTING DRAG AND DROP DUPLICATION FIX ===")
    
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
        
        # Test 2: Get available tags to work with
        print("\n2. Getting available tags...")
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        if response.status_code == 200:
            available_tags = response.json()
            print(f"   - Available tags: {len(available_tags)}")
            
            if len(available_tags) < 3:
                print("❌ Not enough available tags for testing")
                return False
        else:
            print("❌ Could not get available tags")
            return False
        
        # Test 3: Move some tags to selected
        print("\n3. Moving tags to selected...")
        test_tags = available_tags[:3]
        tag_names = [tag.get('Product Name*', '') for tag in test_tags if tag.get('Product Name*')]
        
        if len(tag_names) < 2:
            print("❌ Not enough valid tag names for testing")
            return False
        
        # Move tags to selected
        response = requests.post(f"{base_url}/api/move-tags", 
                               headers={'Content-Type': 'application/json'},
                               json={'tags': tag_names, 'direction': 'to_selected'},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   - Moved {len(tag_names)} tags to selected")
            else:
                print("❌ Failed to move tags to selected")
                return False
        else:
            print(f"❌ Move tags failed with status {response.status_code}")
            return False
        
        # Test 4: Check selected tags for duplicates
        print("\n4. Checking selected tags for duplicates...")
        response = requests.get(f"{base_url}/api/selected-tags", timeout=10)
        if response.status_code == 200:
            selected_data = response.json()
            if isinstance(selected_data, list):
                selected_tags = selected_data
            else:
                selected_tags = selected_data.get('selected_tags', [])
            
            print(f"   - Selected tags count: {len(selected_tags)}")
            
            # Check for duplicates
            if len(selected_tags) == 0:
                selected_names = []
            elif isinstance(selected_tags[0], dict):
                selected_names = [tag.get('Product Name*', '') for tag in selected_tags]
            else:
                selected_names = [str(tag) for tag in selected_tags]
            
            unique_names = list(dict.fromkeys(selected_names))  # Preserve order
            
            if len(selected_names) != len(unique_names):
                print(f"❌ DUPLICATION DETECTED: {len(selected_names)} total vs {len(unique_names)} unique")
                duplicates = [name for name in selected_names if selected_names.count(name) > 1]
                print(f"   - Duplicate tags: {duplicates}")
                return False
            else:
                print("✅ No duplication detected in selected tags")
        else:
            print("❌ Could not get selected tags")
            return False
        
        # Test 5: Test order update with potential duplicates
        print("\n5. Testing order update with potential duplicates...")
        
        # Create an order with duplicates
        duplicate_order = selected_names + selected_names  # Duplicate the entire list
        print(f"   - Test order with duplicates: {duplicate_order}")
        
        response = requests.post(f"{base_url}/api/update-selected-order", 
                               headers={'Content-Type': 'application/json'},
                               json={'order': duplicate_order},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result_tags = data.get('selected_tags', [])
                print(f"   - Backend result count: {len(result_tags)}")
                print(f"   - Backend result: {result_tags}")
                
                # Check if backend properly handled duplicates
                unique_result = list(dict.fromkeys(result_tags))  # Preserve order
                if len(result_tags) == len(unique_result):
                    print("✅ Backend properly handled duplicates")
                else:
                    print(f"❌ Backend did not handle duplicates properly: {len(result_tags)} vs {len(unique_result)} unique")
                    return False
            else:
                print("❌ Order update failed")
                return False
        else:
            print(f"❌ Order update failed with status {response.status_code}")
            return False
        
        # Test 6: Check final state for duplicates
        print("\n6. Checking final state for duplicates...")
        response = requests.get(f"{base_url}/api/selected-tags", timeout=10)
        if response.status_code == 200:
            final_data = response.json()
            if isinstance(final_data, list):
                final_tags = final_data
            else:
                final_tags = final_data.get('selected_tags', [])
            
            print(f"   - Final selected tags count: {len(final_tags)}")
            
            # Check for duplicates in final state
            if len(final_tags) == 0:
                final_names = []
            elif isinstance(final_tags[0], dict):
                final_names = [tag.get('Product Name*', '') for tag in final_tags]
            else:
                final_names = [str(tag) for tag in final_tags]
            
            unique_final = list(dict.fromkeys(final_names))  # Preserve order
            
            if len(final_names) != len(unique_final):
                print(f"❌ FINAL DUPLICATION DETECTED: {len(final_names)} total vs {len(unique_final)} unique")
                duplicates = [name for name in final_names if final_names.count(name) > 1]
                print(f"   - Final duplicate tags: {duplicates}")
                return False
            else:
                print("✅ No final duplication detected")
        else:
            print("❌ Could not get final selected tags")
            return False
        
        # Test 7: Clear selected tags
        print("\n7. Clearing selected tags...")
        response = requests.post(f"{base_url}/api/clear-filters", 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                cleared_tags = data.get('selected_tags', [])
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
        print("✅ Drag and drop duplication issues have been fixed!")
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

if __name__ == "__main__":
    print("Starting Drag and Drop Fix Tests...")
    
    success = test_drag_drop_fix()
    
    if success:
        print("\n🎉 DRAG AND DROP FIX VERIFIED!")
        print("The drag and drop duplication issues have been resolved.")
    else:
        print("\n❌ DRAG AND DROP ISSUES PERSIST!")
        print("There may still be problems with tag duplication in the drag and drop system.") 