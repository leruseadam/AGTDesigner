#!/usr/bin/env python3
"""
Test script for JSON matching functionality
"""

import requests
import json
import sys

def test_json_status():
    """Test the JSON status endpoint"""
    try:
        response = requests.get('http://127.0.0.1:5000/api/json-status')
        if response.status_code == 200:
            status = response.json()
            print("✅ JSON Status:")
            print(f"  Excel loaded: {status['excel_loaded']}")
            print(f"  Excel columns: {status['excel_columns'][:5]}...")  # Show first 5 columns
            print(f"  Excel row count: {status['excel_row_count']}")
            print(f"  Sheet cache status: {status['sheet_cache_status']}")
            print(f"  JSON matched names: {len(status['json_matched_names'])}")
            return status
        else:
            print(f"❌ Failed to get JSON status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error testing JSON status: {e}")
        return None

def test_json_match(url):
    """Test JSON matching with a sample URL"""
    try:
        data = {'url': url}
        response = requests.post('http://127.0.0.1:5000/api/json-match', 
                               json=data, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ JSON Match successful:")
            print(f"  Matched count: {result['matched_count']}")
            print(f"  Cache status: {result.get('cache_status', 'Unknown')}")
            if result['matched_names']:
                print(f"  Sample matches: {result['matched_names'][:3]}...")
            return result
        else:
            error = response.json()
            print(f"❌ JSON Match failed: {error.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"❌ Error testing JSON match: {e}")
        return None

def main():
    print("🧪 Testing JSON Matching Functionality")
    print("=" * 50)
    
    # Test 1: Check JSON status
    print("\n1. Testing JSON Status...")
    status = test_json_status()
    
    if not status or not status['excel_loaded']:
        print("❌ No Excel data loaded. Please upload an Excel file first.")
        return
    
    # Test 2: Test with a sample JSON URL (you'll need to replace this with a real one)
    print("\n2. Testing JSON Match...")
    sample_url = "https://example.com/sample-inventory.json"  # Replace with real URL
    print(f"   Using sample URL: {sample_url}")
    print("   Note: This will fail unless you provide a real JSON URL")
    
    result = test_json_match(sample_url)
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"  Excel data: {'✅ Loaded' if status and status['excel_loaded'] else '❌ Not loaded'}")
    print(f"  Sheet cache: {'✅ Built' if status and 'Built' in status['sheet_cache_status'] else '❌ Not built'}")
    print(f"  JSON matching: {'✅ Working' if result else '❌ Failed'}")
    
    if not status or not status['excel_loaded']:
        print("\n💡 To fix JSON matching:")
        print("   1. Upload an Excel file through the web interface")
        print("   2. Ensure the Excel file has 'Product Name*' column")
        print("   3. Try the JSON matching again")

if __name__ == "__main__":
    main() 