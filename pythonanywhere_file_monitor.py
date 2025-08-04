#!/usr/bin/env python3
"""
PythonAnywhere File Monitor
Monitors Downloads folder and automatically copies files to uploads directory.
"""

import os
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_monitor.log'),
        logging.StreamHandler()
    ]
)

def setup_directories():
    """Ensure required directories exist."""
    directories = [
        "/home/adamcordova/Downloads",
        "/home/adamcordova/AGTDesigner/uploads",
        "/home/adamcordova/uploads"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logging.info(f"Ensured directory exists: {directory}")

def copy_file_to_uploads(file_path, filename, uploads_dir):
    """Copy file to uploads directory with timestamp."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_{timestamp}{ext}"
        destination = os.path.join(uploads_dir, new_filename)
        
        shutil.copy2(file_path, destination)
        logging.info(f"Copied {filename} to {destination}")
        return destination
    except Exception as e:
        logging.error(f"Error copying {filename}: {e}")
        return None

def monitor_downloads():
    """Monitor Downloads folder for new Excel files."""
    downloads_dir = "/home/adamcordova/Downloads"
    uploads_dir = "/home/adamcordova/AGTDesigner/uploads"
    
    if not os.path.exists(downloads_dir):
        logging.error(f"Downloads directory not found: {downloads_dir}")
        return
    
    logging.info(f"Starting file monitor for: {downloads_dir}")
    logging.info(f"Files will be copied to: {uploads_dir}")
    
    # Track processed files to avoid duplicates
    processed_files = set()
    
    while True:
        try:
            if os.path.exists(downloads_dir):
                for filename in os.listdir(downloads_dir):
                    if filename.lower().endswith(('.xlsx', '.xls')):
                        file_path = os.path.join(downloads_dir, filename)
                        
                        # Check if file is complete (not being downloaded)
                        if os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            
                            # Wait a moment to ensure file is complete
                            time.sleep(2)
                            
                            # Check if file size is stable (not being downloaded)
                            new_size = os.path.getsize(file_path)
                            if file_size == new_size and file_path not in processed_files:
                                logging.info(f"Found new Excel file: {filename} ({file_size:,} bytes)")
                                
                                # Copy to uploads directory
                                copy_file_to_uploads(file_path, filename, uploads_dir)
                                processed_files.add(file_path)
            
            # Sleep for 10 seconds before next check
            time.sleep(10)
            
        except Exception as e:
            logging.error(f"Error in file monitor: {e}")
            time.sleep(30)  # Wait longer on error

if __name__ == "__main__":
    setup_directories()
    monitor_downloads()
