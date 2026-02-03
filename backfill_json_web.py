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
    """Update JSON column with three-pass strategy: Excel -> DB Description -> Product Name*"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, "Product Name*", COALESCE("Description","") FROM products')
        products = cursor.fetchall()
        
        total_products = len(products)
        logger.info(f"  Found {total_products} total products in database")

        updated_from_excel = 0
        updated_from_db = 0
        updated_from_name = 0

        # Track which product IDs we've already updated so we don't overwrite
        updated_ids = set()

        # First pass: Match from Excel descriptions (canonical, pre-transform)
        if descriptions:
            for product_id, product_name, _desc in products:
                if not product_name:
                    continue

                product_name_lower = product_name.strip().lower()
                if product_name_lower in descriptions:
                    cursor.execute(
                        'UPDATE products SET "JSON" = ? WHERE id = ?',
                        (descriptions[product_name_lower], product_id)
                    )
                    updated_from_excel += 1
                    updated_ids.add(product_id)

            conn.commit()
            logger.info(f"  Updated {updated_from_excel} products from Excel descriptions")

        # Second pass: For products NOT updated above, copy Description column to JSON
        for product_id, _name, db_description in products:
            if product_id in updated_ids:
                continue
            if not db_description or str(db_description).strip() == '':
                continue

            cursor.execute(
                'UPDATE products SET "JSON" = ? WHERE id = ?',
                (db_description, product_id)
            )
            if cursor.rowcount:
                updated_from_db += 1
                updated_ids.add(product_id)

        conn.commit()
        if updated_from_db > 0:
            logger.info(f"  Updated {updated_from_db} products from DB Description column")

        # Third pass: For any remaining products, set JSON to Product Name*
        for product_id, product_name, _desc in products:
            if product_id in updated_ids:
                continue
            if not product_name or not str(product_name).strip():
                continue

            cursor.execute(
                'UPDATE products SET "JSON" = "Product Name*" WHERE id = ?',
                (product_id,)
            )
            if cursor.rowcount:
                updated_from_name += 1
                updated_ids.add(product_id)

        conn.commit()
        if updated_from_name > 0:
            logger.info(f"  Updated {updated_from_name} products from Product Name* (fallback)")

        conn.close()
        
        total_updated = updated_from_excel + updated_from_db + updated_from_name
        logger.info(f"  ✅ Total updated: {total_updated} out of {total_products} products")
        
        if total_updated < total_products:
            logger.warning(f"  ⚠️  {total_products - total_updated} products still have no JSON value")
        
        return total_updated
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
