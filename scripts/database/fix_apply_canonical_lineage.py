#!/usr/bin/env python3
"""
Simple DB fixer: copy canonical/sovereign lineage from `strains` into `products`.

Usage:
  python fix_apply_canonical_lineage.py [--db PATH] [--apply] [--backup-dir PATH]

By default the script targets `uploads/product_database_AGT_Bothell.db` if present,
otherwise `uploads/product_database.db`.
"""
import argparse
import os
import shutil
import sqlite3
import time
from datetime import datetime


def choose_db_path(provided):
    if provided:
        return provided
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    uploads = os.path.join(base, 'uploads')
    bothell = os.path.join(uploads, 'product_database_AGT_Bothell.db')
    main = os.path.join(uploads, 'product_database.db')
    if os.path.exists(bothell):
        return bothell
    return main


def backup_db(db_path, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    base = os.path.basename(db_path)
    dest = os.path.join(backup_dir, f"{base}.bak.{ts}")
    print(f"Backing up {db_path} -> {dest}")
    shutil.copy2(db_path, dest)
    return dest


def open_conn(db_path):
    conn = sqlite3.connect(db_path, timeout=30)
    cur = conn.cursor()
    # Pragmas for safer writes
    cur.execute('PRAGMA journal_mode = WAL')
    cur.execute('PRAGMA synchronous = NORMAL')
    cur.execute('PRAGMA busy_timeout = 30000')
    return conn


def gather_strains(conn):
    cur = conn.cursor()
    try:
        cur.execute('SELECT id, strain_name, canonical_lineage, sovereign_lineage FROM strains')
    except Exception:
        # Table may not exist or different schema
        print('No `strains` table or unexpected schema. Exiting.')
        return []
    rows = cur.fetchall()
    strains = []
    for r in rows:
        sid, name, canonical, sovereign = r
        strains.append({
            'id': sid,
            'name': name or '',
            'canonical': canonical or '',
            'sovereign': sovereign or ''
        })
    return strains


def estimate_updates(conn, strains):
    cur = conn.cursor()
    plan = []
    total = 0
    for s in strains:
        use_lineage = s['sovereign'].strip() or s['canonical'].strip()
        if not use_lineage:
            continue
        # Count products with strain_id OR product strain name match (case-insensitive)
        cur.execute('''
            SELECT COUNT(*) FROM products
            WHERE strain_id = ?
               OR LOWER(TRIM("Product Strain")) = LOWER(TRIM(?))
        ''', (s['id'], s['name']))
        c = cur.fetchone()[0]
        if c:
            plan.append((s, use_lineage, c))
            total += c
    return plan, total


def apply_updates(conn, plan):
    cur = conn.cursor()
    applied = 0
    for s, lineage, count in plan:
        cur.execute('''
            UPDATE products
            SET "Lineage" = ?, sovereign_lineage = ?
            WHERE strain_id = ?
               OR LOWER(TRIM("Product Strain")) = LOWER(TRIM(?))
        ''', (lineage, lineage, s['id'], s['name']))
        applied += cur.rowcount
        print(f"  Applied to strain id={s['id']} name='{s['name']}' -> {cur.rowcount} rows")
    conn.commit()
    try:
        cur.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    except Exception:
        pass
    return applied


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db', help='Path to sqlite DB file')
    p.add_argument('--apply', action='store_true', help='Apply changes (default is dry-run)')
    p.add_argument('--backup-dir', help='Backup directory', default=None)
    args = p.parse_args()

    db_path = choose_db_path(args.db)
    if not os.path.exists(db_path):
        print(f'Database file not found: {db_path}')
        return

    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    default_backup = os.path.join(base, 'uploads', 'db_backups')
    backup_dir = args.backup_dir or default_backup

    if args.apply:
        backup_db(db_path, backup_dir)

    conn = open_conn(db_path)

    try:
        strains = gather_strains(conn)
        print(f'Found {len(strains)} strains')
        plan, total = estimate_updates(conn, strains)
        print(f'Planned updates for {len(plan)} strains affecting {total} product rows')
        if not args.apply:
            print('Dry-run mode (no changes applied). Use --apply to persist updates.')
            # Show short sample
            for s, lineage, c in plan[:30]:
                print(f"  id={s['id']} name='{s['name']}' -> '{lineage}' ({c} rows)")
            return

        # Apply
        applied = apply_updates(conn, plan)
        print(f'Applied updates to {applied} product rows')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
