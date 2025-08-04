#!/usr/bin/env python3
"""
Fix missing database columns - Final Version
"""

import sqlite3
import os

def fix_database_columns():
    """Fix missing columns in the database."""
    print("🔧 Fixing database columns...")
    
    # Database path
    db_path = "product_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current columns
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Columns to add
        columns_to_add = [
            ('sovereign_lineage', 'TEXT'),
            ('strain_name', 'TEXT'),
            ('thc_content', 'TEXT'),
            ('cbd_content', 'TEXT')
        ]
        
        # Add missing columns
        for column_name, column_type in columns_to_add:
            if column_name not in columns:
                print(f"Adding {column_name} column...")
                cursor.execute(f"ALTER TABLE products ADD COLUMN {column_name} {column_type}")
                print(f"✅ {column_name} column added successfully")
            else:
                print(f"✅ {column_name} column already exists")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("🎉 Database columns fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    fix_database_columns() 