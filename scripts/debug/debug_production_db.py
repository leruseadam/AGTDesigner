#!/usr/bin/env python3
"""
Debug script to check production database status
Run this on PythonAnywhere to diagnose database issues
"""

import os
import sqlite3
import sys

def check_database_status():
    print("=== PythonAnywhere Database Diagnostic ===")
    print()
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # Check if uploads directory exists
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        print(f"✅ uploads/ directory exists")
        
        # List files in uploads
        files = os.listdir(uploads_dir)
        print(f"Files in uploads/: {files}")
        print()
        
        # Check for AGT_Bothell database
        db_path = os.path.join(uploads_dir, "product_database_AGT_Bothell.db")
        if os.path.exists(db_path):
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            print(f"✅ AGT_Bothell database found: {size_mb:.1f} MB")
            
            # Test database connection
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if products table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
                if cursor.fetchone():
                    print("✅ products table exists")
                    
                    # Count products
                    cursor.execute("SELECT COUNT(*) FROM products")
                    count = cursor.fetchone()[0]
                    print(f"✅ Product count: {count}")
                    
                    if count > 10000:
                        print("✅ Database appears to be working correctly!")
                    else:
                        print("⚠️  Database has very few products")
                else:
                    print("❌ products table not found")
                
                conn.close()
                
            except Exception as e:
                print(f"❌ Database connection error: {e}")
        else:
            print("❌ AGT_Bothell database not found")
            
            # Check for other databases
            db_files = [f for f in files if f.endswith('.db')]
            if db_files:
                print(f"Other database files found: {db_files}")
            else:
                print("No database files found in uploads/")
    else:
        print("❌ uploads/ directory not found")
    
    print()
    print("=== Recommendations ===")
    print("1. If database is missing: Upload the zip file and extract it")
    print("2. If database exists but has 0 products: Database is corrupted")
    print("3. If database has products but app shows 0: Check app configuration")
    print("4. If 500 error persists: Check PythonAnywhere error logs")

if __name__ == "__main__":
    check_database_status()
