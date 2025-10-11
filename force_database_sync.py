#!/usr/bin/env python3
"""
Force database sync from the most recent Excel upload.
This ensures the database has the latest values from Excel files.
"""

import sys
import os
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

def find_latest_excel():
    """Find the most recent Excel upload."""
    uploads_dir = Path(__file__).parent / 'uploads'
    
    # Find all Excel files (excluding the product_database folder)
    excel_files = []
    for file in uploads_dir.glob('*.xlsx'):
        if 'product_database' not in file.name.lower():
            excel_files.append(file)
    
    if not excel_files:
        logger.error("No Excel files found in uploads directory")
        return None
    
    # Sort by modification time
    excel_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest = excel_files[0]
    
    logger.info(f"Found latest Excel file: {latest.name}")
    logger.info(f"Last modified: {datetime.fromtimestamp(latest.stat().st_mtime)}")
    
    return latest

def sync_database_from_excel(excel_path):
    """Sync database from Excel file."""
    
    logger.info("="*80)
    logger.info("FORCE DATABASE SYNC FROM EXCEL")
    logger.info("="*80)
    logger.info(f"Excel file: {excel_path}")
    logger.info("")
    
    # Load Excel file
    logger.info("Loading Excel file...")
    df = pd.read_excel(excel_path, engine='openpyxl')
    logger.info(f"Loaded {len(df)} rows from Excel")
    logger.info("")
    
    # Get product database
    from src.core.data.product_database import get_product_database
    product_db = get_product_database()
    
    logger.info("Starting database sync...")
    logger.info("")
    
    # Store Excel data in database
    result = product_db.store_excel_data(df, str(excel_path))
    
    logger.info("="*80)
    logger.info("SYNC COMPLETE")
    logger.info("="*80)
    logger.info(f"Results: {result}")
    logger.info("")
    
    # Verify by checking some Constellation Moonshots
    logger.info("Verifying Constellation Moonshots...")
    
    import sqlite3
    conn = sqlite3.connect(product_db.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT "Product Name*", "Weight*", "Units"
        FROM products
        WHERE "Product Name*" LIKE '%Moonshot%'
        AND "Product Brand" = 'Constellation Cannabis'
        ORDER BY "Product Name*"
    ''')
    
    moonshots = cursor.fetchall()
    
    for name, weight, units in moonshots:
        logger.info(f"  {name}: {weight} {units or ''}")
    
    conn.close()
    
    return result

def check_database_integration():
    """Check if database integration is enabled."""
    
    logger.info("Checking database integration status...")
    
    from app import get_excel_processor
    processor = get_excel_processor()
    
    if hasattr(processor, '_use_product_database'):
        status = processor._use_product_database
        logger.info(f"  Product database integration: {'ENABLED' if status else 'DISABLED'}")
        
        if not status:
            logger.warning("  ⚠ Database integration is DISABLED!")
            logger.warning("  Uploaded Excel files will NOT update the database")
            logger.info("")
            logger.info("  To enable, the app needs to call:")
            logger.info("    processor.enable_product_db_integration(True)")
    else:
        logger.warning("  ⚠ Cannot determine database integration status")
    
    logger.info("")

def enable_database_integration():
    """Enable database integration for Excel uploads."""
    
    logger.info("Enabling database integration...")
    
    from app import get_excel_processor
    processor = get_excel_processor()
    
    if hasattr(processor, 'enable_product_db_integration'):
        processor.enable_product_db_integration(True)
        logger.info("  ✓ Database integration ENABLED")
        logger.info("  Future Excel uploads will automatically update the database")
    else:
        logger.error("  ✗ enable_product_db_integration method not found")
    
    logger.info("")

if __name__ == "__main__":
    print("")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'sync':
            # Force sync from latest Excel
            excel_file = find_latest_excel()
            if excel_file:
                sync_database_from_excel(excel_file)
        
        elif command == 'check':
            # Check database integration status
            check_database_integration()
        
        elif command == 'enable':
            # Enable database integration
            enable_database_integration()
            check_database_integration()
        
        elif command == 'file' and len(sys.argv) > 2:
            # Sync from specific file
            excel_path = Path(sys.argv[2])
            if excel_path.exists():
                sync_database_from_excel(excel_path)
            else:
                logger.error(f"File not found: {excel_path}")
        
        else:
            print("Usage:")
            print("  python force_database_sync.py sync        # Sync from latest Excel")
            print("  python force_database_sync.py check       # Check integration status")
            print("  python force_database_sync.py enable      # Enable database integration")
            print("  python force_database_sync.py file <path> # Sync from specific file")
    else:
        # Default: check status then sync
        check_database_integration()
        
        excel_file = find_latest_excel()
        if excel_file:
            response = input(f"\nSync database from {excel_file.name}? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                sync_database_from_excel(excel_file)
        
        print("\n" + "="*80)
        print("TIP: Run 'python fix_database_weights.py' to normalize weights")
        print("="*80)

