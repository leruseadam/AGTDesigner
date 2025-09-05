#!/usr/bin/env python3
"""
Debug script to see what's happening with the real JSON URL processing.
"""

import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_real_json():
    """Debug the real JSON URL processing."""
    
    # The real JSON URL
    real_url = "https://files.cultivera.com/435553542D5753353635/Interop/25/34/GFJZZ9ZJQKVBWQDR/Cultivera_ORD-11766_422044.json"
    
    print("🔍 Debugging Real JSON URL Processing")
    print("=" * 50)
    
    # Step 1: Fetch the real JSON data
    print("📡 Step 1: Fetching real JSON data...")
    try:
        response = requests.get(real_url, timeout=30)
        response.raise_for_status()
        real_data = response.json()
        print(f"✅ Successfully fetched JSON data")
        print(f"   Type: {type(real_data)}")
        print(f"   Keys: {list(real_data.keys()) if isinstance(real_data, dict) else 'Not a dict'}")
        
        if isinstance(real_data, dict) and 'inventory_transfer_items' in real_data:
            items = real_data['inventory_transfer_items']
            print(f"   Found {len(items)} inventory transfer items")
            
            # Show the first few items
            print("\n📋 First 5 items from real JSON:")
            for i, item in enumerate(items[:5]):
                print(f"   {i+1}. {item.get('product_name', 'No name')}")
                
        else:
            print("❌ No inventory_transfer_items found in JSON")
            return
            
    except Exception as e:
        print(f"❌ Error fetching real JSON: {e}")
        return
    
    # Step 2: Test JSON matching with the real URL
    print("\n📡 Step 2: Testing JSON matching with real URL...")
    try:
        response = requests.post(
            "http://localhost:5001/api/json-match",
            json={"url": real_url},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON matching successful!")
            print(f"   Matched count: {result.get('matched_count', 0)}")
            
            # Check what products were actually created
            matched_products = result.get('json_matched_tags', [])
            print(f"   JSON matched products: {len(matched_products)}")
            
            print("\n📋 Products created by JSON matching:")
            for i, product in enumerate(matched_products[:10]):
                product_name = product.get('Product Name*', product.get('ProductName', 'Unknown'))
                source = product.get('Source', 'Unknown')
                print(f"   {i+1}. {product_name} (Source: {source})")
                
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during JSON matching: {e}")

if __name__ == "__main__":
    debug_real_json()
