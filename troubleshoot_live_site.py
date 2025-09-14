#!/usr/bin/env python3
"""
Troubleshoot Live Website Database Issues
This script helps diagnose and fix the empty database problem on agtpricetags.com
"""

import os
import subprocess
import requests
import time
from pathlib import Path

def check_api_endpoints():
    """Check if the API endpoints are working"""
    print("🔍 Checking API endpoints...")
    
    base_url = "https://agtpricetags.com"
    endpoints = [
        "/api/database-stats",
        "/api/database-vendor-stats", 
        "/api/database-analytics"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"  {endpoint}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"  {endpoint}: ERROR - {e}")

def check_website_status():
    """Check if the main website is accessible"""
    print("\n🌐 Checking website status...")
    
    try:
        response = requests.get("https://agtpricetags.com", timeout=10)
        print(f"  Main site: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ Website is accessible")
        else:
            print("  ❌ Website has issues")
    except Exception as e:
        print(f"  ❌ Website error: {e}")

def create_emergency_fix():
    """Create an emergency fix script"""
    print("\n🚨 Creating emergency fix script...")
    
    emergency_script = """#!/bin/bash
# Emergency fix for agtpricetags.com database issues

echo "🚨 Emergency Database Fix for PythonAnywhere"
echo "============================================="

# 1. Check if files exist
echo "1. Checking critical files..."
ls -la /home/adamcordova/AGTDesigner/app.py
ls -la /home/adamcordova/AGTDesigner/product_database.db
ls -la /home/adamcordova/AGTDesigner/core/data/product_database.py

# 2. Check database content
echo "2. Checking database content..."
sqlite3 /home/adamcordova/AGTDesigner/product_database.db "SELECT COUNT(*) FROM products;"

# 3. Check PythonAnywhere web app status
echo "3. Checking web app status..."
echo "Go to PythonAnywhere Web tab and check if the app is running"

# 4. Restart web app
echo "4. To restart web app:"
echo "   - Go to PythonAnywhere Web tab"
echo "   - Click 'Reload' for your web app"
echo "   - Wait 30 seconds for restart"

# 5. Test endpoints
echo "5. Testing endpoints after restart..."
curl -s https://agtpricetags.com/api/database-stats | head -5
"""
    
    with open("emergency_fix.sh", "w") as f:
        f.write(emergency_script)
    
    print("  ✅ Created emergency_fix.sh")
    print("  Upload this to PythonAnywhere and run it to diagnose issues")

def main():
    print("🚨 AGT Label Maker - Live Website Troubleshooting")
    print("=" * 60)
    print()
    
    print("The live website is still showing empty database. Let's diagnose...")
    print()
    
    # Check website status
    check_website_status()
    
    # Check API endpoints
    check_api_endpoints()
    
    # Create emergency fix
    create_emergency_fix()
    
    print("\n🔧 TROUBLESHOOTING STEPS:")
    print("=" * 30)
    print()
    print("1. **Check PythonAnywhere Web App Status**:")
    print("   - Log into PythonAnywhere")
    print("   - Go to Web tab")
    print("   - Verify your web app is running")
    print("   - If not running, click 'Reload'")
    print()
    print("2. **Verify Files Were Uploaded**:")
    print("   - Go to Files tab")
    print("   - Navigate to /home/adamcordova/AGTDesigner/")
    print("   - Check that these files exist:")
    print("     ✅ app.py (should be ~509KB)")
    print("     ✅ product_database.db (should be ~250MB)")
    print("     ✅ core/data/product_database.py")
    print()
    print("3. **Check Database Content**:")
    print("   - In PythonAnywhere console, run:")
    print("     sqlite3 product_database.db 'SELECT COUNT(*) FROM products;'")
    print("   - Should return: 10285")
    print()
    print("4. **Check Web App Logs**:")
    print("   - Go to Web tab in PythonAnywhere")
    print("   - Click on your web app")
    print("   - Check the 'Error log' for any errors")
    print()
    print("5. **Force Restart**:")
    print("   - Stop the web app")
    print("   - Wait 10 seconds")
    print("   - Start it again")
    print("   - Wait 30 seconds for full restart")
    print()
    print("6. **Test the Fix**:")
    print("   - Go to https://agtpricetags.com")
    print("   - Should show 10,285 products instead of 0")
    print()
    print("🚨 EMERGENCY FIX SCRIPT:")
    print("=" * 30)
    print("Upload emergency_fix.sh to PythonAnywhere and run it to diagnose issues")
    print()
    print("📞 If still not working, check:")
    print("   - PythonAnywhere web app configuration")
    print("   - Database file permissions")
    print("   - PythonAnywhere error logs")
    print("   - Web app domain configuration")

if __name__ == "__main__":
    main()
