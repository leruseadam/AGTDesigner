#!/usr/bin/env python3
"""Add a `JSON` column to the `products` table in a SQLite products DB.

Usage:
  # Dry-run (shows actions, doesn't modify DB)
  python scripts/add_json_column_pa.py --db /path/to/product_database.db

  # Apply changes (add column, do not populate)
  python scripts/add_json_column_pa.py --db /path/to/product_database.db --apply

  # Apply and populate new column using an existing column named 'raw_json'
  python scripts/add_json_column_pa.py --db /path/to/product_database.db --apply --populate-from raw_json

  # Apply and populate by auto-building JSON from common fields
  python scripts/add_json_column_pa.py --db /path/to/product_database.db --apply --populate-from auto

This script is safe by default: it creates a timestamped backup before modifying the DB.
"""

import argparse
import sqlite3
import os
import shutil
import time
import json
from typing import List


def backup_db(path: str) -> str:
    ts = time.strftime('%Y%m%d_%H%M%S')
    dest = f"{path}.backup.{ts}.db"
    shutil.copy2(path, dest)
    return dest


def table_has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    cols = [r[1].lower() for r in cur.fetchall()]
    return column.lower() in cols


def add_column(conn: sqlite3.Connection, table: str, column: str, column_type: str = 'TEXT') -> None:
    cur = conn.cursor()
    cur.execute(f"ALTER TABLE {table} ADD COLUMN \"{column}\" {column_type};")
    conn.commit()


def populate_from_column(conn: sqlite3.Connection, table: str, source_col: str) -> int:
    cur = conn.cursor()
    # Only set JSON where JSON IS NULL or empty
    cur.execute(
        f"UPDATE {table} SET \"JSON\" = {source_col} WHERE (\"JSON\" IS NULL OR trim(\"JSON\") = '') AND {source_col} IS NOT NULL;"
    )
    conn.commit()
    return cur.rowcount


def populate_auto(conn: sqlite3.Connection, table: str, fields: List[str]) -> int:
    cur = conn.cursor()
    # Build JSON from a selection of columns for each row
    updated = 0
    cur.execute(f"SELECT rowid, * FROM {table};")
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    for row in rows:
        rowdict = dict(zip(cols, row))
        # Only populate when JSON empty
        cur_json = rowdict.get('JSON') or rowdict.get('json')
        if cur_json and str(cur_json).strip():
            continue

        obj = {}
        for f in fields:
            # map common names to actual db columns
            # try exact, then lowercase match
            if f in rowdict:
                obj[f] = rowdict.get(f)
            else:
                # case-insensitive fallback
                for k in rowdict.keys():
                    if k.lower() == f.lower():
                        obj[f] = rowdict.get(k)
                        break

        if not obj:
            continue

        try:
            jtext = json.dumps(obj, ensure_ascii=False)
            cur.execute(f"UPDATE {table} SET \"JSON\" = ? WHERE rowid = ?;", (jtext, rowdict['rowid']))
            updated += cur.rowcount
        except Exception:
            continue

    conn.commit()
    return updated


def create_index(conn: sqlite3.Connection, table: str, index_name: str = 'idx_products_json_sub') -> None:
    cur = conn.cursor()
    # Create a substring index to make simple prefix searches faster
    cur.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table} (substr(\"JSON\", 1, 200));")
    conn.commit()


def main():
    p = argparse.ArgumentParser(description='Add JSON column to products DB (safe: backups).')
    p.add_argument('--db', required=True, help='Path to the SQLite products DB')
    p.add_argument('--apply', action='store_true', help='Perform changes (default: dry-run)')
    p.add_argument('--populate-from', help="Populate JSON from an existing column name or 'auto' to build from common fields")
    p.add_argument('--create-index', action='store_true', help='Create a helper index on the JSON column')
    args = p.parse_args()

    db = args.db
    if not os.path.exists(db):
        print('ERROR: DB file not found:', db)
        return

    print('DB:', db)

    if not args.apply:
        print('DRY-RUN: no changes will be made. Use --apply to modify the DB.')

    # Connect (use timeout to avoid locks)
    conn = sqlite3.connect(db, timeout=20)

    try:
        if table_has_column(conn, 'products', 'JSON'):
            print('Column JSON already exists in products table. Nothing to do.')
            return

        if not args.apply:
            print('Would add column: ALTER TABLE products ADD COLUMN "JSON" TEXT;')
            if args.populate_from:
                if args.populate_from.lower() == 'auto':
                    print('Would populate JSON from auto-built fields (Product Name*, Product Type*, Product Strain, Price, Weight*)')
                else:
                    print(f'Would populate JSON from existing column: {args.populate_from}')
            if args.create_index:
                print('Would create index on JSON prefix substr(JSON,1,200)')
            return

        # Apply changes: backup then alter
        bak = backup_db(db)
        print('Backup created at', bak)

        print('Adding JSON column...')
        add_column(conn, 'products', 'JSON', 'TEXT')
        print('Column added.')

        if args.populate_from:
            if args.populate_from.lower() == 'auto':
                fields = ['Product Name*', 'Product Type*', 'Product Strain', 'Price', 'Weight*', 'Description']
                print('Populating JSON column by building JSON from fields:', fields)
                updated = populate_auto(conn, 'products', fields)
                print(f'Populated {updated} rows (auto).')
            else:
                source = args.populate_from
                print('Populating JSON column from existing column:', source)
                updated = populate_from_column(conn, 'products', f'"{source}"')
                print(f'Populated {updated} rows from {source}.')

        if args.create_index:
            print('Creating JSON substring index...')
            create_index(conn, 'products')
            print('Index created.')

        print('Done.')

    finally:
        conn.close()


if __name__ == '__main__':
    main()
