#!/usr/bin/env python3
"""
Fix all store databases by adding DOH and lineage columns.
This script applies the same fixes to all AGT store databases.
"""

import sqlite3
import os
from collections import Counter

# List of all store databases
STORE_DATABASES = [
    'uploads/product_database_AGT_Bothell.db',
    'uploads/product_database_AGT_Burien.db',
    'uploads/product_database_AGT_Goldbar.db',
    'uploads/product_database_AGT_Lynnwood.db',
    'uploads/product_database_AGT_Seattle.db',
    'uploads/product_database_AGT_Shoreline.db',
    'uploads/product_database_AGT_Walla_Walla.db'
]

def fix_database(db_path):
    """Fix a single database by adding required columns and populating data."""
    store_name = os.path.basename(db_path).replace('product_database_', '').replace('.db', '')
    print(f"\n{'='*60}")
    print(f"Processing: {store_name}")
    print(f"{'='*60}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if strains table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strains'")
        if not cursor.fetchone():
            print(f"⚠️  No strains table found in {store_name}")
            conn.close()
            return False
        
        # Step 1: Add DOH columns to strains table if they don't exist
        print("\n1. Adding DOH columns to strains table...")
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(strains)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        columns_to_add = []
        if 'doh_status' not in existing_columns:
            columns_to_add.append(('doh_status', 'TEXT'))
        if 'high_cbd' not in existing_columns:
            columns_to_add.append(('high_cbd', 'INTEGER DEFAULT 0'))
        if 'high_thc' not in existing_columns:
            columns_to_add.append(('high_thc', 'INTEGER DEFAULT 0'))
        
        if columns_to_add:
            for col_name, col_type in columns_to_add:
                cursor.execute(f'ALTER TABLE strains ADD COLUMN {col_name} {col_type}')
                print(f"   ✓ Added column: {col_name}")
        else:
            print("   ✓ All DOH columns already exist")
        
        conn.commit()
        
        # Step 2: Populate DOH data from products
        print("\n2. Populating DOH data from products...")
        
        # Check which columns exist in products table
        cursor.execute("PRAGMA table_info(products)")
        product_columns = {row[1] for row in cursor.fetchall()}
        
        # Determine which columns to use
        strain_col = None
        doh_col = None
        
        if 'Product Strain' in product_columns:
            strain_col = '"Product Strain"'
        elif 'name' in product_columns:
            strain_col = 'name'
        
        # Check for DOH column variations
        for possible_doh in ['DOH', '"DOH Compliant*"', '"DOH Compliant (Yes/No)"']:
            if possible_doh.strip('"') in product_columns:
                doh_col = possible_doh
                break
        
        if not strain_col or not doh_col:
            print(f"   ⚠️  Could not find strain column or DOH column")
            print(f"      Strain column: {strain_col}, DOH column: {doh_col}")
            print("   ⚠️  Skipping DOH population for this database")
            strain_doh_data = {}
        else:
            cursor.execute(f'''
                SELECT {strain_col}, "Product Name*", {doh_col}
                FROM products 
                WHERE {strain_col} IS NOT NULL AND {strain_col} != '' AND {strain_col} != 'None'
            ''')
            
            strain_doh_data = {}
            for strain_name, product_name, doh_value in cursor.fetchall():
                if strain_name not in strain_doh_data:
                    strain_doh_data[strain_name] = []
                strain_doh_data[strain_name].append(doh_value)
        
        update_count = 0
        for strain_name, doh_values in strain_doh_data.items():
            # Use Counter to find most common DOH value
            doh_counter = Counter(doh_values)
            most_common_doh = doh_counter.most_common(1)[0][0] if doh_counter else None
            
            if most_common_doh:
                # Determine high_cbd and high_thc flags
                high_cbd = 1 if 'CBD' in strain_name.upper() else 0
                high_thc = 1 if most_common_doh == 'Yes' else 0
                
                cursor.execute('''
                    UPDATE strains 
                    SET doh_status = ?, high_cbd = ?, high_thc = ?
                    WHERE strain_name = ?
                ''', (most_common_doh, high_cbd, high_thc, strain_name))
                update_count += 1
        
        conn.commit()
        print(f"   ✓ Updated {update_count} strains with DOH data")
        
        # Step 3: Add lineage columns to products table if they don't exist
        print("\n3. Adding lineage columns to products table...")
        
        cursor.execute("PRAGMA table_info(products)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        lineage_columns_to_add = []
        if 'canonical_lineage' not in existing_columns:
            lineage_columns_to_add.append('canonical_lineage')
        if 'currentLineage' not in existing_columns:
            lineage_columns_to_add.append('currentLineage')
        
        if lineage_columns_to_add:
            for col_name in lineage_columns_to_add:
                cursor.execute(f'ALTER TABLE products ADD COLUMN {col_name} TEXT')
                print(f"   ✓ Added column: {col_name}")
        else:
            print("   ✓ All lineage columns already exist")
        
        conn.commit()
        
        # Step 4: Populate lineage columns from existing Lineage column
        print("\n4. Populating lineage columns...")
        
        cursor.execute('''
            UPDATE products 
            SET canonical_lineage = Lineage 
            WHERE Lineage IS NOT NULL AND Lineage != '' AND Lineage != 'None'
        ''')
        canonical_count = cursor.rowcount
        
        cursor.execute('''
            UPDATE products 
            SET currentLineage = canonical_lineage 
            WHERE canonical_lineage IS NOT NULL
        ''')
        current_count = cursor.rowcount
        
        conn.commit()
        print(f"   ✓ Updated {canonical_count} products with canonical_lineage")
        print(f"   ✓ Updated {current_count} products with currentLineage")
        
        # Step 5: Verification
        print("\n5. Verification:")
        
        cursor.execute("SELECT COUNT(*) FROM strains WHERE doh_status IS NOT NULL")
        strains_with_doh = cursor.fetchone()[0]
        print(f"   ✓ Strains with DOH status: {strains_with_doh}")
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE canonical_lineage IS NOT NULL")
        products_with_lineage = cursor.fetchone()[0]
        print(f"   ✓ Products with lineage: {products_with_lineage}")
        
        conn.close()
        print(f"\n✅ Successfully fixed {store_name}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error processing {store_name}: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def main():
    """Process all store databases."""
    print("="*60)
    print("FIXING ALL STORE DATABASES")
    print("="*60)
    
    results = {}
    for db_path in STORE_DATABASES:
        success = fix_database(db_path)
        store_name = os.path.basename(db_path).replace('product_database_', '').replace('.db', '')
        results[store_name] = success
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    successful = [store for store, success in results.items() if success]
    failed = [store for store, success in results.items() if not success]
    
    print(f"\n✅ Successfully fixed {len(successful)} databases:")
    for store in successful:
        print(f"   • {store}")
    
    if failed:
        print(f"\n❌ Failed to fix {len(failed)} databases:")
        for store in failed:
            print(f"   • {store}")
    
    print(f"\nTotal: {len(successful)}/{len(results)} databases fixed")

if __name__ == '__main__':
    main()
