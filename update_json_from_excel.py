#!/usr/bin/env python3
"""
Update JSON Column from Excel Files
====================================
Updates the JSON column in the database to match the current Excel Description values.
This handles format changes in the feed (e.g., old format vs new format).

Usage:
    python update_json_from_excel.py [--dry-run]
    python update_json_from_excel.py --db uploads/product_database_AGT_Bothell.db [--dry-run]
"""

import os
import sys
import sqlite3
import re
import argparse
from pathlib import Path

# Auto-detect environment
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_UPLOADS = os.path.join(SCRIPT_DIR, 'uploads')
PYTHONANYWHERE_UPLOADS = '/home/adamcordova/AGTDesigner/uploads'

if os.path.exists(LOCAL_UPLOADS):
    UPLOADS_DIR = LOCAL_UPLOADS
else:
    UPLOADS_DIR = PYTHONANYWHERE_UPLOADS


def normalize(text):
    """Normalize text for matching."""
    if not text:
        return ''
    return re.sub(r'\s+', ' ', str(text).strip().lower())


def extract_strain(text):
    """Extract strain name from product name."""
    if not text:
        return ''
    text = text.lower()
    # Remove vendor suffix
    text = re.sub(r'\s+by\s+[\w\s]+$', '', text)
    # Remove weight
    text = re.sub(r'\s*-\s*[\d.]+\s*(g|mg|ml|oz)\s*$', '', text)
    # Remove product types
    for ptype in ['cartridge', 'cart', 'vape', 'disposable', 'live resin', 'flower', 'pre-roll']:
        text = re.sub(rf'\s+{ptype}s?\s*', ' ', text, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', text).strip()


def build_excel_lookup(uploads_dir):
    """Build lookup from Excel: Product Name -> Description (JSON value)."""
    try:
        import pandas as pd
    except ImportError:
        print("ERROR: pandas not installed")
        return {}

    lookup = {}
    excel_files = list(Path(uploads_dir).glob('*.xlsx'))
    print(f"Found {len(excel_files)} Excel files")

    for excel_file in excel_files:
        try:
            df = pd.read_excel(excel_file, dtype=str, na_filter=False, keep_default_na=False)

            if 'Product Name*' not in df.columns or 'Description' not in df.columns:
                continue

            for _, row in df.iterrows():
                product_name = str(row['Product Name*']).strip()
                description = str(row['Description']).strip()

                if product_name and description and len(description) >= 10:
                    key = normalize(product_name)
                    # Keep longest/most recent description
                    if key not in lookup or len(description) > len(lookup[key]):
                        lookup[key] = description

        except Exception as e:
            print(f"  Error reading {excel_file.name}: {e}")

    print(f"Built lookup with {len(lookup)} entries")
    return lookup


def update_json_column(db_path, lookup, dry_run=False):
    """Update JSON column from Excel lookup."""
    print(f"\n{'='*60}")
    print(f"Processing: {Path(db_path).name}")
    print(f"{'='*60}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if JSON column exists
    cursor.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'JSON' not in columns:
        print("  No JSON column found")
        conn.close()
        return 0

    # Get all products
    cursor.execute('SELECT id, "Product Name*", "JSON" FROM products')
    products = cursor.fetchall()
    print(f"  Total products: {len(products)}")

    updates = []
    for product_id, product_name, current_json in products:
        if not product_name:
            continue

        key = normalize(product_name)
        if key in lookup:
            new_json = lookup[key]
            # Only update if different
            if new_json != current_json:
                updates.append({
                    'id': product_id,
                    'product_name': product_name,
                    'old_json': current_json,
                    'new_json': new_json
                })

    print(f"  Updates needed: {len(updates)}")

    if updates:
        print(f"\n  Sample updates:")
        for u in updates[:5]:
            print(f"    Product: {u['product_name'][:50]}...")
            print(f"    Old:     {(u['old_json'] or 'NULL')[:50]}...")
            print(f"    New:     {u['new_json'][:50]}...")
            print()

    if dry_run:
        print(f"  [DRY RUN] Would update {len(updates)} JSON values")
        conn.close()
        return len(updates)

    # Apply updates
    for u in updates:
        cursor.execute(
            'UPDATE products SET "JSON" = ? WHERE id = ?',
            (u['new_json'], u['id'])
        )

    conn.commit()
    conn.close()

    print(f"  Updated {len(updates)} JSON values")
    return len(updates)


def main():
    parser = argparse.ArgumentParser(description='Update JSON column from Excel files')
    parser.add_argument('--dry-run', action='store_true', help='Only report, do not update')
    parser.add_argument('--db', type=str, help='Single database path')
    args = parser.parse_args()

    uploads_dir = Path(UPLOADS_DIR)
    if not uploads_dir.exists():
        print(f"Uploads directory not found: {UPLOADS_DIR}")
        sys.exit(1)

    # Build lookup from Excel
    lookup = build_excel_lookup(uploads_dir)
    if not lookup:
        print("ERROR: No products found in Excel files!")
        sys.exit(1)

    if args.db:
        if not Path(args.db).exists():
            print(f"Database not found: {args.db}")
            sys.exit(1)
        total = update_json_column(args.db, lookup, dry_run=args.dry_run)
    else:
        db_files = list(uploads_dir.glob('product_database*.db'))
        print(f"Found {len(db_files)} database files")

        total = 0
        for db_path in db_files:
            total += update_json_column(str(db_path), lookup, dry_run=args.dry_run)

    print(f"\n{'='*60}")
    print(f"TOTAL {'would update' if args.dry_run else 'updated'}: {total}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
