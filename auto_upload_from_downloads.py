#!/usr/bin/env python3
"""
Auto Upload from Downloads to PythonAnywhere

This script automatically finds the most recent Excel file in the user's Downloads folder
and uploads it to PythonAnywhere to keep the web version in sync.
"""

import os
import glob
import requests
import time
from pathlib import Path
from datetime import datetime
import platform

# Configuration
PYTHONANYWHERE_URL = "https://www.agtpricetags.com"

def get_downloads_folder():
    """Get the Downloads folder path for the current operating system."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return Path.home() / "Downloads"
    elif system == "Windows":
        return Path.home() / "Downloads"
    elif system == "Linux":
        return Path.home() / "Downloads"
    else:
        # Fallback to common locations
        possible_paths = [
            Path.home() / "Downloads",
            Path.home() / "downloads",
            Path("/Users") / os.getenv("USER", "") / "Downloads"
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        raise FileNotFoundError("Could not find Downloads folder")

def find_most_recent_excel_in_downloads():
    """Find the most recent Excel file in the Downloads folder."""
    downloads_path = get_downloads_folder()
    
    print(f"📁 Searching Downloads folder: {downloads_path}")
    
    if not downloads_path.exists():
        print(f"❌ Downloads folder not found: {downloads_path}")
        return None
    
    # Find all Excel files (excluding temporary files)
    excel_patterns = [
        "*.xlsx",
        "*.xls"
    ]
    
    excel_files = []
    for pattern in excel_patterns:
        files = list(downloads_path.glob(pattern))
        # Filter out temporary files (starting with ~$)
        files = [f for f in files if not f.name.startswith("~$")]
        excel_files.extend(files)
    
    if not excel_files:
        print("❌ No Excel files found in Downloads folder")
        return None
    
    # Sort by modification time (most recent first)
    excel_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    most_recent = excel_files[0]
    mod_time = datetime.fromtimestamp(most_recent.stat().st_mtime)
    
    print(f"✅ Found most recent Excel file: {most_recent.name}")
    print(f"   Location: {most_recent}")
    print(f"   Modified: {mod_time}")
    print(f"   Size: {most_recent.stat().st_size:,} bytes")
    
    # Show top 5 most recent files
    print("\n📋 Top 5 most recent Excel files in Downloads:")
    for i, file in enumerate(excel_files[:5], 1):
        mod_time = datetime.fromtimestamp(file.stat().st_mtime)
        size = file.stat().st_size
        print(f"   {i}. {file.name} ({mod_time.strftime('%Y-%m-%d %H:%M:%S')}, {size:,} bytes)")
    
    return most_recent

def upload_file_to_pythonanywhere(file_path):
    """Upload file to PythonAnywhere using the web interface."""
    try:
        # Prepare the upload
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print(f"\n📤 Uploading {file_path.name} to PythonAnywhere...")
            
            # Upload to the file upload endpoint
            response = requests.post(
                f"{PYTHONANYWHERE_URL}/upload",
                files=files,
                timeout=120  # Increased timeout for large files
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
    print("🚀 Auto Upload from Downloads to PythonAnywhere")
    print("=" * 60)
    
    # Check if PythonAnywhere is accessible
    if not check_pythonanywhere_status():
        print("❌ Cannot connect to PythonAnywhere. Please check the URL and try again.")
        return
    
    # Find the most recent Excel file in Downloads
    excel_file = find_most_recent_excel_in_downloads()
    if not excel_file:
        print("❌ No Excel file found to upload")
        return
    
    # Ask for confirmation
    print(f"\n🤔 Do you want to upload '{excel_file.name}' to PythonAnywhere?")
    response = input("Enter 'y' to continue, or any other key to cancel: ").strip().lower()
    
    if response != 'y':
        print("❌ Upload cancelled by user")
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