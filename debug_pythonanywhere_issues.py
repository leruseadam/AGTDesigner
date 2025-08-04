#!/usr/bin/env python3
"""
Comprehensive PythonAnywhere Issue Diagnostic Script
This script will help identify the specific problems with default file loading and manual uploads.
"""

import os
import sys
import logging
import traceback
import time
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pythonanywhere_debug.log')
    ]
)
logger = logging.getLogger(__name__)

def check_pythonanywhere_environment():
    """Check if we're on PythonAnywhere and get environment details."""
    print("=== PythonAnywhere Environment Check ===")
    
    # Check PythonAnywhere indicators
    pythonanywhere_indicators = [
        'PYTHONANYWHERE_SITE' in os.environ,
        'PYTHONANYWHERE_DOMAIN' in os.environ,
        os.path.exists('/var/log/pythonanywhere'),
        'pythonanywhere.com' in os.environ.get('HTTP_HOST', '')
    ]
    
    is_pythonanywhere = any(pythonanywhere_indicators)
    print(f"PythonAnywhere detected: {is_pythonanywhere}")
    
    if is_pythonanywhere:
        print(f"PYTHONANYWHERE_SITE: {os.environ.get('PYTHONANYWHERE_SITE', 'Not set')}")
        print(f"PYTHONANYWHERE_DOMAIN: {os.environ.get('PYTHONANYWHERE_DOMAIN', 'Not set')}")
        print(f"HTTP_HOST: {os.environ.get('HTTP_HOST', 'Not set')}")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    return is_pythonanywhere

def check_file_locations():
    """Check all possible file locations for AGT files."""
    print("\n=== File Location Check ===")
    
    current_dir = os.getcwd()
    home_dir = os.path.expanduser("~")
    
    # Define search locations
    search_locations = [
        os.path.join(current_dir, "uploads"),
        os.path.join(home_dir, "Downloads"),
    ]
    
    # Add PythonAnywhere specific paths
    pythonanywhere_paths = [
        "/home/adamcordova/uploads",
        "/home/adamcordova/AGTDesigner/uploads",
        "/home/adamcordova/AGTDesigner/AGTDesigner/uploads",
        "/home/adamcordova/Downloads",
        "/home/adamcordova/AGTDesigner",
        "/home/adamcordova/AGTDesigner/AGTDesigner",
    ]
    search_locations.extend(pythonanywhere_paths)
    
    agt_files = []
    
    for location in search_locations:
        print(f"\nChecking: {location}")
        if os.path.exists(location):
            print(f"  ✓ Location exists")
            try:
                files = os.listdir(location)
                agt_files_in_location = []
                for filename in files:
                    if filename.startswith("A Greener Today") and filename.lower().endswith(".xlsx"):
                        file_path = os.path.join(location, filename)
                        if os.path.isfile(file_path):
                            mod_time = os.path.getmtime(file_path)
                            file_size = os.path.getsize(file_path)
                            agt_files_in_location.append((file_path, filename, mod_time, file_size))
                            print(f"  ✓ Found: {filename} ({file_size:,} bytes, modified: {time.ctime(mod_time)})")
                
                if not agt_files_in_location:
                    print(f"  - No AGT files found")
                else:
                    agt_files.extend(agt_files_in_location)
                    
            except Exception as e:
                print(f"  ✗ Error reading directory: {e}")
        else:
            print(f"  ✗ Location does not exist")
    
    if agt_files:
        print(f"\n=== Found {len(agt_files)} AGT files ===")
        # Sort by modification time
        agt_files.sort(key=lambda x: x[2], reverse=True)
        for i, (file_path, filename, mod_time, file_size) in enumerate(agt_files):
            print(f"{i+1}. {filename}")
            print(f"   Path: {file_path}")
            print(f"   Size: {file_size:,} bytes")
            print(f"   Modified: {time.ctime(mod_time)}")
            print()
        
        return agt_files[0][0]  # Return most recent file path
    else:
        print("\n❌ No AGT files found in any location!")
        return None

def check_app_imports():
    """Check if the app can be imported and initialized."""
    print("\n=== App Import Check ===")
    
    try:
        # Try to import the app
        print("Attempting to import app...")
        import app
        print("✓ App imported successfully")
        
        # Try to get the Excel processor
        print("Attempting to get Excel processor...")
        excel_processor = app.get_excel_processor()
        print("✓ Excel processor retrieved")
        
        # Check if data is loaded
        if hasattr(excel_processor, 'df') and excel_processor.df is not None:
            print(f"✓ Data loaded: {len(excel_processor.df)} rows")
            if len(excel_processor.df) > 0:
                print(f"✓ Columns: {list(excel_processor.df.columns)}")
        else:
            print("✗ No data loaded")
        
        return True
        
    except Exception as e:
        print(f"✗ Error importing app: {e}")
        traceback.print_exc()
        return False

def check_flask_context_fixes():
    """Check if the Flask context fixes are in place."""
    print("\n=== Flask Context Fixes Check ===")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for has_request_context usage
        has_request_context_count = content.count('has_request_context')
        print(f"has_request_context usage count: {has_request_context_count}")
        
        if has_request_context_count > 0:
            print("✓ Flask context fixes appear to be in place")
            
            # Check specific patterns
            patterns_to_check = [
                'if has_request_context():',
                'else:',
                'sid = \'background\'',
                'logging.info("[BG] Skipping Flask cache clear"'
            ]
            
            for pattern in patterns_to_check:
                if pattern in content:
                    print(f"✓ Found: {pattern}")
                else:
                    print(f"✗ Missing: {pattern}")
        else:
            print("✗ No Flask context fixes found!")
        
        return has_request_context_count > 0
        
    except Exception as e:
        print(f"✗ Error checking Flask context fixes: {e}")
        return False

def check_web_app_status():
    """Check if the web app is running and accessible."""
    print("\n=== Web App Status Check ===")
    
    try:
        # Try to make a request to the app
        import requests
        
        # Get the domain from environment or use a default
        domain = os.environ.get('PYTHONANYWHERE_DOMAIN', 'adamcordova.pythonanywhere.com')
        url = f"https://{domain}/api/status"
        
        print(f"Checking web app at: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"✓ Web app responded with status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✓ Status data: {data}")
            except:
                print("✓ Response received but not JSON")
        
        return True
        
    except Exception as e:
        print(f"✗ Error checking web app: {e}")
        return False

def check_git_status():
    """Check the git status to see what version is deployed."""
    print("\n=== Git Status Check ===")
    
    try:
        # Check current commit
        result = subprocess.run(['git', 'log', '--oneline', '-3'], 
                              capture_output=True, text=True)
        print("Recent commits:")
        print(result.stdout)
        
        # Check if we're up to date
        result = subprocess.run(['git', 'status'], 
                              capture_output=True, text=True)
        print("\nGit status:")
        print(result.stdout)
        
        return True
        
    except Exception as e:
        print(f"✗ Error checking git status: {e}")
        return False

def main():
    """Run all diagnostic checks."""
    print("=== PythonAnywhere Issue Diagnostic ===")
    print("This script will help identify the specific problems with your PythonAnywhere deployment.")
    print()
    
    # Run all checks
    checks = [
        ("Environment", check_pythonanywhere_environment),
        ("File Locations", check_file_locations),
        ("App Imports", check_app_imports),
        ("Flask Context Fixes", check_flask_context_fixes),
        ("Web App Status", check_web_app_status),
        ("Git Status", check_git_status),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"✗ Error in {check_name} check: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("=== DIAGNOSTIC SUMMARY ===")
    print("="*50)
    
    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{check_name}: {status}")
    
    print("\n=== RECOMMENDATIONS ===")
    
    if not results.get("File Locations"):
        print("1. No AGT files found - upload a file through the web interface")
    
    if not results.get("Flask Context Fixes"):
        print("2. Flask context fixes missing - pull latest changes from git")
    
    if not results.get("Web App Status"):
        print("3. Web app not responding - check if it's running and reload it")
    
    print("\n=== NEXT STEPS ===")
    print("1. If files are missing: Upload a file through the web interface")
    print("2. If Flask fixes missing: Run 'git pull origin main' and reload web app")
    print("3. If web app not working: Go to Web tab and click 'Reload'")
    print("4. Check the error logs in the Web tab for specific error messages")

if __name__ == "__main__":
    main() 