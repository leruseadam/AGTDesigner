#!/usr/bin/env python3
"""
Test script to verify that the upload and API endpoints are working correctly.
"""

import requests
import time
import os
import sys

def test_api_endpoints():
    """Test the main API endpoints to ensure they're working correctly."""
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 Testing API endpoints...")
    
    # Test 1: Initial data endpoint
    print("\n1. Testing /api/initial-data...")
    try:
        response = requests.get(f"{base_url}/api/initial-data")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', False)}")
            print(f"   Message: {data.get('message', 'No message')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Available tags endpoint
    print("\n2. Testing /api/available-tags...")
    try:
        response = requests.get(f"{base_url}/api/available-tags")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   Tags returned: {len(data)}")
            else:
                print(f"   Response: {data}")
        elif response.status_code == 202:
            print("   File is still being processed (expected for empty state)")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Selected tags endpoint
    print("\n3. Testing /api/selected-tags...")
    try:
        response = requests.get(f"{base_url}/api/selected-tags")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   Tags returned: {len(data)}")
            else:
                print(f"   Response: {data}")
        elif response.status_code == 202:
            print("   File is still being processed (expected for empty state)")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Filter options endpoint
    print("\n4. Testing /api/filter-options...")
    try:
        response = requests.get(f"{base_url}/api/filter-options")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Filters: {list(data.keys())}")
        elif response.status_code == 202:
            print("   File is still being processed (expected for empty state)")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: File upload endpoint
    print("\n5. Testing file upload...")
    try:
        # Create a simple test file
        test_file_path = "test_upload.xlsx"
        if not os.path.exists(test_file_path):
            print("   Creating test file...")
            # Create a minimal Excel file for testing
            import pandas as pd
            df = pd.DataFrame({
                'Product Name*': ['Test Product 1', 'Test Product 2'],
                'Brand': ['Test Brand', 'Test Brand'],
                'Product Type': ['Flower', 'Concentrate']
            })
            df.to_excel(test_file_path, index=False)
        
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/upload", files=files)
        
        print(f"   Upload Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Upload Success: {data.get('success', False)}")
            print(f"   Message: {data.get('message', 'No message')}")
            
            # Wait a moment for processing
            time.sleep(2)
            
            # Test available tags again
            print("\n6. Testing available tags after upload...")
            response = requests.get(f"{base_url}/api/available-tags")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   Tags returned: {len(data)}")
                else:
                    print(f"   Response: {data}")
            else:
                print(f"   Error: {response.text}")
        else:
            print(f"   Upload Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ API endpoint testing complete!")

if __name__ == "__main__":
    test_api_endpoints() 