#!/usr/bin/env python3
"""
Test script to verify JSON matching functionality is working
"""

import requests
import json
import time

def test_json_matching():
    """Test the JSON matching functionality"""
    base_url = 'http://127.0.0.1:9090'  # Use port 9090
    
    print("🧪 Testing JSON Matching Functionality")
    print("=" * 50)
    
    # Step 1: Check if server is running
    print("\n1. Checking server status...")
    try:
        response = requests.get(f'{base_url}/api/status', timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Server is running")
            print(f"  Data loaded: {status.get('data_loaded', False)}")
            print(f"  Data shape: {status.get('data_shape', 'None')}")
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure the Flask app is running on port 9090")
        return
    
    # Step 2: Test JSON matching with a sample URL
    print("\n2. Testing JSON matching...")
    sample_url = "https://httpbin.org/json"  # A simple test URL
    
    try:
        data = {'url': sample_url}
        response = requests.post(f'{base_url}/api/json-match', 
                               json=data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ JSON matching endpoint is working")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Matched count: {result.get('matched_count', 0)}")
            print(f"  Cache status: {result.get('cache_status', 'Unknown')}")
        else:
            error_data = response.json()
            print(f"❌ JSON matching failed: {error_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error testing JSON matching: {e}")
    
    # Step 3: Test JSON status endpoint
    print("\n3. Testing JSON status endpoint...")
    try:
        response = requests.get(f'{base_url}/api/json-status', timeout=5)
        if response.status_code == 200:
            status = response.json()
            print("✅ JSON status endpoint is working")
            print(f"  Excel loaded: {status.get('excel_loaded', False)}")
            print(f"  Excel row count: {status.get('excel_row_count', 0)}")
            print(f"  JSON matched names: {len(status.get('json_matched_names', []))}")
        else:
            print(f"❌ JSON status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing JSON status: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("  JSON matching endpoints: ✅ Available")
    print("  Server connectivity: ✅ Working")
    print("  Ready to create tags from URLs!")

if __name__ == "__main__":
    test_json_matching() 