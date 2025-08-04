#!/usr/bin/env python3
"""
Fix missing sovereign_lineage column in the database.
"""

import sqlite3
import os

def fix_database_columns():
    """Add missing sovereign_lineage column to the database."""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'product_database.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if sovereign_lineage column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'sovereign_lineage' not in columns:
            print("Adding sovereign_lineage column...")
            cursor.execute("ALTER TABLE products ADD COLUMN sovereign_lineage TEXT")
            conn.commit()
            print("✅ sovereign_lineage column added successfully")
        else:
            print("✅ sovereign_lineage column already exists")
        
        # Check if other missing columns exist
        missing_columns = []
        required_columns = [
            'strain_name',
            'lineage',
            'sovereign_lineage',
            'thc_content',
            'cbd_content'
        ]
        
        for column in required_columns:
            if column not in columns:
                missing_columns.append(column)
        
        if missing_columns:
            print(f"Adding missing columns: {missing_columns}")
            for column in missing_columns:
                cursor.execute(f"ALTER TABLE products ADD COLUMN {column} TEXT")
            conn.commit()
            print("✅ All missing columns added")
        else:
            print("✅ All required columns exist")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing database columns...")
    success = fix_database_columns()
    if success:
        print("🎉 Database fix completed successfully!")
    else:
        print("❌ Database fix failed!") 