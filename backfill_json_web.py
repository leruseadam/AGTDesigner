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
UPLOADS_DIR = '/home/adamcordova/AGTDesigner/uploads'  # <-- UPDATE THIS

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
    """Update JSON column ONLY from Excel descriptions. No database fallbacks."""
    try:
        if not descriptions:
            logger.warning("No Excel descriptions provided - skipping update")
            return 0

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, "Product Name*" FROM products')
        products = cursor.fetchall()

        updated_from_excel = 0

        # Only update from Excel descriptions - no fallbacks
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
        conn.close()
        
        if updated_from_excel > 0:
            logger.info(f"  Updated {updated_from_excel} products from Excel")
        else:
            logger.warning("  No products matched Excel descriptions")
        
        return updated_from_excel
    except Exception as e:
        logger.error(f"Error: {e}")
        return 0


def main():
    uploads_dir = Path(UPLOADS_DIR)

    if not uploads_dir.exists():
        logger.error(f"uploads folder not found: {UPLOADS_DIR}")
        logger.error("Please update UPLOADS_DIR at the top of this script")
        return

    # Only process Bothell database
    store_name = 'AGT_Bothell'
    db_path = uploads_dir / f"product_database_{store_name}.db"
    
    if not db_path.exists():
        logger.error(f"Bothell database not found: {db_path}")
        return

    logger.info(f"Processing Bothell database only: {db_path.name}")

    # Find Excel files that match Bothell - REQUIRED
    excel_files = list(uploads_dir.glob('*.xlsx')) + list(uploads_dir.glob('*.xls'))
    bothell_excel_files = [f for f in excel_files if 'bothell' in f.name.lower()]
    
    if not bothell_excel_files:
        logger.error("❌ No Bothell Excel files found - backfill requires a Bothell Excel file")
        logger.error("   Please upload a Bothell Excel file and try again")
        return

    logger.info(f"Found {len(bothell_excel_files)} Bothell Excel file(s)")

    # Process Bothell Excel files - REQUIRED
    descriptions = {}
    for excel_path in bothell_excel_files:
        logger.info(f"\nProcessing Excel: {excel_path.name}")
        excel_descriptions = load_excel_descriptions(str(excel_path))
        if excel_descriptions:
            descriptions.update(excel_descriptions)
            logger.info(f"  Loaded {len(excel_descriptions)} product descriptions")

    if not descriptions:
        logger.error("❌ No descriptions found in Bothell Excel file(s) - nothing to backfill")
        return

    # Update Bothell database - ONLY from Excel, no database fallbacks
    ensure_json_column_exists(str(db_path))
    updated = update_json_column(str(db_path), descriptions)
    logger.info(f"✅ Updated {updated} products in Bothell database from Excel")

    logger.info("\n✅ Bothell backfill complete!")


if __name__ == '__main__':
    main()
