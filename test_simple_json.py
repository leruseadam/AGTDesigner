#!/usr/bin/env python3
"""
Simple test to see what's happening with JSON data.
"""

import requests
import json

def test_simple_json():
    """Test simple JSON access."""
    
    print("=== SIMPLE JSON TEST ===")
    
    # Test the JSON URL directly
    test_url = "http://localhost:5000/test_products.json"
    
    try:
        print(f"1. Testing JSON URL: {test_url}")
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ JSON accessible, type: {type(data)}")
            print(f"   Length: {len(data)}")
            
            if data:
                print(f"   First item type: {type(data[0])}")
                print(f"   First item: {data[0]}")
                
                # Check if it's a list of dictionaries
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    print("   ✅ Data is a list of dictionaries")
                    
                    # Test accessing a field
                    first_item = data[0]
                    print(f"   First item keys: {list(first_item.keys())}")
                    
                    # Test .get() method
                    product_name = first_item.get('product_name', 'Not found')
                    print(f"   Product name: {product_name}")
                    
                else:
                    print(f"   ❌ Data is not a list of dictionaries")
                    print(f"   Data type: {type(data)}")
                    if data:
                        print(f"   First item type: {type(data[0])}")
            else:
                print("   ❌ Data is empty")
        else:
            print(f"   ❌ Failed to access JSON: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_simple_json() 