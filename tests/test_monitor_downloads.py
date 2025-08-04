#!/usr/bin/env python3
"""
Test script to debug Monitor Downloads functionality.
This script tests the monitor-downloads endpoint directly.
"""

import os
import sys
import requests
from pathlib import Path

def test_monitor_downloads_endpoint():
    """Test the monitor-downloads endpoint directly."""
    print("=== Monitor Downloads Endpoint Test ===\n")
    
    try:
        # Test the monitor-downloads endpoint
        url = "http://localhost:5000/api/monitor-downloads"
        
        print(f"Sending POST request to {url}...")
        response = requests.post(url, headers={'Content-Type': 'application/json'})
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"Response data: {data}")
            
            if response.status_code == 200:
                print("✅ Monitor downloads test successful!")
                print(f"Files copied: {data.get('files_copied', 0)}")
                print(f"Message: {data.get('message', 'No message')}")
                if data.get('copied_files'):
                    print(f"Copied files: {data['copied_files']}")
                return True
            else:
                print(f"❌ Monitor downloads test failed: {data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error parsing response: {e}")
            print(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during monitor downloads test: {e}")
        return False

def test_downloads_directory():
    """Test the Downloads directory access and AGT files."""
    print("\n=== Downloads Directory Test ===\n")
    
    downloads_dir = Path.home() / "Downloads"
    
    # Check if Downloads directory exists
    if not downloads_dir.exists():
        print("❌ Downloads directory does not exist")
        return False
    
    print(f"✅ Downloads directory exists: {downloads_dir}")
    
    # Check if directory is readable
    if not os.access(downloads_dir, os.R_OK):
        print("❌ Downloads directory is not readable")
        return False
    
    print("✅ Downloads directory is readable")
    
    # Look for AGT files
    agt_files = []
    try:
        for filename in os.listdir(downloads_dir):
            if filename.startswith("A Greener Today") and filename.lower().endswith(".xlsx"):
                file_path = downloads_dir / filename
                mod_time = os.path.getmtime(file_path)
                size_mb = file_path.stat().st_size / (1024 * 1024)
                agt_files.append({
                    'name': filename,
                    'path': str(file_path),
                    'size_mb': round(size_mb, 2),
                    'mod_time': mod_time
                })
    except Exception as e:
        print(f"❌ Error reading Downloads directory: {e}")
        return False
    
    if not agt_files:
        print("❌ No AGT files found in Downloads directory")
        print("Expected files starting with 'A Greener Today' and ending with '.xlsx'")
        return False
    
    print(f"✅ Found {len(agt_files)} AGT file(s):")
    for file in agt_files:
        print(f"  - {file['name']} ({file['size_mb']} MB)")
    
    return True

def test_uploads_directory():
    """Test the uploads directory access."""
    print("\n=== Uploads Directory Test ===\n")
    
    uploads_dir = Path("uploads")
    
    # Check if uploads directory exists
    if not uploads_dir.exists():
        print("❌ Uploads directory does not exist")
        return False
    
    print(f"✅ Uploads directory exists: {uploads_dir}")
    
    # Check if directory is writable
    if not os.access(uploads_dir, os.W_OK):
        print("❌ Uploads directory is not writable")
        return False
    
    print("✅ Uploads directory is writable")
    
    # List existing files
    existing_files = list(uploads_dir.glob("*.xlsx"))
    if existing_files:
        print(f"✅ Found {len(existing_files)} existing Excel file(s) in uploads:")
        for file in existing_files:
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  - {file.name} ({size_mb:.2f} MB)")
    else:
        print("ℹ️  No existing Excel files in uploads directory")
    
    return True

def test_file_copy_simulation():
    """Simulate the file copy process."""
    print("\n=== File Copy Simulation Test ===\n")
    
    downloads_dir = Path.home() / "Downloads"
    uploads_dir = Path("uploads")
    
    # Find AGT files in Downloads
    agt_files = []
    if downloads_dir.exists():
        for filename in os.listdir(downloads_dir):
            if filename.startswith("A Greener Today") and filename.lower().endswith(".xlsx"):
                file_path = downloads_dir / filename
                upload_path = uploads_dir / filename
                
                # Check if copy would be needed
                needs_copy = False
                if not upload_path.exists():
                    needs_copy = True
                    reason = "File doesn't exist in uploads"
                elif os.path.getmtime(file_path) > os.path.getmtime(upload_path):
                    needs_copy = True
                    reason = "Downloads file is newer"
                else:
                    reason = "File already exists and is up to date"
                
                agt_files.append({
                    'name': filename,
                    'downloads_path': str(file_path),
                    'uploads_path': str(upload_path),
                    'needs_copy': needs_copy,
                    'reason': reason
                })
    
    if not agt_files:
        print("❌ No AGT files found for copy simulation")
        return False
    
    print(f"Found {len(agt_files)} AGT file(s) for copy simulation:")
    for file in agt_files:
        status = "📋 Would copy" if file['needs_copy'] else "✅ No copy needed"
        print(f"  {status}: {file['name']} - {file['reason']}")
    
    return True

def main():
    """Run all tests."""
    print("=== Monitor Downloads Debug Test Suite ===\n")
    
    tests = [
        ("Downloads Directory", test_downloads_directory),
        ("Uploads Directory", test_uploads_directory),
        ("File Copy Simulation", test_file_copy_simulation),
        ("Monitor Downloads Endpoint", test_monitor_downloads_endpoint),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{'✅ PASSED' if result else '❌ FAILED'}: {test_name}\n")
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        
        # Provide troubleshooting tips
        print("\n=== Troubleshooting Tips ===")
        print("1. Make sure the Flask app is running on localhost:5000")
        print("2. Check that the Downloads directory exists and is readable")
        print("3. Verify that AGT Excel files are present in Downloads")
        print("4. Ensure the uploads/ directory exists and is writable")
        print("5. Check the Flask app logs for detailed error messages")
        print("6. On PythonAnywhere, the Downloads directory might be different")

if __name__ == "__main__":
    main() 