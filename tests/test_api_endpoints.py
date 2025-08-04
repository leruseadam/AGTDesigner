#!/usr/bin/env python3
"""
Test the specific API endpoints that are failing
"""

import sys
import os
import json

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("=== Testing API Endpoints ===")

try:
    from app import app
    
    with app.test_client() as client:
        # Test each failing endpoint
        endpoints = [
            '/api/available-tags',
            '/api/selected-tags',
            '/api/filter-options'
        ]
        
        for endpoint in endpoints:
            print(f"\nTesting {endpoint}:")
            try:
                response = client.get(endpoint)
                print(f"  Status: {response.status_code}")
                print(f"  Content-Type: {response.content_type}")
                
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"  Data type: {type(data)}")
                    if isinstance(data, list):
                        print(f"  Items: {len(data)}")
                    elif isinstance(data, dict):
                        print(f"  Keys: {list(data.keys())}")
                else:
                    print(f"  Error response: {response.get_data(as_text=True)}")
                    
            except Exception as e:
                print(f"  Exception: {e}")
                import traceback
                traceback.print_exc()
                
except Exception as e:
    print(f"Failed to import app: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
