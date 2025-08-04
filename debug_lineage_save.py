#!/usr/bin/env python3
"""
Debug script to check lineage save functionality
"""

import requests
import json
import os

def debug_lineage_save():
    """Debug lineage save functionality"""
    
    print("Debugging Lineage Save Functionality")
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
    
    # Test 2: Get debug info about current file
    try:
        response = requests.get("http://127.0.0.1:9090/api/debug-columns", timeout=10)
        if response.status_code == 200:
            debug_info = response.json()
            current_file = debug_info.get('current_file', 'None')
            print(f"✅ Current file: {current_file}")
            
            if current_file != 'None' and os.path.exists(current_file):
                print(f"✅ File exists and is accessible")
                file_size = os.path.getsize(current_file)
                print(f"✅ File size: {file_size} bytes")
                
                # Check if file is writable
                if os.access(current_file, os.W_OK):
                    print(f"✅ File is writable")
                else:
                    print(f"❌ File is NOT writable")
            else:
                print(f"❌ File does not exist or is not accessible")
        else:
            print("❌ Failed to get debug info:", response.status_code)
            return False
    except Exception as e:
        print(f"❌ Error getting debug info: {e}")
        return False
    
    # Test 3: Get available tags to find a test tag
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
                print("❌ No available tags found")
                return False
        else:
            print("❌ Failed to get available tags:", response.status_code)
            return False
    except Exception as e:
        print(f"❌ Error getting available tags: {e}")
        return False
    
    # Test 4: Update lineage and check response
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
            
            # Check if the message indicates the change was actually made
            message = result.get('message', '')
            if 'from' in message and 'to' in message:
                parts = message.split(' from ')
                if len(parts) > 1:
                    change_part = parts[1]
                    if ' to ' in change_part:
                        old_new = change_part.split(' to ')
                        if len(old_new) == 2:
                            old_lineage = old_new[0].strip()
                            new_lineage_actual = old_new[1].strip()
                            print(f"📝 API reported change: '{old_lineage}' → '{new_lineage_actual}'")
                            
                            if old_lineage == current_lineage and new_lineage_actual == new_lineage:
                                print(f"✅ API message matches expected change")
                            else:
                                print(f"⚠️  API message doesn't match expected change")
                                print(f"   Expected: '{current_lineage}' → '{new_lineage}'")
                                print(f"   Actual: '{old_lineage}' → '{new_lineage_actual}'")
        else:
            error_data = response.json()
            print(f"❌ Lineage update failed: {error_data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Error updating lineage: {e}")
        return False
    
    # Test 5: Check if file was actually modified
    try:
        print(f"🔄 Checking if file was modified...")
        
        # Get the current file path again
        response = requests.get("http://127.0.0.1:9090/api/debug-columns", timeout=10)
        if response.status_code == 200:
            debug_info = response.json()
            current_file = debug_info.get('current_file', 'None')
            
            if current_file != 'None' and os.path.exists(current_file):
                # Check file modification time
                mtime = os.path.getmtime(current_file)
                print(f"📝 File modification time: {mtime}")
                
                # Check file size
                file_size = os.path.getsize(current_file)
                print(f"📝 File size: {file_size} bytes")
                
                # Try to read the file and check if the change is there
                import pandas as pd
                try:
                    df = pd.read_excel(current_file)
                    if 'Product Name*' in df.columns and 'Lineage' in df.columns:
                        # Find the tag
                        mask = df['Product Name*'] == tag_name
                        if mask.any():
                            file_lineage = df.loc[mask, 'Lineage'].iloc[0]
                            print(f"📝 Lineage in file: '{file_lineage}'")
                            
                            if file_lineage == new_lineage:
                                print(f"✅ Change found in file!")
                            else:
                                print(f"❌ Change NOT found in file")
                                print(f"   Expected: '{new_lineage}'")
                                print(f"   Found: '{file_lineage}'")
                        else:
                            print(f"❌ Tag not found in file")
                    else:
                        print(f"❌ Required columns not found in file")
                except Exception as read_error:
                    print(f"❌ Error reading file: {read_error}")
            else:
                print(f"❌ Cannot access file for verification")
        else:
            print("❌ Failed to get debug info for verification")
    except Exception as e:
        print(f"❌ Error checking file modification: {e}")
    
    return True

if __name__ == "__main__":
    debug_lineage_save() 