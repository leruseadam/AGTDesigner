#!/usr/bin/env python3
"""
Quick fix script for PythonAnywhere database issues
Run this in PythonAnywhere Bash console to fix database problems
"""

import os
import sqlite3
import subprocess
import sys

def fix_database():
    print("=== PythonAnywhere Database Fix ===")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ ERROR: app.py not found. Make sure you're in the labelMaker_fresh directory")
        print("Run: cd labelMaker_fresh")
        return False
    
    print("✅ Found app.py - in correct directory")
    
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    print("✅ Ensured uploads directory exists")
    
    # Check for compressed database
    compressed_db = 'uploads/product_database.db.gz'
    if os.path.exists(compressed_db):
        print(f"✅ Found compressed database: {compressed_db}")
        print("Decompressing database...")
        try:
            subprocess.run(['gunzip', compressed_db], check=True)
            print("✅ Database decompressed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error decompressing database: {e}")
            return False
    else:
        print("⚠️  No compressed database found")
    
    # Check for database file
    db_path = 'uploads/product_database.db'
    if not os.path.exists(db_path):
        print(f"❌ ERROR: Database file not found at {db_path}")
        print("Please upload product_database.db to the uploads/ directory")
        return False
    
    print(f"✅ Found database: {db_path}")
    
    # Test database and add missing columns
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current product count
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"✅ Database has {product_count:,} products")
        
        # Check for required columns
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add missing columns
        required_columns = [
            ('product_name', 'TEXT'),
            ('vendor', 'TEXT'),
            ('product_type', 'TEXT'),
            ('brand', 'TEXT'),
            ('weight', 'TEXT')
        ]
        
        for col_name, col_type in required_columns:
            if col_name not in columns:
                print(f"Adding missing column: {col_name}")
                cursor.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")
            else:
                print(f"✅ Column {col_name} already exists")
        
        conn.commit()
        
        # Populate the new columns with data from existing columns
        print("Populating new columns with existing data...")
        cursor.execute("""
            UPDATE products SET 
                product_name = "Product Name*",
                vendor = "Vendor/Supplier*",
                product_type = "Product Type*",
                brand = "Product Brand",
                weight = "Weight*"
            WHERE product_name IS NULL OR product_name = ''
        """)
        
        conn.commit()
        
        # Verify the fix
        cursor.execute("SELECT COUNT(*) FROM products WHERE product_name IS NOT NULL AND product_name != ''")
        valid_products = cursor.fetchone()[0]
        print(f"✅ {valid_products:,} products now have valid data in new columns")
        
        conn.close()
        print("✅ Database fix completed successfully!")
        
        print("\n🎯 NEXT STEPS:")
        print("1. Go to PythonAnywhere Web tab")
        print("2. Click 'Reload' to restart your web app")
        print("3. Visit your web app URL to verify it shows products")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Database fix failed: {e}")
        return False

if __name__ == "__main__":
    fix_database()
