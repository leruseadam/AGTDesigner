#!/usr/bin/env python3

"""
PythonAnywhere Database Troubleshooting Script
==============================================
Diagnoses and fixes common database issues on PythonAnywhere
"""

import sqlite3
import os
import sys
import logging
from datetime import datetime

def diagnose_database_issues():
    """Diagnose common database issues on PythonAnywhere"""
    print("🔍 PythonAnywhere Database Diagnostics")
    print("=" * 50)
    
    issues_found = []
    
    # Check if we're on PythonAnywhere
    is_pythonanywhere = (
        os.path.exists("/home/adamcordova") or
        'PYTHONANYWHERE_SITE' in os.environ or
        'PYTHONANYWHERE_DOMAIN' in os.environ
    )
    
    print(f"📍 Environment: {'PythonAnywhere' if is_pythonanywhere else 'Local'}")
    
    # Check database file existence
    db_paths = [
        "uploads/product_database.db",
        "product_database.db",
        "/home/adamcordova/AGTDesigner/uploads/product_database.db"
    ]
    
    db_found = None
    for db_path in db_paths:
        if os.path.exists(db_path):
            db_found = db_path
            break
    
    if not db_found:
        issues_found.append("❌ Database file not found")
        print("❌ Database file not found in any expected location")
        return issues_found
    else:
        print(f"✅ Database found: {db_found}")
    
    # Check database permissions
    try:
        if os.access(db_found, os.R_OK):
            print("✅ Database is readable")
        else:
            issues_found.append("❌ Database not readable")
            print("❌ Database not readable")
            
        if os.access(db_found, os.W_OK):
            print("✅ Database is writable")
        else:
            issues_found.append("❌ Database not writable")
            print("❌ Database not writable")
    except Exception as e:
        issues_found.append(f"❌ Permission check failed: {e}")
        print(f"❌ Permission check failed: {e}")
    
    # Test database connection
    try:
        conn = sqlite3.connect(db_found)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['products', 'strains', 'lineage_history', 'strain_brand_lineage']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            issues_found.append(f"❌ Missing tables: {missing_tables}")
            print(f"❌ Missing tables: {missing_tables}")
        else:
            print("✅ All required tables exist")
        
        # Check table contents
        for table in expected_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count} records")
                
                if count == 0 and table == 'strains':
                    issues_found.append("⚠️ Strains table is empty")
                    print("⚠️ Strains table is empty - this is expected if not populated")
        
        conn.close()
        
    except sqlite3.Error as e:
        issues_found.append(f"❌ Database connection error: {e}")
        print(f"❌ Database connection error: {e}")
    except Exception as e:
        issues_found.append(f"❌ Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
    
    return issues_found

def fix_database_issues():
    """Fix common database issues"""
    print("\n🔧 Fixing Database Issues")
    print("=" * 50)
    
    # Create uploads directory if it doesn't exist
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print("📁 Creating uploads directory...")
        os.makedirs(uploads_dir, exist_ok=True)
        print("✅ Uploads directory created")
    
    # Check if database exists
    db_path = "uploads/product_database.db"
    
    if not os.path.exists(db_path):
        print("📊 Creating new database...")
        create_sample_database()
    else:
        print("📊 Database exists, checking integrity...")
        fix_database_integrity(db_path)

def create_sample_database():
    """Create a sample database with proper schema"""
    db_path = "uploads/product_database.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
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
        
        # Create products table
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
        
        # Create strain_brand_lineage table
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
        
        # Add sample strain
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR IGNORE INTO strains 
            (strain_name, normalized_name, canonical_lineage, first_seen_date, 
             last_seen_date, total_occurrences, lineage_confidence, sovereign_lineage, 
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Sample Strain',
            'sample_strain',
            'HYBRID',
            now,
            now,
            1,
            0.8,
            'HYBRID',
            now,
            now
        ))
        
        conn.commit()
        conn.close()
        
        print("✅ Sample database created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample database: {e}")

def fix_database_integrity(db_path):
    """Fix database integrity issues"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check and fix table structure
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result == "ok":
            print("✅ Database integrity check passed")
        else:
            print(f"⚠️ Database integrity issues: {integrity_result}")
            
            # Try to fix with VACUUM
            print("🔧 Attempting to fix with VACUUM...")
            cursor.execute("VACUUM")
            print("✅ VACUUM completed")
        
        # Check if strains table is empty and add sample
        cursor.execute("SELECT COUNT(*) FROM strains")
        strain_count = cursor.fetchone()[0]
        
        if strain_count == 0:
            print("📊 Adding sample strain...")
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT OR IGNORE INTO strains 
                (strain_name, normalized_name, canonical_lineage, first_seen_date, 
                 last_seen_date, total_occurrences, lineage_confidence, sovereign_lineage, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'Sample Strain',
                'sample_strain',
                'HYBRID',
                now,
                now,
                1,
                0.8,
                'HYBRID',
                now,
                now
            ))
            conn.commit()
            print("✅ Sample strain added")
        
        conn.close()
        print("✅ Database integrity fixes completed")
        
    except Exception as e:
        print(f"❌ Error fixing database integrity: {e}")

def test_application_connection():
    """Test if the application can connect to the database"""
    print("\n🧪 Testing Application Connection")
    print("=" * 50)
    
    try:
        # Try to import the application
        sys.path.insert(0, '.')
        from app import get_product_database
        
        print("✅ Application imports successfully")
        
        # Try to get database
        product_db = get_product_database()
        if product_db:
            print("✅ Database connection successful")
            print(f"📊 Database path: {product_db.db_path}")
            print(f"📊 Database initialized: {product_db._initialized}")
        else:
            print("❌ Database connection failed")
            
    except ImportError as e:
        print(f"❌ Application import failed: {e}")
    except Exception as e:
        print(f"❌ Application connection test failed: {e}")

def main():
    """Main troubleshooting function"""
    print("🚀 PythonAnywhere Database Troubleshooter")
    print("=" * 60)
    
    # Step 1: Diagnose issues
    issues = diagnose_database_issues()
    
    # Step 2: Fix issues if any found
    if issues:
        print(f"\n⚠️ Found {len(issues)} issues:")
        for issue in issues:
            print(f"   {issue}")
        
        fix_database_issues()
    else:
        print("\n✅ No major issues found!")
    
    # Step 3: Test application connection
    test_application_connection()
    
    print("\n🎉 Troubleshooting complete!")
    print("\n📋 Next steps:")
    print("1. If issues persist, check PythonAnywhere error logs")
    print("2. Try reloading your web app")
    print("3. Upload a small Excel file to test functionality")

if __name__ == "__main__":
    main()
