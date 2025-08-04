#!/usr/bin/env python3
"""
Simple diagnostic script to debug upload status issues on PythonAnywhere.
Run this on PythonAnywhere to check what's happening with upload processing.
"""

import requests
import json
import time

def check_upload_status():
    """Check the current upload status."""
    print("=== Upload Status Check ===")
    
    try:
        # Check debug upload status
        response = requests.get('http://localhost:5000/api/debug-upload-status')
        if response.status_code == 200:
            data = response.json()
            print(f"Total files in processing: {data['total_files']}")
            print(f"Processing files: {data['processing_files']}")
            print(f"Ready files: {data['ready_files']}")
            print(f"Error files: {data['error_files']}")
            
            print("\nDetailed statuses:")
            for status in data['statuses']:
                print(f"  {status['filename']}: {status['status']} (age: {status['age_seconds']}s)")
            
            print(f"\nExcel processor info:")
            excel_info = data['excel_processor']
            print(f"  Has processor: {excel_info['has_processor']}")
            print(f"  Has dataframe: {excel_info['has_dataframe']}")
            print(f"  Dataframe shape: {excel_info['dataframe_shape']}")
            print(f"  Dataframe empty: {excel_info['dataframe_empty']}")
            print(f"  Last loaded file: {excel_info['last_loaded_file']}")
            
        else:
            print(f"Error getting debug status: {response.status_code}")
            
    except Exception as e:
        print(f"Error checking upload status: {e}")

def clear_stuck_uploads():
    """Clear any stuck upload statuses."""
    print("\n=== Clearing Stuck Uploads ===")
    
    try:
        response = requests.post('http://localhost:5000/api/clear-upload-status', 
                               json={})
        if response.status_code == 200:
            data = response.json()
            print(f"Result: {data['message']}")
        else:
            print(f"Error clearing uploads: {response.status_code}")
            
    except Exception as e:
        print(f"Error clearing uploads: {e}")

def check_app_status():
    """Check if the app is running and responding."""
    print("\n=== App Status Check ===")
    
    try:
        response = requests.get('http://localhost:5000/api/status')
        if response.status_code == 200:
            data = response.json()
            print(f"App is running: {data.get('status', 'unknown')}")
            print(f"Data loaded: {data.get('data_loaded', False)}")
            print(f"Records count: {data.get('records_count', 0)}")
        else:
            print(f"App not responding: {response.status_code}")
            
    except Exception as e:
        print(f"Error checking app status: {e}")

def main():
    """Run all diagnostic checks."""
    print("=== Upload Issue Diagnostic ===")
    print("This script will help identify why uploads are showing 'not_found' status.")
    print()
    
    # Check if app is running
    check_app_status()
    
    # Check current upload statuses
    check_upload_status()
    
    # Clear stuck uploads if any
    clear_stuck_uploads()
    
    print("\n=== Recommendations ===")
    print("1. If you see stuck 'processing' statuses, they've been cleared")
    print("2. If the Excel processor shows no data, try uploading a file again")
    print("3. If the app is not responding, check if it's running")
    print("4. Check the PythonAnywhere error logs for Flask context errors")

if __name__ == "__main__":
    main() 