#!/usr/bin/env python3
"""
Fix Database Data - Remove Column Headers and Fix Data Quality
This script fixes the database where column headers were imported as data
"""

import sqlite3
import pandas as pd
import os

def fix_database_data():
    print("🔧 Fixing database data quality...")
    
    # Check if database exists
    db_path = 'uploads/product_database.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current data
        print("📊 Checking current data...")
        cursor.execute("SELECT COUNT(*) FROM products")
        total_count = cursor.fetchone()[0]
        print(f"Total products: {total_count}")
        
        # Check for column header contamination
        cursor.execute("SELECT DISTINCT product_name FROM products LIMIT 10")
        sample_names = cursor.fetchall()
        print("Sample product names:")
        for name in sample_names:
            print(f"  - {name[0]}")
        
        # Check if we have column headers as data
        cursor.execute("SELECT COUNT(*) FROM products WHERE product_name = 'Product Name*'")
        header_count = cursor.fetchone()[0]
        
        if header_count > 0:
            print(f"🚨 Found {header_count} rows with column headers as data")
            print("This explains why we only see 1 unique vendor/brand/type")
            
            # Remove rows that are column headers
            print("🧹 Removing column header rows...")
            cursor.execute("DELETE FROM products WHERE product_name = 'Product Name*'")
            deleted = cursor.rowcount
            print(f"Deleted {deleted} header rows")
            
            # Check remaining data
            cursor.execute("SELECT COUNT(*) FROM products")
            remaining_count = cursor.fetchone()[0]
            print(f"Remaining products: {remaining_count}")
            
            # Check unique counts
            cursor.execute("SELECT COUNT(DISTINCT vendor_supplier) FROM products WHERE vendor_supplier != ''")
            unique_vendors = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT product_brand) FROM products WHERE product_brand != ''")
            unique_brands = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT product_type) FROM products WHERE product_type != ''")
            unique_types = cursor.fetchone()[0]
            
            print(f"✅ Unique vendors: {unique_vendors}")
            print(f"✅ Unique brands: {unique_brands}")
            print(f"✅ Unique types: {unique_types}")
            
        else:
            print("✅ No column header contamination found")
            
            # Check data quality
            cursor.execute("SELECT COUNT(DISTINCT vendor_supplier) FROM products WHERE vendor_supplier != ''")
            unique_vendors = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT product_brand) FROM products WHERE product_brand != ''")
            unique_brands = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT product_type) FROM products WHERE product_type != ''")
            unique_types = cursor.fetchone()[0]
            
            print(f"Unique vendors: {unique_vendors}")
            print(f"Unique brands: {unique_brands}")
            print(f"Unique types: {unique_types}")
            
            # Show sample data
            cursor.execute("SELECT product_name, vendor_supplier, product_brand, product_type FROM products LIMIT 5")
            samples = cursor.fetchall()
            print("Sample data:")
            for sample in samples:
                print(f"  Name: {sample[0]}, Vendor: {sample[1]}, Brand: {sample[2]}, Type: {sample[3]}")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Database data fixed!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    success = fix_database_data()
    if success:
        print("\n🎉 Database data quality fixed!")
        print("Next steps:")
        print("1. Restart the web app on PythonAnywhere")
        print("2. Test the website at https://agtpricetags.com")
        print("3. You should now see proper unique counts for vendors, brands, and types")
    else:
        print("\n❌ Failed to fix database data!")
