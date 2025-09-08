#!/usr/bin/env python3
"""
Populate the product database with data from the Excel file.
This will update the existing database with the correct product information.
"""

import pandas as pd
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_database():
    """Populate the database with data from the Excel file."""
    
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
        
        # Update products with data from Excel
        updated_count = 0
        
        for index, row in df.iterrows():
            product_name = row.get('Product Name*', '')
            if not product_name or pd.isna(product_name):
                continue
                
            # Prepare the update data
            update_data = {}
            
            # Map Excel columns to database columns
            column_mapping = {
                'Price* (Tier Name for Bulk)': 'Price* (Tier Name for Bulk)',
                'Weight*': 'Weight*',
                'Weight Unit* (grams/gm or ounces/oz)': 'Weight Unit* (grams/gm or ounces/oz)',
                'Product Type*': 'Product Type*',
                'Product Brand': 'Product Brand',
                'Product Strain': 'Product Strain',
                'Lineage': 'Lineage',
                'Vendor/Supplier*': 'Vendor/Supplier*',
                'Description': 'Description',
                'Quantity*': 'Quantity*',
                'Concentrate Type': 'Concentrate Type',
                'THC test result': 'THC test result',
                'CBD test result': 'CBD test result',
                'Test result unit (% or mg)': 'Test result unit (% or mg)',
                'State': 'State',
                'Is Sample? (yes/no)': 'Is Sample? (yes/no)',
                'Is MJ product?(yes/no)': 'Is MJ product?(yes/no)',
                'Discountable? (yes/no)': 'Discountable? (yes/no)',
                'Room*': 'Room*',
                'Batch Number': 'Batch Number',
                'Lot Number': 'Lot Number',
                'Barcode*': 'Barcode*',
                'Cost*': 'Cost*',
                'Medical Only (Yes/No)': 'Medical Only (Yes/No)',
                'Med Price': 'Med Price',
                'Expiration Date(YYYY-MM-DD)': 'Expiration Date(YYYY-MM-DD)',
                'Is Archived? (yes/no)': 'Is Archived? (yes/no)',
                'THC Per Serving': 'THC Per Serving',
                'Allergens': 'Allergens',
                'Solvent': 'Solvent',
                'Accepted Date': 'Accepted Date',
                'Internal Product Identifier': 'Internal Product Identifier',
                'Product Tags (comma separated)': 'Product Tags (comma separated)',
                'Image URL': 'Image URL',
                'Ingredients': 'Ingredients',
                'DOH Compliant (Yes/No)': 'DOH Compliant (Yes/No)',
                'Total THC': 'Total THC',
                'THCA': 'THCA',
                'CBDA': 'CBDA',
                'CBN': 'CBN'
            }
            
            # Build the update query
            set_clauses = []
            values = []
            
            for excel_col, db_col in column_mapping.items():
                if excel_col in df.columns:
                    value = row.get(excel_col)
                    if pd.notna(value) and value != '':
                        set_clauses.append(f'"{db_col}" = ?')
                        values.append(str(value))
            
            if set_clauses:
                # Check if product exists
                cursor.execute('SELECT COUNT(*) FROM products WHERE "Product Name*" = ?', (product_name,))
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    # Update existing product
                    update_query = f"""
                    UPDATE products 
                    SET {', '.join(set_clauses)}
                    WHERE "Product Name*" = ?
                    """
                    values.append(product_name)
                    cursor.execute(update_query, values)
                else:
                    # Skip inserting new products for now, just update existing ones
                    continue
                
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
    success = populate_database()
    if success:
        print("✅ Database populated successfully!")
    else:
        print("❌ Failed to populate database")
