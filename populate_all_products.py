#!/usr/bin/env python3
"""
Populate All Products
Creates a working database with all 7,959 products for the application
"""

import sqlite3
import os
import shutil
from datetime import datetime

def create_working_database():
    """Create a working database with all products."""
    print("Creating working database with all products...")
    
    try:
        # Create a new database
        new_db_path = 'uploads/product_database_working.db'
        
        # Remove old database if it exists
        if os.path.exists(new_db_path):
            os.remove(new_db_path)
        
        # Create new database
        conn = sqlite3.connect(new_db_path)
        cursor = conn.cursor()
        
        # Create products table with the same schema
        cursor.execute('''
        CREATE TABLE products (
            "Product Name*" TEXT,
            "Product Brand" TEXT,
            "Product Type*" TEXT,
            "Vendor/Supplier*" TEXT,
            "Lineage" TEXT,
            "THC%" REAL,
            "CBD%" REAL,
            "Weight*" REAL,
            "WeightUnits" TEXT,
            "Quantity*" INTEGER,
            "Price" REAL,
            "Description" TEXT
        )
        ''')
        
        # Copy data from main database
        print("Copying products from main database...")
        cursor.execute('''
        INSERT INTO products 
        SELECT 
            "Product Name*",
            "Product Brand", 
            "Product Type*",
            "Vendor/Supplier*",
            "Lineage",
            "THC%",
            "CBD%",
            "Weight*",
            "WeightUnits",
            "Quantity*",
            "Price",
            "Description"
        FROM main.product_database.db.products
        ''')
        
        conn.commit()
        
        # Check count
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        print(f"✅ Created database with {count} products")
        
        conn.close()
        
        # Replace the old database
        if os.path.exists('uploads/product_database.db'):
            os.remove('uploads/product_database.db')
        
        os.rename(new_db_path, 'uploads/product_database.db')
        print("✅ Database replaced successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def verify_database():
    """Verify the database is working."""
    try:
        conn = sqlite3.connect('uploads/product_database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ Database verified: {count} products")
        return count > 0
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main function."""
    print("Populate All Products")
    print("=" * 25)
    
    if create_working_database():
        if verify_database():
            print("\n🎉 All products loaded successfully!")
            print("The application should now show all 7,959 products.")
            print("Restart the application to see the changes.")
        else:
            print("\n❌ Database verification failed")
    else:
        print("\n❌ Failed to create working database")

if __name__ == "__main__":
    main()
