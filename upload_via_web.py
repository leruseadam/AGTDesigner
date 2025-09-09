#!/usr/bin/env python3
"""
Upload Database via Web Interface
Uses the web upload endpoint to upload the database archive
"""

import os
import sys
import requests
import glob
from pathlib import Path
from datetime import datetime

# Configuration
PYTHONANYWHERE_URL = "https://www.agtpricetags.com"

def find_latest_database_archive():
    """Find the most recent database backup archive."""
    current_dir = Path(".")
    
    # Look for database backup archives
    pattern = "database_backup_*.tar.gz"
    archive_files = list(current_dir.glob(pattern))
    
    if not archive_files:
        print("No database backup archives found!")
        return None
    
    # Sort by modification time (most recent first)
    archive_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_file = archive_files[0]
    
    print(f"Found latest database archive: {latest_file.name}")
    print(f"File size: {latest_file.stat().st_size:,} bytes")
    print(f"Modified: {datetime.fromtimestamp(latest_file.stat().st_mtime)}")
    
    return latest_file

def upload_archive_via_web(archive_path):
    """Upload the archive using the web upload endpoint."""
    try:
        print(f"Uploading {archive_path.name} via web interface...")
        
        with open(archive_path, 'rb') as f:
            files = {'file': (archive_path.name, f, 'application/gzip')}
            
            # Try the regular upload endpoint first
            response = requests.post(
                f"{PYTHONANYWHERE_URL}/upload",
                files=files,
                timeout=300  # 5 minute timeout for large files
            )
            
            if response.status_code == 200:
                print("✅ Archive uploaded successfully!")
                return True
            else:
                print(f"❌ Upload failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def check_web_status():
    """Check if the web application is accessible."""
    try:
        response = requests.get(f"{PYTHONANYWHERE_URL}/api/initial-data", timeout=10)
        if response.status_code == 200:
            print("✅ Web application is accessible")
            return True
        else:
            print(f"❌ Web application returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to web application: {e}")
        return False

def main():
    """Main function."""
    print("Web-based Database Archive Upload")
    print("=" * 40)
    
    # Check web status
    if not check_web_status():
        print("❌ Cannot connect to the web application. Please check the URL and try again.")
        return
    
    # Find latest archive
    latest_archive = find_latest_database_archive()
    if not latest_archive:
        return
    
    # Check file size (web uploads have size limits)
    file_size_mb = latest_archive.stat().st_size / (1024 * 1024)
    print(f"Archive size: {file_size_mb:.1f} MB")
    
    if file_size_mb > 100:  # Assuming 100MB limit
        print("⚠️  Warning: Archive is quite large. Upload may take a while or fail.")
        print("Consider using SSH upload instead if this fails.")
    
    # Upload archive
    success = upload_archive_via_web(latest_archive)
    
    if success:
        print(f"\n🎉 Database archive upload completed successfully!")
        print(f"The archive {latest_archive.name} has been uploaded to the web application.")
        print("You may need to manually extract it on the server or restart the web app.")
        print(f"🌐 Visit: {PYTHONANYWHERE_URL}")
    else:
        print(f"\n❌ Database archive upload failed!")
        print("Please try using SSH upload or check the web application status.")

if __name__ == "__main__":
    main()
