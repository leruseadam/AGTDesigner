#!/usr/bin/env python3
"""
Simple script to update the database with price and weight data from Excel.
"""

import pandas as pd
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_database():
    """Update the database with data from the Excel file."""
    
    # Load the Excel file
    excel_file = "uploads/A Greener Today - Bothell_inventory_08-29-2025  8_38 PM.xlsx"
    logger.info(f"Loading Excel file: {excel_file}")
    
    try:
        df = pd.read_excel(excel_file)
        logger.info(f"Loaded Excel file with {len(df)} rows and {len(df.columns)} columns")
    except Exception as e:
        logger.error(f"Error loading Excel file: {e}")
        return False
    
    # Connect to the database
    db_file = "uploads/product_database.db"
    logger.info(f"Connecting to database: {db_file}")
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return False
    
    try:
        # Get the current product count
        cursor.execute("SELECT COUNT(*) FROM products")
        current_count = cursor.fetchone()[0]
        logger.info(f"Current database has {current_count} products")
        
        # Remove duplicates from Excel data (keep first occurrence)
        df_unique = df.drop_duplicates(subset=['Product Name*'], keep='first')
        logger.info(f"Removed duplicates, now processing {len(df_unique)} unique products")
        
        # Update products with data from Excel
        updated_count = 0
        
        for index, row in df_unique.iterrows():
            product_name = row.get('Product Name*', '')
            if not product_name or pd.isna(product_name):
                continue
                
            # Get the data we want to update
            price = row.get('Price* (Tier Name for Bulk)', '')
            weight = row.get('Weight*', '')
            weight_unit = row.get('Weight Unit* (grams/gm or ounces/oz)', '')
            product_type = row.get('Product Type*', '')
            product_brand = row.get('Product Brand', '')
            vendor = row.get('Vendor/Supplier*', '')
            description = row.get('Description', '')
            lineage = row.get('Lineage', '')
            product_strain = row.get('Product Strain', '')
            
            # Skip if no meaningful data
            if pd.isna(price) and pd.isna(weight) and pd.isna(weight_unit):
                continue
                
            # Update only the fields that won't cause constraint violations
            update_query = """
            UPDATE products 
            SET "Price* (Tier Name for Bulk)" = ?,
                "Weight*" = ?,
                "Weight Unit* (grams/gm or ounces/oz)" = ?,
                "Description" = ?,
                "Lineage" = ?,
                "Product Strain" = ?
            WHERE "Product Name*" = ?
            """
            
            values = [
                str(price) if pd.notna(price) else None,
                str(weight) if pd.notna(weight) else None,
                str(weight_unit) if pd.notna(weight_unit) else None,
                str(description) if pd.notna(description) else None,
                str(lineage) if pd.notna(lineage) else None,
                str(product_strain) if pd.notna(product_strain) else None,
                product_name
            ]
            
            cursor.execute(update_query, values)
            updated_count += 1
            
            if updated_count % 100 == 0:
                logger.info(f"Updated {updated_count} products...")
        
        # Commit the changes
        conn.commit()
        logger.info(f"Successfully updated {updated_count} products in the database")
        
        # Verify the update
        cursor.execute('SELECT COUNT(*) FROM products WHERE "Price* (Tier Name for Bulk)" IS NOT NULL AND "Price* (Tier Name for Bulk)" != "None" AND "Price* (Tier Name for Bulk)" != ""')
        products_with_price = cursor.fetchone()[0]
        logger.info(f"Products with price data after update: {products_with_price}")
        
        # Show sample updated data
        cursor.execute('SELECT "Product Name*", "Price* (Tier Name for Bulk)", "Weight*", "Weight Unit* (grams/gm or ounces/oz)" FROM products WHERE "Price* (Tier Name for Bulk)" IS NOT NULL AND "Price* (Tier Name for Bulk)" != "None" AND "Price* (Tier Name for Bulk)" != "" LIMIT 5')
        samples = cursor.fetchall()
        logger.info("Sample updated products:")
        for sample in samples:
            logger.info(f"  {sample[0]} | {sample[1]} | {sample[2]} | {sample[3]}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = update_database()
    if success:
        print("✅ Database updated successfully!")
    else:
        print("❌ Failed to update database")
