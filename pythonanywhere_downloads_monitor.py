#!/usr/bin/env python3
"""
PythonAnywhere Downloads Monitor
Automatically copies "A Greener Today" Excel files from Downloads to uploads directory.
This script can be run manually or set up as a scheduled task on PythonAnywhere.
"""

import os
import shutil
import time
from pathlib import Path
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('downloads_monitor.log'),
        logging.StreamHandler()
    ]
)

def setup_directories():
    """Create necessary directories if they don't exist."""
    current_dir = os.getcwd()
    uploads_dir = os.path.join(current_dir, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    return uploads_dir

def get_downloads_directory():
    """Get the Downloads directory path."""
    downloads_dir = os.path.join(str(Path.home()), "Downloads")
    return downloads_dir

def find_agt_files(directory):
    """Find all 'A Greener Today' Excel files in the given directory."""
    agt_files = []
    
    if not os.path.exists(directory):
        logging.warning(f"Directory does not exist: {directory}")
        return agt_files
    
    try:
        for filename in os.listdir(directory):
            if filename.startswith("A Greener Today") and filename.lower().endswith(".xlsx"):
                file_path = os.path.join(directory, filename)
                mod_time = os.path.getmtime(file_path)
                agt_files.append((file_path, filename, mod_time))
                logging.info(f"Found AGT file: {filename} (modified: {datetime.fromtimestamp(mod_time)})")
    except Exception as e:
        logging.error(f"Error reading directory {directory}: {e}")
    
    return agt_files

def copy_file_to_uploads(file_path, filename, uploads_dir):
    """Copy a file to the uploads directory if it's newer or doesn't exist."""
    upload_path = os.path.join(uploads_dir, filename)
    
    try:
        # Check if file already exists in uploads
        if os.path.exists(upload_path):
            upload_mod_time = os.path.getmtime(upload_path)
            source_mod_time = os.path.getmtime(file_path)
            
            if source_mod_time <= upload_mod_time:
                logging.info(f"File {filename} already exists and is up to date in uploads")
                return False
        
        # Copy the file
        shutil.copy2(file_path, upload_path)
        logging.info(f"Successfully copied {filename} to uploads directory")
        return True
        
    except Exception as e:
        logging.error(f"Error copying {filename}: {e}")
        return False

def monitor_downloads():
    """Main function to monitor Downloads directory and copy AGT files."""
    logging.info("Starting Downloads monitor...")
    
    # Setup directories
    uploads_dir = setup_directories()
    downloads_dir = get_downloads_directory()
    
    logging.info(f"Monitoring Downloads directory: {downloads_dir}")
    logging.info(f"Copying files to uploads directory: {uploads_dir}")
    
    # Find all AGT files in Downloads
    agt_files = find_agt_files(downloads_dir)
    
    if not agt_files:
        logging.info("No 'A Greener Today' files found in Downloads")
        return
    
    # Sort by modification time (most recent first)
    agt_files.sort(key=lambda x: x[2], reverse=True)
    
    # Copy files to uploads
    copied_count = 0
    for file_path, filename, mod_time in agt_files:
        if copy_file_to_uploads(file_path, filename, uploads_dir):
            copied_count += 1
    
    logging.info(f"Monitor completed. Copied {copied_count} new/updated files.")

def create_sample_file():
    """Create a sample AGT file in Downloads for testing."""
    import pandas as pd
    
    downloads_dir = get_downloads_directory()
    os.makedirs(downloads_dir, exist_ok=True)
    
    # Sample data
    sample_data = {
        'ProductName': ['Test Product 1', 'Test Product 2', 'Test Product 3'],
        'Product Type*': ['flower', 'pre-roll', 'concentrate'],
        'ProductBrand': ['Test Brand', 'Test Brand', 'Test Brand'],
        'ProductStrain': ['Test Strain', 'Test Strain', 'Test Strain'],
        'Lineage': ['INDICA', 'HYBRID', 'SATIVA'],
        'Weight*': [3.5, 1.0, 1.0],
        'Units': ['g', 'g', 'g'],
        'Ratio': ['THC: 20%\nCBD: 1%', 'THC: 18%\nCBD: 2%', 'THC: 85%\nCBD: 1%'],
        'Description': ['Test description 1', 'Test description 2', 'Test description 3'],
        'DOH': ['No', 'No', 'No']
    }
    
    df = pd.DataFrame(sample_data)
    sample_file_path = os.path.join(downloads_dir, "A Greener Today - Test Inventory.xlsx")
    df.to_excel(sample_file_path, index=False)
    
    logging.info(f"Created sample file: {sample_file_path}")
    return sample_file_path

def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "monitor":
            monitor_downloads()
        elif command == "create-sample":
            create_sample_file()
        elif command == "setup":
            setup_directories()
            logging.info("Directories set up successfully")
        else:
            print("Usage:")
            print("  python3 pythonanywhere_downloads_monitor.py monitor     - Monitor and copy files")
            print("  python3 pythonanywhere_downloads_monitor.py create-sample - Create sample file")
            print("  python3 pythonanywhere_downloads_monitor.py setup       - Setup directories")
    else:
        # Default: run monitor
        monitor_downloads()

if __name__ == "__main__":
    main() 