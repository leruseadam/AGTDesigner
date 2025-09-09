#!/usr/bin/env python3
"""
Diagnose Web Database Issue
Checks if the web database is properly loaded and has data
"""

import requests
import json
from datetime import datetime

# Configuration
PYTHONANYWHERE_URL = "https://www.agtpricetags.com"

def check_database_status():
    """Check the database status via web API."""
    try:
        print("🔍 Checking web database status...")
        
        # Check initial data endpoint
        response = requests.get(f"{PYTHONANYWHERE_URL}/api/initial-data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Web application is accessible")
            
            # Check database info
            if 'database_info' in data:
                db_info = data['database_info']
                print(f"📊 Database Info:")
                print(f"   - File exists: {db_info.get('file_exists', 'Unknown')}")
                print(f"   - File size: {db_info.get('file_size', 0):,} bytes")
                print(f"   - Database path: {db_info.get('database_path', 'Unknown')}")
            else:
                print("⚠️  No database info in initial data")
            
            # Check product counts
            if 'stats' in data:
                stats = data['stats']
                print(f"📈 Product Statistics:")
                print(f"   - Total products: {stats.get('total_products', 0)}")
                print(f"   - Total strains: {stats.get('total_strains', 0)}")
                print(f"   - Total vendors: {stats.get('total_vendors', 0)}")
            else:
                print("⚠️  No statistics in initial data")
                
        else:
            print(f"❌ Web application returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking web database: {e}")
        return False
    
    return True

def check_database_endpoint():
    """Check the database-specific endpoint."""
    try:
        print("\n🔍 Checking database endpoint...")
        
        response = requests.get(f"{PYTHONANYWHERE_URL}/api/database-stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Database endpoint accessible")
            print(f"📊 Database Stats: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Database endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking database endpoint: {e}")

def check_upload_status():
    """Check if there are any upload issues."""
    try:
        print("\n🔍 Checking upload status...")
        
        response = requests.get(f"{PYTHONANYWHERE_URL}/api/upload-status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload status endpoint accessible")
            if 'status' in data:
                print(f"📤 Upload Status: {data['status']}")
            if 'message' in data:
                print(f"💬 Message: {data['message']}")
        else:
            print(f"❌ Upload status endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking upload status: {e}")

def suggest_solutions():
    """Suggest solutions based on the diagnosis."""
    print("\n💡 Suggested Solutions:")
    print("=" * 30)
    
    print("1. **Check File Location on PythonAnywhere:**")
    print("   - Log into PythonAnywhere")
    print("   - Go to Files tab")
    print("   - Navigate to /home/adamcordova/AGTDesigner/uploads/")
    print("   - Verify product_database.db exists and has data")
    
    print("\n2. **Check File Permissions:**")
    print("   - Make sure the web app can read the database file")
    print("   - Check file ownership and permissions")
    
    print("\n3. **Restart Web Application:**")
    print("   - Go to PythonAnywhere Web tab")
    print("   - Click 'Reload' button")
    print("   - Wait for restart to complete")
    
    print("\n4. **Re-upload Database:**")
    print("   - Use the manual upload process again")
    print("   - Make sure files are in the correct location")
    
    print("\n5. **Check Database Integrity:**")
    print("   - Verify the database file isn't corrupted")
    print("   - Check if it has the products table with data")

def main():
    """Main diagnostic function."""
    print("Web Database Diagnostic Tool")
    print("=" * 35)
    print(f"Checking: {PYTHONANYWHERE_URL}")
    print(f"Time: {datetime.now()}")
    print()
    
    # Run diagnostics
    check_database_status()
    check_database_endpoint()
    check_upload_status()
    
    # Provide solutions
    suggest_solutions()

if __name__ == "__main__":
    main()
