#!/usr/bin/env python3
"""
Fix PythonAnywhere database issue
Run this on PythonAnywhere to restore the correct database
"""

import os
import shutil
import sqlite3
from datetime import datetime

def fix_pythonanywhere_database():
    print("🔧 FIXING PYTHONANYWHERE DATABASE")
    print("=" * 50)
    
    # Check current database
    db_path = "uploads/product_database_AGT_Bothell.db"
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"Current database: {size_mb:.1f} MB")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"Current product count: {count}")
        except Exception as e:
            print(f"Error reading database: {e}")
    else:
        print("❌ Database file not found")
        return
    
    # Check if main database exists and is larger
    main_db_path = "uploads/product_database.db"
    if os.path.exists(main_db_path):
        main_size_mb = os.path.getsize(main_db_path) / (1024 * 1024)
        print(f"Main database: {main_size_mb:.1f} MB")
        
        try:
            conn = sqlite3.connect(main_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            main_count = cursor.fetchone()[0]
            conn.close()
            print(f"Main database product count: {main_count}")
            
            # If main database has more products, use it
            if main_count > 10000:
                print("✅ Main database has correct number of products")
                print("🔄 Restoring from main database...")
                
                # Backup current database
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"uploads/product_database_AGT_Bothell.db.backup.{timestamp}"
                shutil.copy2(db_path, backup_path)
                print(f"✅ Backed up current database to: {backup_path}")
                
                # Copy main database to AGT_Bothell
                shutil.copy2(main_db_path, db_path)
                print("✅ Restored AGT_Bothell database from main database")
                
                # Verify restoration
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM products")
                new_count = cursor.fetchone()[0]
                conn.close()
                
                print(f"✅ New product count: {new_count}")
                
                if new_count > 10000:
                    print("🎉 SUCCESS! Database restored successfully")
                    print("Now reload your web app and it should show the correct data")
                else:
                    print("❌ Restoration failed - still showing low product count")
            else:
                print("⚠️  Main database also has few products")
                
        except Exception as e:
            print(f"Error with main database: {e}")
    else:
        print("❌ Main database not found")
    
    print("\n" + "=" * 50)
    print("📋 NEXT STEPS:")
    print("1. Go to PythonAnywhere Web tab")
    print("2. Click 'Reload' for your web app")
    print("3. Wait 30-60 seconds")
    print("4. Visit https://www.agtpricetags.com")
    print("5. Should now show 10,000+ products")

if __name__ == "__main__":
    fix_pythonanywhere_database()
