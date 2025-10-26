#!/usr/bin/env python3
"""
Fixed database rebuild script for Bothell database.
This version removes the UNIQUE constraint that was causing fragmentation issues.
"""

import sqlite3
import os
from datetime import datetime

def rebuild_bothell_database():
    """Rebuild the Bothell database with a clean schema (without problematic UNIQUE constraint)."""
    
    # Flexible path detection
    current_db_path = 'uploads/product_database_AGT_Bothell.db'
    old_bloated_path = 'uploads/product_database_AGT_Bothell_old_bloated.db'
    
    # Determine source database
    if os.path.exists(old_bloated_path):
        old_db_path = old_bloated_path
        new_db_path = current_db_path
        print(f"Starting Bothell database rebuild with FIXED schema...")
        print(f"Source: {old_db_path} (old bloated version)")
        print(f"Target: {new_db_path}")
    elif os.path.exists(current_db_path):
        # Current database exists - rebuild it in place
        temp_path = 'uploads/product_database_AGT_Bothell_temp.db'
        import shutil
        shutil.copy2(current_db_path, temp_path)
        old_db_path = temp_path
        new_db_path = current_db_path
        print(f"Starting Bothell database rebuild with FIXED schema...")
        print(f"Source: {current_db_path} (copying to temp first)")
        print(f"Target: {new_db_path}")
    else:
        print(f"❌ No Bothell database found!")
        print(f"Checked:")
        print(f"  - {current_db_path}")
        print(f"  - {old_bloated_path}")
        return
    
    backup_path = f'uploads/product_database_AGT_Bothell_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    # Create backup first
    print(f"\n1. Creating backup...")
    if os.path.exists(old_db_path):
        import shutil
        shutil.copy2(old_db_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
    
    # Connect to both databases
    print(f"\n2. Connecting to databases...")
    old_conn = sqlite3.connect(old_db_path)
    
    # Remove new database if it exists
    if os.path.exists(new_db_path) and new_db_path != old_db_path:
        os.remove(new_db_path)
    
    new_conn = sqlite3.connect(new_db_path)
    
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()
    
    # Create clean schema WITHOUT the problematic UNIQUE constraint
    print(f"\n3. Creating clean schema (without UNIQUE constraint)...")
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
            updated_at TEXT
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
    
    print(f"✅ Clean schema created (no UNIQUE constraint on products)")
    
    # Copy data
    print(f"\n4. Copying data from old database...")
    
    # Get column list from old database
    old_cursor.execute("PRAGMA table_info(products)")
    old_columns = [row[1] for row in old_cursor.fetchall()]
    
    # Get column list from new database
    new_cursor.execute("PRAGMA table_info(products)")
    new_columns = [row[1] for row in new_cursor.fetchall()]
    
    # Check if schemas match or need mapping
    common_columns = [col for col in new_columns if col in old_columns and col != 'id']
    
    # If no common columns, we need to map old schema to new schema
    if len(common_columns) == 0:
        print(f"   Detected old schema format - creating column mapping...")
        
        # Column mapping from old schema to new schema
        column_mapping = {
            'name': 'Product Name*',
            'type': 'Product Type*',
            'brand': 'Product Brand',
            'vendor': 'Vendor/Supplier*',
            'strain': 'Product Strain',
            'lineage': 'Lineage',
            'description': 'Description',
            'weight': 'Weight*',
            'weight_unit': 'Units',
            'price': 'Price',
            'quantity': 'Quantity*',
            'doh_compliant': 'DOH',
            'concentrate_type': 'Concentrate Type',
            'ratio': 'Ratio',
            'joint_ratio': 'JointRatio',
            'state': 'State',
            'is_sample': 'Is Sample? (yes/no)',
            'is_mj_product': 'Is MJ product?(yes/no)',
            'discountable': 'Discountable? (yes/no)',
            'room': 'Room*',
            'batch_number': 'Batch Number',
            'lot_number': 'Lot Number',
            'barcode': 'Barcode*',
            'medical_only': 'Medical Only (Yes/No)',
            'med_price': 'Med Price',
            'expiration_date': 'Expiration Date(YYYY-MM-DD)',
            'is_archived': 'Is Archived? (yes/no)',
            'thc_per_serving': 'THC Per Serving',
            'allergens': 'Allergens',
            'solvent': 'Solvent',
            'accepted_date': 'Accepted Date',
            'internal_product_identifier': 'Internal Product Identifier',
            'product_tags': 'Product Tags (comma separated)',
            'image_url': 'Image URL',
            'ingredients': 'Ingredients',
            'combined_weight': 'CombinedWeight',
            'ratio_or_thc_cbd': 'Ratio_or_THC_CBD',
            'description_complexity': 'Description_Complexity',
            'total_thc': 'Total THC',
            'thca': 'THCA',
            'total_cbd': 'Total CBD',
            'cbda': 'CBDA',
            'cbn': 'CBN',
            'cbga': 'CBGA',
            'cbg': 'CBG',
            'total_cbg': 'Total CBG',
            'cbc': 'CBC',
            'cbdv': 'CBDV',
            'thcv': 'THCV',
            'thc_test_result': 'THC test result',
            'cbd_test_result': 'CBD test result',
            'test_result_unit': 'Test result unit (% or mg)',
            'source': 'Source',
            'date_added': 'Date Added',
            'first_seen_date': 'first_seen_date',
            'last_seen_date': 'last_seen_date',
            'total_occurrences': 'total_occurrences',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
            'normalized_name': 'normalized_name',
            'thc_percentage': 'Total THC',
            'cbd_percentage': 'Total CBD'
        }
        
        # Find columns that exist in old database and have a mapping
        mapped_columns = []
        old_col_names = []
        new_col_names = []
        
        for old_col, new_col in column_mapping.items():
            if old_col in old_columns and new_col in new_columns:
                old_col_names.append(old_col)
                new_col_names.append(new_col)
                mapped_columns.append((old_col, new_col))
        
        print(f"   Found {len(mapped_columns)} columns to map from old to new schema")
        
        if len(mapped_columns) == 0:
            print(f"❌ Error: No mappable columns found!")
            print(f"Old columns: {old_columns[:20]}")
            print(f"New columns: {new_columns[:20]}")
            old_conn.close()
            new_conn.close()
            return
        
        # Build SELECT and INSERT statements with mapping
        select_cols = ', '.join([f'"{col}"' for col in old_col_names])
        insert_cols = ', '.join([f'"{col}"' for col in new_col_names])
        placeholders = ', '.join(['?' for _ in mapped_columns])
        
    else:
        # Schemas match - use direct column copy
        print(f"   Found {len(common_columns)} common columns to copy")
        
        # Build SELECT and INSERT statements - quote all column names
        select_cols = ', '.join([f'"{col}"' for col in common_columns])
        insert_cols = ', '.join([f'"{col}"' for col in common_columns])
        placeholders = ', '.join(['?' for _ in common_columns])
    
    # Copy data in batches
    batch_size = 500  # Smaller batches for better reliability
    offset = 0
    total_copied = 0
    
    # Check if we need to generate normalized_name (not in old schema)
    needs_normalized_name = 'normalized_name' not in [col[0] for col in mapped_columns] if len(common_columns) == 0 else 'normalized_name' not in common_columns
    
    while True:
        old_cursor.execute(f'''
            SELECT {select_cols}
            FROM products
            LIMIT {batch_size} OFFSET {offset}
        ''')
        
        rows = old_cursor.fetchall()
        if not rows:
            break
        
        # Process rows to add normalized_name if needed
        if needs_normalized_name and len(common_columns) == 0:
            # We're using mapped columns - need to add normalized_name
            import re
            processed_rows = []
            for row in rows:
                row_list = list(row)
                # Get the product name (first mapped column should be name -> Product Name*)
                product_name = str(row_list[0]) if len(row_list) > 0 else ""
                # Generate normalized name
                normalized = re.sub(r'[^a-z0-9]+', '', product_name.lower())
                row_list.append(normalized)
                processed_rows.append(tuple(row_list))
            
            # Add normalized_name to insert columns
            final_insert_cols = insert_cols + ', "normalized_name"'
            final_placeholders = placeholders + ', ?'
            
            # Insert into new database
            new_cursor.executemany(f'''
                INSERT INTO products ({final_insert_cols})
                VALUES ({final_placeholders})
            ''', processed_rows)
        else:
            # Insert into new database - use INSERT OR REPLACE to handle duplicates
            new_cursor.executemany(f'''
                INSERT INTO products ({insert_cols})
                VALUES ({placeholders})
            ''', rows)
        
        # Commit after each batch to avoid large transactions
        new_conn.commit()
        
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
                
                new_conn.commit()
                print(f"✅ Copied {len(strains)} strains")
    except Exception as e:
        print(f"⚠️  Warning: Could not copy strains: {e}")
    
    # Create indices AFTER all data is inserted (much faster)
    print(f"\n6. Creating indices...")
    new_cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_normalized ON products(normalized_name)')
    new_cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_vendor_brand ON products("Vendor/Supplier*", "Product Brand")')
    new_cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_type ON products("Product Type*")')
    new_cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_strain ON products("Product Strain")')
    new_cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_name ON products("Product Name*")')
    new_conn.commit()
    print(f"✅ Indices created")
    
    # Run VACUUM to optimize database
    print(f"\n7. Running VACUUM to optimize database...")
    new_cursor.execute('VACUUM')
    new_conn.commit()
    print(f"✅ Database optimized")
    
    # Verify integrity
    print(f"\n8. Verifying database integrity...")
    new_cursor.execute('PRAGMA integrity_check')
    result = new_cursor.fetchone()
    if result[0] == 'ok':
        print(f"✅ Database integrity check: OK")
    else:
        print(f"⚠️  Database integrity check: {result[0]}")
    
    # Get stats
    new_cursor.execute("SELECT COUNT(*) FROM products")
    product_count = new_cursor.fetchone()[0]
    
    try:
        new_cursor.execute("SELECT COUNT(*) FROM strains")
        strain_count = new_cursor.fetchone()[0]
    except:
        strain_count = 0
    
    old_conn.close()
    new_conn.close()
    
    # Get file sizes
    old_size = os.path.getsize(old_db_path) / (1024*1024)  # MB
    new_size = os.path.getsize(new_db_path) / (1024*1024)  # MB
    
    print(f"\n✅ BOTHELL DATABASE REBUILD COMPLETE!")
    print(f"\nStatistics:")
    print(f"  Products: {product_count}")
    print(f"  Strains: {strain_count}")
    print(f"  Old database size: {old_size:.2f} MB")
    print(f"  New database size: {new_size:.2f} MB")
    print(f"  Space saved: {old_size - new_size:.2f} MB ({((old_size - new_size) / old_size * 100):.1f}%)")
    print(f"\nNew database location: {new_db_path}")
    print(f"Backup location: {backup_path}")
    
    # If we created a new file, give instructions to replace
    if new_db_path != 'uploads/product_database_AGT_Bothell.db':
        print(f"\nTo activate the new database:")
        print(f"  mv {new_db_path} uploads/product_database_AGT_Bothell.db")

if __name__ == "__main__":
    rebuild_bothell_database()

