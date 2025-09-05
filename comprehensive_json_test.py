#!/usr/bin/env python3
"""
Comprehensive JSON matching test suite
"""

import requests
import json
import base64
import time

def create_test_scenarios():
    """Create various test scenarios for JSON matching"""
    
    scenarios = [
        {
            "name": "Exact Product Matches",
            "data": {
                "inventory_transfer_items": [
                    {
                        "product_name": "Core Reactor Quartz Banger",
                        "vendor": "One Stop Wholesale",
                        "brand": "One Stop Wholesale",
                        "product_type": "Paraphernalia"
                    },
                    {
                        "product_name": "Terp Slurper Quartz Banger", 
                        "vendor": "Hibro Wholesale",
                        "brand": "Hibro Wholesale",
                        "product_type": "Paraphernalia"
                    }
                ],
                "session_id": "test_exact"
            },
            "expected_matches": 2
        },
        {
            "name": "Partial Matches",
            "data": {
                "inventory_transfer_items": [
                    {
                        "product_name": "Quartz Banger",  # Partial name
                        "vendor": "One Stop Wholesale",
                        "product_type": "Paraphernalia"
                    },
                    {
                        "product_name": "Bowl Piece",  # Partial name
                        "vendor": "Hibro Wholesale", 
                        "product_type": "Paraphernalia"
                    }
                ],
                "session_id": "test_partial"
            },
            "expected_matches": 2  # Should find matches
        },
        {
            "name": "No Matches",
            "data": {
                "inventory_transfer_items": [
                    {
                        "product_name": "Non-existent Product XYZ",
                        "vendor": "Fake Vendor",
                        "product_type": "Unknown"
                    }
                ],
                "session_id": "test_no_match"
            },
            "expected_matches": 0
        },
        {
            "name": "Mixed Results",
            "data": {
                "inventory_transfer_items": [
                    {
                        "product_name": "Core Reactor Quartz Banger",  # Should match
                        "vendor": "One Stop Wholesale",
                        "product_type": "Paraphernalia"
                    },
                    {
                        "product_name": "Fake Product 123",  # Should not match
                        "vendor": "Fake Vendor",
                        "product_type": "Unknown"
                    },
                    {
                        "product_name": "Plastic K-clip",  # Should match
                        "vendor": "S & A Wholesale",
                        "product_type": "Paraphernalia"
                    }
                ],
                "session_id": "test_mixed"
            },
            "expected_matches": 2
        },
        {
            "name": "Large Dataset",
            "data": {
                "inventory_transfer_items": [
                    {
                        "product_name": f"Core Reactor Quartz Banger {i}",
                        "vendor": "One Stop Wholesale",
                        "product_type": "Paraphernalia"
                    } for i in range(20)  # 20 similar items
                ] + [
                    {
                        "product_name": "Terp Slurper Quartz Banger",
                        "vendor": "Hibro Wholesale",
                        "product_type": "Paraphernalia"
                    }
                ],
                "session_id": "test_large"
            },
            "expected_matches": 1  # Only the exact match should work
        }
    ]
    
    return scenarios

def encode_json_data(data):
    """Encode JSON data as base64 for data URL"""
    json_str = json.dumps(data)
    encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    return f"data:application/json;base64,{encoded}"

def run_test_scenario(scenario):
    """Run a single test scenario"""
    print(f"\n🧪 Testing: {scenario['name']}")
    print(f"📊 Expected matches: {scenario['expected_matches']}")
    
    # Encode the test data
    data_url = encode_json_data(scenario['data'])
    
    # Test payload
    payload = {"url": data_url}
    
    try:
        start_time = time.time()
        response = requests.post("http://localhost:5001/api/json-match", json=payload, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            actual_matches = result.get('matched_count', 0)
            
            print(f"⏱️  Response time: {end_time - start_time:.2f}s")
            print(f"✅ Status: {response.status_code}")
            print(f"🎯 Actual matches: {actual_matches}")
            print(f"📋 Available tags: {len(result.get('available_tags', []))}")
            
            # Validate results
            if actual_matches == scenario['expected_matches']:
                print(f"✅ PASS: Expected {scenario['expected_matches']}, got {actual_matches}")
                return True
            else:
                print(f"❌ FAIL: Expected {scenario['expected_matches']}, got {actual_matches}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def main():
    """Run comprehensive JSON matching tests"""
    print("🔬 Comprehensive JSON Matching Test Suite")
    print("=" * 50)
    
    scenarios = create_test_scenarios()
    passed = 0
    total = len(scenarios)
    
    for scenario in scenarios:
        if run_test_scenario(scenario):
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} scenarios passed")
    
    if passed == total:
        print("🎉 All tests PASSED! JSON matching is working correctly.")
    else:
        print(f"⚠️  {total - passed} tests FAILED. Need further investigation.")
    
    return passed == total

if __name__ == "__main__":
    main()
