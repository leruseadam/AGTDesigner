#!/usr/bin/env python3
"""
Fix non-classic product lineages in a products SQLite DB.

Rules:
- A product is "classic" if its Product Type matches an entry in `src.core.constants.CLASSIC_TYPES`.
- For non-classic products, allowed lineage values are ['MIXED','CBD','CBD_BLEND','THC'].
- If a non-classic product has a lineage outside the allowed set, set it to:
    - 'CBD' when Product Strain contains CBD indicators ('CBD','HIGH CBD','CBG','CBN','CBC')
    - otherwise 'MIXED'

This script is safe: default is dry-run; pass `--apply` to perform updates.
"""
import argparse
import sqlite3
import sys
from typing import List

import ast
import os


def load_classic_types():
    # Try importing from package first (when running inside virtualenv/project)
    try:
        from src.core.constants import CLASSIC_TYPES as CT
        return CT
    except Exception:
        pass

    # Fallback: attempt to locate src/core/constants.py relative to this script
    here = os.path.dirname(os.path.abspath(__file__))
    # walk up to repository root (max 5 levels)
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
                                # evaluate the assigned value safely
                                #!/usr/bin/env python3
                                """
                                Fix non-classic product lineages in a products SQLite DB.

                                Rules:
                                - A product is "classic" if its Product Type matches an entry in `src.core.constants.CLASSIC_TYPES`.
                                - For non-classic products, allowed lineage values are ['MIXED','CBD','CBD_BLEND','THC'].
                                - If a non-classic product has a lineage outside the allowed set, set it to:
                                    - 'CBD' when Product Strain contains CBD indicators ('CBD','HIGH CBD','CBG','CBN','CBC')
                                    - otherwise 'MIXED'

                                This script is safe: default is dry-run; pass `--apply` to perform updates.

                                Improvements in this version:
                                - `--db` is optional: the script will auto-detect a single candidate DB in the workspace.
                                - `--url` option to download a DB from an HTTP(S) URL for processing.
                                - Better user guidance when multiple candidate DBs are found.
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
                                    # Try importing from package first (when running inside virtualenv/project)
                                    try:
                                        from src.core.constants import CLASSIC_TYPES as CT
                                        return CT
                                    except Exception:
                                        pass

                                    # Fallback: attempt to locate src/core/constants.py relative to this script
                                    here = os.path.dirname(os.path.abspath(__file__))
                                    # walk up to repository root (max 5 levels)
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
                                                                # evaluate the assigned value safely
                                                                value = ast.literal_eval(stmt.value)
                                                                # ensure it's a set
                                                                return set(value)
                                            except Exception:
                                                break
                                        # go up one directory
                                        cur = os.path.dirname(cur)

                                    # Last-resort fallback
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
                                    # remove duplicates and ensure file exists
                                    seen = []
                                    for p in found:
                                        if p not in seen and os.path.isfile(p):
                                            seen.append(p)
                                    return seen


                                def download_db(url: str) -> str:
                                    # download to a temporary file and return path
                                    tmp_dir = tempfile.mkdtemp(prefix='fix_lineage_')
                                    filename = os.path.join(tmp_dir, os.path.basename(url.split('?')[0]))
                                    try:
                                        with urllib.request.urlopen(url) as resp, open(filename, 'wb') as out:
                                            shutil.copyfileobj(resp, out)
                                    except Exception:
                                        shutil.rmtree(tmp_dir, ignore_errors=True)
                                        raise
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
                                            print(f'Downloading DB from URL: {args.url}')
                                            temp_download = download_db(args.url)
                                            db_path = temp_download
                                        except Exception as e:
                                            print('ERROR: could not download DB:', e, file=sys.stderr)
                                            sys.exit(2)
                                    else:
                                        # try to auto-detect candidate DBs in the repo/workspace
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
                                        # cleanup temporary download if any
                                        if temp_download:
                                            shutil.rmtree(os.path.dirname(temp_download), ignore_errors=True)
                                        return

                                    to_apply = fixes[:args.limit] if args.limit and args.limit > 0 else fixes
                                    updated = apply_updates(conn, to_apply)
                                    print(f'Applied updates to {updated} rows.')

                                    # cleanup temporary download
                                    if temp_download:
                                        shutil.rmtree(os.path.dirname(temp_download), ignore_errors=True)


                                if __name__ == '__main__':
                                    main()
