#!/usr/bin/env python3

"""
Comprehensive Database Setup Guide for AGT Label Maker
=====================================================

This script helps you set up and configure the database for your application.
"""

import sqlite3
import os
import sys
from datetime import datetime

def check_database_status():
    """Check the current status of all databases"""
    print("🔍 Database Status Check")
    print("=" * 50)
    
    databases = [
        ('uploads/product_database.db', 'Main Database'),
        ('uploads/product_database_AGT_Bothell.db', 'AGT Bothell Database')
    ]
    
    for db_path, db_name in databases:
        print(f"\n📊 {db_name}: {db_path}")
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get table info
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                if tables:
                    print(f"   Tables: {len(tables)}")
                    for table in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                        count = cursor.fetchone()[0]
                        print(f"     - {table[0]}: {count:,} records")
                else:
                    print("   ❌ No tables found")
                
                conn.close()
            except Exception as e:
                print(f"   ❌ Error reading database: {e}")
        else:
            print("   ❌ Database file not found")

def setup_main_database():
    """Set up the main database with proper schema"""
    print("\n🔧 Setting up Main Database")
    print("=" * 50)
    
    db_path = "uploads/product_database.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create strains table
        print("➕ Creating strains table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                lineage TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Create products table with full schema
        print("➕ Creating products table...")
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
        
        # Create lineage_history table
        print("➕ Creating lineage_history table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lineage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strain_name TEXT NOT NULL,
                old_lineage TEXT,
                new_lineage TEXT,
                changed_at TEXT NOT NULL,
                reason TEXT
            )
        ''')
        
        # Create strain_brand_lineage table
        print("➕ Creating strain_brand_lineage table...")
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
        print("✅ Main database schema created successfully!")
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up main database: {e}")
        return False

def copy_data_from_agt_bothell():
    """Copy data from AGT Bothell database to main database"""
    print("\n📋 Copying Data from AGT Bothell Database")
    print("=" * 50)
    
    source_db = "uploads/product_database_AGT_Bothell.db"
    target_db = "uploads/product_database.db"
    
    if not os.path.exists(source_db):
        print(f"❌ Source database not found: {source_db}")
        return False
    
    try:
        # Connect to both databases
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        
        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()
        
        # Copy strains
        print("📋 Copying strains...")
        source_cursor.execute("SELECT * FROM strains")
        strains = source_cursor.fetchall()
        
        if strains:
            target_cursor.execute("DELETE FROM strains")  # Clear existing
            for strain in strains:
                target_cursor.execute('''
                    INSERT OR REPLACE INTO strains (id, name, lineage, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', strain)
            print(f"✅ Copied {len(strains)} strains")
        
        # Copy products
        print("📋 Copying products...")
        source_cursor.execute("SELECT COUNT(*) FROM products")
        product_count = source_cursor.fetchone()[0]
        
        if product_count > 0:
            # Get column names from source
            source_cursor.execute("PRAGMA table_info(products)")
            source_columns = [col[1] for col in source_cursor.fetchall()]
            
            # Get column names from target
            target_cursor.execute("PRAGMA table_info(products)")
            target_columns = [col[1] for col in target_cursor.fetchall()]
            
            # Find common columns
            common_columns = [col for col in source_columns if col in target_columns]
            
            print(f"📊 Found {len(common_columns)} common columns")
            
            # Copy data in batches
            batch_size = 1000
            offset = 0
            
            while offset < product_count:
                query = f"SELECT {', '.join(common_columns)} FROM products LIMIT {batch_size} OFFSET {offset}"
                source_cursor.execute(query)
                batch = source_cursor.fetchall()
                
                if batch:
                    placeholders = ', '.join(['?' for _ in common_columns])
                    insert_query = f"INSERT OR REPLACE INTO products ({', '.join(common_columns)}) VALUES ({placeholders})"
                    target_cursor.executemany(insert_query, batch)
                    print(f"   Copied batch {offset//batch_size + 1}: {len(batch)} products")
                
                offset += batch_size
            
            print(f"✅ Copied {product_count} products")
        
        # Copy lineage_history
        print("📋 Copying lineage_history...")
        source_cursor.execute("SELECT * FROM lineage_history")
        lineage_history = source_cursor.fetchall()
        
        if lineage_history:
            target_cursor.execute("DELETE FROM lineage_history")
            for record in lineage_history:
                target_cursor.execute('''
                    INSERT OR REPLACE INTO lineage_history (id, strain_name, old_lineage, new_lineage, changed_at, reason)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', record)
            print(f"✅ Copied {len(lineage_history)} lineage history records")
        
        target_conn.commit()
        source_conn.close()
        target_conn.close()
        
        print("✅ Data copying completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error copying data: {e}")
        return False

def test_database_functionality():
    """Test the database functionality"""
    print("\n🧪 Testing Database Functionality")
    print("=" * 50)
    
    db_path = "uploads/product_database.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Check table structure
        print("🔍 Test 1: Checking table structure...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        expected_tables = ['strains', 'products', 'lineage_history', 'strain_brand_lineage']
        
        for table_name in expected_tables:
            if any(table[0] == table_name for table in tables):
                print(f"   ✅ {table_name} table exists")
            else:
                print(f"   ❌ {table_name} table missing")
        
        # Test 2: Check product count
        print("\n🔍 Test 2: Checking product count...")
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"   📊 Products in database: {product_count:,}")
        
        if product_count > 0:
            print("   ✅ Database has products")
            
            # Test 3: Sample product data
            print("\n🔍 Test 3: Checking sample product data...")
            cursor.execute("SELECT \"Product Name*\", \"Product Type*\", \"Weight*\" FROM products LIMIT 3")
            sample_products = cursor.fetchall()
            
            print("   📋 Sample products:")
            for i, product in enumerate(sample_products, 1):
                print(f"     {i}. {product[0]} ({product[1]}) - {product[2]}")
        else:
            print("   ⚠️  Database is empty")
        
        # Test 4: Check strains
        print("\n🔍 Test 4: Checking strains...")
        cursor.execute("SELECT COUNT(*) FROM strains")
        strain_count = cursor.fetchone()[0]
        print(f"   📊 Strains in database: {strain_count}")
        
        conn.close()
        print("\n✅ Database functionality test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        return False

def main():
    """Main database setup function"""
    print("🗃️  AGT Label Maker - Database Setup")
    print("=" * 60)
    print("This script will help you set up and configure your database.")
    print()
    
    # Step 1: Check current status
    check_database_status()
    
    # Step 2: Ask user what they want to do
    print("\n🔧 Database Setup Options:")
    print("1. Set up main database schema only")
    print("2. Copy data from AGT Bothell to main database")
    print("3. Full setup (schema + data copy)")
    print("4. Test database functionality only")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                success = setup_main_database()
                if success:
                    print("\n🎉 Main database schema setup completed!")
                break
                
            elif choice == '2':
                success = copy_data_from_agt_bothell()
                if success:
                    print("\n🎉 Data copying completed!")
                break
                
            elif choice == '3':
                print("\n🚀 Starting full database setup...")
                schema_success = setup_main_database()
                if schema_success:
                    data_success = copy_data_from_agt_bothell()
                    if data_success:
                        print("\n🎉 Full database setup completed!")
                    else:
                        print("\n⚠️  Schema setup completed, but data copying failed")
                else:
                    print("\n❌ Database setup failed")
                break
                
            elif choice == '4':
                test_database_functionality()
                break
                
            elif choice == '5':
                print("👋 Exiting...")
                sys.exit(0)
                
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Final status check
    print("\n📊 Final Database Status:")
    check_database_status()

if __name__ == "__main__":
    main()
