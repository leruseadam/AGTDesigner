#!/usr/bin/env python3
"""
Clear JSON Column Script
========================
This script clears all JSON column values in product databases.

Usage:
    Local:  python clear_json_column.py
    Web:    python clear_json_column.py --web
"""

import os
import sys
import sqlite3
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clear_json_column(db_path):
    """Clear all JSON column values in the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if JSON column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'JSON' not in columns:
            logger.warning(f"JSON column does not exist in {db_path}")
            conn.close()
            return 0

        # Diagnostic: Count total products
        cursor.execute('SELECT COUNT(*) FROM products')
        total_products = cursor.fetchone()[0]
        
        # Diagnostic: Count products with NULL JSON
        cursor.execute('SELECT COUNT(*) FROM products WHERE "JSON" IS NULL')
        count_null = cursor.fetchone()[0]
        
        # Count products with non-empty JSON values
        cursor.execute('SELECT COUNT(*) FROM products WHERE "JSON" IS NOT NULL AND "JSON" != ""')
        count_before = cursor.fetchone()[0]
        
        # Count empty strings
        cursor.execute('SELECT COUNT(*) FROM products WHERE "JSON" = ""')
        count_empty = cursor.fetchone()[0]
        
        # Diagnostic: Show a sample of non-empty JSON values
        cursor.execute('SELECT "Product Name*", "JSON" FROM products WHERE "JSON" IS NOT NULL AND "JSON" != "" LIMIT 3')
        samples = cursor.fetchall()
        
        db_name = Path(db_path).name if isinstance(db_path, str) else db_path.name
        logger.info(f"  Total products: {total_products}")
        logger.info(f"  JSON NULL: {count_null}, Non-empty: {count_before}, Empty strings: {count_empty}")
        if samples:
            logger.info(f"  Sample JSON values:")
            for name, json_val in samples:
                logger.info(f"    - {name[:50]}: {str(json_val)[:50]}...")
        
        total_to_clear = count_before + count_empty
        
        if total_to_clear == 0:
            logger.info(f"  No JSON values to clear (all already NULL)")
            conn.close()
            return 0

        # Clear all JSON values (both non-empty and empty strings)
        cursor.execute('UPDATE products SET "JSON" = NULL WHERE "JSON" IS NOT NULL AND "JSON" != ""')
        cleared_non_empty = cursor.rowcount
        
        # Clear empty strings
        cursor.execute('UPDATE products SET "JSON" = NULL WHERE "JSON" = ""')
        cleared_empty = cursor.rowcount
        
        cleared_count = cleared_non_empty + cleared_empty

        conn.commit()
        conn.close()

        logger.info(f"✅ Cleared JSON column for {cleared_count} products in {db_name} (had {count_before} non-empty, {count_empty} empty strings)")
        return cleared_count

    except Exception as e:
        # Safely get the database filename for error message
        db_name = Path(db_path).name if isinstance(db_path, str) else str(db_path)
        logger.error(f"Error clearing JSON column in {db_name}: {e}")
        return 0


def clear_local():
    """Clear JSON column for local databases."""
    uploads_dir = Path('uploads')

    if not uploads_dir.exists():
        logger.error("uploads folder not found")
        return

    # Find all database files
    db_files = list(uploads_dir.glob('product_database_*.db'))
    logger.info(f"Found {len(db_files)} database files")

    if not db_files:
        logger.warning("No database files found")
        return

    total_cleared = 0
    for db_path in db_files:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {db_path.name}")
        cleared = clear_json_column(str(db_path))
        total_cleared += cleared

    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Local clear complete! Cleared {total_cleared} total products")


def generate_web_script():
    """Generate a script that can be run on PythonAnywhere."""
    script = '''#!/usr/bin/env python3
"""
Web Database JSON Column Clear Script
======================================
Run this script on PythonAnywhere to clear all JSON column values.

Usage:
    1. Upload this script to your PythonAnywhere account
    2. Open a Bash console
    3. cd to your project directory
    4. Run: python clear_json_web.py
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Update this path to match your PythonAnywhere setup
UPLOADS_DIR = '/home/YOUR_USERNAME/labelMaker/uploads'  # <-- UPDATE THIS


def clear_json_column(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if JSON column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'JSON' not in columns:
            logger.warning(f"JSON column does not exist in {db_path}")
            conn.close()
            return 0

        # Count products with non-empty JSON values (including empty strings)
        cursor.execute('SELECT COUNT(*) FROM products WHERE "JSON" IS NOT NULL AND "JSON" != ""')
        count_before = cursor.fetchone()[0]
        
        # Also count empty strings
        cursor.execute('SELECT COUNT(*) FROM products WHERE "JSON" = ""')
        count_empty = cursor.fetchone()[0]
        
        total_to_clear = count_before + count_empty

        # Clear all JSON values (both NULL and empty strings)
        cursor.execute('UPDATE products SET "JSON" = NULL WHERE "JSON" IS NOT NULL AND "JSON" != ""')
        cleared_non_empty = cursor.rowcount
        
        # Clear empty strings
        cursor.execute('UPDATE products SET "JSON" = NULL WHERE "JSON" = ""')
        cleared_empty = cursor.rowcount
        
        cleared_count = cleared_non_empty + cleared_empty

        conn.commit()
        conn.close()

        # Safely get the database filename
        db_name = Path(db_path).name if isinstance(db_path, str) else db_path.name
        logger.info(f"✅ Cleared JSON column for {cleared_count} products in {db_name} (had {count_before} non-empty, {count_empty} empty strings)")
        return cleared_count

    except Exception as e:
        # Safely get the database filename for error message
        db_name = Path(db_path).name if isinstance(db_path, str) else str(db_path)
        logger.error(f"Error clearing JSON column in {db_name}: {e}")
        return 0


def main():
    uploads_dir = Path(UPLOADS_DIR)

    if not uploads_dir.exists():
        logger.error(f"uploads folder not found: {UPLOADS_DIR}")
        logger.error("Please update UPLOADS_DIR at the top of this script")
        return

    # Find all database files
    db_files = list(uploads_dir.glob('product_database_*.db'))
    logger.info(f"Found {len(db_files)} database files")

    if not db_files:
        logger.warning("No database files found")
        return

    total_cleared = 0
    for db_path in db_files:
        logger.info(f"\\nProcessing: {db_path.name}")
        cleared = clear_json_column(str(db_path))
        total_cleared += cleared

    logger.info(f"\\n✅ Clear complete! Cleared {total_cleared} total products")


if __name__ == '__main__':
    main()
'''

    # Write the web script
    web_script_path = Path('clear_json_web.py')
    with open(web_script_path, 'w') as f:
        f.write(script)

    logger.info(f"\n✅ Web script generated: {web_script_path}")
    logger.info("Upload this file to PythonAnywhere and run it there.")
    logger.info("Don't forget to update UPLOADS_DIR at the top of the script!")


def main():
    parser = argparse.ArgumentParser(description='Clear JSON column in product databases')
    parser.add_argument('--web', action='store_true', help='Generate script for web deployment')
    args = parser.parse_args()

    if args.web:
        generate_web_script()
    else:
        clear_local()


if __name__ == '__main__':
    main()
