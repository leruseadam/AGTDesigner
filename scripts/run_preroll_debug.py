#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, get_product_database, get_current_store_name
from src.core.generation.preroll_tag_generator import generate_preroll_tags

class DummyCache:
    def __init__(self):
        self.store = {}
    def set(self, key, value, timeout=None):
        self.store[key] = value
        return True


def load_all_products(product_db):
    conn = product_db._get_connection()
    cursor = conn.cursor()
    # Get available columns dynamically
    cursor.execute("PRAGMA table_info(products)")
    cols = [row[1] for row in cursor.fetchall()]
    # Select all products
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
    app = create_app()
    with app.app_context():
        with app.test_request_context('/'):
            store = get_current_store_name()
            print('Using store:', store)
            product_db = get_product_database(store)
            product_db.init_database()
            records = load_all_products(product_db)
            print('Total products loaded:', len(records))
            cache = DummyCache()
            grouped = generate_preroll_tags(records, cache)
            print('Generated grouped labels:', len(grouped))
            # Print first 20 groups
            for i, g in enumerate(grouped[:20]):
                print(i+1, g.get('Product Name*'), g.get('_group_id'), g.get('_group_key'))

if __name__ == '__main__':
    # Avoid importing flask session here; it's accessed inside generate_preroll_tags
    from flask import session
    main()
