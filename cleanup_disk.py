#!/usr/bin/env python3
"""
Disk cleanup utility for Label Maker application.
Run this script to free up disk space and monitor system resources.
"""

import os
import glob
import shutil
import time
from datetime import datetime, timedelta

def check_disk_space():
    """Check available disk space."""
    total, used, free = shutil.disk_usage('.')
    free_gb = free / (1024**3)
    used_percent = (used / total) * 100
    
    print(f"Disk Space Status:")
    print(f"  Total: {total / (1024**3):.1f} GB")
    print(f"  Used: {used / (1024**3):.1f} GB ({used_percent:.1f}%)")
    print(f"  Free: {free_gb:.1f} GB")
    
    if free_gb < 2.0:
        print(f"  ⚠️  CRITICAL: Only {free_gb:.1f}GB free!")
        return False
    elif free_gb < 5.0:
        print(f"  ⚠️  WARNING: Low disk space ({free_gb:.1f}GB free)")
        return True
    else:
        print(f"  ✅ OK: {free_gb:.1f}GB free")
        return True

def cleanup_logs():
    """Clean up large log files."""
    print("\nCleaning up log files...")
    cleaned = 0
    
    for log_file in glob.glob("*.log"):
        try:
            size = os.path.getsize(log_file)
            if size > 1024 * 1024:  # Larger than 1MB
                with open(log_file, 'w') as f:
                    f.write(f"# Log file cleared on {datetime.now()}\n")
                print(f"  ✅ Truncated {log_file} ({size / (1024*1024):.1f}MB)")
                cleaned += 1
        except Exception as e:
            print(f"  ❌ Failed to clean {log_file}: {e}")
    
    return cleaned

def cleanup_uploads():
    """Clean up old upload files."""
    print("\nCleaning up upload files...")
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print("  ℹ️  No uploads directory found")
        return 0
    
    files = []
    for file in os.listdir(uploads_dir):
        if file.endswith('.xlsx'):
            file_path = os.path.join(uploads_dir, file)
            mtime = os.path.getmtime(file_path)
            files.append((file_path, mtime, file))
    
    if len(files) <= 10:
        print(f"  ℹ️  Only {len(files)} upload files (keeping all)")
        return 0
    
    # Sort by modification time (oldest first)
    files.sort(key=lambda x: x[1])
    
    # Remove old files, keep only the 10 most recent
    removed = 0
    for file_path, mtime, filename in files[:-10]:
        try:
            os.remove(file_path)
            age = time.time() - mtime
            print(f"  ✅ Removed old file: {filename} (age: {age/3600:.1f}h)")
            removed += 1
        except Exception as e:
            print(f"  ❌ Failed to remove {filename}: {e}")
    
    return removed

def cleanup_temp_files():
    """Clean up temporary files."""
    print("\nCleaning up temporary files...")
    removed = 0
    
    patterns = ["*.tmp", "*.temp", "*~", "*.bak"]
    for pattern in patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                print(f"  ✅ Removed: {file_path}")
                removed += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {file_path}: {e}")
    
    return removed

def cleanup_cache():
    """Clean up cache directories."""
    print("\nCleaning up cache...")
    removed = 0
    
    cache_dirs = ["cache", "__pycache__", ".pytest_cache"]
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"  ✅ Removed cache directory: {cache_dir}")
                removed += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {cache_dir}: {e}")
    
    return removed

def main():
    print("🧹 Label Maker Disk Cleanup Utility")
    print("=" * 50)
    
    # Check initial disk space
    initial_ok = check_disk_space()
    
    # Perform cleanup
    total_cleaned = 0
    total_cleaned += cleanup_logs()
    total_cleaned += cleanup_uploads()
    total_cleaned += cleanup_temp_files()
    total_cleaned += cleanup_cache()
    
    print(f"\n📊 Cleanup Summary:")
    print(f"  Total items cleaned: {total_cleaned}")
    
    # Check disk space after cleanup
    print(f"\n" + "=" * 50)
    final_ok = check_disk_space()
    
    if not final_ok:
        print(f"\n⚠️  WARNING: Disk space is still critically low!")
        print(f"   Consider:")
        print(f"   - Moving large files to external storage")
        print(f"   - Deleting unnecessary applications")
        print(f"   - Emptying trash")
    elif total_cleaned > 0:
        print(f"\n✅ Cleanup completed successfully!")
    else:
        print(f"\nℹ️  No cleanup needed - system is already clean")

if __name__ == "__main__":
    main() 