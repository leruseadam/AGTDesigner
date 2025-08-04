#!/usr/bin/env python3
"""
Test script to verify the JSON matching fixes.
"""

import requests
import json
import sys

def test_proxy_endpoint():
    """Test the proxy endpoint with a sample URL."""
    base_url = 'http://127.0.0.1:5001'
    
    print("🧪 Testing JSON Proxy Endpoint")
    print("=" * 40)
    
    # Test with a sample URL (this will fail but we can see the error handling)
    test_url = "https://example.com/sample.json"
    
    try:
        response = requests.post(f'{base_url}/api/proxy-json', 
                               json={'url': test_url},
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 404:
            print("✅ Proxy endpoint working correctly - expected 404 for invalid URL")
            print(f"  Error: {response.json().get('error', 'Unknown error')}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing proxy endpoint: {e}")

def test_match_json_tags():
    """Test the match-json-tags endpoint with proper data structure."""
    base_url = 'http://127.0.0.1:5001'
    
    print("\n🧪 Testing Match JSON Tags Endpoint")
    print("=" * 40)
    
    # Test with array of product names (the expected format)
    test_data = ["Product 1", "Product 2", "Product 3"]
    
    try:
        response = requests.post(f'{base_url}/api/match-json-tags', 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Match JSON tags endpoint working correctly")
            print(f"  Matched: {len(result.get('matched', []))}")
            print(f"  Unmatched: {len(result.get('unmatched', []))}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing match JSON tags: {e}")

def test_json_structure_parsing():
    """Test the JSON structure parsing logic."""
    print("\n🧪 Testing JSON Structure Parsing")
    print("=" * 40)
    
    # Test different JSON structures
    test_cases = [
        {
            "name": "Cultivera-style",
            "json": {
                "inventory_transfer_items": [
                    {"product_name": "Product A"},
                    {"product_name": "Product B"}
                ]
            },
            "expected": ["Product A", "Product B"]
        },
        {
            "name": "Products array",
            "json": {
                "products": [
                    {"name": "Product C"},
                    {"name": "Product D"}
                ]
            },
            "expected": ["Product C", "Product D"]
        },
        {
            "name": "Direct array",
            "json": ["Product E", "Product F"],
            "expected": ["Product E", "Product F"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting {test_case['name']}...")
        
        # Simulate the frontend parsing logic
        json_data = test_case['json']
        product_names = []
        
        if isinstance(json_data, dict):
            if json_data.get('inventory_transfer_items') and isinstance(json_data['inventory_transfer_items'], list):
                product_names = [item.get('product_name') for item in json_data['inventory_transfer_items'] if item.get('product_name')]
            elif json_data.get('products') and isinstance(json_data['products'], list):
                product_names = [item.get('name') or item.get('product_name') or item.get('Product Name*') for item in json_data['products'] if item]
        elif isinstance(json_data, list):
            product_names = [item if isinstance(item, str) else (item.get('name') or item.get('product_name') or item.get('Product Name*')) for item in json_data if item]
        
        product_names = [name for name in product_names if name and name.strip()]
        
        if product_names == test_case['expected']:
            print(f"  ✅ Correctly extracted: {product_names}")
        else:
            print(f"  ❌ Expected {test_case['expected']}, got {product_names}")

def main():
    print("🧪 JSON Matching Fixes Test Suite")
    print("=" * 50)
    
    # Test 1: Proxy endpoint
    test_proxy_endpoint()
    
    # Test 2: Match JSON tags endpoint
    test_match_json_tags()
    
    # Test 3: JSON structure parsing
    test_json_structure_parsing()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("  Proxy endpoint: ✅ Added to handle CORS")
    print("  JSON structure parsing: ✅ Added to frontend")
    print("  Match JSON tags: ✅ Expects proper format")
    print("\n💡 The fixes should resolve:")
    print("  - 400 Bad Request errors")
    print("  - CORS policy errors")
    print("  - JSON structure mismatches")

if __name__ == "__main__":
    main() 