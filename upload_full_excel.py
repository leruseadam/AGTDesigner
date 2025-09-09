#!/usr/bin/env python3
"""
Upload Full Excel File to Application
Uploads the Excel file with all 7,959 products to the local application
"""

import requests
import os
from pathlib import Path

def upload_excel_file(file_path):
    """Upload Excel file to the application."""
    try:
        print(f"Uploading {file_path} to local application...")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            response = requests.post(
                'http://localhost:5001/upload',
                files=files,
                timeout=300  # 5 minute timeout
            )
            
            if response.status_code == 200:
                print("✅ Excel file uploaded successfully!")
                return True
            else:
                print(f"❌ Upload failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def check_application_status():
    """Check if the application is running."""
    try:
        response = requests.get('http://localhost:5001/api/initial-data', timeout=5)
        if response.status_code == 200:
            print("✅ Application is running")
            return True
        else:
            print(f"❌ Application returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to application: {e}")
        return False

def main():
    """Main function."""
    print("Upload Full Excel File to Local Application")
    print("=" * 50)
    
    # Check if application is running
    if not check_application_status():
        print("❌ Application is not running. Please start it first.")
        return
    
    # Find the Excel file with all products
    excel_file = Path("product_database_export_20250908_133117.xlsx")
    if not excel_file.exists():
        print("❌ Excel file not found. Please run export_database_to_excel.py first.")
        return
    
    file_size_mb = excel_file.stat().st_size / (1024 * 1024)
    print(f"📊 Excel file: {excel_file.name}")
    print(f"📊 File size: {file_size_mb:.1f} MB")
    
    # Upload the file
    if upload_excel_file(excel_file):
        print("\n🎉 Upload completed successfully!")
        print("The application should now have all 7,959 products.")
        print("Refresh your browser to see the updated data.")
    else:
        print("\n❌ Upload failed!")

if __name__ == "__main__":
    main()
