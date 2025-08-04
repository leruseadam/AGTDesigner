#!/usr/bin/env python3
"""
Simple test to verify JSON matching behavior.
"""

import requests
import json
import time

def test_json_behavior():
    """Test JSON matching behavior."""
    
    print("🧪 Simple JSON Behavior Test")
    print("=" * 40)
    
    base_url = "http://localhost:5001"
    
    try:
        # Check initial state
        print("1. Initial state...")
        available_response = requests.get(f"{base_url}/api/available-tags")
        selected_response = requests.get(f"{base_url}/api/selected-tags")
        
        initial_available = available_response.json() if isinstance(available_response.json(), list) else []
        initial_selected = selected_response.json() if isinstance(selected_response.json(), list) else []
        
        print(f"   Available: {len(initial_available)}")
        print(f"   Selected: {len(initial_selected)}")
        
        # Test JSON matching with a simple URL
        print("2. Testing JSON matching...")
        json_response = requests.post(f"{base_url}/api/json-match", 
                                    json={"url": "https://httpbin.org/json"})
        
        if json_response.status_code == 200:
            data = json_response.json()
            print(f"   ✅ JSON matching successful")
            print(f"   Matched count: {data.get('matched_count', 0)}")
            print(f"   Message: {data.get('message', 'No message')}")
            
            # Check if available tags were updated
            time.sleep(1)
            available_response = requests.get(f"{base_url}/api/available-tags")
            post_available = available_response.json() if isinstance(available_response.json(), list) else []
            
            print(f"   Post-match available: {len(post_available)}")
            print(f"   Available tags changed: {len(post_available) != len(initial_available)}")
            
            # Check if selected tags are empty
            selected_response = requests.get(f"{base_url}/api/selected-tags")
            post_selected = selected_response.json() if isinstance(selected_response.json(), list) else []
            
            print(f"   Post-match selected: {len(post_selected)}")
            print(f"   Selected tags empty: {len(post_selected) == 0}")
            
            success = len(post_selected) == 0 and len(post_available) > 0
            print(f"   ✅ Test {'PASSED' if success else 'FAILED'}")
            return success
        else:
            print(f"   ❌ JSON matching failed: {json_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        return False

if __name__ == "__main__":
    test_json_behavior() 