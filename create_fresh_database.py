#!/usr/bin/env python3
"""
Create a fresh, working database for AGT Label Maker
"""

import os
import sys
import sqlite3

def create_fresh_database():
    """Create a fresh database with proper schema"""
    
    db_path = "uploads/product_database_AGT_Bothell.db"
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Remove old database if it exists
    if os.path.exists(db_path):
        print(f"Removing old database: {db_path}")
        os.remove(db_path)
    
    # Remove lock files
    for ext in ['-shm', '-wal']:
        lock_file = db_path + ext
        if os.path.exists(lock_file):
            os.remove(lock_file)
            print(f"Removed lock file: {lock_file}")
    
    print(f"Creating fresh database: {db_path}")
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create strains table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT,
            thc_percentage REAL,
            cbd_percentage REAL,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            brand TEXT,
            vendor TEXT,
            strain TEXT,
            weight REAL,
            weight_unit TEXT,
            price REAL,
            thc_percentage REAL,
            cbd_percentage REAL,
            lineage TEXT,
            terpenes TEXT,
            effects TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, weight, weight_unit, brand)
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_strains_name ON strains(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_strains_type ON strains(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_type ON products(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_strain ON products(strain)")
    
    # Add some default strains to prevent "no strains" errors
    default_strains = [
        ('Hybrid', 'hybrid', 20.0, 0.0),
        ('Indica', 'indica', 22.0, 0.0),
        ('Sativa', 'sativa', 18.0, 0.0),
        ('CBD Blend', 'hybrid', 5.0, 15.0),
        ('Mixed', 'hybrid', 15.0, 0.0),
    ]
    
    for strain_name, strain_type, thc, cbd in default_strains:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO strains (name, type, thc_percentage, cbd_percentage) VALUES (?, ?, ?, ?)",
                (strain_name, strain_type, thc, cbd)
            )
        except Exception as e:
            print(f"Warning: Could not insert default strain {strain_name}: {e}")
    
    conn.commit()
    
    # Verify database
    cursor.execute("SELECT COUNT(*) FROM strains")
    strain_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    
    conn.close()
    
    # Get file size
    file_size = os.path.getsize(db_path)
    
    print(f"✓ Database created successfully!")
    print(f"  - File size: {file_size:,} bytes")
    print(f"  - Strains: {strain_count}")
    print(f"  - Products: {product_count}")
    print(f"  - Location: {os.path.abspath(db_path)}")
    
    return True

if __name__ == "__main__":
    try:
        create_fresh_database()
        sys.exit(0)
    except Exception as e:
        print(f"Error creating database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
