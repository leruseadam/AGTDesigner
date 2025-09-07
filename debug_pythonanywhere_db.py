#!/usr/bin/env python3
"""
Debug script to check database status on PythonAnywhere
Run this in PythonAnywhere Bash console to diagnose database issues
"""

import os
import sqlite3
import sys

def check_database_status():
    print("=== PythonAnywhere Database Diagnostic ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ ERROR: app.py not found. Make sure you're in the labelMaker_fresh directory")
        print("Run: cd labelMaker_fresh")
        return False
    
    print("✅ Found app.py - in correct directory")
    print()
    
    # Check uploads directory
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        print(f"❌ ERROR: {uploads_dir} directory not found")
        print("Creating uploads directory...")
        os.makedirs(uploads_dir, exist_ok=True)
        print("✅ Created uploads directory")
    else:
        print(f"✅ Found {uploads_dir} directory")
    
    print(f"Contents of {uploads_dir}/:")
    try:
        contents = os.listdir(uploads_dir)
        for item in contents:
            item_path = os.path.join(uploads_dir, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                print(f"  📄 {item} ({size:,} bytes)")
            else:
                print(f"  📁 {item}/")
    except Exception as e:
        print(f"❌ Error listing directory: {e}")
    
    print()
    
    # Check for database files
    db_paths = [
        'uploads/product_database.db',
        'product_database.db',
        'uploads/product_database/product_database.db',
        'uploads/product_database/product_database.db.gz'
    ]
    
    found_db = None
    for db_path in db_paths:
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"✅ Found database: {db_path} ({size:,} bytes)")
            if db_path.endswith('.gz'):
                print("   ⚠️  Database is compressed - needs to be decompressed")
            else:
                found_db = db_path
        else:
            print(f"❌ Not found: {db_path}")
    
    print()
    
    if not found_db:
        print("❌ No uncompressed database found!")
        print("📋 SOLUTION:")
        print("1. Upload product_database.db.gz to uploads/ directory")
        print("2. Run: gunzip uploads/product_database.db.gz")
        print("3. Run: mv uploads/product_database.db uploads/product_database.db")
        return False
    
    # Test database connection
    print(f"🔍 Testing database: {found_db}")
    try:
        conn = sqlite3.connect(found_db)
        cursor = conn.cursor()
        
        # Check if products table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        if not cursor.fetchone():
            print("❌ ERROR: products table not found in database")
            return False
        
        # Count products
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"✅ Products table found with {product_count:,} products")
        
        # Check for required columns
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ['product_name', 'vendor', 'product_type', 'brand']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"⚠️  Missing columns: {missing_columns}")
            print("   These columns are needed for the web app to work properly")
        else:
            print("✅ All required columns present")
        
        # Test a simple query
        cursor.execute("SELECT COUNT(*) FROM products WHERE product_name IS NOT NULL AND product_name != ''")
        valid_products = cursor.fetchone()[0]
        print(f"✅ {valid_products:,} products have valid names")
        
        conn.close()
        print("✅ Database connection successful")
        
    except Exception as e:
        print(f"❌ ERROR: Database connection failed: {e}")
        return False
    
    print()
    print("🎯 NEXT STEPS:")
    print("1. If database is compressed, decompress it:")
    print("   gunzip uploads/product_database.db.gz")
    print("   mv uploads/product_database.db uploads/product_database.db")
    print()
    print("2. If missing columns, add them:")
    print("   sqlite3 uploads/product_database.db \"ALTER TABLE products ADD COLUMN product_name TEXT;\"")
    print("   sqlite3 uploads/product_database.db \"ALTER TABLE products ADD COLUMN vendor TEXT;\"")
    print("   sqlite3 uploads/product_database.db \"ALTER TABLE products ADD COLUMN product_type TEXT;\"")
    print("   sqlite3 uploads/product_database.db \"ALTER TABLE products ADD COLUMN brand TEXT;\"")
    print("   sqlite3 uploads/product_database.db \"ALTER TABLE products ADD COLUMN weight TEXT;\"")
    print()
    print("3. Populate the new columns:")
    print("   sqlite3 uploads/product_database.db \"UPDATE products SET product_name = \\\"Product Name*\\\", vendor = \\\"Vendor/Supplier*\\\", product_type = \\\"Product Type*\\\", brand = \\\"Product Brand\\\", weight = \\\"Weight*\\\";\"")
    print()
    print("4. Restart your web app in the PythonAnywhere Web tab")
    
    return True

if __name__ == "__main__":
    check_database_status()
