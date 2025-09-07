#!/usr/bin/env python3
"""
Direct Database Deployment Script
Helps deploy the compressed database to PythonAnywhere
"""

import os
import subprocess
import sys

def main():
    print("=== Direct Database Deployment Guide ===")
    print()
    
    # Check if compressed database exists
    if not os.path.exists('product_database.db.gz'):
        print("❌ Compressed database not found. Creating it now...")
        subprocess.run(['gzip', '-c', 'uploads/product_database.db', '>', 'product_database.db.gz'], shell=True)
    
    # Get file size
    size = os.path.getsize('product_database.db.gz')
    size_mb = size / (1024 * 1024)
    
    print(f"✅ Compressed database ready: {size_mb:.1f}MB")
    print()
    
    print("📋 STEP-BY-STEP DEPLOYMENT INSTRUCTIONS:")
    print()
    print("1. 📁 UPLOAD THE COMPRESSED DATABASE:")
    print("   - Go to PythonAnywhere dashboard")
    print("   - Click 'Files' tab")
    print("   - Navigate to your project folder (labelMaker_fresh)")
    print("   - Upload 'product_database.db.gz' (26MB)")
    print()
    
    print("2. 🔧 DECOMPRESS ON THE SERVER:")
    print("   - Open a Bash console in PythonAnywhere")
    print("   - Run these commands:")
    print("     cd labelMaker_fresh")
    print("     gunzip product_database.db.gz")
    print("     mv product_database.db uploads/product_database.db")
    print()
    
    print("3. 🚀 RESTART YOUR WEB APP:")
    print("   - Go to 'Web' tab in PythonAnywhere")
    print("   - Click 'Reload' button")
    print()
    
    print("4. ✅ VERIFY THE DEPLOYMENT:")
    print("   - Visit your web app URL")
    print("   - Check that it shows 7,870 products")
    print("   - Test uploading a new Excel file")
    print()
    
    print("🔗 ALTERNATIVE: Use the migration tool after web app is running:")
    print("   python database_upload_tool.py uploads/product_database.db https://your-username.pythonanywhere.com")
    print()
    
    print("📁 Files ready for upload:")
    print(f"   - product_database.db.gz ({size_mb:.1f}MB)")
    print("   - All source code files")
    print()
    
    print("💡 TIP: The compressed database is small enough for direct upload!")
    print("   No need for chunked uploads or complex migration tools.")

if __name__ == "__main__":
    main()
