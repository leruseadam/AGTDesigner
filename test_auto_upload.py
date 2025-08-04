#!/usr/bin/env python3
"""
Test script for auto-upload functionality on PythonAnywhere
"""

import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_auto_upload():
    """Test the auto-upload functionality."""
    print("=== Testing Auto-Upload Functionality ===")
    
    # Test 1: Check if we're on PythonAnywhere
    current_dir = os.getcwd()
    is_pythonanywhere = os.path.exists("/home/adamcordova") and "pythonanywhere" in current_dir.lower()
    print(f"Current directory: {current_dir}")
    print(f"Detected as PythonAnywhere: {is_pythonanywhere}")
    
    # Test 2: Check uploads directory
    uploads_dir = os.path.join(current_dir, "uploads")
    print(f"Uploads directory: {uploads_dir}")
    print(f"Uploads directory exists: {os.path.exists(uploads_dir)}")
    
    # Test 3: Check Downloads directory
    downloads_dir = os.path.join(str(Path.home()), "Downloads")
    print(f"Downloads directory: {downloads_dir}")
    print(f"Downloads directory exists: {os.path.exists(downloads_dir)}")
    
    # Test 4: Look for AGT files in Downloads
    if os.path.exists(downloads_dir):
        agt_files = []
        for filename in os.listdir(downloads_dir):
            if filename.startswith("A Greener Today") and filename.lower().endswith(".xlsx"):
                file_path = os.path.join(downloads_dir, filename)
                mod_time = os.path.getmtime(file_path)
                agt_files.append((file_path, filename, mod_time))
        
        print(f"Found {len(agt_files)} AGT files in Downloads:")
        for file_path, filename, mod_time in agt_files:
            print(f"  - {filename} (modified: {mod_time})")
    else:
        print("Downloads directory not found")
    
    # Test 5: Check if pythonanywhere_downloads_monitor can be imported
    try:
        from pythonanywhere_downloads_monitor import monitor_downloads
        print("✓ Successfully imported pythonanywhere_downloads_monitor")
        
        # Test 6: Run the monitor
        print("Running downloads monitor...")
        monitor_downloads()
        print("✓ Downloads monitor completed successfully")
        
    except ImportError as e:
        print(f"✗ Could not import pythonanywhere_downloads_monitor: {e}")
    except Exception as e:
        print(f"✗ Error running downloads monitor: {e}")
    
    # Test 7: Check uploads directory after monitor
    if os.path.exists(uploads_dir):
        upload_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith('.xlsx')]
        print(f"Files in uploads directory after monitor: {upload_files}")
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_auto_upload() 