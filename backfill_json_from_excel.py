#!/usr/bin/env python3
"""
JSON Column Backfill Script - From Excel Files
================================================
This script reads Excel files and populates the JSON column with the ORIGINAL
Description values from Excel, BEFORE any transformations are applied.

The JSON column stores the original Excel Description for URL matching purposes.

Usage:
    python backfill_json_from_excel.py
"""

import os
import sys
import sqlite3
import logging
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
UPLOADS_DIR = Path(__file__).parent / 'uploads'
DB_NAME = 'product_database.db'


def normalize_product_name(name):
    """Normalize product name for matching (same logic as database)."""
    if not name:
        return ''
    name = str(name).strip().lower()
    # Remove common suffixes for matching
    for suffix in [' - flower', ' - concentrate', ' - edible', ' - pre-roll']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    return name


def backfill_json_from_excel():
    """Backfill JSON column from original Excel Description values."""

    db_path = UPLOADS_DIR / DB_NAME
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return

    # Find all Excel files in uploads directory
    excel_files = list(UPLOADS_DIR.glob('*.xlsx'))
    logger.info(f"Found {len(excel_files)} Excel files in {UPLOADS_DIR}")

    if not excel_files:
        logger.warning("No Excel files found!")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Ensure JSON column exists
    cursor.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'JSON' not in columns:
        logger.info("Adding JSON column to products table...")
        cursor.execute('ALTER TABLE products ADD COLUMN "JSON" TEXT')
        conn.commit()

    # Get products that need JSON values
    cursor.execute('''
        SELECT id, "Product Name*", normalized_name
        FROM products
        WHERE "JSON" IS NULL OR "JSON" = ''
    ''')
    products_needing_json = {
        normalize_product_name(row[1]): {'id': row[0], 'name': row[1], 'normalized': row[2]}
        for row in cursor.fetchall()
    }

    logger.info(f"Found {len(products_needing_json)} products needing JSON values")

    if not products_needing_json:
        logger.info("All products already have JSON values!")
        conn.close()
        return

    # Build a mapping of product names to original Excel Description values
    excel_descriptions = {}

    for excel_file in excel_files:
        logger.info(f"\nReading: {excel_file.name}")
        try:
            df = pd.read_excel(
                excel_file,
                dtype={'Product Name*': str, 'Description': str},
                na_filter=False,
                keep_default_na=False
            )

            if 'Product Name*' not in df.columns:
                logger.warning(f"  No 'Product Name*' column in {excel_file.name}")
                continue

            if 'Description' not in df.columns:
                logger.warning(f"  No 'Description' column in {excel_file.name}")
                continue

            # Build mapping of normalized product names to original descriptions
            for _, row in df.iterrows():
                product_name = str(row.get('Product Name*', '')).strip()
                description = str(row.get('Description', '')).strip()

                if product_name and description:
                    normalized = normalize_product_name(product_name)
                    if normalized not in excel_descriptions:
                        excel_descriptions[normalized] = description

            logger.info(f"  Found {len(df)} rows with descriptions")

        except Exception as e:
            logger.error(f"  Error reading {excel_file.name}: {e}")
            continue

    logger.info(f"\nTotal Excel descriptions collected: {len(excel_descriptions)}")

    # Now update the database
    updated_count = 0
    not_found_count = 0

    for normalized_name, product_info in products_needing_json.items():
        if normalized_name in excel_descriptions:
            original_description = excel_descriptions[normalized_name]
            try:
                cursor.execute(
                    'UPDATE products SET "JSON" = ? WHERE id = ?',
                    (original_description, product_info['id'])
                )
                updated_count += 1

                if updated_count <= 5:  # Log first 5 updates
                    logger.info(f"  Updated ID {product_info['id']}: {product_info['name'][:50]}...")
                    logger.info(f"    JSON set to: {original_description[:50]}...")
            except Exception as e:
                logger.error(f"  Error updating ID {product_info['id']}: {e}")
        else:
            not_found_count += 1

    conn.commit()
    conn.close()

    logger.info(f"\n{'='*60}")
    logger.info(f"BACKFILL COMPLETE!")
    logger.info(f"  Updated: {updated_count} products")
    logger.info(f"  Not found in Excel: {not_found_count} products")
    logger.info(f"{'='*60}")


def main():
    logger.info("JSON Column Backfill Script")
    logger.info("="*60)
    logger.info(f"Database: {UPLOADS_DIR / DB_NAME}")
    logger.info(f"Excel directory: {UPLOADS_DIR}")
    logger.info("="*60 + "\n")

    backfill_json_from_excel()


if __name__ == '__main__':
    main()
