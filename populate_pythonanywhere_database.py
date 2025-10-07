#!/usr/bin/env python3

"""
PythonAnywhere Database Population Script
=========================================
Uploads and restores the full product database on PythonAnywhere
"""

import sqlite3
import gzip
import os
from datetime import datetime

def restore_full_database():
    """Restore the full database from compressed file"""
    print("🗃️  Restoring Full Database on PythonAnywhere")
    print("=" * 60)
    
    compressed_file = "uploads/product_database_compressed.sql.gz"
    target_db = "uploads/product_database.db"
    
    if not os.path.exists(compressed_file):
        print(f"❌ Compressed file not found: {compressed_file}")
        print("\n📋 To get the full database:")
        print("1. Download product_database_compressed.sql.gz from your local repository")
        print("2. Upload it to PythonAnywhere uploads/ directory")
        print("3. Run this script again")
        return False
    
    try:
        print("📊 Decompressing database...")
        
        # Decompress the file
        with gzip.open(compressed_file, 'rb') as f_in:
            sql_content = f_in.read().decode('utf-8')
        
        print("📊 Restoring database...")
        
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
        print(f"📊 Strains restored: {strain_count:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error restoring database: {e}")
        return False

def create_sample_data():
    """Create sample data if restoration fails"""
    print("\n🔧 Creating Sample Data")
    print("=" * 50)
    
    db_path = "uploads/product_database.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add sample products
        now = datetime.now().isoformat()
        
        sample_products = [
            ("Blue Dream Flower", "blue_dream_flower", "Flower", "Sample Vendor", "Sample Brand", "Premium Blue Dream strain", "3.5g", "$45.00", "HYBRID", "Blue Dream"),
            ("Wedding Cake Pre-Roll", "wedding_cake_preroll", "Pre-Roll", "Sample Vendor", "Sample Brand", "Smooth wedding cake pre-roll", "1g", "$15.00", "HYBRID", "Wedding Cake"),
            ("Sour Diesel Cartridge", "sour_diesel_cart", "Vape Cartridge", "Sample Vendor", "Sample Brand", "Classic sativa cartridge", "1g", "$35.00", "SATIVA", "Sour Diesel"),
            ("CBD Gummies", "cbd_gummies", "Edible", "Sample Vendor", "Sample Brand", "CBD gummies for relaxation", "100mg", "$20.00", "MIXED", "CBD Blend"),
            ("Live Resin Concentrate", "live_resin", "Concentrate", "Sample Vendor", "Sample Brand", "Potent live resin", "1g", "$50.00", "HYBRID", "Live Resin")
        ]
        
        for product_name, normalized_name, product_type, vendor, brand, description, weight, price, lineage, strain in sample_products:
            cursor.execute('''
                INSERT OR IGNORE INTO products 
                ("Product Name*", normalized_name, "Product Type*", "Vendor/Supplier*", 
                 "Product Brand", "Description", "Weight*", "Price", "Lineage", 
                 "Product Strain", first_seen_date, last_seen_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_name, normalized_name, product_type, vendor, brand, 
                description, weight, price, lineage, strain, now, now, now, now
            ))
        
        # Add sample strains
        sample_strains = [
            ("Blue Dream", "blue_dream", "HYBRID", now, now, 1, 0.9, "HYBRID"),
            ("Wedding Cake", "wedding_cake", "HYBRID", now, now, 1, 0.9, "HYBRID"),
            ("Sour Diesel", "sour_diesel", "SATIVA", now, now, 1, 0.9, "SATIVA"),
            ("CBD Blend", "cbd_blend", "MIXED", now, now, 1, 0.9, "MIXED"),
            ("Live Resin", "live_resin", "HYBRID", now, now, 1, 0.9, "HYBRID")
        ]
        
        for strain_name, normalized_name, lineage, first_seen, last_seen, count, confidence, sovereign in sample_strains:
            cursor.execute('''
                INSERT OR IGNORE INTO strains 
                (strain_name, normalized_name, canonical_lineage, first_seen_date, 
                 last_seen_date, total_occurrences, lineage_confidence, sovereign_lineage, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                strain_name, normalized_name, lineage, first_seen, last_seen, 
                count, confidence, sovereign, now, now
            ))
        
        conn.commit()
        conn.close()
        
        print("✅ Sample data created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
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
        
        # Test JointRatio functionality
        cursor.execute('SELECT COUNT(*) FROM products WHERE "JointRatio" IS NOT NULL AND "JointRatio" != ""')
        jointratio_count = cursor.fetchone()[0]
        print(f"✅ JointRatio products: {jointratio_count}")
        
        # Show sample data
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
    print("🚀 PythonAnywhere Database Population")
    print("=" * 60)
    
    # Try to restore from compressed file first
    if restore_full_database():
        print("\n🎉 Full database restoration completed!")
    else:
        print("\n⚠️  Restoration failed, creating sample data...")
        if create_sample_data():
            print("\n🎉 Sample data created!")
        else:
            print("\n❌ Database population failed!")
    
    # Test the database
    test_database()
    
    print("\n📋 Next steps:")
    print("1. Test your web application")
    print("2. Upload an Excel file to verify functionality")
    print("3. Check that JointRatio processing works")
    print("4. Reload your web app in PythonAnywhere Web tab")
