#!/usr/bin/env python3
"""
Test to debug frontend JSON matching behavior.
"""

import requests
import json
import time

def test_json_frontend_debug():
    """Test to see what's happening in the frontend when JSON matching completes."""
    
    print("🔍 Debugging Frontend JSON Matching Behavior")
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
            match_result = response.json()
            print("✅ JSON matching successful!")
            print(f"   Matched count: {match_result.get('matched_count', 0)}")
            print(f"   Available tags: {len(match_result.get('available_tags', []))}")
            print(f"   Selected tags: {len(match_result.get('selected_tags', []))}")
            
            # Check if selected_tags contains all Excel products
            selected_tags = match_result.get('selected_tags', [])
            if len(selected_tags) > 20:  # More than expected JSON matched products
                print(f"⚠️  WARNING: {len(selected_tags)} selected tags (expected ~14)")
                print("   This suggests all Excel products are being selected!")
                
                # Show first few selected tags
                print("   First 5 selected tags:")
                for i, tag in enumerate(selected_tags[:5]):
                    tag_name = tag.get('Product Name*', tag.get('ProductName', 'Unknown'))
                    source = tag.get('Source', 'Unknown')
                    print(f"     {i+1}. {tag_name} (Source: {source})")
                
                # Check if they're all Excel products
                excel_products = [tag for tag in selected_tags if tag.get('Source', '').startswith('Excel')]
                print(f"   Excel products in selected tags: {len(excel_products)}")
                
                if len(excel_products) == len(selected_tags):
                    print("   ❌ CONFIRMED: All selected tags are Excel products!")
                    print("   This means the frontend is selecting all Excel products instead of JSON matched products.")
                else:
                    print("   Mixed sources in selected tags")
            else:
                print("   ✅ Selected tags count looks reasonable")
            
            # Check available_tags
            available_tags = match_result.get('available_tags', [])
            print(f"\n📋 Available tags analysis:")
            print(f"   Total available tags: {len(available_tags)}")
            
            if len(available_tags) > 20:
                print("   ⚠️  WARNING: More available tags than expected JSON matched products")
                
                # Check sources of available tags
                sources = {}
                for tag in available_tags:
                    source = tag.get('Source', 'Unknown')
                    sources[source] = sources.get(source, 0) + 1
                
                print("   Sources in available tags:")
                for source, count in sources.items():
                    print(f"     {source}: {count}")
                
                # Check if available_tags contains all Excel products
                excel_products = [tag for tag in available_tags if tag.get('Source', '').startswith('Excel')]
                if len(excel_products) > 1000:  # Likely all Excel products
                    print(f"   ❌ CONFIRMED: Available tags contains {len(excel_products)} Excel products!")
                    print("   This means the frontend is showing all Excel products instead of just JSON matched products.")
            else:
                print("   ✅ Available tags count looks reasonable")
            
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_json_frontend_debug()
