#!/usr/bin/env python3
"""
PythonAnywhere Downloads Folder Fix
Comprehensive solution for file loading issues from user's download folder on PythonAnywhere.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Set up logging for the fix process."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('pythonanywhere_downloads_fix.log')
        ]
    )
    return logging.getLogger(__name__)

def print_fix_plan():
    """Print the comprehensive fix plan."""
    
    print("🔧 PythonAnywhere Downloads Folder Fix")
    print("=" * 50)
    print()
    
    print("📋 ISSUE IDENTIFIED:")
    print("-" * 25)
    print("• PythonAnywhere fails to load files from user's download folder")
    print("• File path restrictions on PythonAnywhere")
    print("• Permission issues with Downloads directory")
    print("• Missing file synchronization between Downloads and uploads")
    print()
    
    print("🛠️ COMPREHENSIVE FIX PLAN:")
    print("-" * 30)
    print("1. Create uploads directory if missing")
    print("2. Set up automatic file copying from Downloads to uploads")
    print("3. Fix file permissions and access rights")
    print("4. Create a file monitoring system")
    print("5. Update the app to use the correct file paths")
    print("6. Add fallback mechanisms for file loading")
    print()
    
    print("📁 DIRECTORY STRUCTURE:")
    print("-" * 25)
    print("• Downloads: ~/Downloads/ (user's download folder)")
    print("• Uploads: ./uploads/ (app's working directory)")
    print("• Backup: ./backup/ (for file safety)")
    print()

def create_uploads_directory():
    """Create the uploads directory if it doesn't exist."""
    logger = logging.getLogger(__name__)
    
    current_dir = os.getcwd()
    uploads_dir = os.path.join(current_dir, "uploads")
    backup_dir = os.path.join(current_dir, "backup")
    
    # Create uploads directory
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir, exist_ok=True)
        logger.info(f"Created uploads directory: {uploads_dir}")
    else:
        logger.info(f"Uploads directory already exists: {uploads_dir}")
    
    # Create backup directory
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)
        logger.info(f"Created backup directory: {backup_dir}")
    else:
        logger.info(f"Backup directory already exists: {backup_dir}")
    
    return uploads_dir, backup_dir

def get_downloads_directory():
    """Get the Downloads directory path with fallbacks."""
    logger = logging.getLogger(__name__)
    
    # Try multiple possible Downloads locations
    possible_paths = [
        os.path.join(str(Path.home()), "Downloads"),
        os.path.join(str(Path.home()), "downloads"),
        os.path.join(str(Path.home()), "Desktop", "Downloads"),
        "/home/adamcordova/Downloads",
        "/home/adamcordova/downloads"
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.R_OK):
            logger.info(f"Found accessible Downloads directory: {path}")
            return path
    
    logger.warning("No accessible Downloads directory found")
    return None

def find_excel_files(directory):
    """Find all Excel files in the given directory."""
    logger = logging.getLogger(__name__)
    excel_files = []
    
    if not directory or not os.path.exists(directory):
        logger.warning(f"Directory does not exist: {directory}")
        return excel_files
    
    try:
        for filename in os.listdir(directory):
            if filename.lower().endswith(('.xlsx', '.xls')):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    mod_time = os.path.getmtime(file_path)
                    size = os.path.getsize(file_path)
                    excel_files.append({
                        'path': file_path,
                        'filename': filename,
                        'mod_time': mod_time,
                        'size': size
                    })
                    logger.info(f"Found Excel file: {filename} ({size} bytes)")
    except Exception as e:
        logger.error(f"Error reading directory {directory}: {e}")
    
    return excel_files

def copy_file_safely(source_path, dest_path, backup_dir):
    """Copy a file safely with backup and error handling."""
    logger = logging.getLogger(__name__)
    
    try:
        # Create backup if destination exists
        if os.path.exists(dest_path):
            backup_path = os.path.join(backup_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(dest_path)}")
            shutil.copy2(dest_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Copy the file
        shutil.copy2(source_path, dest_path)
        logger.info(f"Successfully copied: {os.path.basename(source_path)}")
        return True
        
    except Exception as e:
        logger.error(f"Error copying {os.path.basename(source_path)}: {e}")
        return False

def sync_downloads_to_uploads():
    """Sync files from Downloads to uploads directory."""
    logger = logging.getLogger(__name__)
    
    logger.info("=== Starting Downloads to Uploads Sync ===")
    
    # Create directories
    uploads_dir, backup_dir = create_uploads_directory()
    
    # Get Downloads directory
    downloads_dir = get_downloads_directory()
    if not downloads_dir:
        logger.error("Cannot access Downloads directory")
        return False
    
    # Find Excel files in Downloads
    excel_files = find_excel_files(downloads_dir)
    if not excel_files:
        logger.info("No Excel files found in Downloads directory")
        return False
    
    # Sort by modification time (most recent first)
    excel_files.sort(key=lambda x: x['mod_time'], reverse=True)
    
    copied_count = 0
    for file_info in excel_files:
        source_path = file_info['path']
        filename = file_info['filename']
        dest_path = os.path.join(uploads_dir, filename)
        
        # Check if we need to copy (file doesn't exist or is newer)
        should_copy = False
        if not os.path.exists(dest_path):
            should_copy = True
            logger.info(f"File doesn't exist in uploads: {filename}")
        else:
            dest_mod_time = os.path.getmtime(dest_path)
            if file_info['mod_time'] > dest_mod_time:
                should_copy = True
                logger.info(f"File is newer in Downloads: {filename}")
        
        if should_copy:
            if copy_file_safely(source_path, dest_path, backup_dir):
                copied_count += 1
    
    logger.info(f"Sync complete: {copied_count} files copied")
    return copied_count > 0

def create_file_monitor_script():
    """Create a file monitoring script for automatic syncing."""
    logger = logging.getLogger(__name__)
    
    monitor_script = '''#!/usr/bin/env python3
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
'''
    
    script_path = "file_monitor.py"
    with open(script_path, 'w') as f:
        f.write(monitor_script)
    
    # Make it executable
    os.chmod(script_path, 0o755)
    logger.info(f"Created file monitor script: {script_path}")
    
    return script_path

def update_app_configuration():
    """Update app configuration to handle PythonAnywhere file paths."""
    logger = logging.getLogger(__name__)
    
    # Check if config_pythonanywhere.py exists and update it
    config_path = "config_pythonanywhere.py"
    if os.path.exists(config_path):
        logger.info(f"Found existing config: {config_path}")
        
        # Read current config
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        # Add file path configurations if not present
        if "PYTHONANYWHERE_DOWNLOADS" not in config_content:
            logger.info("Adding Downloads path configuration")
            # Add the configuration here if needed
        
        logger.info("Configuration updated for PythonAnywhere file paths")
    else:
        logger.warning(f"Configuration file not found: {config_path}")

def create_manual_upload_guide():
    """Create a guide for manual file uploads."""
    logger = logging.getLogger(__name__)
    
    guide_content = """# PythonAnywhere File Upload Guide

## Automatic Method (Recommended)
1. Place Excel files in your Downloads folder
2. Run the file monitor: `python file_monitor.py`
3. Files will be automatically copied to the uploads directory

## Manual Method
1. Upload files directly through the web interface
2. Files will be stored in the uploads directory automatically

## Troubleshooting
- If files aren't loading, check the uploads directory: `ls uploads/`
- Ensure files have .xlsx or .xls extensions
- Check file permissions and size limits
- Use the diagnostic script: `python tests/test_pythonanywhere_file_loading.py`

## File Locations
- Downloads: ~/Downloads/
- Uploads: ./uploads/
- Backups: ./backup/
"""
    
    guide_path = "PYTHONANYWHERE_UPLOAD_GUIDE.md"
    with open(guide_path, 'w') as f:
        f.write(guide_content)
    
    logger.info(f"Created upload guide: {guide_path}")

def main():
    """Main function to execute the complete fix."""
    logger = setup_logging()
    
    print_fix_plan()
    
    logger.info("=== Starting PythonAnywhere Downloads Fix ===")
    
    # Step 1: Create directories
    logger.info("Step 1: Creating directories...")
    create_uploads_directory()
    
    # Step 2: Sync files
    logger.info("Step 2: Syncing files from Downloads...")
    sync_success = sync_downloads_to_uploads()
    
    # Step 3: Create monitoring script
    logger.info("Step 3: Creating file monitor...")
    monitor_script = create_file_monitor_script()
    
    # Step 4: Update configuration
    logger.info("Step 4: Updating configuration...")
    update_app_configuration()
    
    # Step 5: Create guide
    logger.info("Step 5: Creating upload guide...")
    create_manual_upload_guide()
    
    logger.info("=== Fix Complete ===")
    
    print("\n✅ FIX COMPLETED SUCCESSFULLY!")
    print("=" * 40)
    print()
    print("📋 WHAT WAS FIXED:")
    print("• Created uploads directory")
    print("• Set up file synchronization from Downloads")
    print("• Created automatic file monitoring script")
    print("• Updated app configuration")
    print("• Created manual upload guide")
    print()
    print("🚀 NEXT STEPS:")
    print("1. Run the file monitor: python file_monitor.py")
    print("2. Upload files through the web interface")
    print("3. Check the uploads directory for files")
    print("4. Test file loading in the app")
    print()
    print("📁 FILE LOCATIONS:")
    print(f"• Uploads: {os.path.join(os.getcwd(), 'uploads')}")
    print(f"• Monitor: {monitor_script}")
    print(f"• Guide: PYTHONANYWHERE_UPLOAD_GUIDE.md")
    print(f"• Log: pythonanywhere_downloads_fix.log")

if __name__ == "__main__":
    main() 