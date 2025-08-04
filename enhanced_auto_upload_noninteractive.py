#!/usr/bin/env python3
"""
Enhanced Auto Upload to PythonAnywhere (Non-Interactive Version)

This script automatically finds the most recent Excel file in the user's Downloads folder
and uploads it to PythonAnywhere without requiring user interaction.

Features:
- Smart file filtering (excludes temp files, prioritizes inventory files)
- Automatic Downloads folder detection
- File validation and size checking
- Upload progress tracking
- Error handling and retry logic
- Non-interactive mode (no user prompts)
"""

import os
import glob
import requests
import time
import json
from pathlib import Path
from datetime import datetime
import platform
import sys

# Configuration
PYTHONANYWHERE_URL = "https://www.agtpricetags.com"
MAX_FILE_SIZE_MB = 50  # Maximum file size to upload
MIN_FILE_SIZE_KB = 10  # Minimum file size to consider valid

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
        raise OSError(f"Unsupported operating system: {system}")

def calculate_file_priority(filename):
    """Calculate priority score for a file based on its name."""
    filename_lower = filename.lower()
    priority = 0
    
    # High priority keywords (inventory files)
    high_priority_keywords = [
        'inventory', 'bothell', 'greener today', 'product', 'cannabis'
    ]
    
    # Medium priority keywords
    medium_priority_keywords = [
        'data', 'export', 'list', 'catalog', 'items'
    ]
    
    # Low priority keywords (avoid these)
    low_priority_keywords = [
        'temp', '~$', 'backup', 'old', 'draft', 'test'
    ]
    
    # Check for high priority keywords
    for keyword in high_priority_keywords:
        if keyword in filename_lower:
            priority += 10
    
    # Check for medium priority keywords
    for keyword in medium_priority_keywords:
        if keyword in filename_lower:
            priority += 5
    
    # Penalize low priority keywords
    for keyword in low_priority_keywords:
        if keyword in filename_lower:
            priority -= 20
    
    return priority

def find_most_recent_excel_file():
    """Find the most recent Excel file in the Downloads folder with smart filtering."""
    downloads_path = get_downloads_folder()
    
    if not downloads_path.exists():
        print(f"❌ Downloads folder not found: {downloads_path}")
        return None
    
    print(f"🔍 Searching Downloads folder: {downloads_path}")
    
    # Find all Excel files
    excel_patterns = ["*.xlsx", "*.xls"]
    excel_files = []
    
    for pattern in excel_patterns:
        excel_files.extend(downloads_path.glob(pattern))
    
    if not excel_files:
        print("❌ No Excel files found in Downloads folder")
        return None
    
    # Filter and score files
    valid_files = []
    for file_path in excel_files:
        try:
            # Skip temp files
            if file_path.name.startswith('~$'):
                continue
            
            # Get file stats
            stat = file_path.stat()
            file_size = stat.st_size
            
            # Skip files that are too small or too large
            if file_size < MIN_FILE_SIZE_KB * 1024:
                continue
            if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                continue
            
            # Calculate priority score
            priority = calculate_file_priority(file_path.name)
            
            valid_files.append({
                'path': file_path,
                'name': file_path.name,
                'size': file_size,
                'modified': stat.st_mtime,
                'priority': priority,
                'modified_date': datetime.fromtimestamp(stat.st_mtime)
            })
            
        except Exception as e:
            print(f"⚠️  Error processing {file_path.name}: {e}")
            continue
    
    if not valid_files:
        print("❌ No valid Excel files found")
        return None
    
    # Sort by priority (highest first), then by modification time (newest first)
    valid_files.sort(key=lambda x: (x['priority'], x['modified']), reverse=True)
    
    # Show top 5 files
    print(f"\n📋 Found {len(valid_files)} valid Excel files:")
    print("-" * 80)
    for i, file_info in enumerate(valid_files[:5]):
        size_mb = file_info['size'] / (1024 * 1024)
        priority_stars = "★" * min(file_info['priority'] // 5, 5)
        print(f"{i+1}. {file_info['name']}")
        print(f"   📅 Modified: {file_info['modified_date'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📏 Size: {size_mb:.1f} MB")
        print(f"   ⭐ Priority: {priority_stars} ({file_info['priority']})")
        print()
    
    # Return the highest priority file
    best_file = valid_files[0]
    print(f"🎯 Selected file: {best_file['name']}")
    print(f"   Priority: {best_file['priority']}")
    print(f"   Modified: {best_file['modified_date'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    return best_file['path']

def upload_file_to_pythonanywhere(file_path):
    """Upload a file to PythonAnywhere."""
    print(f"\n🚀 Uploading {file_path.name} to PythonAnywhere...")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            # Upload to PythonAnywhere
            response = requests.post(
                f"{PYTHONANYWHERE_URL}/upload",
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                print("✅ File uploaded successfully!")
                result = response.json()
                if 'message' in result:
                    print(f"📝 Server response: {result['message']}")
                return True
            else:
                print(f"❌ Upload failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        print("❌ Upload timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check your internet connection")
        return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def main():
    """Main function - non-interactive version."""
    print("🔄 Enhanced Auto Upload to PythonAnywhere (Non-Interactive)")
    print("=" * 60)
    
    # Find the most recent Excel file
    file_path = find_most_recent_excel_file()
    
    if not file_path:
        print("❌ No suitable Excel file found")
        return False
    
    # Upload the file automatically (no confirmation needed)
    print(f"\n🤖 Auto-uploading '{file_path.name}' to PythonAnywhere...")
    print("This will replace the current default file on the web server.")
    
    success = upload_file_to_pythonanywhere(file_path)
    
    if success:
        print("\n🎉 Upload completed successfully!")
        print(f"🌐 Your web version at {PYTHONANYWHERE_URL} should now have the latest data.")
        print("💡 You may need to refresh the page to see the changes.")
    else:
        print("\n❌ Upload failed. Please try again or upload manually.")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 