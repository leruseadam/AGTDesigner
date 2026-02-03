#!/usr/bin/env python3
"""
Remove Duplicate Products Without Proper JSON Column Data
==========================================================
Finds duplicate products (same Product Name*, Vendor/Supplier*, Product Brand, Weight*),
keeps the row that has proper JSON column data, and deletes the others.

"Proper JSON" = non-null, non-empty, trimmed length >= 10 (feed-style description).

Usage:
    Local:  python remove_duplicate_products_no_json.py [--dry-run]
    Web:    python remove_duplicate_products_no_json.py --web [--dry-run]
    Store:  python remove_duplicate_products_no_json.py --web --store AGT_Bothell [--dry-run]
"""

import os
import sys
import sqlite3
import argparse
import logging
from pathlib import Path
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Same as backfill_json_web.py – update for your PythonAnywhere path
UPLOADS_DIR = '/home/adamcordova/AGTDesigner/uploads'

STORE_PATTERNS = {
    'bothell': 'AGT_Bothell',
    'burien': 'AGT_Burien',
    'goldbar': 'AGT_Goldbar',
    'lynnwood': 'AGT_Lynnwood',
    'seattle': 'AGT_Seattle',
    'shoreline': 'AGT_Shoreline',
    'walla': 'AGT_Walla_Walla',
}


def has_proper_json(json_val) -> bool:
    """True if JSON column has meaningful feed-style description (non-empty, reasonable length)."""
    if json_val is None:
        return False
    s = (json_val or '').strip()
    if not s:
        return False
    # At least 10 chars (e.g. "Pure - 1mL") to avoid trivial/placeholder
    return len(s) >= 10


def get_duplicate_groups(cursor):
    """
    Return list of (group_key, list of (id, has_proper_json, json_len)).
    group_key = (Product Name*, Vendor/Supplier*, Product Brand, Weight*) normalized.
    """
    cursor.execute('PRAGMA table_info(products)')
    columns = [row[1] for row in cursor.fetchall()]
    if 'JSON' not in columns:
        logger.warning('No JSON column in products table')
        return []

    # Group by unique key (same as schema UNIQUE constraint)
    sql = '''
    SELECT id,
           COALESCE("Product Name*", '') AS pname,
           COALESCE("Vendor/Supplier*", '') AS vendor,
           COALESCE("Product Brand", '') AS brand,
           COALESCE("Weight*", '') AS weight,
           "JSON" AS json_val
    FROM products
    '''
    cursor.execute(sql)
    rows = cursor.fetchall()

    groups = defaultdict(list)
    for row in rows:
        id_, pname, vendor, brand, weight, json_val = row
        key = (pname or '', vendor or '', brand or '', weight or '')
        proper = has_proper_json(json_val)
        json_len = len((json_val or '').strip())
        groups[key].append((id_, proper, json_len, json_val))

    # Only groups with more than one row are duplicates
    duplicate_groups = [(k, v) for k, v in groups.items() if len(v) > 1]
    return duplicate_groups


def choose_keep_id(rows_with_proper):
    """
    rows_with_proper = list of (id, has_proper_json, json_len, json_val).
    Keep: first row with proper JSON (prefer longer JSON), else row with smallest id.
    Ignores None ids (some DBs may have nullable id in edge cases).
    """
    with_proper = [(id_, jlen) for id_, proper, jlen, _ in rows_with_proper if proper and id_ is not None]
    if with_proper:
        # Keep id with longest JSON; tie-break by smallest id
        with_proper.sort(key=lambda x: (-x[1], x[0]))
        return with_proper[0][0]
    # No proper JSON: keep smallest id (skip None ids)
    valid_ids = [id_ for id_, _, _, _ in rows_with_proper if id_ is not None]
    if not valid_ids:
        # Fallback: keep first row by position (first non-None or first id in list)
        return rows_with_proper[0][0] if rows_with_proper else None
    return min(valid_ids)


def remove_duplicates_no_json(db_path: str, dry_run: bool = False) -> int:
    """
    Delete duplicate product rows, keeping the one with proper JSON per group.
    Returns number of rows deleted.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM products')
    total_before = cursor.fetchone()[0]

    groups = get_duplicate_groups(cursor)
    if not groups:
        logger.info(f'  No duplicate groups found in {Path(db_path).name}')
        conn.close()
        return 0

    to_delete = []
    for key, rows in groups:
        keep_id = choose_keep_id(rows)
        if keep_id is None:
            continue
        for id_, proper, json_len, _ in rows:
            if id_ is not None and id_ != keep_id:
                to_delete.append(id_)

    deleted_count = len(to_delete)
    if deleted_count == 0:
        conn.close()
        return 0

    logger.info(f'  Duplicate groups: {len(groups)}')
    logger.info(f'  Rows to delete (duplicates without keeping best): {deleted_count}')

    if dry_run:
        logger.info('  [DRY RUN] Would delete ids: %s', to_delete[:20])
        if len(to_delete) > 20:
            logger.info('  ... and %d more', len(to_delete) - 20)
        conn.close()
        return deleted_count

    # Delete in batches to avoid huge IN list
    batch_size = 500
    for i in range(0, len(to_delete), batch_size):
        batch = to_delete[i : i + batch_size]
        placeholders = ','.join(['?'] * len(batch))
        cursor.execute(f'DELETE FROM products WHERE id IN ({placeholders})', batch)
    conn.commit()
    conn.close()

    cursor2 = sqlite3.connect(db_path).cursor()
    cursor2.execute('SELECT COUNT(*) FROM products')
    total_after = cursor2.fetchone()[0]
    cursor2.connection.close()

    logger.info(f'  Deleted: {deleted_count} rows')
    logger.info(f'  Total products before: {total_before} -> after: {total_after}')
    return deleted_count


def main():
    parser = argparse.ArgumentParser(description='Remove duplicate products without proper JSON column data')
    parser.add_argument('--web', action='store_true', help='Use web UPLOADS_DIR and process store DBs')
    parser.add_argument('--store', type=str, default=None, help='Process only this store (e.g. AGT_Bothell)')
    parser.add_argument('--dry-run', action='store_true', help='Only report what would be deleted')
    parser.add_argument('--db', type=str, default=None, help='Path to single database file (overrides --web)')
    args = parser.parse_args()

    if args.db:
        if not Path(args.db).exists():
            logger.error(f'Database not found: {args.db}')
            sys.exit(1)
        total_deleted = remove_duplicates_no_json(args.db, dry_run=args.dry_run)
        logger.info(f'Done. Deleted: {total_deleted}')
        return

    if args.web:
        uploads_dir = Path(UPLOADS_DIR)
        if not uploads_dir.exists():
            logger.error(f'Uploads dir not found: {UPLOADS_DIR}')
            sys.exit(1)
        stores = [args.store] if args.store else list(STORE_PATTERNS.values())
        total_deleted = 0
        for store_name in stores:
            db_path = uploads_dir / f'product_database_{store_name}.db'
            if not db_path.exists():
                logger.warning(f'  Skip (not found): {db_path.name}')
                continue
            logger.info(f'Processing: {db_path.name}')
            total_deleted += remove_duplicates_no_json(str(db_path), dry_run=args.dry_run)
        logger.info(f'Total rows deleted across all stores: {total_deleted}')
        return

    # Local default: current directory or parent, look for product_database_*.db
    local_dbs = list(Path('.').glob('product_database_*.db'))
    if not local_dbs:
        local_dbs = list(Path('.').glob('uploads/product_database_*.db'))
    if not local_dbs:
        logger.error('No product_database_*.db found. Use --db /path/to/db or --web')
        sys.exit(1)
    for db_path in local_dbs:
        logger.info(f'Processing: {db_path}')
        remove_duplicates_no_json(str(db_path), dry_run=args.dry_run)


if __name__ == '__main__':
    main()
