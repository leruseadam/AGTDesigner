#!/usr/bin/env python3
"""
Quick fix script to ensure Excel products are synced to AGT_Bothell database.

This script:
1. Finds the most recent Excel file for Bothell
2. Forces a sync to the database
3. Reports results
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import get_product_database, get_database_path
from src.core.data.excel_processor import ExcelProcessor
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def find_latest_bothell_excel():
    """Find the most recent Bothell Excel file."""
    uploads_dir = Path('uploads')
    if not uploads_dir.exists():
        return None
    
    excel_files = []
    for ext in ['*.xlsx', '*.xls']:
        excel_files.extend(uploads_dir.glob(ext))
    
    # Filter for Bothell files and sort by modification time
    bothell_files = [f for f in excel_files if 'bothell' in f.name.lower()]
    if not bothell_files:
        # If no Bothell-specific files, use any recent file
        excel_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return excel_files[0] if excel_files else None
    
    bothell_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return bothell_files[0]


def sync_excel_to_database(excel_file, store_name='AGT_Bothell'):
    """Sync Excel file to database."""
    logger.info(f"Loading Excel file: {excel_file.name}")
    
    try:
        df = pd.read_excel(excel_file)
        logger.info(f"Loaded {len(df)} rows from Excel")
        
        if df.empty:
            logger.warning("Excel file is empty!")
            return False
        
        # Get product database
        product_db = get_product_database(store_name)
        
        # Ensure initialized
        if not product_db._initialized:
            product_db.init_database()
        
        # Sync to database
        logger.info(f"Syncing {len(df)} products to database...")
        result = product_db.store_excel_data(df, str(excel_file))
        
        stored = result.get('stored', 0)
        updated = result.get('updated', 0)
        errors = result.get('errors', 0)
        
        logger.info(f"✅ Sync complete!")
        logger.info(f"   Stored: {stored}")
        logger.info(f"   Updated: {updated}")
        logger.info(f"   Errors: {errors}")
        
        return errors == 0
        
    except Exception as e:
        logger.error(f"Error syncing: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    print("=" * 60)
    print("AGT_Bothell Database Sync Fix")
    print("=" * 60)
    print()
    
    # Check database
    db_path = get_database_path('AGT_Bothell')
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return 1
    
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM products')
    before_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"📊 Current database: {before_count:,} products")
    print()
    
    # Find Excel file
    excel_file = find_latest_bothell_excel()
    if not excel_file:
        print("❌ No Excel files found in uploads directory")
        return 1
    
    print(f"📄 Found Excel file: {excel_file.name}")
    print(f"   Modified: {datetime.fromtimestamp(excel_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # Sync
    print("🔄 Syncing Excel products to database...")
    print()
    success = sync_excel_to_database(excel_file)
    print()
    
    # Check final count
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM products')
    after_count = cursor.fetchone()[0]
    conn.close()
    
    print("=" * 60)
    print("Results:")
    print(f"  Before: {before_count:,} products")
    print(f"  After:  {after_count:,} products")
    print(f"  Change: {after_count - before_count:,} products")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
