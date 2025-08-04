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
        url = "http://localhost:5000/upload"
        
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

def test_file_permissions():
    """Test file permissions and directory access."""
    print("\n=== File Permissions Test ===\n")
    
    uploads_dir = Path("uploads")
    
    # Check if uploads directory exists
    if not uploads_dir.exists():
        print("❌ Uploads directory does not exist")
        return False
    
    print(f"✅ Uploads directory exists: {uploads_dir}")
    
    # Check if directory is writable
    if not os.access(uploads_dir, os.W_OK):
        print("❌ Uploads directory is not writable")
        return False
    
    print("✅ Uploads directory is writable")
    
    # Check for test files
    test_files = list(uploads_dir.glob("*.xlsx"))
    if not test_files:
        print("❌ No Excel files found in uploads directory")
        return False
    
    print(f"✅ Found {len(test_files)} Excel file(s)")
    
    # Test file access
    test_file = test_files[0]
    if not os.access(test_file, os.R_OK):
        print(f"❌ Cannot read test file: {test_file}")
        return False
    
    print(f"✅ Can read test file: {test_file}")
    
    return True

def test_app_configuration():
    """Test app configuration and settings."""
    print("\n=== App Configuration Test ===\n")
    
    try:
        # Import app configuration
        from config import Config
        
        print(f"✅ Config imported successfully")
        print(f"Upload folder: {Config.UPLOAD_FOLDER}")
        print(f"Development mode: {Config.DEVELOPMENT_MODE}")
        
        # Check if upload folder exists
        upload_folder = Path(Config.UPLOAD_FOLDER)
        if upload_folder.exists():
            print(f"✅ Upload folder exists: {upload_folder}")
        else:
            print(f"❌ Upload folder does not exist: {upload_folder}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing app configuration: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Upload Debug Test Suite ===\n")
    
    tests = [
        ("File Permissions", test_file_permissions),
        ("App Configuration", test_app_configuration),
        ("Upload Endpoint", test_upload_endpoint),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{'✅ PASSED' if result else '❌ FAILED'}: {test_name}\n")
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        
        # Provide troubleshooting tips
        print("\n=== Troubleshooting Tips ===")
        print("1. Make sure the Flask app is running on localhost:5000")
        print("2. Check that the uploads/ directory exists and is writable")
        print("3. Verify that Excel files are present in the uploads/ directory")
        print("4. Check the Flask app logs for detailed error messages")
        print("5. Ensure the file size is under 16MB (the configured limit)")

if __name__ == "__main__":
    main() 