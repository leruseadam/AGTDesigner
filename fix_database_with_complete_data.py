#!/usr/bin/env python3
"""
Fix the database by importing complete data from AGT_Essential_Product_Database_20250822_022042.xlsx
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import sqlite3
from src.core.data.product_database import get_product_database

def fix_database():
    """Import complete data to fix missing Price, DOH, Ratio, and Weight Units."""
    print("Fixing database with complete data...")
    
    # Read the Excel file with complete data
    excel_file = "AGT_Essential_Product_Database_20250822_022042.xlsx"
    print(f"Reading {excel_file}...")
    
    try:
        df = pd.read_excel(excel_file)
        print(f"✓ Loaded {len(df)} products from Excel")
    except Exception as e:
        print(f"✗ Error reading Excel file: {e}")
        return False
    
    # Get the database
    try:
        product_db = get_product_database()
        print("✓ Database loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load database: {e}")
        return False
    
    # Get database connection
    conn = product_db._get_connection()
    cursor = conn.cursor()
    
    updated_count = 0
    
    for index, row in df.iterrows():
        product_name = row.get('Product Name*', '')
        if not product_name or pd.isna(product_name):
            continue
            
        # Check if product exists in database
        cursor.execute('SELECT id FROM products WHERE "Product Name*" = ?', (product_name,))
        if not cursor.fetchone():
            continue
            
        # Prepare update data
        update_data = {}
        
        # Price
        price = row.get('Price*')
        if pd.notna(price) and str(price).strip() and str(price) != 'nan':
            update_data['Price'] = str(price)
            
        # DOH
        doh = row.get('DOH Compliant*')
        if pd.notna(doh) and str(doh).strip() and str(doh) != 'nan':
            update_data['DOH'] = str(doh)
            
        # Ratio
        ratio = row.get('Ratio')
        if pd.notna(ratio) and str(ratio).strip() and str(ratio) != 'nan':
            update_data['Ratio'] = str(ratio)
            
        # Weight Unit
        weight_unit = row.get('Weight Unit*')
        if pd.notna(weight_unit) and str(weight_unit).strip() and str(weight_unit) != 'nan':
            update_data['Weight Unit* (grams/gm or ounces/oz)'] = str(weight_unit)
        
        if update_data:
            try:
                # Update the product in database
                set_clauses = []
                params = []
                for key, value in update_data.items():
                    set_clauses.append(f'"{key}" = ?')
                    params.append(value)
                
                params.append(product_name)
                
                cursor.execute(f'''
                    UPDATE products 
                    SET {', '.join(set_clauses)}
                    WHERE "Product Name*" = ?
                ''', params)
                
                updated_count += 1
                
                if updated_count % 10 == 0:
                    print(f"Updated {updated_count} products...")
                    
            except Exception as e:
                print(f"Error updating {product_name}: {e}")
                continue
    
    conn.commit()
    print(f"✓ Updated {updated_count} products with complete data")
    
    # Verify the fix
    cursor.execute('''
        SELECT COUNT(*) as total, 
               COUNT(CASE WHEN "Price" IS NOT NULL AND "Price" != '' THEN 1 END) as with_price,
               COUNT(CASE WHEN "DOH" IS NOT NULL AND "DOH" != '' THEN 1 END) as with_doh,
               COUNT(CASE WHEN "Ratio" IS NOT NULL AND "Ratio" != '' THEN 1 END) as with_ratio
        FROM products
    ''')
    
    result = cursor.fetchone()
    print(f"Database status after fix:")
    print(f"  Total products: {result[0]}")
    print(f"  With Price: {result[1]}")
    print(f"  With DOH: {result[2]}")
    print(f"  With Ratio: {result[3]}")
    
    return True

if __name__ == "__main__":
    fix_database()
