#!/usr/bin/env python3
"""
Manually initialize database with the correct schema
"""
import sqlite3
import os
from datetime import datetime

def initialize_database():
    """Create fresh database with correct schema."""
    db_path = "uploads/product_database_AGT_Bothell.db"
    
    print("=" * 60)
    print("Initializing Database Schema")
    print("=" * 60)
    
    # Remove old database files
    for ext in ['', '-shm', '-wal']:
        filepath = db_path + ext
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Removed: {filepath}")
    
    print(f"\nCreating new database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create strains table with normalized_name
        print("\nCreating strains table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strain_name TEXT UNIQUE NOT NULL,
                normalized_name TEXT NOT NULL,
                canonical_lineage TEXT,
                first_seen_date TEXT NOT NULL,
                last_seen_date TEXT NOT NULL,
                total_occurrences INTEGER DEFAULT 1,
                lineage_confidence REAL DEFAULT 0.0,
                sovereign_lineage TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        print("✓ Strains table created")
        
        # Create products table
        print("Creating products table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                "Product Name*" TEXT,
                "Vendor/Supplier*" TEXT,
                "Product Brand" TEXT,
                "Product Type*" TEXT,
                "Product Strain" TEXT,
                "Weight*" TEXT,
                "Weight Unit*" TEXT,
                "Price*" TEXT,
                "Quantity*" TEXT,
                "DOH Compliant*" TEXT,
                "Lineage" TEXT,
                "THC Level (%)" TEXT,
                "CBD Level (%)" TEXT,
                strain_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (strain_id) REFERENCES strains (id),
                UNIQUE("Product Name*", "Vendor/Supplier*", "Product Brand")
            )
        ''')
        print("✓ Products table created")
        
        # Create brands table
        print("Creating brands table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strain_name TEXT NOT NULL,
                brand TEXT NOT NULL,
                canonical_lineage TEXT,
                first_seen_date TEXT NOT NULL,
                last_seen_date TEXT NOT NULL,
                total_occurrences INTEGER DEFAULT 1,
                lineage_confidence REAL DEFAULT 0.0,
                sovereign_lineage TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(strain_name, brand)
            )
        ''')
        print("✓ Brands table created")
        
        # Create lineage_history table
        print("Creating lineage_history table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lineage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strain_name TEXT NOT NULL,
                old_lineage TEXT,
                new_lineage TEXT,
                changed_by TEXT,
                changed_at TEXT NOT NULL,
                change_reason TEXT
            )
        ''')
        print("✓ Lineage history table created")
        
        # Create indexes
        print("Creating indexes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_strains_normalized ON strains(normalized_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_strain ON products(strain_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_vendor_brand ON products("Vendor/Supplier*", "Product Brand")')
        print("✓ Indexes created")
        
        conn.commit()
        
        # Verify schema
        print("\n" + "=" * 60)
        print("Verification")
        print("=" * 60)
        
        cursor.execute("PRAGMA table_info(strains)")
        strain_cols = [col[1] for col in cursor.fetchall()]
        print(f"\n✓ Strains table: {len(strain_cols)} columns")
        print(f"  Columns: {', '.join(strain_cols)}")
        
        if 'normalized_name' in strain_cols:
            print("  ✓ normalized_name column present")
        else:
            print("  ❌ normalized_name column MISSING!")
        
        cursor.execute("PRAGMA table_info(products)")
        product_cols = [col[1] for col in cursor.fetchall()]
        print(f"\n✓ Products table: {len(product_cols)} columns")
        
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        print(f"\n✓ Integrity check: {result[0]}")
        
        conn.close()
        
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"✓ Database size: {size_mb:.2f} MB")
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Database initialized successfully")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Start your Flask app")
        print("2. Upload your Excel inventory file")
        print("3. Generate labels")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = initialize_database()
    sys.exit(0 if success else 1)

