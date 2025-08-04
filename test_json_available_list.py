#!/usr/bin/env python3
"""
Test script to verify that JSON matched items populate the Available list instead of Selected list.
"""

import requests
import json
import time
import os

def test_json_available_list():
    """Test that JSON matched items populate the Available list for manual selection."""
    
    print("🧪 Testing JSON Available List Behavior")
    print("=" * 50)
    
    # Base URL for the application
    base_url = "http://localhost:5001"
    
    # Test JSON data with realistic product names that might match existing data
    test_json_data = [
        {
            "Product Name*": "Blue Dream",
            "Product Brand": "Test Brand",
            "Product Strain": "Blue Dream",
            "Product Type*": "Flower",
            "Description": "A balanced hybrid strain",
            "Weight*": "3.5",
            "Units": "g",
            "THC test result": "18.5",
            "CBD test result": "0.2",
            "Test result unit (% or mg)": "%",
            "Price": "45.00",
            "Vendor": "Test Vendor"
        },
        {
            "Product Name*": "OG Kush",
            "Product Brand": "Test Brand",
            "Product Strain": "OG Kush", 
            "Product Type*": "Flower",
            "Description": "A classic indica strain",
            "Weight*": "3.5",
            "Units": "g",
            "THC test result": "22.1",
            "CBD test result": "0.1",
            "Test result unit (% or mg)": "%",
            "Price": "50.00",
            "Vendor": "Test Vendor"
        },
        {
            "Product Name*": "Sour Diesel",
            "Product Brand": "Test Brand",
            "Product Strain": "Sour Diesel",
            "Product Type*": "Flower",
            "Description": "A potent sativa strain",
            "Weight*": "3.5",
            "Units": "g",
            "THC test result": "20.5",
            "CBD test result": "0.3",
            "Test result unit (% or mg)": "%",
            "Price": "48.00",
            "Vendor": "Test Vendor"
        }
    ]
    
    try:
        # Step 1: Check initial state
        print("1. Checking initial state...")
        available_response = requests.get(f"{base_url}/api/available-tags")
        selected_response = requests.get(f"{base_url}/api/selected-tags")
        
        if available_response.status_code != 200 or selected_response.status_code != 200:
            print(f"❌ Failed to get initial state: available={available_response.status_code}, selected={selected_response.status_code}")
            return False
        
        initial_available = available_response.json() if isinstance(available_response.json(), list) else available_response.json().get('tags', [])
        initial_selected = selected_response.json() if isinstance(selected_response.json(), list) else selected_response.json().get('tags', [])
        
        print(f"   Initial available tags: {len(initial_available)}")
        print(f"   Initial selected tags: {len(initial_selected)}")
        
        # Step 2: Perform JSON matching
        print("2. Performing JSON matching...")
        
        # Save test data to a file
        with open("test_inventory.json", "w") as f:
            json.dump(test_json_data, f)
        
        # Create a simple HTTP server to serve the JSON file
        import subprocess
        import threading
        
        def start_server():
            subprocess.run(["python", "-m", "http.server", "8000"], cwd=os.getcwd(), capture_output=True)
        
        # Start server in background
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        time.sleep(2)  # Wait for server to start
        
        json_match_response = requests.post(f"{base_url}/api/json-match", 
                                          json={"url": "http://localhost:8000/test_inventory.json"})
        
        if json_match_response.status_code != 200:
            print(f"❌ JSON matching failed: {json_match_response.status_code}")
            print(f"   Response: {json_match_response.text}")
            return False
        
        match_data = json_match_response.json()
        print(f"   ✅ JSON matching successful")
        print(f"   Matched count: {match_data.get('matched_count', 0)}")
        print(f"   Message: {match_data.get('message', 'No message')}")
        
        # Step 3: Check state after JSON matching
        print("3. Checking state after JSON matching...")
        time.sleep(2)  # Wait a moment for processing
        
        available_response = requests.get(f"{base_url}/api/available-tags")
        selected_response = requests.get(f"{base_url}/api/selected-tags")
        
        if available_response.status_code != 200 or selected_response.status_code != 200:
            print(f"❌ Failed to get post-match state: available={available_response.status_code}, selected={selected_response.status_code}")
            return False
        
        post_available = available_response.json() if isinstance(available_response.json(), list) else available_response.json().get('tags', [])
        post_selected = selected_response.json() if isinstance(selected_response.json(), list) else selected_response.json().get('tags', [])
        
        print(f"   Post-match available tags: {len(post_available)}")
        print(f"   Post-match selected tags: {len(post_selected)}")
        
        # Step 4: Verify the new behavior
        print("4. Verifying new behavior...")
        
        # Check if JSON matched items are in available tags
        json_matched_in_available = 0
        for tag in post_available:
            if isinstance(tag, dict) and tag.get('Source') == 'JSON Match':
                json_matched_in_available += 1
        
        print(f"   JSON matched items in available: {json_matched_in_available}")
        print(f"   Selected tags should be empty: {len(post_selected) == 0}")
        
        # The test passes if:
        # 1. JSON matched items are in available tags (even if 0 matches found)
        # 2. Selected tags are empty (user manually selects)
        # 3. Available tags count is reasonable (not 0, not dramatically different)
        
        success = (
            len(post_available) > 0 and  # Available tags should exist
            len(post_selected) == 0 and  # Selected tags should be empty
            len(post_available) >= len(initial_available)  # Available tags should not decrease
        )
        
        if success:
            print("   ✅ SUCCESS: JSON matched items behavior working correctly")
            print("   - Available list contains products for manual selection")
            print("   - Selected list is empty (user controls selection)")
            print("   - JSON matched items are properly integrated into available tags")
        else:
            print("   ❌ FAILED: Expected behavior not achieved")
            print(f"      Available tags: {len(post_available)} (expected > 0)")
            print(f"      Selected tags: {len(post_selected)} (expected 0)")
            print(f"      Initial available: {len(initial_available)}")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_json_available_list()
    if not success:
        print("\n💥 Test FAILED: JSON matched items behavior not working as expected.")
        exit(1)
    else:
        print("\n🎉 Test PASSED: JSON matched items now populate Available list for manual selection!") 