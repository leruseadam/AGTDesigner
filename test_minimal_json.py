#!/usr/bin/env python3
"""
Minimal test to isolate the JSON matcher issue
"""

import sys
import os
import requests
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_minimal_json():
    """Test with minimal JSON data to isolate the issue"""
    print("🧪 Testing Minimal JSON")
    print("=" * 50)
    
    # Test with a simple JSON structure
    test_data = {
        "inventory_transfer_items": [
            {
                "product_name": "Test Product",
                "strain_name": "Test Strain",
                "qty": 1
            }
        ]
    }
    
    try:
        # Test with Flask endpoint using JSON data directly
        print("Testing with minimal JSON data...")
        
        response = requests.post('http://127.0.0.1:9090/api/match-json-tags',
                               json=test_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Minimal JSON test successful")
            print(f"   Response: {result}")
        else:
            error_data = response.json()
            print(f"❌ Minimal JSON test failed: {error_data}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_simple_url():
    """Test with a simple URL that should work"""
    print("\n🧪 Testing Simple URL")
    print("=" * 50)
    
    # Test with a simple JSON URL
    simple_url = "https://httpbin.org/json"
    
    try:
        data = {'url': simple_url}
        response = requests.post('http://127.0.0.1:9090/api/json-match',
                               json=data,
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Simple URL test successful")
            print(f"   Response: {result}")
        else:
            error_data = response.json()
            print(f"❌ Simple URL test failed: {error_data}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_minimal_json()
    test_simple_url() 