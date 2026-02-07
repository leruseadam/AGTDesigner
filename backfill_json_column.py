#!/usr/bin/env python3
"""
Backfill JSON Column Script
===========================
This script populates the JSON column in the product database with original
Description values from Excel files in the uploads folder.

The JSON column stores the original Description values before they are
transformed, enabling exact matching when JSON URLs are submitted.

Usage:
    Local:  python backfill_json_column.py
    Web:    python backfill_json_column.py --web
"""

import os
import sys
import sqlite3
import pandas as pd
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Store name mappings
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
    """Extract store name from Excel filename."""
    filename_lower = filename.lower()
    for pattern, store_name in STORE_PATTERNS.items():
        if pattern in filename_lower:
            return store_name
    return None


def ensure_json_column_exists(db_path):
    """Ensure the JSON column exists in the products table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if JSON column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'JSON' not in columns:
            logger.info(f"Adding JSON column to {db_path}")
            cursor.execute('ALTER TABLE products ADD COLUMN "JSON" TEXT')
            conn.commit()
            logger.info("✅ JSON column added")
        else:
            logger.info(f"JSON column already exists in {db_path}")

        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error ensuring JSON column exists: {e}")
        return False


def load_excel_descriptions(excel_path):
    """Load Description values from Excel file, keyed by Product Name."""
    try:
        df = pd.read_excel(excel_path, engine='openpyxl')
        logger.info(f"Loaded {len(df)} rows from {excel_path}")

        # Get Description column
        if 'Description' not in df.columns:
            logger.warning(f"No Description column in {excel_path}")
            return {}

        # Get Product Name column
        product_name_col = None
        for col in ['Product Name*', 'ProductName', 'Product Name']:
            if col in df.columns:
                product_name_col = col
                break

        if not product_name_col:
            logger.warning(f"No Product Name column in {excel_path}")
            return {}

        # Create mapping: Product Name -> Description
        descriptions = {}
        for _, row in df.iterrows():
            product_name = str(row.get(product_name_col, '')).strip()
            description = str(row.get('Description', '')).strip()

            if product_name and description and description.lower() != 'nan':
                descriptions[product_name.lower()] = description

        logger.info(f"Extracted {len(descriptions)} descriptions")
        return descriptions

    except Exception as e:
        logger.error(f"Error loading Excel file {excel_path}: {e}")
        return {}


def update_json_column(db_path, descriptions):
    """Update the JSON column in the database with Description values."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all products
        cursor.execute('SELECT id, "Product Name*" FROM products')
        products = cursor.fetchall()
        logger.info(f"Found {len(products)} products in database")

        updated_from_excel = 0

        # First pass: Match from Excel descriptions
        if descriptions:
            for product_id, product_name in products:
                if not product_name:
                    continue

                product_name_lower = product_name.strip().lower()

                # Look for matching description
                if product_name_lower in descriptions:
                    description = descriptions[product_name_lower]
                    cursor.execute(
                        'UPDATE products SET "JSON" = ? WHERE id = ?',
                        (description, product_id)
                    )
                    updated_from_excel += 1

            conn.commit()
            logger.info(f"✅ Updated {updated_from_excel} products from Excel descriptions")

        # Second pass: For products still without JSON, copy from Description column
        # This handles historical products not in current Excel
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
            logger.info(f"✅ Updated {updated_from_db} products from existing Description column")

        conn.close()

        total_updated = updated_from_excel + updated_from_db
        logger.info(f"✅ Total: {total_updated} products with JSON values")
        return total_updated

    except Exception as e:
        logger.error(f"Error updating JSON column: {e}")
        return 0


def backfill_local():
    """Backfill JSON column for local databases."""
    uploads_dir = Path('uploads')

    if not uploads_dir.exists():
        logger.error("uploads folder not found")
        return

    # Find all Excel files
    excel_files = list(uploads_dir.glob('*.xlsx')) + list(uploads_dir.glob('*.xls'))
    logger.info(f"Found {len(excel_files)} Excel files")

    # Find all database files
    db_files = list(uploads_dir.glob('product_database_*.db'))
    logger.info(f"Found {len(db_files)} database files")

    # Process each Excel file
    for excel_path in excel_files:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {excel_path.name}")

        # Determine store
        store_name = get_store_from_filename(excel_path.name)
        if not store_name:
            logger.warning(f"Could not determine store for {excel_path.name}")
            continue

        logger.info(f"Store: {store_name}")

        # Find corresponding database
        db_path = uploads_dir / f"product_database_{store_name}.db"
        if not db_path.exists():
            logger.warning(f"Database not found: {db_path}")
            continue

        # Ensure JSON column exists
        if not ensure_json_column_exists(str(db_path)):
            continue

        # Load descriptions from Excel
        descriptions = load_excel_descriptions(str(excel_path))

        # Update database
        updated = update_json_column(str(db_path), descriptions)
        logger.info(f"Updated {updated} products in {db_path.name}")

    # Process ALL database files to ensure JSON column exists and is populated
    # This handles databases without corresponding Excel files
    logger.info(f"\n{'='*60}")
    logger.info("Processing remaining databases without Excel files...")

    for db_path in db_files:
        logger.info(f"\nChecking: {db_path.name}")

        # Ensure JSON column exists
        if not ensure_json_column_exists(str(db_path)):
            continue

        # Update with empty descriptions dict - this will trigger the fallback
        # to copy Description column to JSON for products without JSON values
        updated = update_json_column(str(db_path), {})
        if updated > 0:
            logger.info(f"Updated {updated} products in {db_path.name}")

    logger.info(f"\n{'='*60}")
    logger.info("✅ Local backfill complete!")


def generate_web_script():
    """Generate a script that can be run on PythonAnywhere."""
    script = '''#!/usr/bin/env python3
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
UPLOADS_DIR = '/home/YOUR_USERNAME/labelMaker/uploads'  # <-- UPDATE THIS

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
    if not descriptions:
        return 0

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, "Product Name*" FROM products')
        products = cursor.fetchall()

        updated = 0
        for product_id, product_name in products:
            if not product_name:
                continue

            product_name_lower = product_name.strip().lower()
            if product_name_lower in descriptions:
                cursor.execute(
                    'UPDATE products SET "JSON" = ? WHERE id = ?',
                    (descriptions[product_name_lower], product_id)
                )
                updated += 1

        conn.commit()
        conn.close()
        return updated
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
        logger.info(f"\\nProcessing: {excel_path.name}")

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

    logger.info("\\n✅ Backfill complete!")


if __name__ == '__main__':
    main()
'''

    # Write the web script
    web_script_path = Path('backfill_json_web.py')
    with open(web_script_path, 'w') as f:
        f.write(script)

    logger.info(f"\n✅ Web script generated: {web_script_path}")
    logger.info("Upload this file to PythonAnywhere and run it there.")
    logger.info("Don't forget to update UPLOADS_DIR at the top of the script!")


def main():
    parser = argparse.ArgumentParser(description='Backfill JSON column in product databases')
    parser.add_argument('--web', action='store_true', help='Generate script for web deployment')
    args = parser.parse_args()

    if args.web:
        generate_web_script()
    else:
        backfill_local()


if __name__ == '__main__':
    main()
