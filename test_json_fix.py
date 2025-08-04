#!/usr/bin/env python3
"""
Test to verify JSON matching properly updates available list.
"""

import requests
import json
import time

def test_json_fix():
    """Test that JSON matching properly updates the available list."""
    
    print("🧪 Testing JSON Matching Fix")
    print("=" * 40)
    
    base_url = "http://localhost:5001"
    
    try:
        # Step 1: Get initial available tags
        print("1. Getting initial available tags...")
        available_response = requests.get(f"{base_url}/api/available-tags")
        initial_available = available_response.json() if isinstance(available_response.json(), list) else []
        print(f"   Initial available tags: {len(initial_available)}")
        
        # Step 2: Perform JSON matching
        print("2. Performing JSON matching...")
        json_response = requests.post(f"{base_url}/api/json-match", 
                                    json={"url": "https://httpbin.org/json"})
        
        if json_response.status_code == 200:
            data = json_response.json()
            print(f"   ✅ JSON matching successful")
            print(f"   Matched count: {data.get('matched_count', 0)}")
            print(f"   Filter mode: {data.get('filter_mode', 'unknown')}")
            
            # Step 3: Check available tags after JSON matching
            print("3. Checking available tags after JSON matching...")
            time.sleep(2)  # Wait for processing
            
            available_response = requests.get(f"{base_url}/api/available-tags")
            post_available = available_response.json() if isinstance(available_response.json(), list) else []
            print(f"   Post-match available tags: {len(post_available)}")
            
            # Step 4: Check if the available list changed
            if len(post_available) != len(initial_available):
                print(f"   ✅ Available list changed: {len(initial_available)} -> {len(post_available)}")
                return True
            else:
                print(f"   ❌ Available list unchanged: {len(post_available)}")
                return False
        else:
            print(f"   ❌ JSON matching failed: {json_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_json_fix()
    if success:
        print("\n🎉 Test PASSED: JSON matching now properly updates available list!")
    else:
        print("\n💥 Test FAILED: Available list still showing default data.") 