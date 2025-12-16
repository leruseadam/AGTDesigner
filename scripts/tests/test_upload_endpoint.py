#!/usr/bin/env python3
"""
Test script to verify the /upload endpoint is working correctly.
"""

import requests
import os
import sys

def test_upload_endpoint():
    """Test the upload endpoint with a sample Excel file."""
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000', timeout=2)
        print("✓ Server is running")
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running. Please start it with: python app.py")
        return False
    except Exception as e:
        print(f"✗ Error connecting to server: {e}")
        return False
    
    # Look for an Excel file in uploads directory
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    excel_files = []
    
    if os.path.exists(uploads_dir):
        # Check root uploads directory
        for f in os.listdir(uploads_dir):
            if f.endswith('.xlsx'):
                excel_files.append(os.path.join(uploads_dir, f))
        
        # Check subdirectories
        for root, dirs, files in os.walk(uploads_dir):
            for f in files:
                if f.endswith('.xlsx'):
                    excel_files.append(os.path.join(root, f))
    
    if not excel_files:
        print("✗ No Excel files found in uploads directory")
        print("  Please place a test Excel file in the uploads directory")
        return False
    
    test_file = excel_files[0]
    print(f"✓ Found test file: {os.path.basename(test_file)}")
    
    # Test the upload endpoint
    print("\nTesting /upload endpoint...")
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post('http://localhost:5000/upload', files=files, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Upload successful!")
            print(f"  Response: {data}")
            
            # Check if response has expected fields
            if 'status' in data:
                print(f"  Status: {data['status']}")
            if 'filename' in data:
                print(f"  Filename: {data['filename']}")
            if 'rows' in data:
                print(f"  Rows: {data['rows']}")
            
            return True
        else:
            try:
                error_data = response.json()
                print(f"✗ Upload failed: {error_data}")
            except:
                print(f"✗ Upload failed: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Upload timed out (file might be too large or processing is slow)")
        return False
    except Exception as e:
        print(f"✗ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Excel Upload Endpoint Test")
    print("=" * 60)
    
    success = test_upload_endpoint()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Tests failed")
        sys.exit(1)

