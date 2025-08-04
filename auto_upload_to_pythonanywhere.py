#!/usr/bin/env python3
"""
Auto Upload to PythonAnywhere Script

This script automatically finds the most recent Excel file in the uploads folder
and uploads it to PythonAnywhere to keep the web version in sync.
"""

import os
import glob
import requests
import time
from pathlib import Path
from datetime import datetime

# Configuration
PYTHONANYWHERE_URL = "https://www.agtpricetags.com"
UPLOADS_FOLDER = "uploads"
PYTHONANYWHERE_USERNAME = "your_username"  # Replace with your PythonAnywhere username

def find_most_recent_excel_file():
    """Find the most recent Excel file in the uploads folder."""
    uploads_path = Path(UPLOADS_FOLDER)
    
    if not uploads_path.exists():
        print(f"❌ Uploads folder not found: {uploads_path}")
        return None
    
    # Find all Excel files (excluding temporary files)
    excel_patterns = [
        "*.xlsx",
        "*.xls"
    ]
    
    excel_files = []
    for pattern in excel_patterns:
        files = list(uploads_path.glob(pattern))
        # Filter out temporary files (starting with ~$)
        files = [f for f in files if not f.name.startswith("~$")]
        excel_files.extend(files)
    
    if not excel_files:
        print("❌ No Excel files found in uploads folder")
        return None
    
    # Sort by modification time (most recent first)
    excel_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    most_recent = excel_files[0]
    mod_time = datetime.fromtimestamp(most_recent.stat().st_mtime)
    
    print(f"✅ Found most recent Excel file: {most_recent.name}")
    print(f"   Modified: {mod_time}")
    print(f"   Size: {most_recent.stat().st_size:,} bytes")
    
    return most_recent

def upload_file_to_pythonanywhere(file_path):
    """Upload file to PythonAnywhere using the web interface."""
    try:
        # Prepare the upload
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print(f"📤 Uploading {file_path.name} to PythonAnywhere...")
            
            # Upload to the file upload endpoint
            response = requests.post(
                f"{PYTHONANYWHERE_URL}/upload",
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                print("✅ File uploaded successfully!")
                return True
            else:
                print(f"❌ Upload failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def check_pythonanywhere_status():
    """Check if PythonAnywhere is accessible."""
    try:
        response = requests.get(f"{PYTHONANYWHERE_URL}/api/initial-data", timeout=10)
        if response.status_code == 200:
            print("✅ PythonAnywhere is accessible")
            return True
        else:
            print(f"❌ PythonAnywhere returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to PythonAnywhere: {e}")
        return False

def main():
    """Main function to orchestrate the upload process."""
    print("🚀 Auto Upload to PythonAnywhere")
    print("=" * 50)
    
    # Check if PythonAnywhere is accessible
    if not check_pythonanywhere_status():
        print("❌ Cannot connect to PythonAnywhere. Please check the URL and try again.")
        return
    
    # Find the most recent Excel file
    excel_file = find_most_recent_excel_file()
    if not excel_file:
        print("❌ No Excel file found to upload")
        return
    
    # Upload the file
    if upload_file_to_pythonanywhere(excel_file):
        print("\n🎉 Upload completed successfully!")
        print(f"📊 The web version should now have the latest data from: {excel_file.name}")
        print(f"🌐 Visit: {PYTHONANYWHERE_URL}")
    else:
        print("\n❌ Upload failed. Please try again.")

if __name__ == "__main__":
    main() 