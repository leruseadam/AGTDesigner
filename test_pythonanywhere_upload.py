#!/usr/bin/env python3
"""
Test script for PythonAnywhere upload fix
"""

import requests
import os

def test_upload():
    """Test the upload functionality."""
    
    print("🧪 Testing PythonAnywhere Upload Fix")
    print("=" * 40)
    
    # Create a test file
    test_file_path = "test_upload.xlsx"
    with open(test_file_path, 'w') as f:
        f.write("test content")
    
    try:
        # Test upload
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:5000/upload', files=files)
        
        print(f"Upload response status: {response.status_code}")
        print(f"Upload response content: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Upload test successful!")
        else:
            print("❌ Upload test failed!")
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    test_upload()
