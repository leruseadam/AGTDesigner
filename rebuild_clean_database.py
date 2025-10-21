#!/usr/bin/env python3
"""
Rebuild a clean, optimized product database from the existing bloated one.
This script will:
1. Extract all essential data from the old database
2. Create a new database with a clean schema
3. Import the data with proper structure
4. Add appropriate indices for performance
"""

import sqlite3
import os
from datetime import datetime

def rebuild_database():
    """Rebuild the database with a clean schema."""
    
    old_db_path = 'uploads/product_database.db'
    new_db_path = 'uploads/product_database_clean.db'
    backup_path = f'uploads/product_database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    print(f"Starting database rebuild...")
    print(f"Old database: {old_db_path}")
    print(f"New database: {new_db_path}")
    
    # Create backup first
    print(f"\n1. Creating backup...")
    if os.path.exists(old_db_path):
        import shutil
        shutil.copy2(old_db_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
    
    # Connect to both databases
    print(f"\n2. Connecting to databases...")
    old_conn = sqlite3.connect(old_db_path)
    new_conn = sqlite3.connect(new_db_path)
    
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()
    
    # Create clean schema
    print(f"\n3. Creating clean schema...")
    new_cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "Product Name*" TEXT NOT NULL,
            normalized_name TEXT NOT NULL,
            "Product Type*" TEXT,
            "Vendor/Supplier*" TEXT,
            "Product Brand" TEXT,
            "Product Strain" TEXT,
            "Lineage" TEXT,
            "Description" TEXT,
            "Weight*" TEXT,
            "Units" TEXT,
            "Price" TEXT,
            "Quantity*" TEXT DEFAULT '1',
            "DOH" TEXT,
            "Concentrate Type" TEXT,
            "Ratio" TEXT,
            "JointRatio" TEXT,
            "State" TEXT DEFAULT 'active',
            "Is Sample? (yes/no)" TEXT DEFAULT 'no',
            "Is MJ product?(yes/no)" TEXT DEFAULT 'yes',
            "Discountable? (yes/no)" TEXT DEFAULT 'yes',
            "Room*" TEXT DEFAULT 'Default',
            "Batch Number" TEXT,
            "Lot Number" TEXT,
            "Barcode*" TEXT,
            "Medical Only (Yes/No)" TEXT DEFAULT 'No',
            "Med Price" TEXT,
            "Expiration Date(YYYY-MM-DD)" TEXT,
            "Is Archived? (yes/no)" TEXT DEFAULT 'no',
            "THC Per Serving" TEXT,
            "Allergens" TEXT,
            "Solvent" TEXT,
            "Accepted Date" TEXT,
            "Internal Product Identifier" TEXT,
            "Product Tags (comma separated)" TEXT,
            "Image URL" TEXT,
            "Ingredients" TEXT,
            "CombinedWeight" TEXT,
            "Ratio_or_THC_CBD" TEXT,
            "Description_Complexity" INTEGER,
            "Total THC" TEXT,
            "THCA" TEXT,
            "Total CBD" TEXT,
            "CBDA" TEXT,
            "CBN" TEXT,
            "CBGA" TEXT,
            "CBG" TEXT,
            "Total CBG" TEXT,
            "CBC" TEXT,
            "CBDV" TEXT,
            "THCV" TEXT,
            "THC test result" TEXT,
            "CBD test result" TEXT,
            "Test result unit (% or mg)" TEXT DEFAULT '%',
            "Source" TEXT,
            "Date Added" TEXT,
            first_seen_date TEXT,
            last_seen_date TEXT,
            total_occurrences INTEGER DEFAULT 1,
            created_at TEXT,
            updated_at TEXT,
            UNIQUE(normalized_name, "Vendor/Supplier*", "Product Brand")
        )
    ''')
    
    # Create strains table
    new_cursor.execute('''
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
    
    print(f"✅ Clean schema created")
    
    # Copy data
    print(f"\n4. Copying data from old database...")
    
    # Get column list from old database
    old_cursor.execute("PRAGMA table_info(products)")
    old_columns = [row[1] for row in old_cursor.fetchall()]
    
    # Get column list from new database
    new_cursor.execute("PRAGMA table_info(products)")
    new_columns = [row[1] for row in new_cursor.fetchall()]
    
    # Find common columns
    common_columns = [col for col in new_columns if col in old_columns and col != 'id']
    
    print(f"   Found {len(common_columns)} common columns to copy")
    
    # Build SELECT and INSERT statements - quote all column names to handle special characters
    select_cols = ', '.join([f'"{col}"' for col in common_columns])
    insert_cols = ', '.join([f'"{col}"' for col in common_columns])
    placeholders = ', '.join(['?' for _ in common_columns])
    
    # Copy data in batches
    batch_size = 1000
    offset = 0
    total_copied = 0
    
    while True:
        old_cursor.execute(f'''
            SELECT {select_cols}
            FROM products
            LIMIT {batch_size} OFFSET {offset}
        ''')
        
        rows = old_cursor.fetchall()
        if not rows:
            break
        
        # Insert into new database
        new_cursor.executemany(f'''
            INSERT OR IGNORE INTO products ({insert_cols})
            VALUES ({placeholders})
        ''', rows)
        
        total_copied += len(rows)
        offset += batch_size
        
        if total_copied % 1000 == 0:
            print(f"   Copied {total_copied} products...")
    
    print(f"✅ Copied {total_copied} products")
    
    # Copy strains table if it exists
    try:
        old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strains'")
        if old_cursor.fetchone():
            print(f"\n5. Copying strains...")
            old_cursor.execute("SELECT * FROM strains")
            strains = old_cursor.fetchall()
            
            if strains:
                # Get column names
                old_cursor.execute("PRAGMA table_info(strains)")
                strain_columns = [row[1] for row in old_cursor.fetchall()]
                
                # Insert strains
                strain_placeholders = ', '.join(['?' for _ in strain_columns])
                new_cursor.executemany(f'''
                    INSERT OR IGNORE INTO strains VALUES ({strain_placeholders})
                ''', strains)
                
                print(f"✅ Copied {len(strains)} strains")
    except Exception as e:
        print(f"⚠️  Warning: Could not copy strains: {e}")
    
    # Create indices
    print(f"\n6. Creating indices...")
    new_cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_normalized ON products(normalized_name)')
    new_cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_vendor_brand ON products("Vendor/Supplier*", "Product Brand")')
    new_cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_type ON products("Product Type*")')
    new_cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_strain ON products("Product Strain")')
    print(f"✅ Indices created")
    
    # Commit and close
    print(f"\n7. Finalizing...")
    new_conn.commit()
    
    # Get stats
    new_cursor.execute("SELECT COUNT(*) FROM products")
    product_count = new_cursor.fetchone()[0]
    
    new_cursor.execute("SELECT COUNT(*) FROM strains")
    strain_count = new_cursor.fetchone()[0]
    
    old_conn.close()
    new_conn.close()
    
    # Get file sizes
    old_size = os.path.getsize(old_db_path) / (1024*1024)  # MB
    new_size = os.path.getsize(new_db_path) / (1024*1024)  # MB
    
    print(f"\n✅ DATABASE REBUILD COMPLETE!")
    print(f"\nStatistics:")
    print(f"  Products: {product_count}")
    print(f"  Strains: {strain_count}")
    print(f"  Old database size: {old_size:.2f} MB")
    print(f"  New database size: {new_size:.2f} MB")
    print(f"  Space saved: {old_size - new_size:.2f} MB ({((old_size - new_size) / old_size * 100):.1f}%)")
    print(f"\nTo use the new database:")
    print(f"  1. Stop the app")
    print(f"  2. mv uploads/product_database.db uploads/product_database_old_bloated.db")
    print(f"  3. mv {new_db_path} uploads/product_database.db")
    print(f"  4. Restart the app")
    print(f"\nBackup location: {backup_path}")

if __name__ == "__main__":
    rebuild_database()

