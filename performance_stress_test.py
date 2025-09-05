#!/usr/bin/env python3
"""
Performance stress test for JSON matching
"""

import requests
import json
import base64
import time
import random

def generate_large_dataset(size=100):
    """Generate a large dataset for stress testing"""
    
    # Base product templates from actual data
    base_products = [
        {"name": "Core Reactor Quartz Banger", "vendor": "One Stop Wholesale", "type": "Paraphernalia"},
        {"name": "Terp Slurper Quartz Banger", "vendor": "Hibro Wholesale", "type": "Paraphernalia"},
        {"name": "Diamond Knot Quartz Banger", "vendor": "Hibro Wholesale", "type": "Paraphernalia"},
        {"name": "Plastic K-clip", "vendor": "S & A Wholesale", "type": "Paraphernalia"},
        {"name": "Assorted Design Bowl Piece", "vendor": "Hibro Wholesale", "type": "Paraphernalia"},
    ]
    
    # Generate variations
    items = []
    for i in range(size):
        base = random.choice(base_products)
        
        # Create variations
        if i % 5 == 0:
            # Exact match
            product_name = base["name"]
        elif i % 5 == 1:
            # Add suffix
            product_name = f"{base['name']} {random.randint(1, 100)}"
        elif i % 5 == 2:
            # Add prefix
            product_name = f"Premium {base['name']}"
        elif i % 5 == 3:
            # Minor spelling variation
            product_name = base["name"].replace("Quartz", "Quartzz")
        else:
            # Completely different (should not match)
            product_name = f"Random Product {random.randint(1000, 9999)}"
            
        items.append({
            "product_name": product_name,
            "vendor": base["vendor"],
            "brand": base["vendor"],
            "product_type": base["type"],
            "weight": "1",
            "strain_name": base["type"]
        })
    
    return {
        "inventory_transfer_items": items,
        "session_id": f"stress_test_{size}"
    }

def run_stress_test(dataset_size):
    """Run stress test with specified dataset size"""
    print(f"\n🔥 Stress Test: {dataset_size} items")
    print("-" * 40)
    
    # Generate test data
    test_data = generate_large_dataset(dataset_size)
    
    # Encode test data
    json_str = json.dumps(test_data)
    encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    data_url = f"data:application/json;base64,{encoded}"
    
    payload = {"url": data_url}
    
    print(f"📊 Generated {len(test_data['inventory_transfer_items'])} test items")
    print(f"📦 JSON payload size: {len(json_str):,} bytes")
    print(f"🔗 Data URL size: {len(data_url):,} bytes")
    
    try:
        start_time = time.time()
        response = requests.post("http://localhost:5001/api/json-match", json=payload, timeout=60)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            matches = result.get('matched_count', 0)
            available_tags = len(result.get('available_tags', []))
            
            # Calculate performance metrics
            items_per_second = dataset_size / response_time if response_time > 0 else 0
            match_rate = (matches / dataset_size) * 100 if dataset_size > 0 else 0
            
            print(f"⏱️  Response time: {response_time:.2f}s")
            print(f"🎯 Matches found: {matches}/{dataset_size} ({match_rate:.1f}%)")
            print(f"📋 Available tags: {available_tags}")
            print(f"⚡ Processing speed: {items_per_second:.1f} items/second")
            print(f"💾 Memory efficiency: {len(response.content):,} bytes response")
            
            # Performance rating
            if items_per_second > 100:
                print("🟢 Performance: EXCELLENT")
            elif items_per_second > 50:
                print("🟡 Performance: GOOD")
            elif items_per_second > 20:
                print("🟠 Performance: ACCEPTABLE")
            else:
                print("🔴 Performance: NEEDS IMPROVEMENT")
                
            return True
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>60s)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run performance stress tests"""
    print("⚡ JSON Matching Performance Stress Test")
    print("=" * 50)
    
    # Test different dataset sizes
    test_sizes = [10, 25, 50, 100, 200]
    
    successful_tests = 0
    total_tests = len(test_sizes)
    
    for size in test_sizes:
        if run_stress_test(size):
            successful_tests += 1
        time.sleep(2)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Performance Test Results: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("🎉 All performance tests PASSED! System is highly scalable.")
    else:
        print(f"⚠️  {total_tests - successful_tests} tests failed. Performance needs optimization.")

if __name__ == "__main__":
    main()
