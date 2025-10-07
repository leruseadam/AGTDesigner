#!/usr/bin/env python3

"""
PythonAnywhere Database Emergency Fix
====================================
Creates a working database when source databases are corrupted
"""

import sqlite3
import os
from datetime import datetime

def create_working_database():
    """Create a working database from scratch"""
    print("🚨 Emergency Database Creation")
    print("=" * 60)
    
    main_db = "uploads/product_database.db"
    
    try:
        # Remove any existing corrupted database
        if os.path.exists(main_db):
            os.remove(main_db)
            print("🗑️  Removed corrupted database")
        
        # Create new database
        conn = sqlite3.connect(main_db)
        cursor = conn.cursor()
        
        print("📊 Creating database schema...")
        
        # Create products table with comprehensive schema
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
        
        print("📊 Adding sample data...")
        
        # Add comprehensive sample data
        now = datetime.now().isoformat()
        
        # Sample strains
        sample_strains = [
            ("Blue Dream", "blue_dream", "HYBRID", now, now, 1, 0.9, "HYBRID"),
            ("Wedding Cake", "wedding_cake", "HYBRID", now, now, 1, 0.9, "HYBRID"),
            ("Sour Diesel", "sour_diesel", "SATIVA", now, now, 1, 0.9, "SATIVA"),
            ("CBD Blend", "cbd_blend", "MIXED", now, now, 1, 0.9, "MIXED"),
            ("Live Resin", "live_resin", "HYBRID", now, now, 1, 0.9, "HYBRID"),
            ("OG Kush", "og_kush", "INDICA", now, now, 1, 0.9, "INDICA"),
            ("Gelato", "gelato", "HYBRID", now, now, 1, 0.9, "HYBRID"),
            ("Jack Herer", "jack_herer", "SATIVA", now, now, 1, 0.9, "SATIVA"),
            ("Granddaddy Purple", "granddaddy_purple", "INDICA", now, now, 1, 0.9, "INDICA"),
            ("White Widow", "white_widow", "HYBRID", now, now, 1, 0.9, "HYBRID")
        ]
        
        for strain_name, normalized_name, lineage, first_seen, last_seen, count, confidence, sovereign in sample_strains:
            cursor.execute('''
                INSERT INTO strains 
                (strain_name, normalized_name, canonical_lineage, first_seen_date, 
                 last_seen_date, total_occurrences, lineage_confidence, sovereign_lineage, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                strain_name, normalized_name, lineage, first_seen, last_seen, 
                count, confidence, sovereign, now, now
            ))
        
        # Sample products with JointRatio
        sample_products = [
            ("Blue Dream Flower", "blue_dream_flower", "Flower", "AGT Dispensary", "AGT Brand", "Premium Blue Dream strain", "3.5g", "$45.00", "HYBRID", "Blue Dream", "1:1", "1:1"),
            ("Wedding Cake Pre-Roll", "wedding_cake_preroll", "Pre-Roll", "AGT Dispensary", "AGT Brand", "Smooth wedding cake pre-roll", "1g", "$15.00", "HYBRID", "Wedding Cake", "1:1", "1:1"),
            ("Sour Diesel Cartridge", "sour_diesel_cart", "Vape Cartridge", "AGT Dispensary", "AGT Brand", "Classic sativa cartridge", "1g", "$35.00", "SATIVA", "Sour Diesel", "1:1", "1:1"),
            ("CBD Gummies", "cbd_gummies", "Edible", "AGT Dispensary", "AGT Brand", "CBD gummies for relaxation", "100mg", "$20.00", "MIXED", "CBD Blend", "1:10", "1:10"),
            ("Live Resin Concentrate", "live_resin", "Concentrate", "AGT Dispensary", "AGT Brand", "Potent live resin", "1g", "$50.00", "HYBRID", "Live Resin", "1:1", "1:1"),
            ("OG Kush Flower", "og_kush_flower", "Flower", "AGT Dispensary", "AGT Brand", "Classic OG Kush", "3.5g", "$40.00", "INDICA", "OG Kush", "1:1", "1:1"),
            ("Gelato Pre-Roll", "gelato_preroll", "Pre-Roll", "AGT Dispensary", "AGT Brand", "Sweet gelato pre-roll", "1g", "$18.00", "HYBRID", "Gelato", "1:1", "1:1"),
            ("Jack Herer Cartridge", "jack_herer_cart", "Vape Cartridge", "AGT Dispensary", "AGT Brand", "Energizing sativa", "1g", "$38.00", "SATIVA", "Jack Herer", "1:1", "1:1"),
            ("Granddaddy Purple Flower", "granddaddy_purple_flower", "Flower", "AGT Dispensary", "AGT Brand", "Relaxing indica", "3.5g", "$42.00", "INDICA", "Granddaddy Purple", "1:1", "1:1"),
            ("White Widow Concentrate", "white_widow_concentrate", "Concentrate", "AGT Dispensary", "AGT Brand", "Balanced hybrid", "1g", "$48.00", "HYBRID", "White Widow", "1:1", "1:1")
        ]
        
        for product_name, normalized_name, product_type, vendor, brand, description, weight, price, lineage, strain, ratio, jointratio in sample_products:
            cursor.execute('''
                INSERT INTO products 
                ("Product Name*", normalized_name, "Product Type*", "Vendor/Supplier*", "Product Brand", 
                 "Description", "Weight*", "Price", "Lineage", "Product Strain", "Ratio", "JointRatio",
                 first_seen_date, last_seen_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_name, normalized_name, product_type, vendor, brand, 
                description, weight, price, lineage, strain, ratio, jointratio,
                now, now, now, now
            ))
        
        conn.commit()
        conn.close()
        
        print("✅ Working database created successfully!")
        
        # Verify database
        conn = sqlite3.connect(main_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM strains")
        strain_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM products WHERE "JointRatio" IS NOT NULL AND "JointRatio" != ""')
        jointratio_count = cursor.fetchone()[0]
        
        print(f"📊 Database contains:")
        print(f"   Products: {product_count}")
        print(f"   Strains: {strain_count}")
        print(f"   JointRatio products: {jointratio_count}")
        
        # Test integrity
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result == "ok":
            print("✅ Database integrity check passed")
        else:
            print(f"⚠️  Database integrity issues: {integrity_result}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating working database: {e}")
        return False

def test_application():
    """Test the application with the working database"""
    print("\n🧪 Testing Application with Working Database")
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

def provide_upload_instructions():
    """Provide instructions for uploading a clean database"""
    print("\n📋 Instructions for Full Database Upload")
    print("=" * 50)
    
    print("🔧 To get your full 8,000+ product database:")
    print("")
    print("1. 📥 Download a clean database file from your local machine")
    print("2. 📤 Upload it to PythonAnywhere Files tab:")
    print("   - Go to Files tab in PythonAnywhere")
    print("   - Navigate to /home/adamcordova/AGTDesigner/uploads/")
    print("   - Upload your clean database file")
    print("")
    print("3. 🔄 Replace the current database:")
    print("   - Rename your uploaded file to 'product_database_AGT_Bothell.db'")
    print("   - Run: python3 rebuild_database_clean.py")
    print("")
    print("4. 🔄 Reload your web app in PythonAnywhere Web tab")
    print("")
    print("💡 Alternative: Use the sample database for testing")
    print("   The current database has 10 products and works for testing")

if __name__ == "__main__":
    print("🚨 PythonAnywhere Emergency Database Fix")
    print("=" * 60)
    
    # Step 1: Create working database
    if create_working_database():
        print("\n✅ Emergency database creation completed!")
    else:
        print("\n❌ Emergency database creation failed!")
        exit(1)
    
    # Step 2: Test application
    if test_application():
        print("\n✅ Application test passed!")
    else:
        print("\n❌ Application test failed!")
        exit(1)
    
    # Step 3: Provide instructions
    provide_upload_instructions()
    
    print("\n🎉 Emergency database fix complete!")
    print("\n📋 Next steps:")
    print("1. Reload your web app in PythonAnywhere Web tab")
    print("2. Visit your site - should show 10 products")
    print("3. Test file upload functionality")
    print("4. Upload a clean database file for full functionality")
    print("\n🔗 Your app: https://$(whoami).pythonanywhere.com")
