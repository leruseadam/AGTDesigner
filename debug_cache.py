#!/usr/bin/env python3
"""
Debug script to check cache and filter mode.
"""

import requests
import json

def debug_cache():
    """Debug cache and filter mode."""
    
    print("🔍 Debug Cache and Filter Mode")
    print("=" * 40)
    
    base_url = "http://localhost:5001"
    
    try:
        # Check initial state
        print("1. Initial state...")
        available_response = requests.get(f"{base_url}/api/available-tags")
        initial_available = available_response.json() if isinstance(available_response.json(), list) else []
        print(f"   Available tags: {len(initial_available)}")
        
        # Check filter status
        filter_response = requests.get(f"{base_url}/api/get-filter-status")
        if filter_response.status_code == 200:
            filter_data = filter_response.json()
            print(f"   Filter mode: {filter_data.get('current_mode', 'unknown')}")
            print(f"   Has full Excel: {filter_data.get('has_full_excel', False)}")
            print(f"   Has JSON matched: {filter_data.get('has_json_matched', False)}")
        
        # Perform JSON matching
        print("\n2. Performing JSON matching...")
        json_response = requests.post(f"{base_url}/api/json-match", 
                                    json={"url": "https://httpbin.org/json"})
        
        if json_response.status_code == 200:
            data = json_response.json()
            print(f"   ✅ JSON matching successful")
            print(f"   Matched count: {data.get('matched_count', 0)}")
            print(f"   Filter mode: {data.get('filter_mode', 'unknown')}")
            print(f"   Has full Excel: {data.get('has_full_excel', False)}")
            
            # Check filter status after JSON matching
            print("\n3. Filter status after JSON matching...")
            filter_response = requests.get(f"{base_url}/api/get-filter-status")
            if filter_response.status_code == 200:
                filter_data = filter_response.json()
                print(f"   Filter mode: {filter_data.get('filter_mode', 'unknown')}")
                print(f"   Has full Excel: {filter_data.get('has_full_excel', False)}")
                print(f"   Has JSON matched: {filter_data.get('has_json_matched', False)}")
            
            # Check available tags
            print("\n4. Available tags after JSON matching...")
            available_response = requests.get(f"{base_url}/api/available-tags")
            post_available = available_response.json() if isinstance(available_response.json(), list) else []
            print(f"   Available tags: {len(post_available)}")
            
            if len(post_available) != len(initial_available):
                print(f"   ✅ Available list changed!")
            else:
                print(f"   ❌ Available list unchanged")
                
                # Check if we're getting the right filter mode
                print(f"   Expected filter mode: json_matched")
                print(f"   Actual filter mode: {filter_data.get('current_mode', 'unknown')}")
                
        else:
            print(f"   ❌ JSON matching failed: {json_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Debug error: {e}")

if __name__ == "__main__":
    debug_cache() 