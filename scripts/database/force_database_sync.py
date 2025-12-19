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

# Add project root to path so we can import app
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

def find_latest_excel():
    """Find the most recent Excel upload."""
    # Try multiple possible locations
    possible_dirs = [
        project_root / 'uploads',  # Standard location
        Path.cwd() / 'uploads',     # Current working directory
        Path.home() / 'AGTDesigner' / 'uploads',  # Home directory
        Path('/home/adamcordova/AGTDesigner/uploads'),  # PythonAnywhere
    ]
    
    uploads_dir = None
    for dir_path in possible_dirs:
        if dir_path.exists():
            uploads_dir = dir_path
            logger.info(f"Found uploads directory: {uploads_dir}")
            break
    
    if not uploads_dir:
        logger.error("Could not find uploads directory in any of these locations:")
        for dir_path in possible_dirs:
            logger.error(f"  - {dir_path}")
        logger.error("\nPlease specify the file path manually:")
        logger.error("  python scripts/database/force_database_sync.py file <path/to/file.xlsx>")
        return None
    
    # Find all Excel files (excluding the product_database folder)
    excel_files = []
    for file in uploads_dir.glob('*.xlsx'):
        if 'product_database' not in file.name.lower():
            excel_files.append(file)
    
    # Also check for files with spaces in name (common pattern)
    for pattern in ['**/*.xlsx', '**/*Bothell*.xlsx', '**/*inventory*.xlsx']:
        for file in uploads_dir.glob(pattern):
            if 'product_database' not in file.name.lower() and file not in excel_files:
                excel_files.append(file)
    
    if not excel_files:
        logger.error(f"No Excel files found in uploads directory: {uploads_dir}")
        logger.info(f"Directory contents: {list(uploads_dir.iterdir())[:10] if uploads_dir.exists() else 'N/A'}")
        logger.info("\nOptions:")
        logger.info("  1. Upload your Excel file through the web interface first")
        logger.info("  2. Copy your Excel file to: " + str(uploads_dir))
        logger.info("  3. Use: python scripts/database/force_database_sync.py file <path/to/file.xlsx>")
        return None
    
    # Sort by modification time
    excel_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest = excel_files[0]
    
    logger.info(f"Found latest Excel file: {latest.name}")
    logger.info(f"Last modified: {datetime.fromtimestamp(latest.stat().st_mtime)}")
    
    return latest

def _load_excel_all_sheets(excel_path):
    """Load every sheet in the workbook and concatenate them."""
    logger.info(f"Loading Excel file: {excel_path.name}")
    loaded_excel = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')
    if isinstance(loaded_excel, dict):
        sheet_names = list(loaded_excel.keys())
        df = pd.concat(loaded_excel.values(), ignore_index=True)
        logger.info(f"✅ Excel sheets loaded: {sheet_names}")
    else:
        df = loaded_excel
        logger.info("✅ Excel loaded from a single sheet")
    df = df.reset_index(drop=True)
    logger.info(f"  Total rows after concat: {len(df)}")
    return df

def sync_database_from_excel(excel_path):
    """Sync database from Excel file."""
    
    logger.info("="*80)
    logger.info("FORCE DATABASE SYNC FROM EXCEL")
    logger.info("="*80)
    logger.info(f"Excel file: {excel_path}")
    logger.info("")
    
    # Load Excel file
    logger.info("Loading Excel file...")
    df = _load_excel_all_sheets(excel_path)
    logger.info(f"Loaded {len(df)} rows from Excel")
    logger.info("")
    
    # Get product database for Bothell store
    from src.core.data.product_database import get_product_database
    product_db = get_product_database('AGT_Bothell')
    
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
    
    try:
        from app import get_excel_processor
        processor = get_excel_processor()
    except ImportError as e:
        logger.warning(f"  ⚠ Cannot import app module: {e}")
        logger.warning("  Run this script from the project root directory")
        logger.info("")
        return
    
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
    
    try:
        from app import get_excel_processor
        processor = get_excel_processor()
    except ImportError as e:
        logger.error(f"  ✗ Cannot import app module: {e}")
        logger.error("  Run this script from the project root directory")
        logger.info("")
        return
    
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
                logger.error(f"Current directory: {Path.cwd()}")
                logger.error(f"Try absolute path: {Path.cwd() / excel_path}")
        
        elif command == 'list':
            # List available Excel files
            logger.info("Searching for Excel files...")
            excel_file = find_latest_excel()
            if excel_file:
                logger.info(f"\n✅ Found Excel file: {excel_file}")
                logger.info(f"   Path: {excel_file.absolute()}")
                logger.info(f"   Size: {excel_file.stat().st_size / (1024*1024):.2f} MB")
                logger.info(f"   Modified: {datetime.fromtimestamp(excel_file.stat().st_mtime)}")
            else:
                # Try to show what's in uploads directories
                for dir_path in [project_root / 'uploads', Path.cwd() / 'uploads']:
                    if dir_path.exists():
                        logger.info(f"\nContents of {dir_path}:")
                        for item in sorted(dir_path.iterdir()):
                            if item.is_file():
                                logger.info(f"  📄 {item.name} ({item.stat().st_size / 1024:.1f} KB)")
                            elif item.is_dir():
                                logger.info(f"  📁 {item.name}/")
        
        else:
            print("Usage:")
            print("  python force_database_sync.py sync        # Sync from latest Excel")
            print("  python force_database_sync.py list        # List available Excel files")
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

