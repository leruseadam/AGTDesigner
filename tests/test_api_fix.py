#!/usr/bin/env python3
"""
Test script to verify API endpoints are working correctly.
"""

import sys
import os
import requests
import json

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_api_endpoints():
    """Test the API endpoints to ensure they're working."""
    base_url = "http://127.0.0.1:5001"  # Default Flask development server
    
    print("=== Testing API Endpoints ===")
    
    # Test 1: Available tags endpoint
    print("\n1. Testing /api/available-tags...")
    try:
        response = requests.get(f"{base_url}/api/available-tags")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available tags endpoint working: {len(data)} tags returned")
        else:
            print(f"❌ Available tags endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing available tags: {e}")
    
    # Test 2: Selected tags endpoint
    print("\n2. Testing /api/selected-tags...")
    try:
        response = requests.get(f"{base_url}/api/selected-tags")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Selected tags endpoint working: {len(data)} tags returned")
        else:
            print(f"❌ Selected tags endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing selected tags: {e}")
    
    # Test 3: Filter options endpoint
    print("\n3. Testing /api/filter-options...")
    try:
        response = requests.get(f"{base_url}/api/filter-options")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Filter options endpoint working: {list(data.keys())}")
            for key, values in data.items():
                print(f"   - {key}: {len(values)} options")
        else:
            print(f"❌ Filter options endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing filter options: {e}")
    
    # Test 4: Debug columns endpoint
    print("\n4. Testing /api/debug-columns...")
    try:
        response = requests.get(f"{base_url}/api/debug-columns")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug columns endpoint working: {data.get('shape', 'Unknown shape')}")
            print(f"   - Columns: {len(data.get('columns', []))}")
        else:
            print(f"❌ Debug columns endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing debug columns: {e}")
    
    print("\n=== API Test Complete ===")

def test_default_file_loading():
    """Test that the default file loading is working."""
    print("\n=== Testing Default File Loading ===")
    
    try:
        from src.core.data.excel_processor import get_default_upload_file, ExcelProcessor
        
        # Test default file detection
        default_file = get_default_upload_file()
        if default_file:
            print(f"✅ Default file found: {default_file}")
            
            # Test loading the file
            excel_processor = ExcelProcessor()
            success = excel_processor.load_file(default_file)
            
            if success and excel_processor.df is not None:
                print(f"✅ Default file loaded successfully: {len(excel_processor.df)} records")
                
                # Test getting available tags
                try:
                    tags = excel_processor.get_available_tags()
                    print(f"✅ Available tags retrieved: {len(tags)} tags")
                except Exception as e:
                    print(f"❌ Error getting available tags: {e}")
                    
            else:
                print("❌ Failed to load default file")
        else:
            print("⚠️  No default file found - this is normal if no 'A Greener Today' file exists")
            
    except Exception as e:
        print(f"❌ Error testing default file loading: {e}")

if __name__ == "__main__":
    print("API Endpoint Test Script")
    print("Make sure the Flask server is running on http://127.0.0.1:5001")
    print()
    
    # Test default file loading first
    test_default_file_loading()
    
    # Test API endpoints
    test_api_endpoints() 