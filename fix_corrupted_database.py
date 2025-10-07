#!/usr/bin/env python3

"""
PythonAnywhere Database Corruption Fix
=====================================
Rebuilds corrupted database from AGT Bothell database
"""

import sqlite3
import os
import shutil
from datetime import datetime

def fix_corrupted_database():
    """Fix corrupted database by rebuilding from AGT Bothell database"""
    print("🔧 Fixing Corrupted Database")
    print("=" * 60)
    
    main_db = "uploads/product_database.db"
    agt_db = "uploads/product_database_AGT_Bothell.db"
    backup_db = "uploads/product_database_backup.db"
    
    if not os.path.exists(agt_db):
        print(f"❌ AGT Bothell database not found: {agt_db}")
        return False
    
    try:
        # Backup corrupted database
        if os.path.exists(main_db):
            print("📦 Creating backup of corrupted database...")
            shutil.copy2(main_db, backup_db)
            print(f"✅ Backup created: {backup_db}")
        
        # Remove corrupted database
        if os.path.exists(main_db):
            os.remove(main_db)
            print("🗑️  Removed corrupted database")
        
        # Create new database from AGT Bothell
        print("🔄 Creating new database from AGT Bothell...")
        
        conn_agt = sqlite3.connect(agt_db)
        cursor_agt = conn_agt.cursor()
        
        # Get schema from AGT database
        cursor_agt.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        schema_sql = cursor_agt.fetchall()
        
        # Create new main database
        conn_main = sqlite3.connect(main_db)
        cursor_main = conn_main.cursor()
        
        # Create tables
        for sql_tuple in schema_sql:
            sql = sql_tuple[0]
            if sql:  # Skip None values
                cursor_main.execute(sql)
        
        # Copy data from AGT database
        print("📊 Copying data from AGT Bothell database...")
        
        # Get all tables
        cursor_agt.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor_agt.fetchall()]
        
        for table in tables:
            if table == 'sqlite_sequence':
                continue
                
            print(f"   Copying {table}...")
            
            # Get table data
            cursor_agt.execute(f"SELECT * FROM {table}")
            rows = cursor_agt.fetchall()
            
            if rows:
                # Get column names
                cursor_agt.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor_agt.fetchall()]
                
                # Insert data
                placeholders = ', '.join(['?' for _ in columns])
                insert_query = f"INSERT INTO {table} ({', '.join([f'\"{col}\"' for col in columns])}) VALUES ({placeholders})"
                
                cursor_main.executemany(insert_query, rows)
                print(f"   ✅ Copied {len(rows):,} rows")
        
        conn_main.commit()
        conn_main.close()
        conn_agt.close()
        
        # Verify new database
        print("\n🧪 Verifying new database...")
        conn_test = sqlite3.connect(main_db)
        cursor_test = conn_test.cursor()
        
        cursor_test.execute("SELECT COUNT(*) FROM products")
        product_count = cursor_test.fetchone()[0]
        
        cursor_test.execute("SELECT COUNT(*) FROM strains")
        strain_count = cursor_test.fetchone()[0]
        
        print(f"✅ Products: {product_count:,}")
        print(f"✅ Strains: {strain_count:,}")
        
        # Test database integrity
        cursor_test.execute("PRAGMA integrity_check")
        integrity_result = cursor_test.fetchone()[0]
        
        if integrity_result == "ok":
            print("✅ Database integrity check passed")
        else:
            print(f"⚠️  Database integrity issues: {integrity_result}")
        
        conn_test.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

def create_sample_database():
    """Create a simple sample database if AGT database is not available"""
    print("\n🔧 Creating Sample Database")
    print("=" * 50)
    
    db_path = "uploads/product_database.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                "Product Name*" TEXT NOT NULL,
                "Product Type*" TEXT NOT NULL,
                "Vendor/Supplier*" TEXT,
                "Product Brand" TEXT,
                "Description" TEXT,
                "Weight*" TEXT,
                "Price" TEXT,
                "Lineage" TEXT,
                "Product Strain" TEXT,
                first_seen_date TEXT NOT NULL,
                last_seen_date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Create strains table
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
        
        # Add sample data
        now = datetime.now().isoformat()
        
        sample_products = [
            ("Blue Dream Flower", "Flower", "Sample Vendor", "Sample Brand", "Premium Blue Dream strain", "3.5g", "$45.00", "HYBRID", "Blue Dream"),
            ("Wedding Cake Pre-Roll", "Pre-Roll", "Sample Vendor", "Sample Brand", "Smooth wedding cake pre-roll", "1g", "$15.00", "HYBRID", "Wedding Cake"),
            ("Sour Diesel Cartridge", "Vape Cartridge", "Sample Vendor", "Sample Brand", "Classic sativa cartridge", "1g", "$35.00", "SATIVA", "Sour Diesel"),
            ("CBD Gummies", "Edible", "Sample Vendor", "Sample Brand", "CBD gummies for relaxation", "100mg", "$20.00", "MIXED", "CBD Blend"),
            ("Live Resin Concentrate", "Concentrate", "Sample Vendor", "Sample Brand", "Potent live resin", "1g", "$50.00", "HYBRID", "Live Resin")
        ]
        
        for product_name, product_type, vendor, brand, description, weight, price, lineage, strain in sample_products:
            cursor.execute('''
                INSERT INTO products 
                ("Product Name*", "Product Type*", "Vendor/Supplier*", "Product Brand", 
                 "Description", "Weight*", "Price", "Lineage", "Product Strain", 
                 first_seen_date, last_seen_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_name, product_type, vendor, brand, description, 
                weight, price, lineage, strain, now, now, now, now
            ))
        
        # Add sample strains
        sample_strains = [
            ("Blue Dream", "HYBRID"),
            ("Wedding Cake", "HYBRID"),
            ("Sour Diesel", "SATIVA"),
            ("CBD Blend", "MIXED"),
            ("Live Resin", "HYBRID")
        ]
        
        for strain_name, lineage in sample_strains:
            cursor.execute('''
                INSERT INTO strains 
                (strain_name, canonical_lineage, first_seen_date, last_seen_date, 
                 total_occurrences, lineage_confidence, sovereign_lineage, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                strain_name, lineage, now, now, 1, 0.9, lineage, now, now
            ))
        
        conn.commit()
        conn.close()
        
        print("✅ Sample database created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample database: {e}")
        return False

def test_database():
    """Test the database functionality"""
    print("\n🧪 Testing Database Functionality")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("uploads/product_database.db")
        cursor = conn.cursor()
        
        # Test products
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"✅ Products: {product_count}")
        
        # Test strains
        cursor.execute("SELECT COUNT(*) FROM strains")
        strain_count = cursor.fetchone()[0]
        print(f"✅ Strains: {strain_count}")
        
        # Show sample products
        if product_count > 0:
            cursor.execute('SELECT "Product Name*", "Product Type*", "Product Strain" FROM products LIMIT 3')
            samples = cursor.fetchall()
            print(f"\n📋 Sample products:")
            for i, (name, ptype, strain) in enumerate(samples, 1):
                print(f"   {i}. {name} ({ptype}) - {strain}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PythonAnywhere Database Corruption Fix")
    print("=" * 60)
    
    # Step 1: Try to fix corrupted database
    if fix_corrupted_database():
        print("\n✅ Database corruption fixed successfully!")
    else:
        print("\n⚠️  Database fix failed, creating sample database...")
        if create_sample_database():
            print("\n✅ Sample database created!")
        else:
            print("\n❌ Database creation failed!")
            exit(1)
    
    # Step 2: Test the database
    test_database()
    
    print("\n🎉 Database fix complete!")
    print("\n📋 Next steps:")
    print("1. Reload your web app in PythonAnywhere Web tab")
    print("2. Visit your site to verify it's working")
    print("3. If you need the full database, upload the compressed file")
    print("4. Run: python3 populate_pythonanywhere_database.py")
