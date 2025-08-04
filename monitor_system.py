#!/usr/bin/env python3
"""
System monitoring utility for Label Maker application.
Run this script to check system health and application status.
"""

import os
import shutil
import subprocess
import time
import requests
from datetime import datetime

def check_disk_space():
    """Check available disk space."""
    total, used, free = shutil.disk_usage('.')
    free_gb = free / (1024**3)
    used_percent = (used / total) * 100
    
    print(f"💾 Disk Space:")
    print(f"  Free: {free_gb:.1f}GB ({used_percent:.1f}% used)")
    
    if free_gb < 2.0:
        print(f"  ⚠️  CRITICAL: Only {free_gb:.1f}GB free!")
        return False
    elif free_gb < 5.0:
        print(f"  ⚠️  WARNING: Low disk space")
        return True
    else:
        print(f"  ✅ OK")
        return True

def check_app_status():
    """Check if the Flask application is running."""
    try:
        response = requests.get('http://127.0.0.1:9090/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"🌐 Application Status:")
            print(f"  ✅ Running on http://127.0.0.1:9090")
            print(f"  Data loaded: {data.get('data_loaded', 'Unknown')}")
            print(f"  Records: {data.get('data_shape', 'Unknown')}")
            return True
        else:
            print(f"🌐 Application Status:")
            print(f"  ❌ HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"🌐 Application Status:")
        print(f"  ❌ Not responding: {e}")
        return False

def check_large_files():
    """Check for large files that might be consuming space."""
    print(f"📁 Large Files (>10MB):")
    large_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv' and d != '.venv']
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > 10 * 1024 * 1024:  # Larger than 10MB
                    relative_path = os.path.relpath(file_path, '.')
                    large_files.append((relative_path, size))
            except (OSError, FileNotFoundError):
                continue
    
    if large_files:
        # Sort by size (largest first)
        large_files.sort(key=lambda x: x[1], reverse=True)
        for file_path, size in large_files[:5]:  # Show top 5
            size_mb = size / (1024 * 1024)
            print(f"  📄 {file_path} ({size_mb:.1f}MB)")
    else:
        print(f"  ℹ️  No large files found")

def check_processes():
    """Check for running Python processes."""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        python_processes = [line for line in result.stdout.split('\n') if 'python' in line.lower() and 'app.py' in line]
        
        print(f"🔄 Python Processes:")
        if python_processes:
            for process in python_processes[:3]:  # Show first 3
                parts = process.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    cmd = ' '.join(parts[10:])
                    print(f"  🔵 PID {pid}: {cmd[:50]}...")
        else:
            print(f"  ❌ No Python app.py processes found")
            return False
        return True
    except Exception as e:
        print(f"🔄 Python Processes:")
        print(f"  ❌ Error checking processes: {e}")
        return False

def main():
    print("🔍 Label Maker System Monitor")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check various system aspects
    disk_ok = check_disk_space()
    print()
    
    app_ok = check_app_status()
    print()
    
    process_ok = check_processes()
    print()
    
    check_large_files()
    print()
    
    # Summary
    print("=" * 50)
    print("📊 Summary:")
    if disk_ok and app_ok and process_ok:
        print("  ✅ System is healthy")
    else:
        print("  ⚠️  Issues detected:")
        if not disk_ok:
            print("    - Low disk space")
        if not app_ok:
            print("    - Application not responding")
        if not process_ok:
            print("    - Application process not found")
    
    print(f"\n💡 Recommendations:")
    if not disk_ok:
        print("  - Run: python cleanup_disk.py")
    if not app_ok or not process_ok:
        print("  - Restart application: python app.py")
    if disk_ok and app_ok and process_ok:
        print("  - System is running well!")

if __name__ == "__main__":
    main() 