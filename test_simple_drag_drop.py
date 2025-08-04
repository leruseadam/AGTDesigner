#!/usr/bin/env python3
"""
Simple test to verify drag and drop duplication fix.
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

def test_simple_drag_drop():
    """Simple test for drag and drop duplication issues."""
    
    print("=== SIMPLE DRAG AND DROP DUPLICATION TEST ===")
    
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
        
        # Test 2: Test the backend order update with duplicates
        print("\n2. Testing backend duplicate handling...")
        
        # Create a test order with duplicates
        test_order = ["Tag1", "Tag2", "Tag1", "Tag3", "Tag2"]  # Contains duplicates
        print(f"   - Test order with duplicates: {test_order}")
        
        response = requests.post(f"{base_url}/api/update-selected-order", 
                               headers={'Content-Type': 'application/json'},
                               json={'order': test_order},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result_tags = data.get('selected_tags', [])
                print(f"   - Backend result: {result_tags}")
                
                # Check if backend properly deduplicated
                unique_result = list(dict.fromkeys(result_tags))  # Preserve order
                if len(result_tags) == len(unique_result):
                    print("✅ Backend properly deduplicated tags")
                else:
                    print(f"❌ Backend did not deduplicate: {len(result_tags)} vs {len(unique_result)} unique")
                    duplicates = [name for name in result_tags if result_tags.count(name) > 1]
                    print(f"   - Duplicate tags in result: {duplicates}")
                    return False
            else:
                print("❌ Order update failed")
                return False
        else:
            print(f"❌ Order update failed with status {response.status_code}")
            return False
        
        # Test 3: Test clear operation
        print("\n3. Testing clear operation...")
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
    print("Starting Simple Drag and Drop Test...")
    
    success = test_simple_drag_drop()
    
    if success:
        print("\n🎉 DRAG AND DROP FIX VERIFIED!")
        print("The drag and drop duplication issues have been resolved.")
    else:
        print("\n❌ DRAG AND DROP ISSUES PERSIST!")
        print("There may still be problems with tag duplication in the drag and drop system.") 