#!/usr/bin/env python3
"""
Check the database schema for Gravity Gummies products.
"""

import sqlite3
from pathlib import Path

def check_schema(db_path: str = 'uploads/product_database_AGT_Bothell.db'):
    """Check the database schema."""
    
    if not Path(db_path).exists():
        print(f"Database not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        
        print("Database schema:")
        print("-" * 50)
        for col in columns:
            print(f"{col[1]} ({col[2]})")
        
        print("\n" + "="*50)
        print("Sample Gravity Gummies data:")
        print("="*50)
        
        # Get sample data
        cursor.execute('''
            SELECT * FROM products 
            WHERE "Product Brand" LIKE '%Gravity%'
            LIMIT 3
        ''')
        
        sample_data = cursor.fetchall()
        
        if sample_data:
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            for i, row in enumerate(sample_data):
                print(f"\nProduct {i+1}:")
                for j, value in enumerate(row):
                    if value is not None and str(value).strip():
                        print(f"  {column_names[j]}: {value}")
        else:
            print("No Gravity Gummies products found.")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_schema()
