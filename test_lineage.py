#!/usr/bin/env python3
from flask import Flask, session
from src.core.generation.preroll_tag_generator import generate_preroll_tags

class SimpleCache:
    def __init__(self):
        self._d = {}
    def set(self, k, v, timeout=None):
        self._d[k] = v
    def get(self, k, default=None):
        return self._d.get(k, default)

app = Flask(__name__)
app.secret_key = 'test-secret'

with app.test_request_context('/'):
    records = [
        {
            'Product Name*': 'Khalifa Kush - 7g',
            'Description': 'Khalifa Kush - 7g',
            # Insert non-breaking space and soft hyphen plus extra spaces
            'Lineage': 'Indica\u00A0\u00AD   Kush   Family',
            'Price': '$14'
        }
    ]
    cache = SimpleCache()
    grouped = generate_preroll_tags(records, cache)
    print('GROUPED COUNT:', len(grouped))
    for rep in grouped:
        print('REPRESENTATIVE Lineage:', repr(rep.get('Lineage')))
        print('REPRESENTATIVE ProductName:', rep.get('ProductName'))
    print('SESSION KEYS:', list(session.keys()))
    gkeys = session.get('preroll_group_keys', [])
    print('GROUP KEYS:', gkeys)
    for k in gkeys:
        items = cache.get(f'preroll_group_latest_{k}')
        print('CACHED ITEMS for', k, ':', items)
