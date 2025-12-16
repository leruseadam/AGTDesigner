#!/usr/bin/env python3
"""
Script to add missing 'DOH Compliant (Yes/No)' column to PythonAnywhere PostgreSQL database.
Run this on PythonAnywhere after deployment.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database_postgresql_complete import ProductDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_doh_column():
    """Add the missing DOH column to the PostgreSQL database."""
    try:
        # Initialize the database connection
        db = ProductDatabase()
        conn = db._get_connection()
        
        if not conn:
            logger.error("Failed to get database connection")
            return False
        
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products' AND column_name = 'DOH Compliant (Yes/No)'
        """)
        
        exists = cursor.fetchone()
        
        if exists:
            logger.info("Column 'DOH Compliant (Yes/No)' already exists")
            return True
        
        # Add the column
        logger.info("Adding column 'DOH Compliant (Yes/No)' to products table...")
        cursor.execute('ALTER TABLE products ADD COLUMN "DOH Compliant (Yes/No)" TEXT')
        conn.commit()
        
        logger.info("Successfully added 'DOH Compliant (Yes/No)' column to products table")
        return True
        
    except Exception as e:
        logger.error(f"Error adding DOH column: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Fixing PythonAnywhere PostgreSQL Database Schema")
    print("=" * 60)
    
    success = fix_doh_column()
    
    if success:
        print("\n✅ Database schema fixed successfully!")
        print("You can now deploy and use the DOH functionality.")
    else:
        print("\n❌ Failed to fix database schema.")
        print("Please check the error messages above.")
    
    print("=" * 60)

