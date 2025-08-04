#!/usr/bin/env python3
"""
Test script to check upload status and debug the "Finalizing upload..." issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time

def test_upload_status():
    """Test the upload status endpoint to see what's happening."""
    
    print("=== Testing Upload Status ===")
    
    # Test the upload status endpoint
    try:
        response = requests.get('http://localhost:9090/api/upload-status?filename=test.xlsx')
        print(f"Upload status response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Upload status data: {json.dumps(data, indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error testing upload status: {e}")
    
    # Test the debug upload status endpoint
    try:
        response = requests.get('http://localhost:9090/api/debug-upload-status')
        print(f"\nDebug upload status response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Debug upload status data: {json.dumps(data, indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error testing debug upload status: {e}")
    
    # Test the available tags endpoint
    try:
        response = requests.get('http://localhost:5000/api/available-tags')
        print(f"\nAvailable tags response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Available tags count: {len(data) if isinstance(data, list) else 'Not a list'}")
            if isinstance(data, list) and len(data) > 0:
                print(f"First tag: {data[0]}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error testing available tags: {e}")
    
    # Test the selected tags endpoint
    try:
        response = requests.get('http://localhost:5000/api/selected-tags')
        print(f"\nSelected tags response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Selected tags count: {len(data) if isinstance(data, list) else 'Not a list'}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error testing selected tags: {e}")

if __name__ == "__main__":
    test_upload_status() 