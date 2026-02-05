#!/usr/bin/env python3
"""
JSON Backfill Script for PythonAnywhere
=======================================
Populates JSON column with ORIGINAL Excel Description values.

Upload to PythonAnywhere and run:
    cd /home/adamcordova/AGTDesigner
    python backfill_json_pythonanywhere.py
"""

import sqlite3
import re
from pathlib import Path

# PythonAnywhere path
UPLOADS_DIR = '/home/adamcordova/AGTDesigner/uploads'


def normalize(text):
    """Normalize text for matching."""
    if not text:
        return ''
    return re.sub(r'\s+', ' ', str(text).strip().lower())


def main():
    print("="*60)
    print("JSON Backfill - Original Excel Descriptions")
    print("="*60)

    uploads_dir = Path(UPLOADS_DIR)

    if not uploads_dir.exists():
        print(f"ERROR: Directory not found: {UPLOADS_DIR}")
        return

    # Import pandas
    try:
        import pandas as pd
    except ImportError:
        print("ERROR: pandas not installed")
        return

    # Build lookup: normalized Product Name -> Original Excel Description
    print("\nBuilding lookup from Excel files...")
    lookup = {}

    excel_files = list(uploads_dir.glob('*.xlsx'))
    print(f"Found {len(excel_files)} Excel files")

    for excel_file in excel_files:
        try:
            df = pd.read_excel(
                excel_file,
                dtype=str,
                na_filter=False,
                keep_default_na=False
            )

            if 'Product Name*' not in df.columns or 'Description' not in df.columns:
                print(f"  Skipping {excel_file.name} - missing columns")
                continue

            count = 0
            for _, row in df.iterrows():
                product_name = str(row['Product Name*']).strip()
                description = str(row['Description']).strip()

                if product_name and description:
                    key = normalize(product_name)
                    # Keep longest description (most complete)
                    if key not in lookup or len(description) > len(lookup[key]):
                        lookup[key] = description
                        count += 1

            print(f"  {excel_file.name}: {count} products")

        except Exception as e:
            print(f"  Error reading {excel_file.name}: {e}")

    print(f"\nTotal lookup entries: {len(lookup)}")

    if not lookup:
        print("ERROR: No products found in Excel files!")
        return

    # Find all database files
    db_files = list(uploads_dir.glob('product_database*.db'))
    print(f"\nFound {len(db_files)} database files")

    # Update each database
    total_updated = 0

    for db_path in db_files:
        print(f"\n{'='*60}")
        print(f"Processing: {db_path.name}")
        print(f"{'='*60}")

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Ensure JSON column exists
            cursor.execute("PRAGMA table_info(products)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'JSON' not in columns:
                print("  Adding JSON column...")
                cursor.execute('ALTER TABLE products ADD COLUMN "JSON" TEXT')
                conn.commit()

            # Get all products
            cursor.execute('SELECT id, "Product Name*" FROM products')
            products = cursor.fetchall()
            print(f"  Total products: {len(products)}")

            # Update JSON from lookup
            updated = 0
            for product_id, product_name in products:
                if not product_name:
                    continue

                key = normalize(product_name)
                if key in lookup:
                    json_value = lookup[key]
                    cursor.execute(
                        'UPDATE products SET "JSON" = ? WHERE id = ?',
                        (json_value, product_id)
                    )
                    updated += 1

            conn.commit()

            # Verify results
            cursor.execute('SELECT COUNT(*) FROM products WHERE "JSON" IS NOT NULL AND "JSON" != ""')
            with_json = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM products')
            total = cursor.fetchone()[0]

            print(f"  Updated: {updated}")
            print(f"  With JSON: {with_json}/{total} ({100*with_json/max(total,1):.1f}%)")

            total_updated += updated
            conn.close()

        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{'='*60}")
    print(f"COMPLETE! Total updated: {total_updated}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
