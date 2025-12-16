#!/usr/bin/env python3
"""
Test if Excel uploads are adding products to the database
"""

import sys
import os
import sqlite3

def test_excel_upload():
    """Test Excel upload functionality."""
    
    print("=" * 80)
    print("TESTING EXCEL UPLOAD TO DATABASE")
    print("=" * 80)
    
    db_path = "uploads/product_database.db"
    
    # Check current product count
    print("\n1️⃣  Checking current database state...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM products;")
        initial_count = cursor.fetchone()[0]
        print(f"   Current products in database: {initial_count:,}")
        
        # Get most recent product
        cursor.execute('SELECT "Product Name*", "Source", datetime(created_at) FROM products ORDER BY created_at DESC LIMIT 5;')
        recent = cursor.fetchall()
        
        if recent:
            print(f"\n   📊 Most recent products:")
            for name, source, created in recent:
                print(f"      '{name}' from '{source}' ({created})")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Check if ProductDatabase.store_excel_data exists
    print("\n2️⃣  Checking ProductDatabase.store_excel_data method...")
    try:
        from src.core.data.product_database import ProductDatabase
        db = ProductDatabase()
        
        if hasattr(db, 'store_excel_data'):
            print(f"   ✅ store_excel_data method exists")
        else:
            print(f"   ❌ store_excel_data method NOT FOUND!")
            print(f"   Available methods: {[m for m in dir(db) if not m.startswith('_')][:10]}")
            return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Check app.py upload endpoint
    print("\n3️⃣  Checking app.py upload endpoint...")
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        checks = [
            ('@app.route(\'/upload\'', 'Upload route'),
            ('product_db.store_excel_data', 'store_excel_data call'),
            ('.load_file(', 'Excel file loading'),
        ]
        
        for check_str, description in checks:
            if check_str in app_content:
                print(f"   ✅ {description} found")
            else:
                print(f"   ⚠️  {description} NOT found")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check for recent Excel files
    print("\n4️⃣  Checking for recent Excel uploads...")
    try:
        excel_files = []
        if os.path.exists('uploads'):
            for file in os.listdir('uploads'):
                if file.endswith(('.xlsx', '.xls')):
                    full_path = os.path.join('uploads', file)
                    size = os.path.getsize(full_path)
                    from datetime import datetime
                    modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                    excel_files.append((file, size, modified))
        
        if excel_files:
            excel_files.sort(key=lambda x: x[2], reverse=True)
            print(f"   📊 Found {len(excel_files)} Excel file(s):")
            for file, size, modified in excel_files[:5]:
                size_mb = size / (1024 * 1024)
                print(f"      {file} ({size_mb:.2f} MB, modified {modified})")
        else:
            print(f"   ⚠️  No Excel files found in uploads/")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check server logs for upload errors
    print("\n5️⃣  Checking for upload errors in logs...")
    log_path = "/var/log/www.agtpricetags.com.error.log"
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                lines = f.readlines()
                
            # Look for upload-related errors in last 100 lines
            upload_errors = []
            for line in lines[-100:]:
                if any(keyword in line.lower() for keyword in ['upload', 'store_excel', 'database storage']):
                    if any(err in line.lower() for err in ['error', 'fail', 'exception']):
                        upload_errors.append(line.strip())
            
            if upload_errors:
                print(f"   ⚠️  Found {len(upload_errors)} upload-related errors:")
                for error in upload_errors[-5:]:
                    print(f"      {error[:100]}...")
            else:
                print(f"   ✅ No upload errors found in recent logs")
        except Exception as e:
            print(f"   ⚠️  Could not read logs: {e}")
    else:
        print(f"   ℹ️  Log file not found at {log_path}")
    
    # Summary
    print("\n" + "=" * 80)
    print("DIAGNOSIS SUMMARY")
    print("=" * 80)
    
    print(f"\n📊 Current database status:")
    print(f"   Products: {initial_count:,}")
    
    if initial_count == 0:
        print(f"\n⚠️  Database is empty!")
        print(f"\n💡 Possible reasons:")
        print(f"   1. No Excel files have been uploaded yet")
        print(f"   2. Excel upload is failing silently")
        print(f"   3. store_excel_data method is not working")
        print(f"   4. Wrong database file is being used")
        
        print(f"\n🔧 How to fix:")
        print(f"   1. Upload an Excel file via the web interface")
        print(f"   2. Check server logs: tail -f /var/log/www.agtpricetags.com.error.log")
        print(f"   3. Monitor database: watch -n 2 'sqlite3 uploads/product_database.db \"SELECT COUNT(*) FROM products;\"'")
    else:
        print(f"\n✅ Database has products")
        print(f"\n💡 If new uploads aren't adding products:")
        print(f"   1. Check if uploads are completing successfully")
        print(f"   2. Check server logs for errors")
        print(f"   3. Verify store_excel_data is being called")
    
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        test_excel_upload()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

