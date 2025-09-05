#!/usr/bin/env python3
"""
Test script to check matching scores for JSON products
"""

import requests
import json
import base64

def test_matching_scores():
    base_url = "http://127.0.0.1:5003"
    
    print("🔍 Testing Matching Scores for JSON Products")
    print("=" * 50)
    
    # Create test JSON with products that should be new (including generic names)
    test_json = {
        "inventory_transfer_items": [
            {
                "name": "Live Resin by Oleum",  # Generic name that might match existing products
                "vendor": "Oleum",
                "brand": "Oleum",
                "strain_name": "Blue Dream",
                "inventory_type": "vape_cartridge",
                "unit_weight": "1",
                "price": "25"
            },
            {
                "name": "Disposable Vape by Oleum",  # Generic name that might match existing products
                "vendor": "Oleum",
                "brand": "Oleum",
                "strain_name": "Wedding Cake",
                "inventory_type": "vape_cartridge",
                "unit_weight": "1",
                "price": "30"
            },
            {
                "name": "Honey Crystal by Oleum",  # Generic name that might match existing products
                "vendor": "Oleum",
                "brand": "Oleum",
                "strain_name": "Blue Dream",
                "inventory_type": "concentrate",
                "unit_weight": "1",
                "price": "40"
            }
        ],
        "from_license_name": "Oleum"
    }
    
    # Convert to data URL
    json_str = json.dumps(test_json)
    data_url = f"data:application/json;base64,{base64.b64encode(json_str.encode()).decode()}"
    
    print("📦 Testing JSON matching with unique products...")
    try:
        response = requests.post(
            f"{base_url}/api/json-match",
            json={"url": data_url},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON matching successful!")
            print(f"   Matched count: {result.get('matched_count', 0)}")
            print(f"   Available tags: {result.get('available_tags', [])}")
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error during JSON matching: {e}")
        return

if __name__ == "__main__":
    test_matching_scores()
