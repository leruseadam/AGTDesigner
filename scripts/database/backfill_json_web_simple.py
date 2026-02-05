#!/usr/bin/env python3
"""
Simple JSON Backfill Script for PythonAnywhere
===============================================
Backfills JSON column with original Excel Description values.

Usage:
    1. Upload this script to PythonAnywhere
    2. cd /home/adamcordova/AGTDesigner
    3. python backfill_json_web_simple.py
"""

import sqlite3
import re
from pathlib import Path

# ============================================================
# CONFIGURATION - Auto-detects local vs PythonAnywhere
# ============================================================
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_UPLOADS = os.path.join(SCRIPT_DIR, 'uploads')
PYTHONANYWHERE_UPLOADS = '/home/adamcordova/AGTDesigner/uploads'

# Use local path if it exists, otherwise try PythonAnywhere path
if os.path.exists(LOCAL_UPLOADS):
    UPLOADS_DIR = LOCAL_UPLOADS
else:
    UPLOADS_DIR = PYTHONANYWHERE_UPLOADS
# ============================================================


def normalize_for_matching(text):
    """Normalize text for matching."""
    if not text:
        return ''
    text = str(text).strip().lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_core_name(name):
    """Extract core product name without vendor/weight."""
    if not name:
        return ''
    name = str(name).strip()
    if ' by ' in name:
        name = name.split(' by ')[0].strip()
    name = re.sub(r'\s*-\s*[\d.]+g$', '', name)
    return normalize_for_matching(name)


def backfill_database(db_path, excel_lookup):
    """Backfill JSON column in a single database."""
    print(f"\n{'='*60}")
    print(f"Processing: {Path(db_path).name}")
    print(f"{'='*60}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Ensure JSON column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'JSON' not in columns:
            print("  Adding JSON column...")
            cursor.execute('ALTER TABLE products ADD COLUMN "JSON" TEXT')
            conn.commit()

        # Get products needing JSON
        cursor.execute('''
            SELECT id, "Product Name*", Description
            FROM products
            WHERE "JSON" IS NULL OR "JSON" = ''
        ''')
        products = cursor.fetchall()
        print(f"  Products needing JSON: {len(products)}")

        if not products:
            print("  All products already have JSON!")
            conn.close()
            return 0

        updated = 0
        for product_id, product_name, description in products:
            json_value = None

            # Try exact match
            if product_name and product_name in excel_lookup['exact']:
                json_value = excel_lookup['exact'][product_name]

            # Try normalized match
            if not json_value and product_name:
                normalized = normalize_for_matching(product_name)
                if normalized in excel_lookup['normalized']:
                    json_value = excel_lookup['normalized'][normalized]

            # Try core name match
            if not json_value and product_name:
                core = extract_core_name(product_name)
                if core in excel_lookup['core']:
                    json_value = excel_lookup['core'][core]

            # Try matching description
            if not json_value and description:
                desc_norm = normalize_for_matching(description)
                if desc_norm in excel_lookup['normalized']:
                    json_value = excel_lookup['normalized'][desc_norm]

            if json_value:
                cursor.execute(
                    'UPDATE products SET "JSON" = ? WHERE id = ?',
                    (json_value, product_id)
                )
                updated += 1

        conn.commit()

        # Verify
        cursor.execute('SELECT COUNT(*) FROM products WHERE "JSON" IS NOT NULL AND "JSON" != ""')
        with_json = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM products')
        total = cursor.fetchone()[0]

        print(f"  Updated: {updated} products")
        print(f"  Total with JSON: {with_json}/{total} ({100*with_json/max(total,1):.1f}%)")

        conn.close()
        return updated

    except Exception as e:
        print(f"  ERROR: {e}")
        return 0


def main():
    print("="*60)
    print("JSON Column Backfill Script for PythonAnywhere")
    print("="*60)

    uploads_dir = Path(UPLOADS_DIR)

    if not uploads_dir.exists():
        print(f"ERROR: Uploads directory not found: {UPLOADS_DIR}")
        print("Please update UPLOADS_DIR at the top of this script")
        return

    # Find Excel files
    excel_files = list(uploads_dir.glob('*.xlsx'))
    print(f"\nFound {len(excel_files)} Excel files")

    if not excel_files:
        print("ERROR: No Excel files found!")
        return

    # Import pandas
    try:
        import pandas as pd
    except ImportError:
        print("ERROR: pandas not installed. Run: pip install pandas openpyxl")
        return

    # Build lookup tables from ALL Excel files
    print("\nBuilding lookup tables from Excel files...")
    excel_lookup = {
        'exact': {},
        'normalized': {},
        'core': {}
    }

    for excel_file in excel_files:
        print(f"  Reading: {excel_file.name}")
        try:
            df = pd.read_excel(
                excel_file,
                dtype=str,
                na_filter=False,
                keep_default_na=False
            )

            # Find columns
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
                print(f"    Skipping - missing columns")
                continue

            count = 0
            for _, row in df.iterrows():
                product_name = str(row.get(product_col, '')).strip()
                description = str(row.get(desc_col, '')).strip()

                if not product_name or not description:
                    continue

                count += 1

                # Exact match
                if product_name not in excel_lookup['exact']:
                    excel_lookup['exact'][product_name] = description

                # Normalized match
                normalized = normalize_for_matching(product_name)
                if normalized and normalized not in excel_lookup['normalized']:
                    excel_lookup['normalized'][normalized] = description

                # Core name match
                core = extract_core_name(product_name)
                if core and core not in excel_lookup['core']:
                    excel_lookup['core'][core] = description

            print(f"    Processed {count} rows")

        except Exception as e:
            print(f"    Error: {e}")

    print(f"\nLookup tables built:")
    print(f"  Exact matches: {len(excel_lookup['exact'])}")
    print(f"  Normalized matches: {len(excel_lookup['normalized'])}")
    print(f"  Core name matches: {len(excel_lookup['core'])}")

    if not excel_lookup['exact']:
        print("\nERROR: No products found in Excel files!")
        return

    # Find all database files
    db_files = list(uploads_dir.glob('product_database*.db'))
    print(f"\nFound {len(db_files)} database files")

    if not db_files:
        print("ERROR: No database files found!")
        return

    # Process each database
    total_updated = 0
    for db_path in db_files:
        updated = backfill_database(str(db_path), excel_lookup)
        total_updated += updated

    print(f"\n{'='*60}")
    print(f"BACKFILL COMPLETE!")
    print(f"Total products updated: {total_updated}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
