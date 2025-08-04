#!/usr/bin/env python3
"""
Test script to check performance issues with API endpoints.
"""
import requests
import time
import sys

def test_api_performance():
    """Test the performance of key API endpoints."""
    base_url = "http://127.0.0.1:5001"
    
    print("🚀 Testing API endpoint performance...")
    
    # Test 1: Initial data endpoint
    print("\n1. Testing /api/initial-data...")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/api/initial-data", timeout=10)
        elapsed = time.time() - start_time
        print(f"   Status: {response.status_code}")
        print(f"   Time: {elapsed:.2f}s")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', False)}")
        else:
            print(f"   Error: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print(f"   ❌ TIMEOUT after {time.time() - start_time:.2f}s")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Available tags endpoint
    print("\n2. Testing /api/available-tags...")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        elapsed = time.time() - start_time
        print(f"   Status: {response.status_code}")
        print(f"   Time: {elapsed:.2f}s")
        if response.status_code == 200:
            data = response.json()
            print(f"   Tags returned: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"   Error: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print(f"   ❌ TIMEOUT after {time.time() - start_time:.2f}s")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Health check
    print("\n3. Testing /api/health...")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        elapsed = time.time() - start_time
        print(f"   Status: {response.status_code}")
        print(f"   Time: {elapsed:.2f}s")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Performance test completed.")

if __name__ == "__main__":
    test_api_performance() 