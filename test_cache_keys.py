#!/usr/bin/env python3
"""
Test script to check cache keys and data
"""

import requests
import json

def test_cache_keys():
    base_url = "http://127.0.0.1:5003"
    
    print("🔍 Testing Cache Keys and Data")
    print("=" * 50)
    
    # Step 1: Perform JSON matching to populate cache
    print("📦 Step 1: Performing JSON matching...")
    try:
        response = requests.post(
            f"{base_url}/api/json-match",
            json={"url": "https://files.cultivera.com/435553542D5753353635/Interop/25/34/GFJZZ9ZJQKVBWQDR/Cultivera_ORD-11766_422044.json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON matching successful!")
            print(f"   Matched count: {result.get('matched_count', 'Unknown')}")
            print(f"   Available tags: {len(result.get('available_tags', []))}")
            print(f"   Selected tags: {len(result.get('selected_tags', []))}")
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ JSON matching error: {e}")
        return
    
    # Step 2: Check session stats to see cache keys
    print("\n📋 Step 2: Checking session stats...")
    try:
        response = requests.get(f"{base_url}/api/session-stats")
        if response.status_code == 200:
            session_stats = response.json()
            print(f"✅ Session stats retrieved:")
            print(f"   Current filter mode: {session_stats.get('current_filter_mode', 'Unknown')}")
            print(f"   JSON matched cache key: {session_stats.get('json_matched_cache_key', 'None')}")
            print(f"   Available tags cache key: {session_stats.get('available_tags_cache_key', 'None')}")
            print(f"   Selected tags count: {session_stats.get('selected_tags_count', 'Unknown')}")
        else:
            print(f"❌ Session stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Session stats error: {e}")
    
    # Step 3: Check available tags endpoint
    print("\n📋 Step 3: Checking available tags endpoint...")
    try:
        response = requests.get(f"{base_url}/api/available-tags")
        if response.status_code == 200:
            available_tags = response.json()
            print(f"✅ Available tags endpoint successful!")
            print(f"   Total available tags: {len(available_tags)}")
            
            # Count JSON matched products
            json_matched_count = 0
            excel_count = 0
            for tag in available_tags:
                if isinstance(tag, dict):
                    source = tag.get('Source', '')
                    if 'JSON' in source or 'Excel Match' in source:
                        json_matched_count += 1
                    else:
                        excel_count += 1
            
            print(f"   JSON matched products: {json_matched_count}")
            print(f"   Excel products: {excel_count}")
            
            # Show sample products
            print(f"\n📋 Sample products from available tags:")
            for i, tag in enumerate(available_tags[:5]):
                if isinstance(tag, dict):
                    name = tag.get('Product Name*', tag.get('ProductName', 'Unknown'))
                    source = tag.get('Source', 'Unknown')
                    print(f"   {i+1}. {name} (Source: {source})")
        else:
            print(f"❌ Available tags failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Available tags error: {e}")

if __name__ == "__main__":
    test_cache_keys()
