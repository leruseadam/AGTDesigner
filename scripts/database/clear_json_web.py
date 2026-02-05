#!/usr/bin/env python3
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
UPLOADS_DIR = '/home/adamcordova/AGTDesigner/uploads'  # <-- UPDATE THIS


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

        # Count products with non-empty JSON values before clearing
        cursor.execute('SELECT COUNT(*) FROM products WHERE "JSON" IS NOT NULL AND "JSON" != ""')
        count_before = cursor.fetchone()[0]

        # Clear all JSON values
        cursor.execute('UPDATE products SET "JSON" = NULL WHERE "JSON" IS NOT NULL')
        cleared_count = cursor.rowcount

        conn.commit()
        conn.close()

        logger.info(f"✅ Cleared JSON column for {cleared_count} products in {Path(db_path).name} (had {count_before} non-empty values)")
        return cleared_count

    except Exception as e:
        logger.error(f"Error clearing JSON column in {db_path}: {e}")
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
        logger.info(f"\nProcessing: {db_path.name}")
        cleared = clear_json_column(str(db_path))
        total_cleared += cleared

    logger.info(f"\n✅ Clear complete! Cleared {total_cleared} total products")


if __name__ == '__main__':
    main()
