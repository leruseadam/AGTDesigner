import json
import logging
import re
from pprint import pprint

logging.basicConfig(level=logging.INFO)

from src.core.data.json_matcher import JSONMatcher
try:
    from fuzzywuzzy import fuzz
except Exception:
    fuzz = None

m = JSONMatcher(None)
print('Building sheet cache from ProductDatabase...')
try:
    m._build_cache_from_database()
    print('Sheet cache length:', len(m._sheet_cache) if m._sheet_cache else 0)
except Exception as e:
    print('Failed to build sheet cache:', e)

items = [
    {"product_name":"Gelato 33 1G","brand":None,"vendor":"MT Baker Homegrown","type":"Usable Marijuana"},
    {"product_name":"Gelato 33 3.5G","brand":None,"vendor":"MT Baker Homegrown","type":"Usable Marijuana"},
    {"product_name":"Gelato 33 28G","brand":None,"vendor":"MT Baker Homegrown","type":"Usable Marijuana"},
    {"product_name":"Gelato 33 14G","brand":None,"vendor":"MT Baker Homegrown","type":"Usable Marijuana"}
]
url = 'data:application/json,' + json.dumps(items)

print('\nRunning fetch_and_match...')
res = m.fetch_and_match(url)
print('\nMatches returned:', len(res))
for i, r in enumerate(res):
    print('\n--- Item', i+1)
    print('JSON name:', items[i]['product_name'])
    if isinstance(r, dict):
        pprint({
            'Matched DB': r.get('Product Name*'),
            'Vendor': r.get('Vendor/Supplier*'),
            'Weight*': r.get('Weight*'),
            'Similarity': r.get('_similarity_score'),
            'Source': r.get('Source')
        })
    else:
        print('Result (non-dict):', r)

# Additional diagnostics: list top candidate products from sheet cache for Gelato 33
print('\nDiagnostic candidate list (from sheet cache):')
base = 'gelato 33'
candidates = []
if m._sheet_cache:
    for c in m._sheet_cache:
        name = (c.get('original_name') or c.get('Product Name*') or '').lower()
        vendor = (c.get('vendor') or c.get('Vendor/Supplier*') or '').lower()
        if base in name and ('mt baker' in vendor or 'mt baker homegrown' in vendor):
            candidates.append(c)

print(f'Found {len(candidates)} candidates matching "{base}" and vendor filter')
if fuzz:
    for c in sorted(candidates, key=lambda x: float(x.get('Weight*') or 0), reverse=False)[:20]:
        name = (c.get('original_name') or c.get('Product Name*') or '')
        weight = c.get('Weight*') or c.get('weight') or ''
        vendor = c.get('vendor') or c.get('Vendor/Supplier*') or ''
        score = fuzz.token_sort_ratio('Gelato 33 1G', name)
        pprint({'name': name, 'vendor': vendor, 'weight': weight, 'fuzz_score_vs_1G': score})
else:
    print('fuzzywuzzy not available; listing basic fields')
    for c in candidates[:20]:
        name = (c.get('original_name') or c.get('Product Name*') or '')
        weight = c.get('Weight*') or c.get('weight') or ''
        vendor = c.get('vendor') or c.get('Vendor/Supplier*') or ''
        pprint({'name': name, 'vendor': vendor, 'weight': weight})

print('\nDone.')
