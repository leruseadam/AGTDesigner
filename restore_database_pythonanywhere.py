#!/usr/bin/env python3

"""
PythonAnywhere Database Restore Script
=====================================
This script restores the compressed database on PythonAnywhere
"""

import sqlite3
import gzip
import os
from datetime import datetime

def restore_database():
    """Restore database from compressed SQL dump"""
    print("🗃️  Restoring Database on PythonAnywhere")
    print("=" * 50)
    
    # Paths
    compressed_file = "uploads/product_database_compressed.sql.gz"
    target_db = "uploads/product_database.db"
    
    if not os.path.exists(compressed_file):
        print(f"❌ Compressed file not found: {compressed_file}")
        print("Please upload product_database_compressed.sql.gz to the uploads/ directory")
        return False
    
    try:
        print("📊 Decompressing database...")
        
        # Decompress the file
        with gzip.open(compressed_file, 'rb') as f_in:
            sql_content = f_in.read().decode('utf-8')
        
        print("📊 Creating database...")
        
        # Create new database
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()
        
        # Execute SQL dump
        print("📊 Restoring data...")
        cursor.executescript(sql_content)
        
        conn.commit()
        conn.close()
        
        print("✅ Database restored successfully!")
        
        # Verify restoration
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()
        
        # Check products count
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        # Check strains count
        cursor.execute("SELECT COUNT(*) FROM strains")
        strain_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📊 Products restored: {product_count:,}")
        print(f"📊 Strains restored: {strain_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error restoring database: {e}")
        return False

def create_sample_database():
    """Create a sample database if restoration fails"""
    print("\n🔧 Creating Sample Database")
    print("=" * 50)
    
    db_path = "uploads/product_database.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        print("➕ Creating tables...")
        
        # Strains table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strain_name TEXT UNIQUE NOT NULL,
                normalized_name TEXT,
                canonical_lineage TEXT,
                first_seen_date TEXT NOT NULL,
                last_seen_date TEXT NOT NULL,
                total_occurrences INTEGER DEFAULT 1,
                lineage_confidence REAL,
                sovereign_lineage TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                "Product Name*" TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                strain_id INTEGER,
                "Product Type*" TEXT NOT NULL,
                "Vendor/Supplier*" TEXT,
                "Product Brand" TEXT,
                "Description" TEXT,
                "Weight*" TEXT,
                "Units" TEXT,
                "Price" TEXT,
                "Lineage" TEXT,
                first_seen_date TEXT NOT NULL,
                last_seen_date TEXT NOT NULL,
                total_occurrences INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                "Product Strain" TEXT,
                "Quantity*" TEXT,
                "DOH" TEXT,
                "Concentrate Type" TEXT,
                "Ratio" TEXT,
                "JointRatio" TEXT,
                "THC test result" TEXT,
                "CBD test result" TEXT,
                "Test result unit (% or mg)" TEXT,
                "State" TEXT,
                "Is Sample? (yes/no)" TEXT,
                "Is MJ product?(yes/no)" TEXT,
                "Discountable? (yes/no)" TEXT,
                "Room*" TEXT,
                "Batch Number" TEXT,
                "Lot Number" TEXT,
                "Barcode*" TEXT,
                "Medical Only (Yes/No)" TEXT,
                "Med Price" TEXT,
                "Expiration Date(YYYY-MM-DD)" TEXT,
                "Is Archived? (yes/no)" TEXT,
                "THC Per Serving" TEXT,
                "Allergens" TEXT,
                "Solvent" TEXT,
                "Accepted Date" TEXT,
                "Internal Product Identifier" TEXT,
                "Product Tags (comma separated)" TEXT,
                "Image URL" TEXT,
                "Ingredients" TEXT,
                "Total THC" TEXT,
                "THCA" TEXT,
                "CBDA" TEXT,
                "CBN" TEXT,
                "THC" TEXT,
                "CBD" TEXT,
                "Total CBD" TEXT,
                "CBGA" TEXT,
                "CBG" TEXT,
                "Total CBG" TEXT,
                "CBC" TEXT,
                "CBDV" TEXT,
                "THCV" TEXT,
                "CBGV" TEXT,
                "CBNV" TEXT,
                "CBGVA" TEXT,
                FOREIGN KEY (strain_id) REFERENCES strains (id),
                UNIQUE("Product Name*", "Vendor/Supplier*", "Product Brand")
            )
        ''')
        
        # Lineage history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lineage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strain_id INTEGER,
                old_lineage TEXT,
                new_lineage TEXT,
                change_date TEXT NOT NULL,
                change_reason TEXT,
                FOREIGN KEY (strain_id) REFERENCES strains (id)
            )
        ''')
        
        # Strain brand lineage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strain_brand_lineage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strain_name TEXT NOT NULL,
                brand TEXT,
                lineage TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(strain_name, brand)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Sample database created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PythonAnywhere Database Setup")
    print("=" * 60)
    
    # Try to restore from compressed file first
    if restore_database():
        print("\n🎉 Database restoration completed!")
    else:
        print("\n⚠️  Restoration failed, creating sample database...")
        if create_sample_database():
            print("\n🎉 Sample database created!")
        else:
            print("\n❌ Database setup failed!")
    
    print("\n📋 Next steps:")
    print("1. Test your application")
    print("2. Upload Excel files to populate the database")
    print("3. Use the default sample file for testing")
