#!/usr/bin/env python3
"""
Rebuild database to ensure 10,000+ products are loaded.
This script clears the database and reloads from Excel with ALL sheets.
"""

import sys
import os
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import logging
from src.core.data.product_database import get_product_database

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def find_excel_file():
    """Find the Excel file to use."""
    possible_dirs = [
        project_root / 'uploads',
        Path.cwd() / 'uploads',
        Path('/home/adamcordova/AGTDesigner/uploads'),
    ]
    
    for uploads_dir in possible_dirs:
        if uploads_dir.exists():
            # Look for Bothell inventory files
            for pattern in ['*Bothell*.xlsx', '*inventory*.xlsx', '*.xlsx']:
                for file in uploads_dir.glob(pattern):
                    if 'product_database' not in file.name.lower():
                        return file
    
    return None

def load_all_sheets(excel_path):
    """Load ALL sheets from Excel."""
    logger.info(f"Loading Excel file: {excel_path.name}")
    loaded_excel = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')
    
    if isinstance(loaded_excel, dict):
        sheet_names = list(loaded_excel.keys())
        df = pd.concat(loaded_excel.values(), ignore_index=True)
        logger.info(f"✅ Loaded {len(sheet_names)} sheets: {sheet_names}")
    else:
        df = loaded_excel
        logger.info("✅ Loaded single sheet")
    
    df = df.reset_index(drop=True)
    logger.info(f"✅ Total rows: {len(df)}")
    return df

def rebuild_database():
    """Rebuild database from Excel."""
    logger.info("="*80)
    logger.info("REBUILDING DATABASE FOR 10,000+ PRODUCTS")
    logger.info("="*80)
    logger.info("")
    
    # Find Excel file
    excel_file = find_excel_file()
    if not excel_file:
        logger.error("❌ No Excel file found!")
        logger.error("Please upload your Excel file to the uploads directory first")
        return False
    
    logger.info(f"Found Excel file: {excel_file}")
    logger.info("")
    
    # Load ALL sheets
    df = load_all_sheets(excel_file)
    
    if len(df) < 10000:
        logger.warning(f"⚠️  Excel file only has {len(df)} rows")
        logger.warning("   Make sure your Excel file has all sheets with products")
    
    logger.info("")
    
    # Get database
    logger.info("Connecting to database...")
    product_db = get_product_database('AGT_Bothell')
    
    # CLEAR database first
    logger.info("Clearing existing database...")
    try:
        product_db.clear_all_data()
        logger.info("✅ Database cleared")
    except Exception as e:
        logger.warning(f"Could not clear (may be empty): {e}")
    
    logger.info("")
    
    # Import ALL data
    logger.info("Importing ALL products from Excel...")
    logger.info(f"Processing {len(df)} rows...")
    
    result = product_db.store_excel_data(df, str(excel_file))
    
    logger.info("")
    logger.info("="*80)
    logger.info("IMPORT RESULTS")
    logger.info("="*80)
    logger.info(f"Stored: {result.get('stored', 0)}")
    logger.info(f"Updated: {result.get('updated', 0)}")
    logger.info(f"Skipped duplicates: {result.get('skipped_duplicates', 0)}")
    logger.info(f"Errors: {result.get('errors', 0)}")
    logger.info("")
    
    # Verify final count
    import sqlite3
    conn = sqlite3.connect(product_db.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    final_count = cursor.fetchone()[0]
    conn.close()
    
    logger.info("="*80)
    logger.info(f"FINAL PRODUCT COUNT: {final_count}")
    logger.info("="*80)
    
    if final_count >= 10000:
        logger.info("✅ SUCCESS! Database has 10,000+ products!")
        return True
    else:
        logger.error(f"❌ FAILED! Only {final_count} products (expected 10,000+)")
        logger.error("")
        logger.error("Possible issues:")
        logger.error("  1. Excel file may only have one sheet (check if it has multiple sheets)")
        logger.error("  2. Many rows may be filtered out (blank names, missing vendor/type)")
        logger.error("  3. Excel file may not have 10,000+ rows")
        return False

if __name__ == "__main__":
    success = rebuild_database()
    sys.exit(0 if success else 1)
