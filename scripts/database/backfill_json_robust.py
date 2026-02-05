#!/usr/bin/env python3
"""
Robust JSON Column Backfill Script
===================================
This script reads Excel files and populates the JSON column with the ORIGINAL
Description values from Excel using multiple matching strategies.

Usage:
    python backfill_json_robust.py
"""

import os
import sys
import sqlite3
import logging
import pandas as pd
from pathlib import Path
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
UPLOADS_DIR = Path(__file__).parent / 'uploads'
DB_NAME = 'product_database.db'


def normalize_for_matching(text):
    """Normalize text for fuzzy matching."""
    if not text:
        return ''
    text = str(text).strip().lower()
    # Remove special characters but keep alphanumeric and spaces
    text = re.sub(r'[^\w\s]', '', text)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_core_product_name(name):
    """Extract the core product name without vendor/weight info."""
    if not name:
        return ''
    name = str(name).strip()

    # Remove " by Vendor" suffix
    if ' by ' in name:
        name = name.split(' by ')[0].strip()

    # Remove weight suffix like " - 3.5g" or " - 1g"
    name = re.sub(r'\s*-\s*[\d.]+g$', '', name)
    name = re.sub(r'\s*-\s*[\d.]+\s*g$', '', name)

    return normalize_for_matching(name)


def backfill_json_robust():
    """Backfill JSON column using multiple matching strategies."""

    db_path = UPLOADS_DIR / DB_NAME
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}")
        return

    # Find all Excel files
    excel_files = list(UPLOADS_DIR.glob('*.xlsx'))
    logger.info(f"Found {len(excel_files)} Excel files")

    if not excel_files:
        logger.warning("No Excel files found!")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Ensure JSON column exists
    cursor.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'JSON' not in columns:
        logger.info("Adding JSON column...")
        cursor.execute('ALTER TABLE products ADD COLUMN "JSON" TEXT')
        conn.commit()

    # Get ALL products (we'll update those missing JSON)
    cursor.execute('''
        SELECT id, "Product Name*", Description
        FROM products
        WHERE "JSON" IS NULL OR "JSON" = ''
    ''')
    products = cursor.fetchall()
    logger.info(f"Found {len(products)} products needing JSON values")

    if not products:
        logger.info("All products already have JSON values!")
        conn.close()
        return

    # Build multiple lookup dictionaries from Excel
    # Strategy 1: Exact product name match
    exact_match = {}
    # Strategy 2: Normalized product name match
    normalized_match = {}
    # Strategy 3: Core product name match (without vendor/weight)
    core_match = {}

    for excel_file in excel_files:
        logger.info(f"Reading: {excel_file.name}")
        try:
            df = pd.read_excel(
                excel_file,
                dtype=str,
                na_filter=False,
                keep_default_na=False
            )

            # Try different column name variations
            product_col = None
            for col in ['Product Name*', 'ProductName', 'Product Name']:
                if col in df.columns:
                    product_col = col
                    break

            desc_col = None
            for col in ['Description', 'description']:
                if col in df.columns:
                    desc_col = col
                    break

            if not product_col or not desc_col:
                logger.warning(f"  Missing required columns in {excel_file.name}")
                continue

            count = 0
            for _, row in df.iterrows():
                product_name = str(row.get(product_col, '')).strip()
                description = str(row.get(desc_col, '')).strip()

                if not product_name or not description:
                    continue

                count += 1

                # Strategy 1: Exact match
                if product_name not in exact_match:
                    exact_match[product_name] = description

                # Strategy 2: Normalized match
                normalized = normalize_for_matching(product_name)
                if normalized and normalized not in normalized_match:
                    normalized_match[normalized] = description

                # Strategy 3: Core name match
                core = extract_core_product_name(product_name)
                if core and core not in core_match:
                    core_match[core] = description

            logger.info(f"  Processed {count} rows")

        except Exception as e:
            logger.error(f"  Error: {e}")

    logger.info(f"\nLookup tables built:")
    logger.info(f"  Exact matches: {len(exact_match)}")
    logger.info(f"  Normalized matches: {len(normalized_match)}")
    logger.info(f"  Core name matches: {len(core_match)}")

    # Now update products
    updated = 0
    not_found = 0

    for product_id, product_name, description in products:
        json_value = None

        # Try Strategy 1: Exact match
        if product_name in exact_match:
            json_value = exact_match[product_name]

        # Try Strategy 2: Normalized match
        if not json_value:
            normalized = normalize_for_matching(product_name)
            if normalized in normalized_match:
                json_value = normalized_match[normalized]

        # Try Strategy 3: Core name match
        if not json_value:
            core = extract_core_product_name(product_name)
            if core in core_match:
                json_value = core_match[core]

        # Try matching with the current Description (which came from Product Name)
        if not json_value and description:
            desc_normalized = normalize_for_matching(description)
            if desc_normalized in normalized_match:
                json_value = normalized_match[desc_normalized]

        if json_value:
            cursor.execute(
                'UPDATE products SET "JSON" = ? WHERE id = ?',
                (json_value, product_id)
            )
            updated += 1
            if updated <= 10:
                logger.info(f"  Updated: {product_name[:50]}...")
                logger.info(f"    -> JSON: {json_value[:50]}...")
        else:
            not_found += 1
            if not_found <= 5:
                logger.warning(f"  Not found: {product_name[:50]}...")

    conn.commit()
    conn.close()

    logger.info(f"\n{'='*60}")
    logger.info(f"BACKFILL COMPLETE!")
    logger.info(f"  Updated: {updated} products")
    logger.info(f"  Not found: {not_found} products")
    logger.info(f"{'='*60}")


if __name__ == '__main__':
    backfill_json_robust()
