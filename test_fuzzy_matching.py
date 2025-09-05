#!/usr/bin/env python3
"""
Test fuzzy matching behavior in detail
"""

import requests
import json
import base64

def test_fuzzy_behavior():
    """Test how fuzzy matching works with similar names"""
    
    test_data = {
        "inventory_transfer_items": [
            {
                "product_name": "Core Reactor Quartz Banger 1",  # Very similar to existing
                "vendor": "One Stop Wholesale",
                "product_type": "Paraphernalia"
            },
            {
                "product_name": "Core Reactor Quartz Banger",  # Exact match
                "vendor": "One Stop Wholesale", 
                "product_type": "Paraphernalia"
            }
        ],
        "session_id": "test_fuzzy"
    }
    
    # Encode test data
    json_str = json.dumps(test_data)
    encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    data_url = f"data:application/json;base64,{encoded}"
    
    payload = {"url": data_url}
    
    print("🔍 Testing Fuzzy Matching Behavior")
    print("=" * 40)
    print("Test items:")
    print("1. 'Core Reactor Quartz Banger 1' (fuzzy)")
    print("2. 'Core Reactor Quartz Banger' (exact)")
    
    try:
        response = requests.post("http://localhost:5001/api/json-match", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Response received")
            print(f"🎯 Matches found: {result.get('matched_count', 0)}")
            print(f"📋 Available tags: {len(result.get('available_tags', []))}")
            
            # Show details of matched items
            available_tags = result.get('available_tags', [])
            for i, tag in enumerate(available_tags):
                product_name = tag.get('Product Name*', 'Unknown')
                confidence = tag.get('Match Confidence', 'Unknown')
                vendor = tag.get('Vendor', 'Unknown')
                print(f"\nMatch {i+1}:")
                print(f"  📝 Product: {product_name}")
                print(f"  🏪 Vendor: {vendor}")
                print(f"  🎯 Confidence: {confidence}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_edge_cases():
    """Test various edge cases"""
    
    edge_cases = [
        {
            "name": "Empty Product Name",
            "data": {
                "inventory_transfer_items": [
                    {
                        "product_name": "",
                        "vendor": "One Stop Wholesale",
                        "product_type": "Paraphernalia"
                    }
                ],
                "session_id": "test_empty_name"
            }
        },
        {
            "name": "Special Characters",
            "data": {
                "inventory_transfer_items": [
                    {
                        "product_name": "Core Reactor Quartz Banger™",
                        "vendor": "One Stop Wholesale",
                        "product_type": "Paraphernalia"
                    }
                ],
                "session_id": "test_special_chars"
            }
        },
        {
            "name": "Case Insensitive",
            "data": {
                "inventory_transfer_items": [
                    {
                        "product_name": "CORE REACTOR QUARTZ BANGER",
                        "vendor": "ONE STOP WHOLESALE",
                        "product_type": "PARAPHERNALIA"
                    }
                ],
                "session_id": "test_case_insensitive"
            }
        },
        {
            "name": "Extra Whitespace",
            "data": {
                "inventory_transfer_items": [
                    {
                        "product_name": "  Core Reactor Quartz Banger  ",
                        "vendor": "  One Stop Wholesale  ",
                        "product_type": "  Paraphernalia  "
                    }
                ],
                "session_id": "test_whitespace"
            }
        }
    ]
    
    print("\n🧪 Testing Edge Cases")
    print("=" * 40)
    
    for test_case in edge_cases:
        print(f"\n🔍 {test_case['name']}")
        
        # Encode test data
        json_str = json.dumps(test_case['data'])
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        data_url = f"data:application/json;base64,{encoded}"
        
        payload = {"url": data_url}
        
        try:
            response = requests.post("http://localhost:5001/api/json-match", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                matches = result.get('matched_count', 0)
                print(f"  ✅ Matches: {matches}")
                
                if matches > 0:
                    available_tags = result.get('available_tags', [])
                    if available_tags:
                        first_match = available_tags[0]
                        product_name = first_match.get('Product Name*', 'Unknown')
                        confidence = first_match.get('Match Confidence', 'Unknown')
                        print(f"  📝 Found: {product_name} (confidence: {confidence})")
            else:
                print(f"  ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    test_fuzzy_behavior()
    test_edge_cases()
