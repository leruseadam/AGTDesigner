#!/usr/bin/env python3

"""
PythonAnywhere Compact Database Creator
======================================
Creates a smaller, manageable database for PythonAnywhere upload
"""

import sqlite3
import os
import random
from datetime import datetime

def create_compact_database():
    """Create a compact database with essential products"""
    print("🗜️  Creating Compact Database for PythonAnywhere")
    print("=" * 60)
    
    main_db = "uploads/product_database_compact.db"
    
    try:
        # Remove existing compact database
        if os.path.exists(main_db):
            os.remove(main_db)
            print("🗑️  Removed existing compact database")
        
        # Create new compact database
        conn = sqlite3.connect(main_db)
        cursor = conn.cursor()
        
        print("📊 Creating compact database schema...")
        
        # Create products table with essential columns only
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
                "Price" TEXT,
                "Lineage" TEXT,
                first_seen_date TEXT NOT NULL,
                last_seen_date TEXT NOT NULL,
                total_occurrences INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                "Product Strain" TEXT,
                "JointRatio" TEXT,
                "THC test result" TEXT,
                "CBD test result" TEXT,
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
        
        print("📊 Adding compact sample data...")
        
        # Add essential strains (most common ones)
        now = datetime.now().isoformat()
        
        essential_strains = [
            ("Blue Dream", "blue_dream", "HYBRID", now, now, 1, 0.9, "HYBRID"),
            ("Wedding Cake", "wedding_cake", "HYBRID", now, now, 1, 0.9, "HYBRID"),
            ("Sour Diesel", "sour_diesel", "SATIVA", now, now, 1, 0.9, "SATIVA"),
            ("OG Kush", "og_kush", "INDICA", now, now, 1, 0.9, "INDICA"),
            ("Gelato", "gelato", "HYBRID", now, now, 1, 0.9, "HYBRID"),
            ("Jack Herer", "jack_herer", "SATIVA", now, now, 1, 0.9, "SATIVA"),
            ("Granddaddy Purple", "granddaddy_purple", "INDICA", now, now, 1, 0.9, "INDICA"),
            ("White Widow", "white_widow", "HYBRID", now, now, 1, 0.9, "HYBRID"),
            ("CBD Blend", "cbd_blend", "MIXED", now, now, 1, 0.9, "MIXED"),
            ("Live Resin", "live_resin", "HYBRID", now, now, 1, 0.9, "HYBRID"),
            ("Purple Haze", "purple_haze", "SATIVA", now, now, 1, 0.9, "SATIVA"),
            ("Bubba Kush", "bubba_kush", "INDICA", now, now, 1, 0.9, "INDICA"),
            ("Green Crack", "green_crack", "SATIVA", now, now, 1, 0.9, "SATIVA"),
            ("Northern Lights", "northern_lights", "INDICA", now, now, 1, 0.9, "INDICA"),
            ("AK-47", "ak47", "HYBRID", now, now, 1, 0.9, "HYBRID")
        ]
        
        for strain_name, normalized_name, lineage, first_seen, last_seen, count, confidence, sovereign in essential_strains:
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
        
        # Add compact product set (50 products)
        product_types = ["Flower", "Pre-Roll", "Vape Cartridge", "Edible", "Concentrate"]
        vendors = ["AGT Dispensary", "Green Revolution", "Cannabis Co", "Herb House", "Dank Depot"]
        brands = ["AGT Brand", "Green Revolution", "Cannabis Co", "Herb House", "Dank Depot"]
        
        compact_products = []
        
        # Generate 50 diverse products
        for i in range(50):
            strain = random.choice(essential_strains)[0]
            product_type = random.choice(product_types)
            vendor = random.choice(vendors)
            brand = random.choice(brands)
            
            # Create product name based on type and strain
            if product_type == "Flower":
                product_name = f"{strain} Flower"
                weight = "3.5g"
                price = f"${random.randint(35, 55)}.00"
            elif product_type == "Pre-Roll":
                product_name = f"{strain} Pre-Roll"
                weight = "1g"
                price = f"${random.randint(12, 20)}.00"
            elif product_type == "Vape Cartridge":
                product_name = f"{strain} Cartridge"
                weight = "1g"
                price = f"${random.randint(30, 45)}.00"
            elif product_type == "Edible":
                product_name = f"{strain} Gummies"
                weight = f"{random.randint(50, 200)}mg"
                price = f"${random.randint(15, 30)}.00"
            else:  # Concentrate
                product_name = f"{strain} Concentrate"
                weight = "1g"
                price = f"${random.randint(40, 60)}.00"
            
            # Add JointRatio
            jointratio_options = ["1:1", "1:2", "1:5", "1:10", "2:1", "5:1", "10:1"]
            jointratio = random.choice(jointratio_options)
            
            # Add THC/CBD content
            thc_content = f"{random.randint(15, 30)}%"
            cbd_content = f"{random.randint(0, 5)}%"
            
            compact_products.append((
                product_name, product_name.lower().replace(' ', '_'), product_type, vendor, brand,
                f"Premium {strain} {product_type.lower()}", weight, price, "HYBRID", strain,
                jointratio, thc_content, cbd_content, now, now, now, now
            ))
        
        # Insert compact products
        for product_data in compact_products:
            cursor.execute('''
                INSERT INTO products 
                ("Product Name*", normalized_name, "Product Type*", "Vendor/Supplier*", "Product Brand", 
                 "Description", "Weight*", "Price", "Lineage", "Product Strain", "JointRatio",
                 "THC test result", "CBD test result", first_seen_date, last_seen_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', product_data)
        
        conn.commit()
        conn.close()
        
        print("✅ Compact database created successfully!")
        
        # Verify database size
        file_size = os.path.getsize(main_db)
        print(f"📊 Database size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        # Verify database content
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
        print(f"❌ Error creating compact database: {e}")
        return False

def create_compressed_compact_database():
    """Create a compressed version of the compact database"""
    print("\n🗜️  Creating Compressed Compact Database")
    print("=" * 50)
    
    import gzip
    
    compact_db = "uploads/product_database_compact.db"
    compressed_file = "uploads/product_database_compact.sql.gz"
    
    if not os.path.exists(compact_db):
        print(f"❌ Compact database not found: {compact_db}")
        return False
    
    try:
        # Create SQL dump
        conn = sqlite3.connect(compact_db)
        dump_file = "temp_compact_dump.sql"
        
        with open(dump_file, 'w') as f:
            for line in conn.iterdump():
                f.write(f'{line}\n')
        
        conn.close()
        
        # Compress the dump
        with open(dump_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                f_out.write(f_in.read())
        
        # Clean up
        os.remove(dump_file)
        
        # Check sizes
        original_size = os.path.getsize(compact_db)
        compressed_size = os.path.getsize(compressed_file)
        compression_ratio = (1 - compressed_size/original_size) * 100
        
        print(f"✅ Compressed compact database created!")
        print(f"📊 Original size: {original_size:,} bytes ({original_size/1024/1024:.1f} MB)")
        print(f"📊 Compressed size: {compressed_size:,} bytes ({compressed_size/1024/1024:.1f} MB)")
        print(f"📊 Compression: {compression_ratio:.1f}% reduction")
        
        if compressed_size < 5 * 1024 * 1024:  # Less than 5MB
            print("✅ Compressed file is under 5MB - perfect for PythonAnywhere upload!")
        else:
            print("⚠️  Still too large for easy upload")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating compressed compact database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PythonAnywhere Compact Database Creator")
    print("=" * 60)
    
    # Step 1: Create compact database
    if create_compact_database():
        print("\n✅ Compact database creation completed!")
    else:
        print("\n❌ Compact database creation failed!")
        exit(1)
    
    # Step 2: Create compressed version
    if create_compressed_compact_database():
        print("\n✅ Compressed compact database created!")
    else:
        print("\n⚠️  Compressed version creation failed!")
    
    print("\n🎉 Compact database creation complete!")
    print("\n📋 Files created:")
    print("1. uploads/product_database_compact.db - Compact database (50 products)")
    print("2. uploads/product_database_compact.sql.gz - Compressed version for upload")
    print("\n📋 Next steps:")
    print("1. Upload product_database_compact.sql.gz to PythonAnywhere")
    print("2. Run: python3 restore_database_fixed.py")
    print("3. Reload your web app")
    print("4. Enjoy 50 products with full functionality!")
