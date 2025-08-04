#!/usr/bin/env python3
"""
Downloads Folder Watcher for PythonAnywhere

This script watches the Downloads folder for new Excel files and automatically
uploads them to PythonAnywhere to keep the web version in sync.
"""

import os
import time
import requests
import threading
from pathlib import Path
from datetime import datetime
import platform
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
PYTHONANYWHERE_URL = "https://www.agtpricetags.com"
WATCH_DELAY = 5  # Seconds to wait before uploading (to ensure file is complete)

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

class DownloadsExcelHandler(FileSystemEventHandler):
    """Handler for Excel file events in Downloads folder."""
    
    def __init__(self):
        self.last_uploaded = None
        self.upload_times = {}
        self.uploaded_files = set()
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if self._is_excel_file(file_path):
            print(f"📁 New Excel file detected in Downloads: {file_path.name}")
            self._schedule_upload(file_path)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if self._is_excel_file(file_path):
            print(f"📝 Excel file modified in Downloads: {file_path.name}")
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
            
            # Check if we've already uploaded this file recently
            file_id = f"{file_path.name}_{file_path.stat().st_mtime}"
            if file_id in self.uploaded_files:
                print(f"🔄 File {file_path.name} already uploaded recently, skipping")
                return
            
            print(f"📤 Uploading {file_path.name} to PythonAnywhere...")
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                
                response = requests.post(
                    f"{PYTHONANYWHERE_URL}/upload",
                    files=files,
                    timeout=120
                )
                
                if response.status_code == 200:
                    print(f"✅ Successfully uploaded {file_path.name}")
                    self.last_uploaded = file_path
                    self.uploaded_files.add(file_id)
                    
                    # Keep only last 10 uploaded files to prevent memory growth
                    if len(self.uploaded_files) > 10:
                        self.uploaded_files.clear()
                else:
                    print(f"❌ Failed to upload {file_path.name}: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Error uploading {file_path.name}: {e}")
        finally:
            # Clean up timer
            if file_path in self.upload_times:
                del self.upload_times[file_path]

def start_downloads_watcher():
    """Start watching the Downloads folder."""
    downloads_path = get_downloads_folder()
    
    if not downloads_path.exists():
        print(f"❌ Downloads folder not found: {downloads_path}")
        return
    
    print(f"👀 Starting Downloads folder watcher for: {downloads_path}")
    print(f"🌐 Will upload to: {PYTHONANYWHERE_URL}")
    print("📋 Will automatically upload new Excel files as they appear")
    print("Press Ctrl+C to stop watching...")
    
    event_handler = DownloadsExcelHandler()
    observer = Observer()
    observer.schedule(event_handler, str(downloads_path), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Downloads folder watcher...")
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    start_downloads_watcher() 