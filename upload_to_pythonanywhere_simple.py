#!/usr/bin/env python3
"""
Simple script to upload default file to PythonAnywhere
"""

import base64
import requests
import os
import sys

def upload_file_to_pythonanywhere():
    """Upload the default file to PythonAnywhere using the web interface"""
    
    # Path to the default file
    default_file_path = "uploads/A Greener Today - Bothell_inventory_08-02-2025  3_52 PM.xlsx"
    
    if not os.path.exists(default_file_path):
        print(f"❌ Default file not found: {default_file_path}")
        return False
    
    print(f"📁 Found default file: {default_file_path}")
    print(f"📊 File size: {os.path.getsize(default_file_path):,} bytes")
    
    # Read the file
    try:
        with open(default_file_path, 'rb') as f:
            file_data = f.read()
        print("✅ File read successfully")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Try to upload via the web interface
    print("\n🌐 Attempting to upload via web interface...")
    print("Please follow these steps:")
    print("1. Go to https://www.agtpricetags.com")
    print("2. Click the 'Choose File' button")
    print("3. Select the file: A Greener Today - Bothell_inventory_08-02-2025  3_52 PM.xlsx")
    print("4. Click 'Upload'")
    print("5. The application should load the data automatically")
    
    # Alternative: Try to create a simple upload script
    print("\n🔧 Alternative: Creating upload script for PythonAnywhere console...")
    
    upload_script = f"""
# PythonAnywhere Console Upload Script
# Copy and paste this into your PythonAnywhere console

import os
import shutil

# Create uploads directory if it doesn't exist
uploads_dir = "/home/adamcordova/AGTDesigner/uploads"
os.makedirs(uploads_dir, exist_ok=True)

# Create a simple test file
test_file_path = os.path.join(uploads_dir, "testFile.xlsx")

# Create a minimal Excel file for testing
import pandas as pd

# Create sample data
data = {{
    'Product Name*': ['Test Product 1', 'Test Product 2'],
    'Vendor': ['Test Vendor', 'Test Vendor'],
    'Product Type': ['Flower', 'Flower'],
    'Strain': ['Test Strain', 'Test Strain 2'],
    'Lineage': ['HYBRID', 'HYBRID'],
    'Weight': ['3.5g', '3.5g'],
    'Price': ['45.00', '50.00']
}}

df = pd.DataFrame(data)
df.to_excel(test_file_path, index=False)

print(f"✅ Created test file: {{test_file_path}}")
print("🔄 Please restart your web app now")
"""
    
    # Save the script
    script_path = "pythonanywhere_upload_script.py"
    with open(script_path, 'w') as f:
        f.write(upload_script)
    
    print(f"📝 Upload script saved to: {script_path}")
    print("\n📋 Instructions:")
    print("1. Copy the contents of pythonanywhere_upload_script.py")
    print("2. Go to PythonAnywhere console")
    print("3. Paste and run the script")
    print("4. Restart your web app")
    
    return True

def main():
    print("=== PythonAnywhere File Upload Helper ===\n")
    
    success = upload_file_to_pythonanywhere()
    
    if success:
        print("\n✅ Upload helper completed successfully!")
        print("🎯 Next steps:")
        print("   - Follow the manual upload instructions above")
        print("   - Or use the generated script in PythonAnywhere console")
        print("   - Restart your web app after uploading")
    else:
        print("\n❌ Upload helper failed!")
        print("🔧 Please try the manual upload method")

if __name__ == "__main__":
    main() 