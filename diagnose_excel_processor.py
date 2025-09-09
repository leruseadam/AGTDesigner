#!/usr/bin/env python3
"""
Diagnose Excel Processor Issue
Checks if the Excel processor is working on the web version
"""

import requests
import json
from datetime import datetime

# Configuration
PYTHONANYWHERE_URL = "https://www.agtpricetags.com"

def check_excel_processor():
    """Check if Excel processor is working."""
    try:
        print("🔍 Checking Excel processor status...")
        
        # Test the products search endpoint which uses Excel processor
        response = requests.get(
            f"{PYTHONANYWHERE_URL}/api/products/search?vendor=Test&q=test",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Products search endpoint accessible")
            
            if 'error' in data:
                print(f"❌ Excel processor error: {data['error']}")
                return False
            else:
                print("✅ Excel processor appears to be working")
                return True
        else:
            print(f"❌ Products search failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Excel processor: {e}")
        return False

def check_excel_files():
    """Check if Excel files are available."""
    try:
        print("\n🔍 Checking Excel file availability...")
        
        # Check the product database file info endpoint
        response = requests.get(f"{PYTHONANYWHERE_URL}/api/product-db/file-info", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Product database file info accessible")
            print(f"📊 File Info: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ File info endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Excel files: {e}")
        return False

def check_initial_data():
    """Check initial data for Excel processor info."""
    try:
        print("\n🔍 Checking initial data for Excel info...")
        
        response = requests.get(f"{PYTHONANYWHERE_URL}/api/initial-data", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Look for Excel processor related info
            if 'excel_info' in data:
                print("✅ Excel info found in initial data")
                print(f"📊 Excel Info: {json.dumps(data['excel_info'], indent=2)}")
            else:
                print("⚠️  No Excel info in initial data")
            
            # Check if there's any indication of Excel data loading
            if 'data_loaded' in data:
                print(f"📈 Data loaded status: {data['data_loaded']}")
            
            return True
        else:
            print(f"❌ Initial data check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking initial data: {e}")
        return False

def suggest_excel_solutions():
    """Suggest solutions for Excel processor issues."""
    print("\n💡 Solutions for Excel Processor Issues:")
    print("=" * 45)
    
    print("1. **Upload Excel Files to PythonAnywhere:**")
    print("   - The Product Sheet uses Excel data, not the database")
    print("   - Upload your Excel files to /home/adamcordova/AGTDesigner/uploads/")
    print("   - Make sure the Excel files are in the correct format")
    
    print("\n2. **Check Excel File Format:**")
    print("   - Ensure Excel files have the required columns:")
    print("     - 'Vendor/Supplier*'")
    print("     - 'Product Brand'")
    print("     - 'Product Type*'")
    print("     - 'Strain Names' (for lineage)")
    
    print("\n3. **Restart Web Application:**")
    print("   - Go to PythonAnywhere Web tab")
    print("   - Click 'Reload' button")
    print("   - This will reload the Excel processor")
    
    print("\n4. **Check File Permissions:**")
    print("   - Ensure the web app can read Excel files")
    print("   - Check file ownership and permissions")
    
    print("\n5. **Use Database Instead of Excel:**")
    print("   - The database is working (7,959 products)")
    print("   - Consider modifying the Product Sheet to use database data")
    print("   - This would be more reliable than Excel files")

def main():
    """Main diagnostic function."""
    print("Excel Processor Diagnostic Tool")
    print("=" * 35)
    print(f"Checking: {PYTHONANYWHERE_URL}")
    print(f"Time: {datetime.now()}")
    print()
    
    # Run diagnostics
    excel_working = check_excel_processor()
    file_info_working = check_excel_files()
    initial_data_working = check_initial_data()
    
    # Summary
    print(f"\n📊 Diagnostic Summary:")
    print(f"   - Excel Processor: {'✅ Working' if excel_working else '❌ Not Working'}")
    print(f"   - File Info: {'✅ Working' if file_info_working else '❌ Not Working'}")
    print(f"   - Initial Data: {'✅ Working' if initial_data_working else '❌ Not Working'}")
    
    if not excel_working:
        suggest_excel_solutions()

if __name__ == "__main__":
    main()
