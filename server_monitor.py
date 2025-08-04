#!/usr/bin/env python3
"""
PythonAnywhere Server Monitor
"""

import os
import time
import psutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/adamcordova/server_monitor.log'),
        logging.StreamHandler()
    ]
)

def check_server_status():
    """Check server status and resources."""
    try:
        # Check disk space
        disk_usage = psutil.disk_usage('/home/adamcordova')
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        
        # Check memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        logging.info(f"Server Status - Disk: {disk_percent:.1f}%, Memory: {memory_percent:.1f}%, CPU: {cpu_percent:.1f}%")
        
        # Check for potential issues
        if disk_percent > 90:
            logging.warning(f"Disk usage is high: {disk_percent:.1f}%")
        
        if memory_percent > 80:
            logging.warning(f"Memory usage is high: {memory_percent:.1f}%")
        
        if cpu_percent > 80:
            logging.warning(f"CPU usage is high: {cpu_percent:.1f}%")
            
    except Exception as e:
        logging.error(f"Error checking server status: {e}")

def check_log_files():
    """Check for log file issues."""
    log_files = [
        '/home/adamcordova/pythonanywhere.log',
        '/home/adamcordova/AGTDesigner/pythonanywhere.log',
        '/var/log/pythonanywhere/error.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                # Check file size
                size = os.path.getsize(log_file)
                if size > 10 * 1024 * 1024:  # 10MB
                    logging.warning(f"Log file is large: {log_file} ({size / 1024 / 1024:.1f}MB)")
                
                # Check for recent errors
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-100:]  # Last 100 lines
                    
                    error_count = sum(1 for line in recent_lines if 'ERROR' in line or '--- Logging error ---' in line)
                    if error_count > 10:
                        logging.warning(f"Many errors in log file: {log_file} ({error_count} errors in last 100 lines)")
                        
            except Exception as e:
                logging.error(f"Error checking log file {log_file}: {e}")

def cleanup_old_files():
    """Clean up old files to free space."""
    try:
        # Clean up old log files
        log_dir = '/home/adamcordova/AGTDesigner/logs'
        if os.path.exists(log_dir):
            for file in os.listdir(log_dir):
                file_path = os.path.join(log_dir, file)
                if os.path.isfile(file_path):
                    # Remove files older than 7 days
                    if time.time() - os.path.getmtime(file_path) > 7 * 24 * 3600:
                        os.remove(file_path)
                        logging.info(f"Removed old log file: {file}")
        
        # Clean up old uploads
        uploads_dir = '/home/adamcordova/AGTDesigner/uploads'
        if os.path.exists(uploads_dir):
            for file in os.listdir(uploads_dir):
                file_path = os.path.join(uploads_dir, file)
                if os.path.isfile(file_path):
                    # Remove files older than 30 days
                    if time.time() - os.path.getmtime(file_path) > 30 * 24 * 3600:
                        os.remove(file_path)
                        logging.info(f"Removed old upload file: {file}")
                        
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")

def main():
    """Main monitoring function."""
    logging.info("Starting server monitor...")
    
    while True:
        try:
            check_server_status()
            check_log_files()
            cleanup_old_files()
            
            # Wait 5 minutes before next check
            time.sleep(300)
            
        except KeyboardInterrupt:
            logging.info("Server monitor stopped by user")
            break
        except Exception as e:
            logging.error(f"Error in server monitor: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    main()
