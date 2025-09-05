#!/usr/bin/env python3
"""
Debug cache to see what's happening with JSON matched products.
"""

import requests
import json

def test_cache_debug():
    """Debug what's in the cache after JSON matching."""
    
    print("🔍 Debugging Cache After JSON Matching")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5003"
    json_url = "https://files.cultivera.com/435553542D5753353635/Interop/25/34/GFJZZ9ZJQKVBWQDR/Cultivera_ORD-11766_422044.json"
    
    try:
        # Step 1: Perform JSON matching
        print("📦 Step 1: Performing JSON matching...")
        response = requests.post(
            f"{base_url}/api/json-match",
            json={"url": json_url},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON matching successful!")
            print(f"   Matched count: {result.get('matched_count', 0)}")
            print(f"   Available tags: {len(result.get('available_tags', []))}")
            print(f"   Selected tags: {len(result.get('selected_tags', []))}")
            
            # Step 2: Check available tags endpoint
            print(f"\n📋 Step 2: Checking available tags endpoint...")
            response2 = requests.get(f"{base_url}/api/available-tags", timeout=30)
            
            if response2.status_code == 200:
                result2 = response2.json()
                if isinstance(result2, dict):
                    available_tags = result2.get('tags', [])
                else:
                    available_tags = result2
                
                print(f"✅ Available tags endpoint successful!")
                print(f"   Total available tags: {len(available_tags)}")
                
                # Look for JSON matched products
                json_matched_count = 0
                excel_match_count = 0
                for tag in available_tags:
                    if isinstance(tag, dict):
                        source = tag.get('Source', '')
                        if 'JSON Match' in source:
                            json_matched_count += 1
                        elif 'Excel Match' in source:
                            excel_match_count += 1
                
                print(f"   JSON matched products: {json_matched_count}")
                print(f"   Excel match products: {excel_match_count}")
                
                # Show sample products
                print(f"\n📋 Sample products from available tags:")
                for i, tag in enumerate(available_tags[:10], 1):
                    if isinstance(tag, dict):
                        product_name = tag.get('Product Name*', tag.get('ProductName', 'Unknown'))
                        source = tag.get('Source', 'Unknown')
                        print(f"   {i}. {product_name} (Source: {source})")
                
                # Step 3: Check session info
                print(f"\n🔧 Step 3: Checking session info...")
                response3 = requests.get(f"{base_url}/api/session-info", timeout=30)
                
                if response3.status_code == 200:
                    session_info = response3.json()
                    print(f"✅ Session info retrieved!")
                    print(f"   Current filter mode: {session_info.get('current_filter_mode', 'Unknown')}")
                    print(f"   JSON matched cache key: {session_info.get('json_matched_cache_key', 'None')}")
                    print(f"   Available tags cache key: {session_info.get('available_tags_cache_key', 'None')}")
                else:
                    print(f"❌ Session info failed: {response3.status_code}")
                
            else:
                print(f"❌ Available tags endpoint failed: {response2.status_code}")
                print(f"   Response: {response2.text}")
                
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_cache_debug()
