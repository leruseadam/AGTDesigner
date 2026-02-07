# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Fix non-classic product lineages in a products SQLite DB.

This is a cleaned, self-contained replacement for `fix_nonclassic_lineage.py`.
Usage examples:
  # dry-run with explicit DB
  python fix_nonclassic_lineage_fixed.py --db /path/to/store_products.db

  # dry-run auto-detect DB (searches workspace for *_products.db)
  python fix_nonclassic_lineage_fixed.py

  # download DB from URL then apply
  python fix_nonclassic_lineage_fixed.py --url https://host/file.db --apply

This script defaults to dry-run. Add --apply to perform updates.
"""

import argparse
import sqlite3
import sys
from typing import List
import ast
import os
import glob
import tempfile
import urllib.request
import shutil


def load_classic_types():
    try:
        from src.core.constants import CLASSIC_TYPES as CT
        return CT
    except Exception:
        pass

    here = os.path.dirname(os.path.abspath(__file__))
    cur = here
    for _ in range(6):
        candidate = os.path.join(cur, 'src', 'core', 'constants.py')
        if os.path.exists(candidate):
            try:
                with open(candidate, 'r', encoding='utf-8') as f:
                    node = ast.parse(f.read(), filename=candidate)
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if getattr(target, 'id', None) == 'CLASSIC_TYPES':
                                value = ast.literal_eval(stmt.value)
                                return set(value)
            except Exception:
                break
        cur = os.path.dirname(cur)

    return {"flower", "pre-roll", "infused pre-roll", "preroll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"}


CLASSIC_TYPES = load_classic_types()
VALID_NONCLASSIC_LINEAGES = {'MIXED', 'CBD', 'CBD_BLEND', 'THC'}
CBD_INDICATORS = ['CBD', 'HIGH CBD', 'CBG', 'CBN', 'CBC']


def is_classic_type(product_type: str) -> bool:
    if not product_type:
        return False
    pt = product_type.strip().lower()
    return pt in {ct.lower() for ct in CLASSIC_TYPES} or any(ct.lower() in pt for ct in CLASSIC_TYPES)


def has_cbd_from_strain(strain: str) -> bool:
    if not strain:
        return False
    s = strain.strip().upper()
    return any(ind in s for ind in CBD_INDICATORS)


def gather_nonclassic_rows(conn) -> List[tuple]:
    cur = conn.cursor()
    cur.execute(
        'SELECT id, "Product Name*", "Product Type*", "Product Strain", Lineage, canonical_lineage, sovereign_lineage, currentLineage FROM products'
    )
    rows = cur.fetchall()
    to_fix = []
    for r in rows:
        pid, name, ptype, strain, lineage, canonical, sovereign, current = r
        ptype = ptype or ''
        if is_classic_type(ptype):
            continue
        current_lineage = (lineage or current or canonical or '')
        cur_up = str(current_lineage).strip().upper()
        if cur_up in VALID_NONCLASSIC_LINEAGES:
            continue
        correct = 'CBD' if has_cbd_from_strain(strain) else 'MIXED'
        to_fix.append((pid, name, ptype, strain, cur_up, correct))
    return to_fix


def apply_updates(conn, fixes: List[tuple]) -> int:
    if not fixes:
        return 0
    cur = conn.cursor()
    updated = 0
    for pid, _, _, _, _, correct in fixes:
        cur.execute("UPDATE products SET Lineage=?, canonical_lineage=?, sovereign_lineage=?, currentLineage=? WHERE id=?",
                    (correct, correct, correct, correct, pid))
        updated += cur.rowcount
    conn.commit()
    return updated


def find_candidate_db_paths(search_root: str = '.'):
    patterns = ['**/*_products.db', '**/*products.db', '*_products.db', '*products.db']
    found = []
    for pat in patterns:
        found.extend(glob.glob(os.path.join(search_root, pat), recursive=True))
    seen = []
    for p in found:
        if p not in seen and os.path.isfile(p):
            seen.append(p)
    return seen


def download_db(url: str) -> str:
    tmp_dir = tempfile.mkdtemp(prefix='fix_lineage_')
    filename = os.path.join(tmp_dir, os.path.basename(url.split('?')[0]))
    with urllib.request.urlopen(url) as resp, open(filename, 'wb') as out:
        shutil.copyfileobj(resp, out)
    return filename


def main():
    p = argparse.ArgumentParser(description='Fix non-classic product lineages')
    p.add_argument('--db', required=False, help='Path to SQLite products DB (optional)')
    p.add_argument('--url', required=False, help='HTTP(S) URL to download a SQLite DB')
    p.add_argument('--apply', action='store_true', help='Apply changes (default: dry-run)')
    p.add_argument('--limit', type=int, default=0, help='Limit number of fixes applied (0 = no limit)')
    args = p.parse_args()

    db_path = None
    temp_download = None
    if args.db:
        db_path = args.db
    elif args.url:
        try:
            temp_download = download_db(args.url)
            db_path = temp_download
        except Exception as e:
            print('ERROR: could not download DB:', e, file=sys.stderr)
            sys.exit(2)
    else:
        candidates = find_candidate_db_paths('.')
        if len(candidates) == 1:
            db_path = candidates[0]
            print(f'Auto-detected DB: {db_path}')
        elif len(candidates) > 1:
            print('Multiple candidate DBs found; please supply --db pointing to the desired file:')
            for c in candidates:
                print(' -', c)
            sys.exit(2)
        else:
            print('No candidate DB found. Provide --db or --url.', file=sys.stderr)
            sys.exit(2)

    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        print('ERROR: could not open DB:', e, file=sys.stderr)
        if temp_download:
            shutil.rmtree(os.path.dirname(temp_download), ignore_errors=True)
        sys.exit(2)

    fixes = gather_nonclassic_rows(conn)
    print(f'Found {len(fixes)} non-classic products that would be fixed.')
    if fixes:
        print('\nSample fixes (first 50):')
        for f in fixes[:50]:
            pid, name, ptype, strain, cur_up, correct = f
            print(f'id={pid} name="{name}" type="{ptype}" strain="{strain}" current="{cur_up}" -> {correct}')

    if not args.apply:
        print('\nDry-run complete. Re-run with --apply to perform updates.')
        if temp_download:
            shutil.rmtree(os.path.dirname(temp_download), ignore_errors=True)
        return

    to_apply = fixes[:args.limit] if args.limit and args.limit > 0 else fixes
    updated = apply_updates(conn, to_apply)
    print(f'Applied updates to {updated} rows.')

    if temp_download:
        shutil.rmtree(os.path.dirname(temp_download), ignore_errors=True)


if __name__ == '__main__':
    main()
