#!/usr/bin/env python3
"""
File Watcher for Auto Upload to PythonAnywhere

This script watches the uploads folder for new Excel files and automatically
uploads them to PythonAnywhere to keep the web version in sync.
"""

import os
import time
import requests
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
PYTHONANYWHERE_URL = "https://www.agtpricetags.com"
UPLOADS_FOLDER = "uploads"
WATCH_DELAY = 5  # Seconds to wait before uploading (to ensure file is complete)

class ExcelFileHandler(FileSystemEventHandler):
    """Handler for Excel file events."""
    
    def __init__(self):
        self.last_uploaded = None
        self.upload_times = {}
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if self._is_excel_file(file_path):
            print(f"📁 New Excel file detected: {file_path.name}")
            self._schedule_upload(file_path)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if self._is_excel_file(file_path):
            print(f"📝 Excel file modified: {file_path.name}")
            self._schedule_upload(file_path)
    
    def _is_excel_file(self, file_path):
        """Check if file is an Excel file (excluding temporary files)."""
        if file_path.name.startswith("~$"):
            return False
        
        return file_path.suffix.lower() in ['.xlsx', '.xls']
    
    def _schedule_upload(self, file_path):
        """Schedule an upload for the file."""
        # Cancel any existing upload for this file
        if file_path in self.upload_times:
            self.upload_times[file_path].cancel()
        
        # Schedule new upload
        timer = threading.Timer(WATCH_DELAY, self._upload_file, args=[file_path])
        self.upload_times[file_path] = timer
        timer.start()
        
        print(f"⏰ Scheduled upload for {file_path.name} in {WATCH_DELAY} seconds...")
    
    def _upload_file(self, file_path):
        """Upload the file to PythonAnywhere."""
        try:
            # Check if file still exists and is not a temporary file
            if not file_path.exists() or file_path.name.startswith("~$"):
                print(f"❌ File no longer exists or is temporary: {file_path.name}")
                return
            
            # Check if file is still being written (size hasn't changed in 2 seconds)
            initial_size = file_path.stat().st_size
            time.sleep(2)
            if file_path.stat().st_size != initial_size:
                print(f"⏳ File {file_path.name} is still being written, skipping upload")
                return
            
            print(f"📤 Uploading {file_path.name} to PythonAnywhere...")
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                
                response = requests.post(
                    f"{PYTHONANYWHERE_URL}/upload",
                    files=files,
                    timeout=60
                )
                
                if response.status_code == 200:
                    print(f"✅ Successfully uploaded {file_path.name}")
                    self.last_uploaded = file_path
                else:
                    print(f"❌ Failed to upload {file_path.name}: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Error uploading {file_path.name}: {e}")
        finally:
            # Clean up timer
            if file_path in self.upload_times:
                del self.upload_times[file_path]

def start_file_watcher():
    """Start watching the uploads folder."""
    uploads_path = Path(UPLOADS_FOLDER)
    
    if not uploads_path.exists():
        print(f"❌ Uploads folder not found: {uploads_path}")
        return
    
    print(f"👀 Starting file watcher for: {uploads_path}")
    print(f"🌐 Will upload to: {PYTHONANYWHERE_URL}")
    print("Press Ctrl+C to stop watching...")
    
    event_handler = ExcelFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(uploads_path), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping file watcher...")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    import threading
    start_file_watcher() 