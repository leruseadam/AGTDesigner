#!/usr/bin/env python3
"""
Test script for Cultivera JSON format
"""

import requests
import json

def test_cultivera_format():
    """Test the Cultivera JSON format parsing"""
    base_url = 'http://127.0.0.1:5001'
    
    print("🧪 Testing Cultivera JSON Format")
    print("=" * 40)
    
    # Sample Cultivera format JSON
    cultivera_json = {
        "inventory_transfer_items": [
            {
                "product_name": "Blue Dream Flower",
                "quantity": 10,
                "unit": "grams"
            },
            {
                "product_name": "OG Kush Pre-Roll",
                "quantity": 5,
                "unit": "each"
            },
            {
                "product_name": "CBD Tincture",
                "quantity": 2,
                "unit": "bottles"
            }
        ]
    }
    
    try:
        response = requests.post(f'{base_url}/api/match-json-tags', 
                               json=cultivera_json,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Cultivera format parsing successful")
            print(f"  Extracted names: {[item.get('product_name', '') for item in cultivera_json['inventory_transfer_items']]}")
            print(f"  Matched: {len(result.get('matched', []))}")
            print(f"  Unmatched: {len(result.get('unmatched', []))}")
        else:
            error = response.json()
            print(f"❌ Error: {error.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error testing Cultivera format: {e}")

def test_cultivera_url():
    """Test the actual Cultivera URL"""
    base_url = 'http://127.0.0.1:5001'
    
    print("\n🧪 Testing Cultivera URL")
    print("=" * 40)
    
    cultivera_url = "https://files.cultivera.com/435553542D57533130383235/Interop/25/16/3EGQ3216P7YSVJCF/Cultivera_ORD-5430_422044.json"
    
    try:
        # First test the proxy endpoint
        response = requests.post(f'{base_url}/api/proxy-json', 
                               json={'url': cultivera_url},
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            json_data = response.json()
            print("✅ Successfully fetched Cultivera JSON")
            print(f"  JSON keys: {list(json_data.keys())}")
            
            if 'inventory_transfer_items' in json_data:
                items = json_data['inventory_transfer_items']
                print(f"  Found {len(items)} inventory items")
                if items:
                    print(f"  Sample item: {items[0]}")
                    
                    # Extract product names
                    product_names = []
                    for item in items:
                        if isinstance(item, dict) and 'product_name' in item:
                            product_names.append(item['product_name'])
                    
                    print(f"  Product names: {product_names[:3]}...")
                    
                    # Test matching
                    match_response = requests.post(f'{base_url}/api/match-json-tags', 
                                                 json=product_names,
                                                 headers={'Content-Type': 'application/json'})
                    
                    if match_response.status_code == 200:
                        match_result = match_response.json()
                        print(f"  Matched: {len(match_result.get('matched', []))}")
                        print(f"  Unmatched: {len(match_result.get('unmatched', []))}")
                    else:
                        print(f"  Matching failed: {match_response.status_code}")
            else:
                print("❌ No inventory_transfer_items found in JSON")
        else:
            error = response.json()
            print(f"❌ Error fetching URL: {error.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error testing Cultivera URL: {e}")

if __name__ == "__main__":
    test_cultivera_format()
    test_cultivera_url() 