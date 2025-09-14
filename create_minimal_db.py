#!/usr/bin/env python3
"""
Create a minimal working database for PythonAnywhere
This creates a smaller, more reliable database file
"""

import sqlite3
import os

def create_minimal_database():
    print("🔧 Creating minimal working database...")
    
    # Connect to the main database
    main_db = sqlite3.connect('uploads/product_database.db')
    main_cursor = main_db.cursor()
    
    # Create a new minimal database
    minimal_db = sqlite3.connect('minimal_database.db')
    minimal_cursor = minimal_db.cursor()
    
    # Get the schema from the main database
    main_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='products'")
    schema = main_cursor.fetchone()[0]
    
    # Create the products table in the minimal database
    minimal_cursor.execute(schema)
    
    # Copy all products to the minimal database
    print("Copying products...")
    main_cursor.execute("SELECT * FROM products")
    
    # Get column names
    column_names = [description[0] for description in main_cursor.description]
    placeholders = ','.join(['?' for _ in column_names])
    
    # Insert all products
    batch_size = 1000
    while True:
        rows = main_cursor.fetchmany(batch_size)
        if not rows:
            break
        minimal_cursor.executemany(f"INSERT INTO products ({','.join(column_names)}) VALUES ({placeholders})", rows)
        print(f"Copied {len(rows)} products...")
    
    # Commit and close
    minimal_db.commit()
    minimal_db.close()
    main_db.close()
    
    # Verify the minimal database
    verify_db = sqlite3.connect('minimal_database.db')
    verify_cursor = verify_db.cursor()
    verify_cursor.execute("SELECT COUNT(*) FROM products")
    count = verify_cursor.fetchone()[0]
    verify_db.close()
    
    print(f"✅ Minimal database created with {count} products")
    print(f"File size: {os.path.getsize('minimal_database.db') / (1024*1024):.1f} MB")
    
    return count

if __name__ == "__main__":
    create_minimal_database()
