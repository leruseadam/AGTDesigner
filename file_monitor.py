#!/usr/bin/env python3
"""
Automatic file monitor for PythonAnywhere
Monitors Downloads directory and syncs Excel files to uploads.
"""

import os
import time
import logging
from pathlib import Path
import shutil
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('file_monitor.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def monitor_and_sync():
    logger = setup_logging()
    logger.info("File monitor started")
    
    uploads_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    
    downloads_dir = os.path.join(str(Path.home()), "Downloads")
    
    while True:
        try:
            # Find Excel files in Downloads
            excel_files = []
            if os.path.exists(downloads_dir):
                for filename in os.listdir(downloads_dir):
                    if filename.lower().endswith(('.xlsx', '.xls')):
                        file_path = os.path.join(downloads_dir, filename)
                        if os.path.isfile(file_path):
                            excel_files.append((file_path, filename))
            
            # Copy new files
            for file_path, filename in excel_files:
                dest_path = os.path.join(uploads_dir, filename)
                if not os.path.exists(dest_path):
                    shutil.copy2(file_path, dest_path)
                    logger.info(f"Auto-copied: {filename}")
            
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    monitor_and_sync()
