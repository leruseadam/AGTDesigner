#!/usr/bin/env python3
"""
Upload Debug Script for PythonAnywhere
"""

import os
import requests
import time

def test_upload_endpoints():
    """Test all upload endpoints."""
    print("🔍 Testing upload endpoints...")
    
    endpoints = [
        '/upload',
        '/upload-simple',
        '/api/status',
        '/api/health'
    ]
    
    for endpoint in endpoints:
        try:
            print(f"Testing {endpoint}...")
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            print(f"  Status: {response.status_code}")
            if response.status_code == 405:  # Method Not Allowed
                print(f"  Note: {endpoint} exists but doesn't accept GET requests")
            elif response.status_code == 200:
                print(f"  Success: {endpoint} is working")
        except Exception as e:
            print(f"  Error: {e}")
    
    print()

def test_file_upload():
    """Test actual file upload."""
    print("📤 Testing file upload...")
    
    # Find a test file
    test_files = []
    uploads_dir = "/home/adamcordova/AGTDesigner/uploads"
    
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            if filename.lower().endswith('.xlsx') and filename.startswith('A Greener Today'):
                file_path = os.path.join(uploads_dir, filename)
                file_size = os.path.getsize(file_path)
                if file_size < 1000000:  # Less than 1MB
                    test_files.append((file_path, filename, file_size))
    
    if not test_files:
        print("❌ No suitable test files found")
        return
    
    # Use the smallest file
    test_files.sort(key=lambda x: x[2])
    test_file_path, test_filename, test_file_size = test_files[0]
    
    print(f"Using test file: {test_filename} ({test_file_size:,} bytes)")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_filename, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            # Test simple upload
            print("Testing /upload-simple...")
            response = requests.post('http://localhost:5000/upload-simple', files=files, timeout=30)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Success: {data}")
            else:
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"Upload test error: {e}")

def check_upload_configuration():
    """Check upload configuration."""
    print("⚙️  Checking upload configuration...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        checks = [
            ('MAX_CONTENT_LENGTH', 'File size limit'),
            ('UPLOAD_FOLDER', 'Upload folder configuration'),
            ('@app.route.*upload', 'Upload routes'),
            ('upload-simple', 'Simple upload route')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description}: Found")
            else:
                print(f"❌ {description}: Not found")
                
    except Exception as e:
        print(f"Configuration check error: {e}")

def main():
    """Run all tests."""
    print("🧪 PythonAnywhere Upload Debug")
    print("=" * 40)
    
    check_upload_configuration()
    print()
    test_upload_endpoints()
    test_file_upload()
    
    print("=" * 40)
    print("📋 Next steps:")
    print("1. Visit: https://yourusername.pythonanywhere.com/upload-test")
    print("2. Try uploading a file through the web interface")
    print("3. Check the PythonAnywhere error logs if uploads fail")

if __name__ == "__main__":
    main()
