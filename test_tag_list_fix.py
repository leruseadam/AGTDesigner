#!/usr/bin/env python3
"""
Test script to verify that the tag list no longer disappears after upload.
This test simulates the upload process and checks that tags remain visible.
"""

import requests
import time
import json
import os

def test_tag_list_persistence():
    """Test that tag list persists after upload"""
    base_url = "http://127.0.0.1:9090"
    
    print("Testing tag list persistence after upload...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✓ Server is running")
        else:
            print("✗ Server returned status code:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Make sure it's running on port 9090")
        return False
    
    # Test 2: Check available tags endpoint before upload
    try:
        response = requests.get(f"{base_url}/api/available-tags")
        if response.status_code == 200:
            tags_before = response.json()
            print(f"✓ Available tags before upload: {len(tags_before)} tags")
        else:
            print(f"✗ Failed to get available tags before upload: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error getting available tags before upload: {e}")
        return False
    
    # Test 3: Upload a test file
    test_file_path = "data/default_inventory.xlsx"
    if not os.path.exists(test_file_path):
        print(f"✗ Test file not found: {test_file_path}")
        return False
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            filename = data.get('filename')
            print(f"✓ File uploaded successfully: {filename}")
        else:
            print(f"✗ Upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error uploading file: {e}")
        return False
    
    # Test 4: Wait for processing and check tags
    print("Waiting for file processing...")
    max_wait = 60  # 60 seconds max
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            # Check upload status
            response = requests.get(f"{base_url}/api/upload-status?filename={filename}")
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status')
                print(f"  Status: {status}")
                
                if status in ['ready', 'done']:
                    # Check available tags after processing
                    response = requests.get(f"{base_url}/api/available-tags")
                    if response.status_code == 200:
                        tags_after = response.json()
                        print(f"✓ Available tags after upload: {len(tags_after)} tags")
                        
                        # Verify tags are present
                        if len(tags_after) > 0:
                            print("✓ Tag list is not empty after upload - FIX VERIFIED!")
                            return True
                        else:
                            print("✗ Tag list is empty after upload - FIX FAILED!")
                            return False
                    else:
                        print(f"✗ Failed to get available tags after upload: {response.status_code}")
                        return False
                
                elif status == 'processing':
                    time.sleep(3)  # Wait 3 seconds before next check
                    continue
                else:
                    print(f"✗ Unexpected status: {status}")
                    return False
            else:
                print(f"✗ Failed to get upload status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Error checking status: {e}")
            return False
    
    print("✗ Timeout waiting for file processing")
    return False

if __name__ == "__main__":
    success = test_tag_list_persistence()
    if success:
        print("\n🎉 SUCCESS: Tag list persistence fix is working!")
    else:
        print("\n❌ FAILED: Tag list persistence fix is not working!")
    
    exit(0 if success else 1) 