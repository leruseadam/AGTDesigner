#!/usr/bin/env python3
"""
Safe script to find and optionally update Ceres "apple/chew" products to MIXED lineage

Usage:
  python3 scripts/fix_ceres_apple_lineage.py --db uploads/product_database_AGT_Bothell.db --dry-run
  python3 scripts/fix_ceres_apple_lineage.py --db /path/to/web.db --apply

The script supports SQLite databases with the same `products` schema used locally.
It performs a SELECT to show matches and only runs an UPDATE when `--apply` is passed.
"""
import argparse
import sqlite3
import sys


def find_matches(conn, vendor_like='ceres', name_pattern='%apple%'):
    cur = conn.cursor()
    query = (
        "SELECT id, \"Product Name*\", \"Product Brand\", Lineage, canonical_lineage, sovereign_lineage, \"Product Strain\""
        " FROM products"
        " WHERE (LOWER(\"Product Brand\") LIKE ? OR LOWER(\"Vendor/Supplier*\") LIKE ? OR LOWER(\"Product Name*\") LIKE ? )"
    )
    cur.execute(query, (f"%{vendor_like}%", f"%{vendor_like}%", name_pattern))
    return cur.fetchall()


def apply_update(conn, ids):
    if not ids:
        return 0
    cur = conn.cursor()
    placeholders = ','.join('?' for _ in ids)
    update_sql = (
        f"UPDATE products SET Lineage='MIXED', canonical_lineage='MIXED', sovereign_lineage='MIXED' WHERE id IN ({placeholders})"
    )
    cur.execute(update_sql, ids)
    conn.commit()
    return cur.rowcount


def main():
    p = argparse.ArgumentParser(description='Fix Ceres apple-chew lineage to MIXED')
    p.add_argument('--db', required=True, help='Path to SQLite products DB')
    p.add_argument('--vendor', default='ceres', help='Vendor/brand substring to match')
    p.add_argument('--name-like', default='%apple%', help='SQL LIKE pattern for product name')
    p.add_argument('--apply', action='store_true', help='Apply updates (otherwise dry-run)')
    args = p.parse_args()

    try:
        conn = sqlite3.connect(args.db)
    except Exception as e:
        print('ERROR: could not open DB:', e, file=sys.stderr)
        sys.exit(2)

    matches = find_matches(conn, vendor_like=args.vendor.lower(), name_pattern=args.name_like.lower())
    print(f'Found {len(matches)} matching rows (sample up to 20):')
    for row in matches[:20]:
        print(row)

    if not matches:
        print('No matches. Exiting.')
        return

    ids = [r[0] for r in matches]

    if args.apply:
        updated = apply_update(conn, ids)
        print(f'Updated {updated} rows to MIXED')
    else:
        print('\nDry-run: no changes made. Rerun with --apply to perform update.')


if __name__ == '__main__':
    main()
