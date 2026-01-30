#!/usr/bin/env python3
"""
Script: fix_copy_canonical_lineage.py

Backs up `uploads/product_database.db` and copies canonical/sovereign lineage
from the `strains` table into the `products.Lineage` and `products.sovereign_lineage`
fields for all products that are linked to a strain (by `strain_id`) or match the
strain name in the `Product Strain` column.

Usage:
  python scripts/database/fix_copy_canonical_lineage.py         # dry-run, no changes
  python scripts/database/fix_copy_canonical_lineage.py --apply # perform updates
  python scripts/database/fix_copy_canonical_lineage.py --db path/to/db --apply

The script is safe to run multiple times. It creates a timestamped backup before
making any changes.
"""
import argparse
import os
import shutil
import sqlite3
import time
from datetime import datetime

DEFAULT_DB = os.path.join(os.getcwd(), 'uploads', 'product_database.db')
BACKUP_DIR = os.path.join(os.getcwd(), 'uploads', 'db_backups')


def ensure_backup(db_path: str) -> str:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base = os.path.basename(db_path)
    backup_name = f"{base}.backup.{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    shutil.copy2(db_path, backup_path)
    return backup_path


def normalize(s):
    if s is None:
        return None
    return str(s).strip()


def main():
    parser = argparse.ArgumentParser(description='Copy canonical lineage from strains to products')
    parser.add_argument('--db', default=DEFAULT_DB, help='Path to product_database.db')
    parser.add_argument('--apply', action='store_true', help='Apply updates (default is dry-run)')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    args = parser.parse_args()

    db_path = args.db
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at: {db_path}")
        return 2

    print(f"Using database: {db_path}")
    if args.apply:
        print("Creating backup before applying changes...")
        backup_path = ensure_backup(db_path)
        print(f"Backup created: {backup_path}")
    else:
        print("Dry-run mode (no changes). Use --apply to make changes.")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        # Fetch all strains with canonical or sovereign lineage
        cur.execute("SELECT id, strain_name, canonical_lineage, sovereign_lineage FROM strains")
        strains = cur.fetchall()
        if not strains:
            print("No strains found in database; nothing to do.")
            return 0

        total_products_checked = 0
        total_products_will_update = 0
        total_products_updated = 0

        for s in strains:
            sid = s['id']
            sname = normalize(s['strain_name'])
            canon = normalize(s['canonical_lineage'])
            sov = normalize(s['sovereign_lineage'])

            # Prefer sovereign_lineage if set, otherwise canonical_lineage
            target_lineage = sov or canon
            if not target_lineage:
                if args.verbose:
                    print(f"Skipping strain id={sid} '{sname}': no canonical/sovereign lineage")
                continue

            # Count matching products
            cur.execute(
                """
                SELECT COUNT(*) as cnt
                FROM products
                WHERE strain_id = ?
                   OR (LOWER(TRIM("Product Strain")) = LOWER(TRIM(?)))
                """,
                (sid, sname)
            )
            cnt_row = cur.fetchone()
            cnt = cnt_row['cnt'] if cnt_row else 0
            total_products_checked += cnt
            if cnt == 0:
                if args.verbose:
                    print(f"No products for strain id={sid} '{sname}'")
                continue

            # Show preview of what would change: how many rows and the target value
            print(f"Strain id={sid} '{sname}': {cnt} product(s) -> set Lineage and sovereign_lineage to '{target_lineage}'")
            total_products_will_update += cnt

            if args.apply:
                try:
                    cur.execute(
                        """
                        UPDATE products
                        SET "Lineage" = ?, sovereign_lineage = ?
                        WHERE strain_id = ?
                           OR (LOWER(TRIM("Product Strain")) = LOWER(TRIM(?)))
                        """,
                        (target_lineage, target_lineage, sid, sname)
                    )
                    updated = cur.rowcount
                    total_products_updated += updated
                    if args.verbose:
                        print(f"  -> Updated {updated} rows for strain id={sid}")
                except Exception as e:
                    print(f"  WARNING: failed to update products for strain id={sid} '{sname}': {e}")

        if args.apply:
            conn.commit()
            # Force WAL checkpoint if pragmas are supported
            try:
                cur.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            except Exception:
                pass

        # Summary
        print("\nSummary:")
        print(f"  Strains processed: {len(strains)}")
        print(f"  Products matched: {total_products_checked}")
        print(f"  Products to update: {total_products_will_update} (dry-run)")
        if args.apply:
            print(f"  Products updated: {total_products_updated}")
            print("  Changes committed.")
        else:
            print("  No changes applied (dry-run). Use --apply to commit changes.")

        return 0

    finally:
        conn.close()


if __name__ == '__main__':
    raise SystemExit(main())
