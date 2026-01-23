#!/usr/bin/env python3
import sys, os, glob
sys.path.insert(0, os.path.abspath('.'))

from src.core.data.product_database import ProductDatabase
from src.core.generation.preroll_tag_generator import generate_preroll_tags, identify_preroll_product_group

class DummyCache:
    def __init__(self):
        self.store = {}
    def set(self, key, value, timeout=None):
        self.store[key] = value
        return True


def find_latest_db():
    base = os.path.abspath('uploads')
    patterns = [os.path.join(base, 'product_database_*.db'), os.path.join(base, 'product_database*.db')]
    candidates = []
    for p in patterns:
        candidates += glob.glob(p)
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def load_all_products(product_db):
    conn = product_db._get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(products)")
    cols = [row[1] for row in cursor.fetchall()]
    cursor.execute('SELECT * FROM products')
    rows = cursor.fetchall()
    records = []
    for row in rows:
        rec = {}
        for i, col in enumerate(cols):
            rec[col] = row[i]
        records.append(rec)
    return records


def main():
    db_path = find_latest_db()
    if not db_path:
        print('No product database file found in uploads/. Please upload a product database first.')
        return
    print('Using DB:', db_path)
    product_db = ProductDatabase(db_path=db_path)
    product_db.init_database()
    records = load_all_products(product_db)
    print('Total products loaded:', len(records))
    # Monkeypatch session used by generate_preroll_tags
    generate_preroll_tags.__globals__['session'] = {}
    cache = DummyCache()
    grouped = generate_preroll_tags(records, cache)
    print('Generated grouped labels:', len(grouped))
    # Print counts per group key from cache
    session = generate_preroll_tags.__globals__['session']
    print('Session group_keys stored:', len(session.get('preroll_group_keys', [])))
    # Print first 30 groups
    for i, g in enumerate(grouped[:30]):
        print(i+1, g.get('Product Name*'), g.get('_group_id'), g.get('_group_key'))
    
        # Diagnostic: find products that look like prerolls but got group_id == 'other'
        mismatches = []
        for rec in records:
            pt = (rec.get('Product Type*') or '')
            name = rec.get('Product Name*') or ''
            desc = rec.get('Description') or ''
            lower_check = (pt + ' ' + name + ' ' + desc).lower()
            if 'pre' in lower_check or 'roll' in lower_check:
                gid = identify_preroll_product_group(desc, name)['group_id']
                if gid == 'other':
                    mismatches.append((rec.get('Product Name*'), pt, gid, desc[:120]))
        print('Potential mismatches (preroll-like but grouped as other):', len(mismatches))
        for m in mismatches[:30]:
            print(m)

if __name__ == '__main__':
    main()
