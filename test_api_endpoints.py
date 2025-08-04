#!/usr/bin/env python3
"""
Test script to verify API endpoints are working correctly.
"""

import requests
import json

def test_api_endpoints():
    """Test the API endpoints to ensure they're working correctly."""
    base_url = "http://127.0.0.1:5001"
    
    print("Testing API endpoints...")
    
    # Test /api/initial-data endpoint
    try:
        response = requests.get(f"{base_url}/api/initial-data", timeout=10)
        print(f"✓ /api/initial-data - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success', False)}")
            print(f"  Message: {data.get('message', 'No message')}")
            print(f"  Total records: {data.get('total_records', 0)}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ /api/initial-data - Error: {e}")
    
    # Test /api/available-tags endpoint
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        print(f"✓ /api/available-tags - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Tags count: {len(data)}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ /api/available-tags - Error: {e}")
    
    # Test /api/health endpoint
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"✓ /api/health - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Status: {data.get('status', 'Unknown')}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ /api/health - Error: {e}")

if __name__ == "__main__":
    test_api_endpoints() 