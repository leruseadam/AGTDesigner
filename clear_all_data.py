#!/usr/bin/env python3
"""
Script to clear all default files, cached data, and stored uploads.
This ensures the app starts completely clean with no default data.
"""

import os
import shutil
import json
import time
from pathlib import Path

def clear_all_data():
    """Clear all cached data, processing status, and stored uploads."""
    print("🧹 Clearing all default files and cached data...")
    
    # 1. Clear uploads directory
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        for file in uploads_dir.glob("*"):
            if file.is_file():
                file.unlink()
                print(f"  ✓ Removed: {file}")
        print(f"  ✓ Cleared uploads directory")
    
    # 2. Clear cache directory
    cache_dir = Path("cache")
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        print(f"  ✓ Cleared cache directory")
    
    # 3. Clear logs directory (optional)
    logs_dir = Path("logs")
    if logs_dir.exists():
        for file in logs_dir.glob("*.log"):
            file.unlink()
        print(f"  ✓ Cleared log files")
    
    # 4. Clear output directory
    output_dir = Path("output")
    if output_dir.exists():
        for file in output_dir.glob("*"):
            if file.is_file():
                file.unlink()
        print(f"  ✓ Cleared output directory")
    
    # 5. Clear shared data files
    shared_files = [
        "shared_data.pkl",
        "shared_data.json",
        "processing_status.json",
        "excel_processor_cache.pkl"
    ]
    
    for filename in shared_files:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"  ✓ Removed: {filename}")
    
    # 6. Clear any temporary files
    temp_files = [
        "temp_upload.xlsx",
        "temp_data.xlsx",
        "default_inventory.xlsx"
    ]
    
    for filename in temp_files:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"  ✓ Removed: {filename}")
    
    # 7. Clear data directory default files
    data_dir = Path("data")
    if data_dir.exists():
        default_files = [
            "default_inventory.xlsx",
            "sample_inventory.xlsx"
        ]
        for filename in default_files:
            file_path = data_dir / filename
            if file_path.exists():
                file_path.unlink()
                print(f"  ✓ Removed: {file_path}")
    
    print("\n✅ All default files and cached data cleared!")
    print("📝 The app will now start completely clean with no default data.")
    print("📤 Users must upload their own files to use the application.")

if __name__ == "__main__":
    clear_all_data() 