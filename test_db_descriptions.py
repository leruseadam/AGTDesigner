#!/usr/bin/env python3
"""
Test script to check what's actually in the database Description column
"""

import sqlite3
import os

def test_database_descriptions():
    """Check what's in the database Description column"""
    
    # Find the database file
    db_paths = [
        'uploads/product_database.db',
        'uploads/product_database_AGT_Bothell.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"\n🔍 Checking database: {db_path}")
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get table info
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"Tables: {[t[0] for t in tables]}")
                
                # Check products table
                if any('product' in t[0].lower() for t in tables):
                    table_name = next(t[0] for t in tables if 'product' in t[0].lower())
                    print(f"Using table: {table_name}")
                    
                    # Get column info
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    print(f"Columns: {[c[1] for c in columns]}")
                    
                    # Look for Description column
                    desc_columns = [c[1] for c in columns if 'description' in c[1].lower()]
                    print(f"Description-like columns: {desc_columns}")
                    
                    # Sample some data
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                    rows = cursor.fetchall()
                    
                    if rows:
                        print(f"\nSample data (first 5 rows):")
                        for i, row in enumerate(rows):
                            print(f"Row {i+1}: {row}")
                    
                    # Look for BALL_SAT_CARAMEL specifically
                    cursor.execute(f"SELECT * FROM {table_name} WHERE \"Product Name*\" LIKE '%BALL_SAT_CARAMEL%' OR \"Description\" LIKE '%BALL_SAT_CARAMEL%' OR \"Product Name*\" LIKE '%caramel%' OR \"Description\" LIKE '%caramel%' LIMIT 3;")
                    caramel_rows = cursor.fetchall()
                    
                    if caramel_rows:
                        print(f"\n🍯 Caramel-related products:")
                        for i, row in enumerate(caramel_rows):
                            print(f"Caramel Row {i+1}: {row}")
                    else:
                        print(f"\n❌ No caramel products found")
                        
                        # Try broader search
                        cursor.execute(f"SELECT \"Product Name*\", \"Description\" FROM {table_name} WHERE \"Product Name*\" LIKE '%BALL%' OR \"Description\" LIKE '%ball%' LIMIT 5;")
                        ball_rows = cursor.fetchall()
                        
                        if ball_rows:
                            print(f"\n⚽ Ball-related products:")
                            for i, row in enumerate(ball_rows):
                                print(f"Ball Row {i+1}: Product Name*='{row[0]}', Description='{row[1]}'")
                
                conn.close()
                
            except Exception as e:
                print(f"Error checking {db_path}: {e}")
        else:
            print(f"❌ Database not found: {db_path}")

if __name__ == "__main__":
    test_database_descriptions()
