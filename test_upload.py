#!/usr/bin/env python3
"""
Test script to check upload functionality
"""
import requests
import os

def test_upload():
    # Find a test Excel file
    downloads_dir = os.path.expanduser('~/Downloads')
    test_file = None
    
    for file in os.listdir(downloads_dir):
        if file.endswith('.xlsx'):
            test_file = os.path.join(downloads_dir, file)
            break
    
    if not test_file:
        print("❌ No Excel file found in Downloads folder")
        return
    
    print(f"📁 Found test file: {os.path.basename(test_file)}")
    print(f"📏 File size: {os.path.getsize(test_file):,} bytes")
    
    # Test upload to local server
    url = "http://localhost:5000/upload"
    
    try:
        print(f"\n🚀 Testing upload to {url}...")
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(url, files=files, timeout=60)
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📊 Response: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ Upload successful!")
        else:
            print(f"\n❌ Upload failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to localhost:5000")
        print("💡 Make sure the Flask app is running: python run_app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_upload()

