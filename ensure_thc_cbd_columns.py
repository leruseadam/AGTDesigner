#!/usr/bin/env python3
"""
Ensure database has all necessary THC/CBD columns
"""

import sqlite3
import os

def ensure_thc_cbd_columns():
    """Ensure the database has all necessary THC/CBD columns."""
    
    db_path = "product_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current table schema
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        
        print(f"📊 Current products table has {len(existing_columns)} columns")
        
        # Define required THC/CBD columns
        required_thc_cbd_columns = [
            ("THC", "TEXT"),
            ("CBD", "TEXT"),
            ("Total THC", "TEXT"),
            ("Total CBD", "TEXT"),
            ("THCA", "TEXT"),
            ("CBDA", "TEXT"),
            ("CBN", "TEXT"),
            ("CBGA", "TEXT"),
            ("CBG", "TEXT"),
            ("Total CBG", "TEXT"),
            ("CBC", "TEXT"),
            ("CBDV", "TEXT"),
            ("THCV", "TEXT"),
            ("CBGV", "TEXT"),
            ("CBNV", "TEXT"),
            ("CBGVA", "TEXT"),
            ("THC test result", "TEXT"),
            ("CBD test result", "TEXT"),
            ("Test result unit (% or mg)", "TEXT"),
            ("Ratio", "TEXT"),
            ("Ratio_or_THC_CBD", "TEXT"),
            ("JointRatio", "TEXT")
        ]
        
        added_columns = []
        
        for column_name, column_type in required_thc_cbd_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE products ADD COLUMN "{column_name}" {column_type}')
                    added_columns.append(column_name)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"❌ Error adding column {column_name}: {e}")
            else:
                print(f"✓ Column already exists: {column_name}")
        
        if added_columns:
            conn.commit()
            print(f"\n🎉 Added {len(added_columns)} new columns to the products table")
        else:
            print("\n✅ All required THC/CBD columns already exist")
        
        # Show final column count
        cursor.execute("PRAGMA table_info(products)")
        final_columns = cursor.fetchall()
        print(f"\n📊 Final products table has {len(final_columns)} columns")
        
        # Show THC/CBD related columns
        thc_cbd_columns = [col for col in final_columns if any(keyword in col[1].upper() for keyword in ['THC', 'CBD', 'RATIO'])]
        print(f"\n📋 THC/CBD related columns ({len(thc_cbd_columns)}):")
        for col in thc_cbd_columns:
            print(f"   {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error ensuring columns: {e}")

if __name__ == "__main__":
    ensure_thc_cbd_columns()
