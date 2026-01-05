#!/usr/bin/env python3
"""
Diagnose why Excel products aren't automatically syncing to AGT_Bothell database.

This script checks:
1. Database status and product count
2. Recent Excel files that should have synced
3. Whether automatic sync is working
4. Provides option to manually trigger sync
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
    
    # Get products by source
    cursor.execute('SELECT "Source", COUNT(*) FROM products GROUP BY "Source"')
    source_counts = dict(cursor.fetchall())
    
    # Get most recent products
    cursor.execute('SELECT MAX(last_seen_date) FROM products')
    most_recent = cursor.fetchone()[0]
    
    # Get products added today
    cursor.execute('SELECT COUNT(*) FROM products WHERE date(last_seen_date) = date("now")')
    today_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'db_path': db_path,
        'integrity': integrity,
        'product_count': product_count,
        'source_counts': source_counts,
        'most_recent': most_recent,
        'today_count': today_count
    }


def find_recent_excel_files(uploads_dir='uploads', days=7):
    """Find Excel files modified in the last N days."""
    uploads_path = Path(uploads_dir)
    if not uploads_path.exists():
        return []
    
    excel_files = []
    cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
    
    for ext in ['*.xlsx', '*.xls']:
        for file_path in uploads_path.glob(ext):
            if file_path.stat().st_mtime > cutoff_time:
                excel_files.append(file_path)
    
    # Sort by modification time (newest first)
    excel_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    return excel_files


def check_excel_file_products(excel_file_path):
    """Check how many products are in an Excel file."""
    try:
        df = pd.read_excel(excel_file_path)
        return len(df)
    except Exception as e:
        logger.error(f"Error reading {excel_file_path}: {e}")
        return 0


def test_database_sync(excel_file_path, store_name='AGT_Bothell'):
    """Test if we can sync products from an Excel file."""
    logger.info(f"Testing sync with: {excel_file_path}")
    
    try:
        # Load Excel file
        df = pd.read_excel(excel_file_path)
        logger.info(f"Loaded {len(df)} rows from Excel")
        
        if df.empty:
            logger.warning("Excel file is empty")
            return False
        
        # Get product database
        product_db = get_product_database(store_name)
        
        # Check if store_excel_data method exists
        if not hasattr(product_db, 'store_excel_data'):
            logger.error("ProductDatabase does not have store_excel_data method!")
            return False
        
        # Ensure database is initialized
        if not product_db._initialized:
            logger.info("Initializing database...")
            product_db.init_database()
        
        # Try to store (this is what should happen automatically)
        logger.info(f"Attempting to store {len(df)} products...")
        result = product_db.store_excel_data(df, str(excel_file_path))
        
        logger.info(f"Sync result: {result}")
        return True
        
    except Exception as e:
        logger.error(f"Error testing sync: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """Main diagnostic function."""
    store_name = 'AGT_Bothell'
    
    print("=" * 70)
    print("AGT_Bothell Database Sync Diagnostic")
    print("=" * 70)
    print()
    
    # Check database status
    print("📊 Checking database status...")
    status = check_database_status(store_name)
    
    if not status:
        print("❌ Cannot access database. Exiting.")
        return 1
    
    print(f"✅ Database: {status['db_path']}")
    print(f"   Integrity: {status['integrity']}")
    print(f"   Total Products: {status['product_count']:,}")
    print(f"   Products added today: {status['today_count']:,}")
    print(f"   Most recent product: {status['most_recent']}")
    print()
    
    if status['source_counts']:
        print("   Products by source:")
        for source, count in status['source_counts'].items():
            print(f"     - {source or 'Unknown'}: {count:,}")
    print()
    
    # Find recent Excel files
    print("🔍 Checking for recent Excel files...")
    recent_files = find_recent_excel_files(days=7)
    
    if not recent_files:
        print("   ⚠️  No Excel files found in uploads directory (last 7 days)")
    else:
        print(f"   ✅ Found {len(recent_files)} Excel file(s) modified in last 7 days:")
        for i, excel_file in enumerate(recent_files[:5], 1):
            size_mb = excel_file.stat().st_size / (1024 * 1024)
            mod_time = datetime.fromtimestamp(excel_file.stat().st_mtime)
            product_count = check_excel_file_products(excel_file)
            print(f"     {i}. {excel_file.name}")
            print(f"        Size: {size_mb:.2f} MB, Modified: {mod_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"        Products in file: {product_count:,}")
        if len(recent_files) > 5:
            print(f"     ... and {len(recent_files) - 5} more")
    print()
    
    # Check if sync is working
    print("🔧 Testing database sync capability...")
    product_db = get_product_database(store_name)
    
    if not hasattr(product_db, 'store_excel_data'):
        print("   ❌ ProductDatabase missing store_excel_data method!")
        print("   This means automatic sync cannot work.")
        return 1
    else:
        print("   ✅ ProductDatabase has store_excel_data method")
    
    if not product_db._initialized:
        print("   ⚠️  Database not initialized, initializing now...")
        product_db.init_database()
    else:
        print("   ✅ Database is initialized")
    print()
    
    # Offer to test sync
    if recent_files:
        print("💡 Diagnostic complete!")
        print()
        print("Possible issues:")
        print("  1. Background sync thread might be failing silently")
        print("  2. Errors might be caught and logged as warnings")
        print("  3. Sync might be disabled for performance (PC optimization)")
        print()
        response = input(f"Test sync with most recent Excel file? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            test_file = recent_files[0]
            print()
            print(f"🔄 Testing sync with: {test_file.name}")
            success = test_database_sync(test_file, store_name)
            
            if success:
                print()
                print("✅ Sync test completed!")
                print("   Check the results above to see if products were stored.")
                
                # Check updated status
                new_status = check_database_status(store_name)
                if new_status:
                    print()
                    print(f"   Products before: {status['product_count']:,}")
                    print(f"   Products after:  {new_status['product_count']:,}")
                    print(f"   Difference:      {new_status['product_count'] - status['product_count']:,}")
            else:
                print()
                print("❌ Sync test failed!")
                print("   Check the error messages above for details.")
        else:
            print("Skipping sync test.")
    else:
        print("💡 No recent Excel files to test with.")
        print()
        print("To diagnose further:")
        print("  1. Check application logs for '[BACKGROUND] Database storage' messages")
        print("  2. Look for warnings about database storage failures")
        print("  3. Upload a new Excel file and watch the logs")
    
    print()
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
