#!/usr/bin/env python3
"""
Test script to verify that the session size issue is resolved.
"""

import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_session_size_fix():
    """Test that session size is kept small by using cache for large data."""
    
    print("🧪 Testing Session Size Fix")
    print("=" * 60)
    
    # Test URL - you can replace this with your actual JSON URL
    test_url = "https://api-trace.getbamboo.com/api/v1/inventory-transfers/12345"
    
    try:
        # Test 1: Check if the server is running
        print("\n1️⃣ Checking server status...")
        response = requests.get("http://127.0.0.1:9090/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not running: {e}")
        print("💡 Please start the server first with: python app.py")
        return
    
    # Test 2: Perform JSON matching to trigger session storage
    print("\n2️⃣ Performing JSON matching...")
    try:
        response = requests.post(
            "http://127.0.0.1:9090/api/json-match",
            json={"url": test_url},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ JSON matching completed successfully")
            print(f"   - Matched count: {data.get('matched_count', 0)}")
            print(f"   - Available tags: {len(data.get('available_tags', []))}")
            print(f"   - Selected tags: {len(data.get('selected_tags', []))}")
            print(f"   - Filter mode: {data.get('filter_mode', 'unknown')}")
            print(f"   - Has full Excel: {data.get('has_full_excel', False)}")
        else:
            print(f"❌ JSON matching failed with status code: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error during JSON matching: {e}")
        return
    
    # Test 3: Check filter status
    print("\n3️⃣ Checking filter status...")
    try:
        response = requests.get("http://127.0.0.1:9090/api/get-filter-status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Filter status retrieved successfully")
            print(f"   - Current mode: {data.get('current_mode', 'unknown')}")
            print(f"   - Has full Excel: {data.get('has_full_excel', False)}")
            print(f"   - Has JSON matched: {data.get('has_json_matched', False)}")
            print(f"   - JSON matched count: {data.get('json_matched_count', 0)}")
            print(f"   - Full Excel count: {data.get('full_excel_count', 0)}")
            print(f"   - Can toggle: {data.get('can_toggle', False)}")
        else:
            print(f"❌ Filter status failed with status code: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error getting filter status: {e}")
    
    # Test 4: Toggle filter mode
    print("\n4️⃣ Testing filter toggle...")
    try:
        response = requests.post(
            "http://127.0.0.1:9090/api/toggle-json-filter",
            json={"filter_mode": "toggle"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Filter toggle completed successfully")
            print(f"   - Previous mode: {data.get('previous_mode', 'unknown')}")
            print(f"   - New mode: {data.get('filter_mode', 'unknown')}")
            print(f"   - Mode name: {data.get('mode_name', 'unknown')}")
            print(f"   - Available count: {data.get('available_count', 0)}")
        else:
            print(f"❌ Filter toggle failed with status code: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error during filter toggle: {e}")
    
    # Test 5: Check session stats
    print("\n5️⃣ Checking session stats...")
    try:
        response = requests.get("http://127.0.0.1:9090/api/session-stats", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Session stats retrieved successfully")
            print(f"   - Session ID: {data.get('session_id', 'unknown')}")
            print(f"   - Session keys: {len(data.get('session_keys', []))}")
            print(f"   - Session size: {data.get('session_size', 'unknown')}")
            print(f"   - Cache keys: {len(data.get('cache_keys', []))}")
            
            # Check if session size is reasonable (should be small now)
            session_size = data.get('session_size', '0')
            if isinstance(session_size, str) and 'bytes' in session_size:
                size_value = int(session_size.split()[0])
                if size_value < 4000:  # Should be well under 4KB
                    print("✅ Session size is within acceptable limits")
                else:
                    print(f"⚠️  Session size might be too large: {session_size}")
            else:
                print(f"ℹ️  Session size info: {session_size}")
        else:
            print(f"❌ Session stats failed with status code: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error getting session stats: {e}")
    
    print("\n🎉 Session size fix test completed!")
    print("\n📋 Summary:")
    print("   - JSON matching should now use cache for large data")
    print("   - Session should only store small cache keys")
    print("   - Filter toggle should work with cached data")
    print("   - Session size should stay under 4KB limit")

if __name__ == "__main__":
    test_session_size_fix() 