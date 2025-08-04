#!/usr/bin/env python3
"""
Test script to debug upload issues.
This script tests the upload functionality directly to help identify problems.
"""

import os
import sys
import requests
from pathlib import Path

def test_upload_endpoint():
    """Test the upload endpoint directly."""
    print("=== Upload Endpoint Test ===\n")
    
    # Check if we have test files
    uploads_dir = Path("uploads")
    test_files = list(uploads_dir.glob("*.xlsx"))
    
    if not test_files:
        print("❌ No test files found in uploads/ directory")
        return False
    
    print(f"Found {len(test_files)} test file(s):")
    for i, file in enumerate(test_files, 1):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"{i}. {file.name} ({size_mb:.2f} MB)")
    
    # Use the first file for testing
    test_file = test_files[0]
    print(f"\nTesting with file: {test_file.name}")
    
    try:
        # Test the upload endpoint
        url = "http://localhost:9090/upload"
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print(f"Sending POST request to {url}...")
            response = requests.post(url, files=files)
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            try:
                data = response.json()
                print(f"Response data: {data}")
                
                if response.status_code == 200:
                    print("✅ Upload test successful!")
                    
                    # Test the upload status endpoint
                    filename = data.get('filename', test_file.name)
                    print(f"\nTesting upload status for: {filename}")
                    
                    status_url = f"http://localhost:9090/api/upload-status?filename={filename}"
                    status_response = requests.get(status_url)
                    
                    print(f"Status response: {status_response.status_code}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"Status data: {status_data}")
                        
                        # Poll for status changes
                        print("\nPolling for status changes...")
                        for i in range(10):
                            status_response = requests.get(status_url)
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                print(f"Poll {i+1}: {status_data}")
                                
                                if status_data.get('status') in ['ready', 'done']:
                                    print("✅ File processing completed!")
                                    break
                            else:
                                print(f"❌ Status check failed: {status_response.status_code}")
                            
                            import time
                            time.sleep(2)
                    
                    return True
                else:
                    print(f"❌ Upload test failed: {data.get('error', 'Unknown error')}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error parsing response: {e}")
                print(f"Response text: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error during upload test: {e}")
        return False

def test_upload_status_endpoint():
    """Test the upload status endpoint directly."""
    print("\n=== Upload Status Endpoint Test ===\n")
    
    # Test with a non-existent file
    test_filename = "test_file.xlsx"
    url = f"http://localhost:9090/api/upload-status?filename={test_filename}"
    
    try:
        response = requests.get(url)
        print(f"Status response for non-existent file: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status data: {data}")
            
            if data.get('status') == 'not_found':
                print("✅ Status endpoint working correctly for non-existent files")
                return True
            else:
                print(f"❌ Unexpected status: {data.get('status')}")
                return False
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing status endpoint: {e}")
        return False

def main():
    """Run all tests."""
    print("Starting upload debugging tests...\n")
    
    # Test 1: Upload endpoint
    test1_result = test_upload_endpoint()
    
    # Test 2: Status endpoint
    test2_result = test_upload_status_endpoint()
    
    print(f"\n=== Test Results ===")
    print(f"Upload endpoint: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Status endpoint: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! Upload functionality is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 