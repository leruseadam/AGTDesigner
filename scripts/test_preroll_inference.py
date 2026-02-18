import sys
import os

# Ensure project root is on sys.path so `src` package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib
preroll_mod = importlib.import_module('src.core.generation.preroll_tag_generator')
# Provide a simple session-like object to avoid Flask request-context errors during testing
class DummySession(dict):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.modified = False
    def get(self, key, default=None):
        return super().get(key, default)
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.modified = True

preroll_mod.session = DummySession()
generate_preroll_tags = preroll_mod.generate_preroll_tags

# Simple cache implementation for testing
class SimpleCache:
    def __init__(self):
        self._d = {}
    def set(self, k, v, timeout=None):
        self._d[k] = v
    def get(self, k, default=None):
        return self._d.get(k, default)

cache = SimpleCache()

# Sample records with subbrand-like product names and missing Product Brand
sample_products = [
    {'Product Name*': 'Honey Stixx Infused Pre-Roll - 0.5g', 'ProductName': 'Honey Stixx Infused Pre-Roll - 0.5g', 'Description': 'Honey Stixx Infused Pre-Roll - 0.5g', 'Product Type*': 'Pre-Roll'},
    {'Product Name*': 'Sugar Stix Classic Pre-Roll by SweetCo - 1g', 'ProductName': 'Sugar Stix Classic Pre-Roll by SweetCo - 1g', 'Description': 'Sugar Stix Classic Pre-Roll - 1g', 'Product Type*': 'Pre-Roll'},
    {'Product Name*': 'Flavour Stix Tropical Pre-Roll - 0.6g', 'ProductName': 'Flavour Stix Tropical Pre-Roll - 0.6g', 'Description': 'Flavour Stix Tropical - 0.6g', 'Product Type*': 'Pre-Roll'},
    {'Product Name*': 'Rosin Rolls Pack - 5x0.5g', 'ProductName': 'Rosin Rolls Pack - 5x0.5g', 'Description': 'Rosin Rolls Pack - 5x0.5g', 'Product Type*': 'Pre-Roll'},
    {'Product Name*': 'Bang Stix - 1g by BangCo', 'ProductName': 'Bang Stix - 1g by BangCo', 'Description': 'Bang Stix - 1g', 'Product Type*': 'Pre-Roll'},
    {'Product Name*': 'SnickerDoobie Pre-Roll - 1g', 'ProductName': 'SnickerDoobie Pre-Roll - 1g', 'Description': 'SnickerDoobie Pre-Roll - 1g', 'Product Type*': 'Pre-Roll'},
    {'Product Name*': 'Hash Holes Infused Pre-Roll', 'ProductName': 'Hash Holes Infused Pre-Roll', 'Description': 'Hash Holes Infused Pre-Roll', 'Product Type*': 'Pre-Roll'},
    {'Product Name*': 'SparkLers Mini Pre-Roll 0.5g', 'ProductName': 'SparkLers Mini Pre-Roll 0.5g', 'Description': 'SparkLers Mini Pre-Roll', 'Product Type*': 'Pre-Roll'},
    {'Product Name*': 'Melt Stix - 0.5g', 'ProductName': 'Melt Stix - 0.5g', 'Description': 'Melt Stix - 0.5g', 'Product Type*': 'Pre-Roll'},
    {'Product Name*': 'Bubble Hash Pre-Roll - 1g by Bubbly', 'ProductName': 'Bubble Hash Pre-Roll - 1g by Bubbly', 'Description': 'Bubble Hash Pre-Roll - 1g', 'Product Type*': 'Pre-Roll'},
]

print('Running preroll inference test with sample products...')
result = generate_preroll_tags(sample_products, cache)

print(f'Generated {len(result)} representative preroll records:')
for r in result:
    print('---')
    print('ProductName:', r.get('ProductName'))
    print('Brand:', r.get('Product Brand') or r.get('ProductBrand') or r.get('Brand'))
    print('Description:', r.get('Description'))
    print('Product Type*:', r.get('Product Type*'))

print('\nCached group keys:')
print(list(cache._d.keys()))
