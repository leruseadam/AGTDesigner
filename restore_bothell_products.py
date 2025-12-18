#!/usr/bin/env python3
"""
Restore missing products to AGT_Bothell database from Excel files.

This script:
1. Checks current product count in Bothell database
2. Finds Excel files in uploads directory
3. Re-syncs products from Excel files to the database
"""

import sys
import os
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import get_product_database, get_database_path
from src.core.data.excel_processor import ExcelProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_database_status(store_name='AGT_Bothell'):
    """Check current status of the database."""
    db_path = get_database_path(store_name)
    
    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}")
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check integrity
    cursor.execute('PRAGMA integrity_check')
    integrity = cursor.fetchone()[0]
    
    # Get product count
    cursor.execute('SELECT COUNT(*) FROM products')
    product_count = cursor.fetchone()[0]
    
    # Get vendor count
    cursor.execute('SELECT COUNT(DISTINCT "Vendor/Supplier*") FROM products WHERE "Vendor/Supplier*" IS NOT NULL AND "Vendor/Supplier*" != ""')
    vendor_count = cursor.fetchone()[0]
    
    # Get recent products
    cursor.execute('SELECT COUNT(*) FROM products WHERE last_seen_date >= date("now", "-30 days")')
    recent_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'db_path': db_path,
        'integrity': integrity,
        'product_count': product_count,
        'vendor_count': vendor_count,
        'recent_count': recent_count
    }


def find_excel_files(uploads_dir='uploads'):
    """Find Excel files in uploads directory."""
    uploads_path = Path(uploads_dir)
    if not uploads_path.exists():
        logger.warning(f"Uploads directory not found: {uploads_dir}")
        return []
    
    # Find Excel files, prioritizing Bothell files
    excel_files = []
    for ext in ['*.xlsx', '*.xls']:
        excel_files.extend(uploads_path.glob(ext))
    
    # Sort by modification time (newest first) and prioritize Bothell files
    excel_files.sort(key=lambda p: (p.name.lower().find('bothell') == -1, p.stat().st_mtime), reverse=True)
    
    return excel_files


def restore_products_from_excel(excel_file_path, store_name='AGT_Bothell'):
    """Restore products from an Excel file to the database."""
    logger.info(f"Processing Excel file: {excel_file_path}")
    
    try:
        # Load Excel file
        logger.info(f"Loading Excel file: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        logger.info(f"Loaded {len(df)} rows from Excel file")
        
        if df.empty:
            logger.warning("Excel file is empty")
            return {'stored': 0, 'updated': 0, 'errors': 0}
        
        # Get product database
        product_db = get_product_database(store_name)
        
        # Ensure database is initialized
        if not product_db._initialized:
            product_db.init_database()
        
        # Store Excel data in database
        logger.info(f"Syncing {len(df)} products to database...")
        result = product_db.store_excel_data(df, str(excel_file_path))
        
        logger.info(f"Sync complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error restoring products from {excel_file_path}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {'stored': 0, 'updated': 0, 'errors': 1, 'error': str(e)}


def main():
    """Main restoration function."""
    store_name = 'AGT_Bothell'
    
    print("=" * 70)
    print("AGT_Bothell Product Database Restoration")
    print("=" * 70)
    print()
    
    # Check current database status
    print("📊 Checking current database status...")
    status = check_database_status(store_name)
    
    if not status:
        print("❌ Cannot access database. Exiting.")
        return 1
    
    print(f"✅ Database: {status['db_path']}")
    print(f"   Integrity: {status['integrity']}")
    print(f"   Current Products: {status['product_count']:,}")
    print(f"   Unique Vendors: {status['vendor_count']}")
    print(f"   Products (last 30 days): {status['recent_count']:,}")
    print()
    
    # Find Excel files
    print("🔍 Searching for Excel files...")
    excel_files = find_excel_files()
    
    if not excel_files:
        print("❌ No Excel files found in uploads directory")
        return 1
    
    print(f"✅ Found {len(excel_files)} Excel file(s):")
    for i, excel_file in enumerate(excel_files[:10], 1):  # Show first 10
        size_mb = excel_file.stat().st_size / (1024 * 1024)
        mod_time = datetime.fromtimestamp(excel_file.stat().st_mtime)
        print(f"   {i}. {excel_file.name} ({size_mb:.2f} MB, modified: {mod_time.strftime('%Y-%m-%d %H:%M')})")
    if len(excel_files) > 10:
        print(f"   ... and {len(excel_files) - 10} more")
    print()
    
    # Ask for confirmation
    response = input(f"Restore products from Excel files? This will sync products to the database. (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cancelled.")
        return 0
    
    # Process Excel files
    print()
    print("🔄 Starting product restoration...")
    print()
    
    total_stored = 0
    total_updated = 0
    total_errors = 0
    
    # Process files (prioritize Bothell files)
    bothell_files = [f for f in excel_files if 'bothell' in f.name.lower()]
    other_files = [f for f in excel_files if 'bothell' not in f.name.lower()]
    
    files_to_process = bothell_files + other_files[:3]  # Process Bothell files + up to 3 others
    
    for excel_file in files_to_process:
        print(f"📄 Processing: {excel_file.name}")
        result = restore_products_from_excel(excel_file, store_name)
        
        stored = result.get('stored', 0)
        updated = result.get('updated', 0)
        errors = result.get('errors', 0)
        
        total_stored += stored
        total_updated += updated
        total_errors += errors
        
        print(f"   ✅ Stored: {stored}, Updated: {updated}, Errors: {errors}")
        print()
    
    # Check final status
    print("📊 Checking final database status...")
    final_status = check_database_status(store_name)
    
    print()
    print("=" * 70)
    print("Restoration Summary")
    print("=" * 70)
    print(f"Products before: {status['product_count']:,}")
    print(f"Products after:  {final_status['product_count']:,}")
    print(f"Difference:      {final_status['product_count'] - status['product_count']:,}")
    print()
    print(f"Total stored:    {total_stored:,}")
    print(f"Total updated:   {total_updated:,}")
    print(f"Total errors:    {total_errors}")
    print("=" * 70)
    
    return 0 if total_errors == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
