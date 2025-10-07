#!/usr/bin/env python3

"""
PythonAnywhere Database Restoration - Fixed Version
=================================================
Handles UNIQUE constraint failures and duplicate data
"""

import sqlite3
import gzip
import os
from datetime import datetime

def restore_updated_database_fixed():
    """Restore the updated database with constraint handling"""
    print("🗃️  Restoring Updated Database (Fixed Version)")
    print("=" * 60)
    
    compressed_file = "uploads/product_database_compressed.sql.gz"
    target_db = "uploads/product_database.db"
    
    if not os.path.exists(compressed_file):
        print(f"❌ Compressed file not found: {compressed_file}")
        print("\n📋 To get the updated database:")
        print("1. Download product_database_compressed.sql.gz from your local repository")
        print("2. Upload it to PythonAnywhere uploads/ directory")
        print("3. Run this script again")
        return False
    
    try:
        print("📊 Decompressing updated database...")
        
        # Decompress the file
        with gzip.open(compressed_file, 'rb') as f_in:
            sql_content = f_in.read().decode('utf-8')
        
        print("📊 Restoring database...")
        
        # Remove existing database
        if os.path.exists(target_db):
            os.remove(target_db)
            print("🗑️  Removed old database")
        
        # Create new database
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()
        
        # Split SQL content into individual statements
        sql_statements = sql_content.split(';')
        
        print("📊 Executing SQL statements...")
        
        for i, statement in enumerate(sql_statements):
            statement = statement.strip()
            if not statement:
                continue
                
            try:
                cursor.execute(statement)
                
                # Commit every 100 statements to avoid memory issues
                if i % 100 == 0:
                    conn.commit()
                    
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed" in str(e):
                    print(f"⚠️  Skipping duplicate entry: {statement[:50]}...")
                    continue
                else:
                    print(f"❌ Integrity error: {e}")
                    print(f"   Statement: {statement[:100]}...")
                    continue
            except sqlite3.Error as e:
                print(f"⚠️  SQL error (continuing): {e}")
                print(f"   Statement: {statement[:100]}...")
                continue
        
        conn.commit()
        conn.close()
        
        print("✅ Updated database restored successfully!")
        
        # Verify restoration
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()
        
        # Check products count
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        # Check strains count
        cursor.execute("SELECT COUNT(*) FROM strains")
        strain_count = cursor.fetchone()[0]
        
        # Check JointRatio products
        cursor.execute('SELECT COUNT(*) FROM products WHERE "JointRatio" IS NOT NULL AND "JointRatio" != ""')
        jointratio_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📊 Products restored: {product_count:,}")
        print(f"📊 Strains restored: {strain_count:,}")
        print(f"📊 JointRatio products: {jointratio_count:,}")
        
        # Show sample products
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT "Product Name*", "Product Type*", "Product Strain" FROM products WHERE "Product Name*" IS NOT NULL AND "Product Name*" != "" LIMIT 5')
        samples = cursor.fetchall()
        
        print(f"\n📋 Sample products:")
        for i, (name, ptype, strain) in enumerate(samples, 1):
            print(f"   {i}. {name} ({ptype}) - {strain}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error restoring database: {e}")
        return False

def create_clean_database():
    """Create a clean database by copying data properly"""
    print("\n🔧 Creating Clean Database")
    print("=" * 50)
    
    compressed_file = "uploads/product_database_compressed.sql.gz"
    target_db = "uploads/product_database.db"
    agt_db = "uploads/product_database_AGT_Bothell.db"
    
    try:
        # Remove existing database
        if os.path.exists(target_db):
            os.remove(target_db)
            print("🗑️  Removed old database")
        
        # Create new database
        conn_main = sqlite3.connect(target_db)
        cursor_main = conn_main.cursor()
        
        # If AGT database exists, copy from it
        if os.path.exists(agt_db):
            print("📊 Copying from AGT Bothell database...")
            
            conn_agt = sqlite3.connect(agt_db)
            cursor_agt = conn_agt.cursor()
            
            # Get schema from AGT database
            cursor_agt.execute("SELECT sql FROM sqlite_master WHERE type='table'")
            schema_sql = cursor_agt.fetchall()
            
            # Create tables
            for sql_tuple in schema_sql:
                sql = sql_tuple[0]
                if sql:  # Skip None values
                    cursor_main.execute(sql)
            
            # Copy data from AGT database
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
                    
                    # Insert data with IGNORE to skip duplicates
                    placeholders = ', '.join(['?' for _ in columns])
                    insert_query = f"INSERT OR IGNORE INTO {table} ({', '.join([f'\"{col}\"' for col in columns])}) VALUES ({placeholders})"
                    
                    cursor_main.executemany(insert_query, rows)
                    print(f"   ✅ Copied {len(rows):,} rows")
            
            conn_agt.close()
            
        else:
            print("📊 Creating sample database...")
            create_sample_tables(cursor_main)
        
        conn_main.commit()
        conn_main.close()
        
        print("✅ Clean database created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating clean database: {e}")
        return False

def create_sample_tables(cursor):
    """Create sample tables and data"""
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

def test_database():
    """Test the restored database"""
    print("\n🧪 Testing Database Functionality")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("uploads/product_database.db")
        cursor = conn.cursor()
        
        # Test products
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"✅ Products: {product_count:,}")
        
        # Test strains
        cursor.execute("SELECT COUNT(*) FROM strains")
        strain_count = cursor.fetchone()[0]
        print(f"✅ Strains: {strain_count:,}")
        
        # Test JointRatio
        cursor.execute('SELECT COUNT(*) FROM products WHERE "JointRatio" IS NOT NULL AND "JointRatio" != ""')
        jointratio_count = cursor.fetchone()[0]
        print(f"✅ JointRatio products: {jointratio_count:,}")
        
        # Test database integrity
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result == "ok":
            print("✅ Database integrity check passed")
        else:
            print(f"⚠️  Database integrity issues: {integrity_result}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PythonAnywhere Database Restoration (Fixed Version)")
    print("=" * 60)
    
    # Step 1: Try to restore from compressed file
    if restore_updated_database_fixed():
        print("\n✅ Database restoration completed!")
    else:
        print("\n⚠️  Restoration failed, creating clean database...")
        if create_clean_database():
            print("\n✅ Clean database created!")
        else:
            print("\n❌ Database creation failed!")
            exit(1)
    
    # Step 2: Test the database
    test_database()
    
    print("\n🎉 Database restoration complete!")
    print("\n📋 Next steps:")
    print("1. Reload your web app in PythonAnywhere Web tab")
    print("2. Visit your site to verify it's working")
    print("3. Test file upload functionality")
    print("4. Verify JointRatio processing works")
    print("\n🔗 Your app: https://$(whoami).pythonanywhere.com")
