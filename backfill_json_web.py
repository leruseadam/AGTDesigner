#!/usr/bin/env python3
"""
Web Database JSON Column Backfill Script
=========================================
Run this script on PythonAnywhere to backfill the JSON column.

Usage:
    1. Upload this script to your PythonAnywhere account
    2. Open a Bash console
    3. cd to your project directory
    4. Run: python backfill_json_web.py
"""

import os
import sys
import sqlite3
import pandas as pd
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Update this path to match your PythonAnywhere setup
UPLOADS_DIR = '/home/adamcordova/labelMaker/uploads'  # <-- UPDATE THIS

STORE_PATTERNS = {
    'bothell': 'AGT_Bothell',
    'burien': 'AGT_Burien',
    'goldbar': 'AGT_Goldbar',
    'lynnwood': 'AGT_Lynnwood',
    'seattle': 'AGT_Seattle',
    'shoreline': 'AGT_Shoreline',
    'walla': 'AGT_Walla_Walla',
}


def get_store_from_filename(filename):
    filename_lower = filename.lower()
    for pattern, store_name in STORE_PATTERNS.items():
        if pattern in filename_lower:
            return store_name
    return None


def ensure_json_column_exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'JSON' not in columns:
            logger.info(f"Adding JSON column to {db_path}")
            cursor.execute('ALTER TABLE products ADD COLUMN "JSON" TEXT')
            conn.commit()

        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def load_excel_descriptions(excel_path):
    try:
        df = pd.read_excel(excel_path, engine='openpyxl')

        if 'Description' not in df.columns:
            return {}

        product_name_col = None
        for col in ['Product Name*', 'ProductName', 'Product Name']:
            if col in df.columns:
                product_name_col = col
                break

        if not product_name_col:
            return {}

        descriptions = {}
        for _, row in df.iterrows():
            product_name = str(row.get(product_name_col, '')).strip()
            description = str(row.get('Description', '')).strip()

            if product_name and description and description.lower() != 'nan':
                descriptions[product_name.lower()] = description

        return descriptions
    except Exception as e:
        logger.error(f"Error: {e}")
        return {}


def update_json_column(db_path, descriptions):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, "Product Name*" FROM products')
        products = cursor.fetchall()

        updated_from_excel = 0

        # First pass: Match from Excel descriptions
        if descriptions:
            for product_id, product_name in products:
                if not product_name:
                    continue

                product_name_lower = product_name.strip().lower()
                if product_name_lower in descriptions:
                    cursor.execute(
                        'UPDATE products SET "JSON" = ? WHERE id = ?',
                        (descriptions[product_name_lower], product_id)
                    )
                    updated_from_excel += 1

            conn.commit()
            logger.info(f"  From Excel: {updated_from_excel}")

        # Second pass: Copy Description to JSON for remaining products
        cursor.execute('''
            UPDATE products
            SET "JSON" = "Description"
            WHERE ("JSON" IS NULL OR "JSON" = "")
              AND "Description" IS NOT NULL
              AND "Description" != ""
        ''')
        updated_from_db = cursor.rowcount
        conn.commit()

        if updated_from_db > 0:
            logger.info(f"  From DB Description: {updated_from_db}")

        conn.close()
        return updated_from_excel + updated_from_db
    except Exception as e:
        logger.error(f"Error: {e}")
        return 0


def main():
    uploads_dir = Path(UPLOADS_DIR)

    if not uploads_dir.exists():
        logger.error(f"uploads folder not found: {UPLOADS_DIR}")
        logger.error("Please update UPLOADS_DIR at the top of this script")
        return

    excel_files = list(uploads_dir.glob('*.xlsx')) + list(uploads_dir.glob('*.xls'))
    logger.info(f"Found {len(excel_files)} Excel files")

    for excel_path in excel_files:
        logger.info(f"\nProcessing: {excel_path.name}")

        store_name = get_store_from_filename(excel_path.name)
        if not store_name:
            logger.warning(f"Could not determine store")
            continue

        db_path = uploads_dir / f"product_database_{store_name}.db"
        if not db_path.exists():
            logger.warning(f"Database not found: {db_path}")
            continue

        ensure_json_column_exists(str(db_path))
        descriptions = load_excel_descriptions(str(excel_path))
        updated = update_json_column(str(db_path), descriptions)
        logger.info(f"✅ Updated {updated} products")

    logger.info("\n✅ Backfill complete!")


if __name__ == '__main__':
    main()
