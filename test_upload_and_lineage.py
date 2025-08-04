#!/usr/bin/env python3
"""
Test script to upload a file and then test lineage changes
"""

import requests
import json
import os
import time

def test_upload_and_lineage():
    """Test file upload and then lineage changes"""
    
    print("Testing File Upload and Lineage Changes")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get("http://127.0.0.1:9090/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server responded with error:", response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        print("❌ Server is not running:", e)
        return False
    
    # Test 2: Find a file to upload
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print(f"❌ Uploads directory not found: {uploads_dir}")
        return False
    
    # Find the most recent Excel file
    excel_files = []
    for file in os.listdir(uploads_dir):
        if file.endswith('.xlsx') and 'A Greener Today' in file:
            file_path = os.path.join(uploads_dir, file)
            mtime = os.path.getmtime(file_path)
            excel_files.append((file_path, mtime))
    
    if not excel_files:
        print("❌ No Excel files found in uploads directory")
        return False
    
    # Sort by modification time (most recent first)
    excel_files.sort(key=lambda x: x[1], reverse=True)
    test_file = excel_files[0][0]
    print(f"✅ Found test file: {test_file}")
    
    # Test 3: Upload the file
    try:
        print(f"🔄 Uploading file: {test_file}")
        
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(
                "http://127.0.0.1:9090/upload",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            print("✅ File upload successful")
        else:
            print(f"❌ File upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return False
    
    # Test 4: Wait for processing and check if file is loaded
    print("🔄 Waiting for file processing...")
    
    # Wait for background processing to complete
    max_wait_time = 60  # Wait up to 60 seconds
    wait_interval = 2   # Check every 2 seconds
    waited_time = 0
    
    while waited_time < max_wait_time:
        try:
            # Check upload status
            response = requests.get(
                f"http://127.0.0.1:9090/api/upload-status?filename={os.path.basename(test_file)}",
                timeout=5
            )
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status', 'unknown')
                age = status_data.get('age_seconds', 0)
                
                print(f"📊 Upload status: {status} (age: {age}s)")
                
                if status == 'ready':
                    print("✅ File processing completed")
                    break
                elif status.startswith('error:'):
                    error_msg = status.replace('error:', '').strip()
                    print(f"❌ File processing failed: {error_msg}")
                    return False
                elif status == 'processing':
                    print(f"⏳ Still processing... (waited {waited_time}s)")
                else:
                    print(f"⚠️  Unknown status: {status}")
            else:
                print(f"⚠️  Failed to get upload status: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Error checking upload status: {e}")
        
        time.sleep(wait_interval)
        waited_time += wait_interval
    
    if waited_time >= max_wait_time:
        print("❌ Timeout waiting for file processing")
        return False
    
    # Now check if file is loaded
    try:
        response = requests.get("http://127.0.0.1:9090/api/debug-columns", timeout=10)
        if response.status_code == 200:
            debug_info = response.json()
            current_file = debug_info.get('current_file', 'None')
            print(f"✅ Current file after upload: {current_file}")
            
            if current_file == 'None':
                print("❌ File still not loaded after upload")
                return False
        else:
            print("❌ Failed to get debug info after upload")
            return False
    except Exception as e:
        print(f"❌ Error checking file status after upload: {e}")
        return False
    
    # Test 5: Get available tags
    try:
        response = requests.get("http://127.0.0.1:9090/api/available-tags", timeout=10)
        if response.status_code == 200:
            available_tags = response.json()
            if available_tags:
                test_tag = available_tags[0]
                tag_name = test_tag.get('Product Name*', '')
                current_lineage = test_tag.get('Lineage', 'MIXED')
                print(f"✅ Found test tag: '{tag_name}' with current lineage: '{current_lineage}'")
            else:
                print("❌ No available tags found after upload")
                return False
        else:
            print("❌ Failed to get available tags after upload")
            return False
    except Exception as e:
        print(f"❌ Error getting available tags after upload: {e}")
        return False
    
    # Test 6: Update lineage
    try:
        # Choose a different lineage for testing
        new_lineage = "SATIVA" if current_lineage != "SATIVA" else "INDICA"
        
        print(f"🔄 Updating lineage for '{tag_name}' from '{current_lineage}' to '{new_lineage}'")
        
        response = requests.post(
            "http://127.0.0.1:9090/api/update-lineage",
            json={
                "tag_name": tag_name,
                "lineage": new_lineage
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Lineage update successful: {result.get('message', '')}")
        else:
            error_data = response.json()
            print(f"❌ Lineage update failed: {error_data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Error updating lineage: {e}")
        return False
    
    # Test 7: Verify the change was saved
    try:
        print("🔄 Verifying lineage change was saved...")
        time.sleep(1)
        
        response = requests.get("http://127.0.0.1:9090/api/available-tags", timeout=10)
        if response.status_code == 200:
            available_tags = response.json()
            updated_tag = None
            for tag in available_tags:
                if tag.get('Product Name*', '') == tag_name:
                    updated_tag = tag
                    break
            
            if updated_tag:
                updated_lineage = updated_tag.get('Lineage', '')
                if updated_lineage == new_lineage:
                    print(f"✅ Lineage change verified! Tag '{tag_name}' now has lineage '{updated_lineage}'")
                else:
                    print(f"❌ Lineage change not persisted! Expected '{new_lineage}', got '{updated_lineage}'")
                    return False
            else:
                print(f"❌ Could not find updated tag '{tag_name}' in available tags")
                return False
        else:
            print("❌ Failed to get available tags for verification")
            return False
    except Exception as e:
        print(f"❌ Error verifying lineage change: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_upload_and_lineage()
    
    if success:
        print("\n🎉 File upload and lineage change test passed!")
        print("✅ Lineage changes are working correctly when a file is loaded")
    else:
        print("\n❌ File upload and lineage change test failed")
        print("⚠️  There may be an issue with file loading or lineage persistence")
    
    print("=" * 60) 