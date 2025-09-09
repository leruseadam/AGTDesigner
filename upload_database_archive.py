#!/usr/bin/env python3
"""
Upload Database Archive to PythonAnywhere
Uploads the compressed database archive to PythonAnywhere for web deployment
"""

import os
import sys
import subprocess
import glob
from pathlib import Path
from datetime import datetime

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

def upload_to_pythonanywhere(local_file_path):
    """Upload file to PythonAnywhere using scp."""
    if not local_file_path or not local_file_path.exists():
        print("Local file not found!")
        return False
    
    # PythonAnywhere file path
    remote_path = "/home/adamcordova/AGTDesigner/"
    filename = local_file_path.name
    
    print(f"\nUploading {filename} to PythonAnywhere...")
    print(f"Remote path: {remote_path}")
    
    try:
        # Use scp to upload the file
        cmd = [
            "scp",
            str(local_file_path),
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

def extract_on_pythonanywhere(archive_name):
    """Extract the archive on PythonAnywhere."""
    print(f"\nExtracting {archive_name} on PythonAnywhere...")
    
    try:
        # SSH command to extract the archive
        extract_cmd = f"cd /home/adamcordova/AGTDesigner && tar -xzf {archive_name}"
        cleanup_cmd = f"cd /home/adamcordova/AGTDesigner && rm {archive_name}"
        
        # Extract the archive
        cmd = ["ssh", "adamcordova@ssh.pythonanywhere.com", extract_cmd]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✓ Archive extracted successfully!")
            
            # Clean up the archive file
            cleanup_result = subprocess.run(
                ["ssh", "adamcordova@ssh.pythonanywhere.com", cleanup_cmd],
                capture_output=True, text=True, timeout=30
            )
            
            if cleanup_result.returncode == 0:
                print("✓ Archive file cleaned up!")
            else:
                print("⚠ Warning: Could not clean up archive file")
            
            return True
        else:
            print(f"✗ Extraction failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Extraction timeout")
        return False
    except Exception as e:
        print(f"✗ Error during extraction: {e}")
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
    print("PythonAnywhere Database Archive Upload Script")
    print("=" * 50)
    
    # Check connection
    if not check_pythonanywhere_connection():
        print("\nCannot connect to PythonAnywhere. Please check your SSH configuration.")
        print("Make sure you have SSH access set up for PythonAnywhere.")
        return
    
    # Find latest archive
    latest_archive = find_latest_database_archive()
    if not latest_archive:
        return
    
    # Upload archive
    success = upload_to_pythonanywhere(latest_archive)
    
    if success:
        # Extract on PythonAnywhere
        if extract_on_pythonanywhere(latest_archive.name):
            print(f"\n✓ Database upload and extraction completed successfully!")
            print(f"The database archive {latest_archive.name} has been uploaded and extracted on PythonAnywhere.")
            print("The web version should now have access to the local database.")
            print("You may need to restart your PythonAnywhere web app to load the new database.")
        else:
            print(f"\n⚠ Archive uploaded but extraction failed!")
            print("You may need to manually extract the archive on PythonAnywhere.")
    else:
        print(f"\n✗ Database upload failed!")
        print("Please check your PythonAnywhere SSH configuration and try again.")

if __name__ == "__main__":
    main()
