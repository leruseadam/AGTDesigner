#!/usr/bin/env python3

"""
PythonAnywhere Database Restoration - Updated Version
===================================================
Restores the updated database with 8,334 products and 2,580 strains
"""

import sqlite3
import gzip
import os
from datetime import datetime

def restore_updated_database():
    """Restore the updated database from compressed file"""
    print("🗃️  Restoring Updated Database on PythonAnywhere")
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
        
        # Execute SQL dump
        print("📊 Restoring data...")
        cursor.executescript(sql_content)
        
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

def test_database():
    """Test the restored database"""
    print("\n🧪 Testing Restored Database")
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

def test_application():
    """Test the application with updated database"""
    print("\n🧪 Testing Application with Updated Database")
    print("=" * 50)
    
    try:
        from app import get_product_database, get_excel_processor
        
        # Test database
        product_db = get_product_database()
        if product_db:
            print("✅ Database connection successful")
            print(f"📊 Database path: {product_db.db_path}")
        else:
            print("❌ Database connection failed")
            return False
        
        # Test Excel processor
        processor = get_excel_processor()
        if processor:
            print("✅ Excel processor loaded successfully")
        else:
            print("❌ Excel processor failed to load")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PythonAnywhere Updated Database Restoration")
    print("=" * 60)
    
    # Step 1: Restore database
    if restore_updated_database():
        print("\n✅ Database restoration completed!")
    else:
        print("\n❌ Database restoration failed!")
        exit(1)
    
    # Step 2: Test database
    if test_database():
        print("\n✅ Database test passed!")
    else:
        print("\n❌ Database test failed!")
        exit(1)
    
    # Step 3: Test application
    if test_application():
        print("\n✅ Application test passed!")
    else:
        print("\n❌ Application test failed!")
        exit(1)
    
    print("\n🎉 Updated database restoration complete!")
    print("\n📋 Next steps:")
    print("1. Reload your web app in PythonAnywhere Web tab")
    print("2. Visit your site - should show 8,000+ products")
    print("3. Test file upload functionality")
    print("4. Verify JointRatio processing works")
    print("\n🔗 Your app: https://$(whoami).pythonanywhere.com")
