#!/usr/bin/env python3
"""
Script to upload the most recent AGT file to PythonAnywhere
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

def find_latest_agt_file():
    """Find the most recent AGT file in the local Downloads directory."""
    downloads_dir = os.path.expanduser("~/Downloads")
    
    # Look for AGT files
    pattern = os.path.join(downloads_dir, "A Greener Today*.xlsx")
    agt_files = glob.glob(pattern)
    
    if not agt_files:
        print("No AGT files found in Downloads directory!")
        return None
    
    # Sort by modification time (most recent first)
    agt_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_file = agt_files[0]
    
    print(f"Found latest AGT file: {os.path.basename(latest_file)}")
    print(f"File path: {latest_file}")
    print(f"File size: {os.path.getsize(latest_file):,} bytes")
    print(f"Modified: {os.path.getmtime(latest_file)}")
    
    return latest_file

def upload_to_pythonanywhere(local_file_path):
    """Upload file to PythonAnywhere using scp."""
    if not local_file_path or not os.path.exists(local_file_path):
        print("Local file not found!")
        return False
    
    # PythonAnywhere file path
    remote_path = "/home/adamcordova/AGTDesigner/uploads/"
    filename = os.path.basename(local_file_path)
    
    print(f"\nUploading {filename} to PythonAnywhere...")
    print(f"Remote path: {remote_path}")
    
    try:
        # Use scp to upload the file
        cmd = [
            "scp",
            local_file_path,
            f"adamcordova@ssh.pythonanywhere.com:{remote_path}{filename}"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Successfully uploaded {filename} to PythonAnywhere!")
            return True
        else:
            print(f"✗ Upload failed!")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error during upload: {e}")
        return False

def check_pythonanywhere_connection():
    """Test connection to PythonAnywhere."""
    print("Testing connection to PythonAnywhere...")
    
    try:
        cmd = ["ssh", "adamcordova@ssh.pythonanywhere.com", "echo 'Connection successful'"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ Connection to PythonAnywhere successful!")
            return True
        else:
            print(f"✗ Connection failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Connection timeout")
        return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

def main():
    """Main function."""
    print("PythonAnywhere File Upload Script")
    print("=" * 40)
    
    # Check connection
    if not check_pythonanywhere_connection():
        print("\nCannot connect to PythonAnywhere. Please check your SSH configuration.")
        print("Make sure you have SSH access set up for PythonAnywhere.")
        return
    
    # Find latest file
    latest_file = find_latest_agt_file()
    if not latest_file:
        return
    
    # Upload file
    success = upload_to_pythonanywhere(latest_file)
    
    if success:
        print(f"\n✓ File upload completed successfully!")
        print(f"The file {os.path.basename(latest_file)} is now available on PythonAnywhere.")
        print("You can now restart your PythonAnywhere web app to load the new default file.")
    else:
        print(f"\n✗ File upload failed!")
        print("Please check your PythonAnywhere SSH configuration and try again.")

if __name__ == "__main__":
    main() 