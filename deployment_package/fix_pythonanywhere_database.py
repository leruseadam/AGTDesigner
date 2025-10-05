#!/usr/bin/env python3
"""
PythonAnywhere Database Fix Script
This script will create and populate the database on PythonAnywhere
"""

import os
import sys
import sqlite3
from datetime import datetime

def create_database_structure():
    """Create the database structure on PythonAnywhere"""
    
    # Get the correct database path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(current_dir, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Create the main database
    db_path = os.path.join(uploads_dir, 'product_database.db')
    print(f"Creating database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create strains table
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
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database structure created successfully at: {db_path}")
        return db_path
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return None

def add_sample_data(db_path):
    """Add some sample data to test the database"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add sample strain
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR IGNORE INTO strains 
            (strain_name, normalized_name, first_seen_date, last_seen_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Blue Dream', 'blue_dream', now, now, now, now))
        
        # Add sample products
        sample_products = [
            {
                'Product Name*': 'Blue Dream Flower 1g',
                'normalized_name': 'blue_dream_flower_1g',
                'Product Type*': 'Flower',
                'Weight*': '1g',
                'Units': 'g',
                'Price': '$15.00',
                'Vendor/Supplier*': 'AGT Bothell',
                'first_seen_date': now,
                'last_seen_date': now,
                'created_at': now,
                'updated_at': now,
                'Product Strain': 'Blue Dream'
            },
            {
                'Product Name*': 'Blue Dream Concentrate 0.5g',
                'normalized_name': 'blue_dream_concentrate_0_5g',
                'Product Type*': 'Concentrate',
                'Weight*': '0.5g',
                'Units': 'g',
                'Price': '$25.00',
                'Vendor/Supplier*': 'AGT Bothell',
                'first_seen_date': now,
                'last_seen_date': now,
                'created_at': now,
                'updated_at': now,
                'Product Strain': 'Blue Dream',
                'Concentrate Type': 'Wax'
            },
            {
                'Product Name*': 'Blue Dream Pre-roll',
                'normalized_name': 'blue_dream_preroll',
                'Product Type*': 'Pre-roll',
                'Weight*': '1g',
                'Units': 'g',
                'Price': '$12.00',
                'Vendor/Supplier*': 'AGT Bothell',
                'first_seen_date': now,
                'last_seen_date': now,
                'created_at': now,
                'updated_at': now,
                'Product Strain': 'Blue Dream'
            }
        ]
        
        for product in sample_products:
            columns = list(product.keys())
            placeholders = ', '.join(['?' for _ in columns])
            column_names = ', '.join([f'"{col}"' for col in columns])
            
            sql = f'''
                INSERT OR REPLACE INTO products 
                ({column_names})
                VALUES ({placeholders})
            '''
            
            values = [product[col] for col in columns]
            cursor.execute(sql, values)
        
        conn.commit()
        conn.close()
        
        print(f"✅ Added {len(sample_products)} sample products")
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")

def create_agt_bothell_database():
    """Create the AGT_Bothell specific database"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(current_dir, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Create the AGT_Bothell database
    db_path = os.path.join(uploads_dir, 'product_database_AGT_Bothell.db')
    print(f"Creating AGT_Bothell database at: {db_path}")
    
    # Use the same structure as the main database
    main_db_path = create_database_structure()
    if main_db_path:
        add_sample_data(db_path)
        print(f"✅ AGT_Bothell database created successfully")
        return db_path
    
    return None

def main():
    print("🚀 PythonAnywhere Database Setup")
    print("=" * 40)
    
    # Create main database
    main_db = create_database_structure()
    if main_db:
        add_sample_data(main_db)
    
    # Create AGT_Bothell database
    agt_db = create_agt_bothell_database()
    
    print("\n✅ Database setup complete!")
    print(f"📁 Main database: {main_db}")
    print(f"📁 AGT_Bothell database: {agt_db}")
    print("\n🎯 Your site should now have data to display!")

if __name__ == "__main__":
    main()