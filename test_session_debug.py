#!/usr/bin/env python3
"""
Test script to debug session storage and retrieval of selected tags.
"""

import requests
import json
import time

def test_session_debug():
    """Test session storage and retrieval of selected tags."""
    base_url = 'http://127.0.0.1:9090'
    json_url = 'https://files.cultivera.com/435553542D57533130383235/Interop/25/16/3EGQ3216P7YSVJCF/Cultivera_ORD-5430_422044.json'
    
    print("🔍 Testing Session Storage and Retrieval")
    print("=" * 50)
    
    # Step 1: Check if server is running
    try:
        response = requests.get(f'{base_url}/api/status', timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            return False
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Step 2: Get initial state
    print("\n2. Getting initial state...")
    try:
        response = requests.get(f'{base_url}/api/selected-tags')
        if response.status_code != 200:
            print("❌ Failed to get selected tags")
            return False
        
        initial_selected = response.json()
        initial_count = len(initial_selected) if isinstance(initial_selected, list) else 0
        print(f"✅ Initial selected tags: {initial_count}")
        
        if initial_selected:
            print("   First few selected tags:")
            for i, tag in enumerate(initial_selected[:3]):
                if isinstance(tag, dict):
                    name = tag.get('Product Name*', 'Unknown')
                else:
                    name = str(tag)
                print(f"   {i+1}. {name}")
        
    except Exception as e:
        print(f"❌ Error getting initial state: {e}")
        return False
    
    # Step 3: Perform JSON matching
    print("\n3. Performing JSON matching...")
    try:
        response = requests.post(f'{base_url}/api/json-match', 
                               json={'url': json_url},
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code != 200:
            error_data = response.json()
            print(f"❌ JSON matching failed: {error_data.get('error', 'Unknown error')}")
            return False
        
        match_result = response.json()
        print(f"✅ JSON matching successful!")
        print(f"   Matched count: {match_result.get('matched_count', 0)}")
        print(f"   Selected tags in response: {len(match_result.get('selected_tags', []))}")
        
        # Show some matched names
        matched_names = match_result.get('matched_names', [])
        if matched_names:
            print("   First few matched names:")
            for i, name in enumerate(matched_names[:3]):
                print(f"   {i+1}. {name}")
        
    except Exception as e:
        print(f"❌ Error during JSON matching: {e}")
        return False
    
    # Step 4: Check selected tags immediately after JSON match
    print("\n4. Checking selected tags immediately after JSON match...")
    try:
        time.sleep(1)  # Give the system time to update
        response = requests.get(f'{base_url}/api/selected-tags')
        if response.status_code != 200:
            print("❌ Failed to get selected tags after JSON match")
            return False
        
        immediate_selected = response.json()
        immediate_count = len(immediate_selected) if isinstance(immediate_selected, list) else 0
        print(f"✅ Selected tags after JSON match: {immediate_count}")
        
        if immediate_selected:
            print("   First few selected tags:")
            for i, tag in enumerate(immediate_selected[:3]):
                if isinstance(tag, dict):
                    name = tag.get('Product Name*', 'Unknown')
                else:
                    name = str(tag)
                print(f"   {i+1}. {name}")
        
        if immediate_count > initial_count:
            print(f"✅ Selected tags increased from {initial_count} to {immediate_count}")
            return True
        else:
            print(f"⚠️  Selected tags count unchanged: {initial_count} -> {immediate_count}")
            
    except Exception as e:
        print(f"❌ Error checking selected tags after JSON match: {e}")
        return False
    
    # Step 5: Check session status
    print("\n5. Checking session status...")
    try:
        response = requests.get(f'{base_url}/api/status')
        if response.status_code == 200:
            status = response.json()
            selected_count = status.get('selected_tags_count', 0)
            print(f"✅ Session status shows {selected_count} selected tags")
        else:
            print("❌ Failed to get session status")
            
    except Exception as e:
        print(f"❌ Error checking session status: {e}")
    
    return False

if __name__ == "__main__":
    test_session_debug() 