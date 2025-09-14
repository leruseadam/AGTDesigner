#!/usr/bin/env python3
"""
Deploy Critical Database Fixes to PythonAnywhere
This script helps deploy the essential files to fix the empty database issue
"""

import os
import subprocess
from pathlib import Path

def main():
    print("🚀 AGT Label Maker - Deploy Critical Database Fixes")
    print("=" * 60)
    print()
    
    print("The live website is showing empty database because it needs these critical files:")
    print()
    
    # Check if critical files exist
    critical_files = [
        "pythonanywhere_deployment/app.py",
        "pythonanywhere_deployment/core/data/product_database.py", 
        "pythonanywhere_deployment/product_database.db"
    ]
    
    print("Checking critical files...")
    for file in critical_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING!")
    
    print()
    print("🔧 DEPLOYMENT INSTRUCTIONS:")
    print("=" * 40)
    print()
    print("1. Log into PythonAnywhere (https://www.pythonanywhere.com)")
    print("2. Go to Files tab")
    print("3. Navigate to /home/adamcordova/AGTDesigner/")
    print("4. Upload these CRITICAL files from pythonanywhere_deployment/:")
    print()
    
    # List critical files to upload
    critical_uploads = [
        "app.py (MOST IMPORTANT - contains database fallback fixes)",
        "core/data/product_database.py (contains duplicate column fixes)",
        "product_database.db (contains 10,285 products)",
        "core/data/excel_processor.py",
        "core/generation/template_processor.py", 
        "core/generation/tag_generator.py",
        "core/generation/unified_font_sizing.py",
        "core/data/json_matcher.py",
        "static/js/main.js",
        "templates/index.html"
    ]
    
    for i, file in enumerate(critical_uploads, 1):
        print(f"{i:2d}. {file}")
    
    print()
    print("5. After uploading, restart the web app:")
    print("   - Go to Web tab")
    print("   - Click 'Reload' for your web app")
    print()
    print("6. Test at https://agtpricetags.com")
    print("   - Should show 10,285 products instead of 0")
    print()
    print("🔧 QUICK SCP DEPLOYMENT (if you have SSH access):")
    print("=" * 50)
    print()
    print("Run this command to upload all files automatically:")
    print()
    print("scp -r pythonanywhere_deployment/* adamcordova@ssh.pythonanywhere.com:/home/adamcordova/AGTDesigner/")
    print()
    print("⚠️  IMPORTANT: The app.py file contains the database fallback logic")
    print("   that fixes the 'no such table: products' error!")
    print()
    print("📊 EXPECTED RESULTS AFTER DEPLOYMENT:")
    print("=" * 40)
    print("✅ Total Products: 10,285 (instead of 0)")
    print("✅ Unique Vendors: 108 (instead of 0)")
    print("✅ Unique Brands: 170 (instead of 0)")
    print("✅ Product Types: 19 (instead of 0)")

if __name__ == "__main__":
    main()
