#!/usr/bin/env python3
"""
Test script to verify API endpoints are working correctly and diagnose 500 errors.
"""

import requests
import json
import time

def test_api_endpoints():
    """Test the API endpoints to ensure they're working correctly."""
    base_url = "http://127.0.0.1:5001"
    
    print("Testing API endpoints...")
    
    # Test /api/initial-data endpoint
    try:
        print(f"Testing {base_url}/api/initial-data...")
        response = requests.get(f"{base_url}/api/initial-data", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success: {data.get('success', False)}")
            print(f"✓ Message: {data.get('message', 'No message')}")
            print(f"✓ Total records: {data.get('total_records', 0)}")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection error - server not running")
        return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def test_server_startup():
    """Test if the server can start up correctly."""
    print("\nTesting server startup...")
    
    try:
        import app
        print("✓ Flask app imported successfully")
        
        # Check if the flags are set correctly
        print(f"✓ DISABLE_STARTUP_FILE_LOADING: {app.DISABLE_STARTUP_FILE_LOADING}")
        print(f"✓ LAZY_LOADING_ENABLED: {app.LAZY_LOADING_ENABLED}")
        
        return True
    except Exception as e:
        print(f"✗ Error importing app: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("API ENDPOINT TEST")
    print("=" * 50)
    
    # Test server startup
    if test_server_startup():
        print("\n✓ Server startup test passed")
    else:
        print("\n✗ Server startup test failed")
        exit(1)
    
    # Test API endpoints
    if test_api_endpoints():
        print("\n✓ API endpoint test passed")
    else:
        print("\n✗ API endpoint test failed")
        print("\nPossible solutions:")
        print("1. Make sure the server is running: python3 app.py")
        print("2. Check if port 5001 is available")
        print("3. Restart the server to apply the latest changes") 