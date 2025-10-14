#!/usr/bin/env python3
"""
Automatic cleanup script to prevent large data accumulation.
This script removes old backups and temporary files to maintain disk space.
"""

import os
import glob
import time
from datetime import datetime, timedelta
from pathlib import Path

# Import configuration
try:
    from cleanup_config import *
except ImportError:
    # Default values if config file doesn't exist
    DATABASE_BACKUP_RETENTION_DAYS = 3
    EMERGENCY_BACKUP_RETENTION_DAYS = 1
    TEMP_FILE_RETENTION_HOURS = 0
    ZIP_FILE_RETENTION_DAYS = 7
    CORRUPTED_BACKUP_RETENTION_HOURS = 0

def cleanup_large_files():
    """Clean up large files to prevent disk quota issues."""
    
    print("🧹 Starting automatic cleanup of large files...")
    
    # Define cleanup rules using configuration
    cleanup_rules = [
        {
            'pattern': 'uploads/backups/db_backup_auto_*.db',
            'max_age_days': DATABASE_BACKUP_RETENTION_DAYS,
            'description': 'Database auto backups'
        },
        {
            'pattern': 'uploads/backups/emergency_backup_*.db',
            'max_age_days': EMERGENCY_BACKUP_RETENTION_DAYS,
            'description': 'Emergency backups'
        },
        {
            'pattern': 'uploads/*.db-shm',
            'max_age_days': TEMP_FILE_RETENTION_HOURS / 24,  # Convert hours to days
            'description': 'SQLite shared memory files'
        },
        {
            'pattern': 'uploads/*.db-wal',
            'max_age_days': TEMP_FILE_RETENTION_HOURS / 24,  # Convert hours to days
            'description': 'SQLite WAL files'
        },
        {
            'pattern': 'uploads/*.db-journal',
            'max_age_days': TEMP_FILE_RETENTION_HOURS / 24,  # Convert hours to days
            'description': 'SQLite journal files'
        },
        {
            'pattern': '*.zip',
            'max_age_days': ZIP_FILE_RETENTION_DAYS,
            'description': 'Zip archives'
        },
        {
            'pattern': 'uploads/old_corrupted_backups/*',
            'max_age_days': CORRUPTED_BACKUP_RETENTION_HOURS / 24,  # Convert hours to days
            'description': 'Old corrupted backups'
        }
    ]
    
    total_freed = 0
    files_removed = 0
    
    for rule in cleanup_rules:
        pattern = rule['pattern']
        max_age_days = rule['max_age_days']
        description = rule['description']
        
        print(f"\n📁 Cleaning {description} (pattern: {pattern})")
        
        # Find files matching pattern
        files = glob.glob(pattern)
        
        if not files:
            print(f"   No files found matching {pattern}")
            continue
            
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        for file_path in files:
            try:
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                file_age = time.time() - file_stat.st_mtime
                
                # Check if file should be removed
                should_remove = False
                if max_age_days == 0:
                    should_remove = True  # Remove immediately
                elif file_age > (max_age_days * 24 * 60 * 60):
                    should_remove = True  # File is older than max age
                
                if should_remove:
                    print(f"   🗑️  Removing: {file_path} ({file_size:,} bytes, {file_age/3600:.1f}h old)")
                    os.remove(file_path)
                    total_freed += file_size
                    files_removed += 1
                else:
                    print(f"   ✅ Keeping: {file_path} ({file_size:,} bytes, {file_age/3600:.1f}h old)")
                    
            except Exception as e:
                print(f"   ❌ Error processing {file_path}: {e}")
    
    print(f"\n📊 Cleanup Summary:")
    print(f"   Files removed: {files_removed}")
    print(f"   Space freed: {total_freed:,} bytes ({total_freed/1024/1024:.1f} MB)")
    
    return total_freed, files_removed

def get_disk_usage():
    """Get current disk usage."""
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        return {
            'total': total,
            'used': used,
            'free': free,
            'percent_used': (used / total) * 100
        }
    except Exception as e:
        print(f"Error getting disk usage: {e}")
        return None

def main():
    """Main cleanup function."""
    print("🚀 Starting Large Data Cleanup")
    print("=" * 50)
    
    # Get initial disk usage
    disk_info = get_disk_usage()
    if disk_info:
        print(f"📊 Initial disk usage: {disk_info['percent_used']:.1f}% used")
        print(f"   Free space: {disk_info['free']/1024/1024/1024:.1f} GB")
    
    # Run cleanup
    freed_bytes, removed_files = cleanup_large_files()
    
    # Get final disk usage
    disk_info_after = get_disk_usage()
    if disk_info_after:
        print(f"\n📊 Final disk usage: {disk_info_after['percent_used']:.1f}% used")
        print(f"   Free space: {disk_info_after['free']/1024/1024/1024:.1f} GB")
        
        if disk_info:
            improvement = disk_info['percent_used'] - disk_info_after['percent_used']
            print(f"   Improvement: {improvement:.1f}% reduction")
    
    print(f"\n✅ Cleanup complete!")
    print(f"   Removed {removed_files} files")
    print(f"   Freed {freed_bytes/1024/1024:.1f} MB")

if __name__ == "__main__":
    main()
