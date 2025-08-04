#!/usr/bin/env python3
"""
Simple script to clear stuck upload processing statuses.
Run this if uploads get stuck on "Processing..."
"""

import requests
import json

def clear_stuck_uploads():
    """Clear stuck upload processing statuses."""
    try:
        # Try to connect to the local server
        response = requests.post('http://localhost:5000/api/clear-upload-status', 
                               json={}, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('message', 'Unknown result')}")
            if 'files' in result:
                print(f"   Cleared files: {result['files']}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the Flask app is running.")
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out.")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_upload_status():
    """Check current upload processing statuses."""
    try:
        response = requests.get('http://localhost:5000/api/debug-upload-status', 
                              timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 Current upload statuses:")
            print(f"   Total files: {result.get('total_files', 0)}")
            
            for status_info in result.get('statuses', []):
                print(f"   - {status_info['filename']}: {status_info['status']} (age: {status_info['age_seconds']}s)")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the Flask app is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 Upload Status Management Tool")
    print("=" * 40)
    
    print("\n1. Checking current upload statuses...")
    check_upload_status()
    
    print("\n2. Clearing stuck uploads...")
    clear_stuck_uploads()
    
    print("\n3. Checking status after cleanup...")
    check_upload_status()
    
    print("\n✅ Done!") 