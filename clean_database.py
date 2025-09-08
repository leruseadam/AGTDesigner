#!/usr/bin/env python3
"""
Clean up the product database by removing extra columns and keeping only essential product data.
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def clean_database():
    """Clean up the database by removing unnecessary columns."""
    
    # Connect to the database
    conn = sqlite3.connect('uploads/product_database.db')
    cursor = conn.cursor()
    
    # Get current table info
    cursor.execute('PRAGMA table_info(products)')
    columns = cursor.fetchall()
    logger.info(f"Current database has {len(columns)} columns")
    
    # Define the essential columns we want to keep
    essential_columns = [
        'id',
        'Product Name*',
        'Product Type*',
        'Product Brand',
        'Vendor/Supplier*',
        'Description',
        'Weight*',
        'Weight Unit* (grams/gm or ounces/oz)',
        'Price* (Tier Name for Bulk)',
        'Product Strain',
        'Lineage',
        'Quantity*',
        'DOH Compliant (Yes/No)',
        'DOH',
        'Concentrate Type',
        'Ratio',
        'JointRatio',
        'THC test result',
        'CBD test result',
        'Test result unit (% or mg)',
        'State',
        'Is Sample? (yes/no)',
        'Is MJ product?(yes/no)',
        'Discountable? (yes/no)',
        'Room*',
        'Batch Number',
        'Lot Number',
        'Barcode*',
        'Cost*',
        'Medical Only (Yes/No)',
        'Med Price',
        'Expiration Date(YYYY-MM-DD)',
        'Is Archived? (yes/no)',
        'THC Per Serving',
        'Allergens',
        'Solvent',
        'Accepted Date',
        'Internal Product Identifier',
        'Product Tags (comma separated)',
        'Image URL',
        'Ingredients',
        'CombinedWeight',
        'Ratio_or_THC_CBD',
        'Description_Complexity',
        'Total THC',
        'THCA',
        'CBDA',
        'CBN'
    ]
    
    # Get current column names
    current_columns = [col[1] for col in columns]
    
    # Find columns to remove (all columns not in essential_columns)
    columns_to_remove = [col for col in current_columns if col not in essential_columns]
    
    logger.info(f"Will remove {len(columns_to_remove)} columns")
    logger.info(f"Will keep {len(essential_columns)} essential columns")
    
    if not columns_to_remove:
        logger.info("No columns to remove - database is already clean")
        return
    
    # Create a new table with only essential columns
    logger.info("Creating new clean products table...")
    
    # First, get sample data to determine column types
    cursor.execute(f"SELECT * FROM products LIMIT 1")
    sample_row = cursor.fetchone()
    
    # Build CREATE TABLE statement
    create_columns = []
    for col_name in essential_columns:
        if col_name in current_columns:
            # Find the column type from the original table
            col_info = next((col for col in columns if col[1] == col_name), None)
            if col_info:
                create_columns.append(f'"{col_name}" {col_info[2]}')
    
    create_sql = f"""
    CREATE TABLE products_clean (
        {', '.join(create_columns)}
    )
    """
    
    cursor.execute(create_sql)
    
    # Copy data from old table to new table
    logger.info("Copying data to clean table...")
    
    # Build INSERT statement
    select_columns = [f'"{col}"' for col in essential_columns if col in current_columns]
    insert_sql = f"""
    INSERT INTO products_clean ({', '.join(select_columns)})
    SELECT {', '.join(select_columns)} FROM products
    """
    
    cursor.execute(insert_sql)
    
    # Drop old table and rename new table
    logger.info("Replacing old table with clean table...")
    cursor.execute("DROP TABLE products")
    cursor.execute("ALTER TABLE products_clean RENAME TO products")
    
    # Commit changes
    conn.commit()
    
    # Verify the cleanup
    cursor.execute('PRAGMA table_info(products)')
    new_columns = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    
    logger.info(f"Cleanup complete!")
    logger.info(f"New database has {len(new_columns)} columns")
    logger.info(f"Products: {count} records")
    
    # Show sample data
    cursor.execute('SELECT "Product Name*", "Product Type*", "Vendor/Supplier*", "Price* (Tier Name for Bulk)" FROM products LIMIT 3')
    samples = cursor.fetchall()
    logger.info("Sample products:")
    for sample in samples:
        logger.info(f"  {sample[0]} | {sample[1]} | {sample[2]} | {sample[3]}")
    
    conn.close()
    logger.info("✅ Database cleaned successfully!")

if __name__ == "__main__":
    clean_database()
