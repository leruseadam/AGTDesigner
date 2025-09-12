#!/usr/bin/env python3
"""
Add missing columns to the products table
"""

import sqlite3

def add_missing_columns():
    """Add missing columns to the products table"""
    
    # Missing columns that need to be added
    missing_columns = [
        'Ratio_or_THC_CBD',
        'Description_Complexity', 
        'THC',
        'CBD',
        'Total CBD',
        'CBGA',
        'CBG',
        'Total CBG',
        'CBC',
        'CBDV',
        'THCV',
        'CBGV',
        'CBNV',
        'CBGVA',
        'ProductName',
        'qty',
        'THC test result',
        'CBD test result',
        'Vendor'
    ]
    
    conn = sqlite3.connect('product_database.db')
    cursor = conn.cursor()
    
    try:
        # Add each missing column
        for column in missing_columns:
            try:
                cursor.execute(f'ALTER TABLE products ADD COLUMN "{column}" TEXT')
                print(f"✅ Added column: {column}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"⚠️  Column already exists: {column}")
                else:
                    print(f"❌ Error adding column {column}: {e}")
        
        conn.commit()
        print(f"\n✅ Successfully added {len(missing_columns)} columns")
        
        # Verify the columns were added
        cursor.execute('PRAGMA table_info(products)')
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"\n📊 Total columns in database: {len(columns)}")
        
        # Check if all required columns now exist
        all_present = all(col in columns for col in missing_columns)
        print(f"✅ All missing columns added: {all_present}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_missing_columns()