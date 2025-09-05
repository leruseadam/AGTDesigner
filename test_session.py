#!/usr/bin/env python3
"""
Test script to check session management
"""

import requests
import json

def test_session():
    base_url = "http://127.0.0.1:5003"
    
    print("🔍 Testing Session Management")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Check initial session state
    print("📦 Step 1: Checking initial session state...")
    try:
        response = session.get(f"{base_url}/api/session-stats")
        if response.status_code == 200:
            initial_stats = response.json()
            print(f"✅ Initial session stats:")
            print(f"   Current filter mode: {initial_stats.get('current_filter_mode', 'Unknown')}")
            print(f"   JSON matched cache key: {initial_stats.get('json_matched_cache_key', 'None')}")
        else:
            print(f"❌ Initial session stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Initial session stats error: {e}")
    
    # Step 2: Perform JSON matching
    print("\n📦 Step 2: Performing JSON matching...")
    try:
        response = session.post(
            f"{base_url}/api/json-match",
            json={"url": "https://files.cultivera.com/435553542D5753353635/Interop/25/34/GFJZZ9ZJQKVBWQDR/Cultivera_ORD-11766_422044.json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON matching successful!")
            print(f"   Matched count: {result.get('matched_count', 'Unknown')}")
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ JSON matching error: {e}")
        return
    
    # Step 3: Check session state after JSON matching
    print("\n📦 Step 3: Checking session state after JSON matching...")
    try:
        response = session.get(f"{base_url}/api/session-stats")
        if response.status_code == 200:
            after_stats = response.json()
            print(f"✅ Session stats after JSON matching:")
            print(f"   Current filter mode: {after_stats.get('current_filter_mode', 'Unknown')}")
            print(f"   JSON matched cache key: {after_stats.get('json_matched_cache_key', 'None')}")
            print(f"   Available tags cache key: {after_stats.get('available_tags_cache_key', 'None')}")
        else:
            print(f"❌ Session stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Session stats error: {e}")
    
    # Step 4: Check available tags with same session
    print("\n📦 Step 4: Checking available tags with same session...")
    try:
        response = session.get(f"{base_url}/api/available-tags")
        if response.status_code == 200:
            available_tags = response.json()
            print(f"✅ Available tags with session:")
            print(f"   Total available tags: {len(available_tags)}")
            
            # Count JSON matched products
            json_matched_count = 0
            for tag in available_tags:
                if isinstance(tag, dict):
                    source = tag.get('Source', '')
                    if 'JSON' in source or 'Excel Match' in source:
                        json_matched_count += 1
            
            print(f"   JSON matched products: {json_matched_count}")
        else:
            print(f"❌ Available tags failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Available tags error: {e}")

if __name__ == "__main__":
    test_session()
