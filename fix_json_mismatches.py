#!/usr/bin/env python3
"""
Fix JSON Column Mismatches
==========================
Finds products where the JSON column value doesn't actually match the product name,
and clears those incorrect mappings.

Usage:
    python fix_json_mismatches.py [--dry-run]
    python fix_json_mismatches.py --web [--dry-run]
"""

import os
import sys
import sqlite3
import argparse
import re
from pathlib import Path

# Auto-detect environment
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_UPLOADS = os.path.join(SCRIPT_DIR, 'uploads')
PYTHONANYWHERE_UPLOADS = '/home/adamcordova/AGTDesigner/uploads'

if os.path.exists(LOCAL_UPLOADS):
    UPLOADS_DIR = LOCAL_UPLOADS
else:
    UPLOADS_DIR = PYTHONANYWHERE_UPLOADS


def extract_key_terms(text):
    """Extract meaningful terms from product name for matching."""
    if not text:
        return set()
    text = text.lower()
    # Remove common filler words and units
    text = re.sub(r'\b(by|the|a|an|and|or|for|in|of|to|with)\b', ' ', text)
    text = re.sub(r'\b\d+(\.\d+)?\s*(g|mg|ml|oz|pack|pk)\b', ' ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    words = text.split()
    # Filter out very short words and common terms
    stopwords = {'indica', 'sativa', 'hybrid', 'dominant', 'live', 'resin'}
    return set(w for w in words if len(w) > 2 and w not in stopwords)


def extract_strain_name(text):
    """Extract the core strain/product name (not vendor, type, weight)."""
    if not text:
        return ''
    text = text.lower()
    # Remove vendor suffix (e.g., "by Honey Tree")
    text = re.sub(r'\s+by\s+[\w\s]+$', '', text)
    # Remove weight patterns anywhere in string
    text = re.sub(r'\b\d+(\.\d+)?\s*(g|mg|ml|oz|pack|pk)\b', '', text)
    text = re.sub(r'\b\d+x\d+(\.\d+)?\s*(g|mg|ml)?\b', '', text)
    # Remove type indicators
    text = re.sub(r'\b(cartridge|cart|vape|disposable|pre-?roll|flower|concentrate|tincture|edible|infused|joint|blunt)s?\b', '', text, flags=re.IGNORECASE)
    # Remove lineage indicators
    text = re.sub(r'\b(indica|sativa|hybrid|dominant)\b', '', text, flags=re.IGNORECASE)
    # Clean up separators and extra spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def check_mismatch(product_name, json_value):
    """
    Check if JSON value is a mismatch for the product name.
    Returns True if it's a BAD match that should be cleared.
    """
    if not product_name or not json_value:
        return False

    # Extract strain names (core product identifier)
    product_strain = extract_strain_name(product_name)
    json_strain = extract_strain_name(json_value)

    # If we can extract strain names, check if they have any overlap
    if product_strain and json_strain:
        product_words = set(product_strain.split())
        json_words = set(json_strain.split())

        # Remove vendor names from both (they often match but don't indicate same product)
        common_vendors = {'honey', 'tree', 'phat', 'panda', 'sticky', 'frog', 'dose', 'oil',
                         'dabstract', 'bodhi', 'high', 'crystal', 'clear', 'geez', 'fkit',
                         'thunder', 'chief', 'thunderchief', 'baker', 'homegrown', 'ceres',
                         'snickle', 'fritz', 'kushco', 'leafwerx', 'noble', 'farms'}
        product_words -= common_vendors
        json_words -= common_vendors

        # Also remove common filler words
        filler_words = {'live', 'resin', 'hte', 'aio', 'prana', '510', 'the', 'and', 'for', 'pack'}
        product_words -= filler_words
        json_words -= filler_words

        # Filter out very short words (< 3 chars) and single letters
        product_words = {w for w in product_words if len(w) >= 3}
        json_words = {w for w in json_words if len(w) >= 3}

        if product_words and json_words:
            overlap = product_words & json_words
            # If no meaningful word overlap in strain name, it's a mismatch
            if not overlap:
                return True  # MISMATCH

    return False


def fix_mismatches(db_path, dry_run=False):
    """Find and fix JSON column mismatches in a database."""
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

    # Get all products with JSON values
    cursor.execute('''
        SELECT id, "Product Name*", "JSON"
        FROM products
        WHERE "JSON" IS NOT NULL AND "JSON" <> ''
    ''')
    products = cursor.fetchall()
    print(f"  Products with JSON: {len(products)}")

    mismatches = []
    for product_id, product_name, json_value in products:
        if check_mismatch(product_name, json_value):
            mismatches.append({
                'id': product_id,
                'product_name': product_name,
                'json_value': json_value
            })

    print(f"  Mismatches found: {len(mismatches)}")

    if mismatches:
        print(f"\n  Sample mismatches:")
        for m in mismatches[:10]:
            print(f"    Product: {m['product_name'][:50]}...")
            print(f"    JSON:    {m['json_value'][:50]}...")
            print()

    if dry_run:
        print(f"  [DRY RUN] Would clear {len(mismatches)} mismatched JSON values")
        conn.close()
        return len(mismatches)

    # Clear mismatched JSON values
    for m in mismatches:
        cursor.execute(
            'UPDATE products SET "JSON" = NULL WHERE id = ?',
            (m['id'],)
        )

    conn.commit()
    conn.close()

    print(f"  Cleared {len(mismatches)} mismatched JSON values")
    return len(mismatches)


def main():
    parser = argparse.ArgumentParser(description='Fix JSON column mismatches')
    parser.add_argument('--web', action='store_true', help='Process web databases')
    parser.add_argument('--dry-run', action='store_true', help='Only report, do not fix')
    parser.add_argument('--db', type=str, help='Single database path')
    args = parser.parse_args()

    if args.db:
        if not Path(args.db).exists():
            print(f"Database not found: {args.db}")
            sys.exit(1)
        fix_mismatches(args.db, dry_run=args.dry_run)
        return

    uploads_dir = Path(UPLOADS_DIR)
    if not uploads_dir.exists():
        print(f"Uploads directory not found: {UPLOADS_DIR}")
        sys.exit(1)

    db_files = list(uploads_dir.glob('product_database*.db'))
    print(f"Found {len(db_files)} database files")

    total_fixed = 0
    for db_path in db_files:
        total_fixed += fix_mismatches(str(db_path), dry_run=args.dry_run)

    print(f"\n{'='*60}")
    print(f"TOTAL {'would fix' if args.dry_run else 'fixed'}: {total_fixed} mismatches")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
