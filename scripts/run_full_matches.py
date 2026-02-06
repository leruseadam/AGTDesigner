import os
import sys
import csv
import json
import requests

# ensure project root on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.core.data.advanced_matcher import AdvancedMatcher, MatchResult

# Settings
CULTIVERA_URL = 'https://files.cultivera.com/435553542D5753313835/Interop/25/44/HHPBSZMVT6QT56JS/Cultivera_ORD-28444_422044.json'
CSV_GLOBS = [
    'scripts/debug/all_mappings_cultivera.csv',
    'scripts/debug/all_mappings_cultivera_after_overrides.csv',
    'scripts/debug/mismatches_cultivera.csv'
]
OUT_CSV = 'scripts/debug/match_results_cultivera_full.csv'
TOP_K = 5

matcher = AdvancedMatcher()

# fetch Cultivera JSON
print('Fetching Cultivera JSON...')
resp = requests.get(CULTIVERA_URL, timeout=30)
resp.raise_for_status()
js = resp.json()

items = js.get('inventory_transfer_items') or js.get('inventory_transfer_items') or []
if not items:
    # try to search for the key anywhere
    for k in js:
        if isinstance(js[k], list) and len(js[k])>0 and isinstance(js[k][0], dict) and 'product_name' in js[k][0]:
            items = js[k]
            break

print(f'Found {len(items)} inventory items.')

# load candidates from CSVs
candidates = []
seen = set()
for path in CSV_GLOBS:
    if not os.path.exists(path):
        continue
    with open(path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            name = (row.get('product_name') or row.get('product') or '').strip()
            if not name:
                continue
            if name in seen:
                continue
            seen.add(name)
            candidates.append({
                'product_name': name,
                'inventory_type': row.get('inventory_type',''),
                'inventory_category': row.get('inventory_category',''),
                **row
            })
print(f'Loaded {len(candidates)} unique candidates from CSVs.')

# run matching
with open(OUT_CSV, 'w', newline='', encoding='utf-8') as out:
    fieldnames = ['query_index','query_name','candidate_rank','candidate_name','overall_score','weight_pattern','token_overlap','core_ngram','core_levenshtein','keywords','ngram','levenshtein','type_pattern']
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()

    for qi, it in enumerate(items):
        qname = it.get('product_name') or it.get('productName') or it.get('product') or ''
        if not qname:
            continue
        scores = []
        for c in candidates:
            # Pass json_item (it) and candidate (c) in the correct order
            ai = matcher.calculate_ai_powered_scores(qname, c['product_name'], it, c)
            mr = MatchResult(item={'Product Name*': c['product_name']}, overall_score=0.0, fuzzy_score=ai.get('core_ngram', ai.get('ngram',0)), semantic_score=ai.get('keywords',0), phonetic_score=ai.get('soundex',0), vendor_match=False, brand_match=False, type_match=False, weight_match=False, strain_match=False)
            # Attach original query name so gating rules can inspect strain tokens
            try:
                mr.query_name = qname
            except Exception:
                pass
            overall = matcher.calculate_overall_score_with_ai(mr, ai)
            scores.append((overall, c['product_name'], ai))
        scores.sort(key=lambda x: x[0], reverse=True)
        for rank, (sc, name, ai) in enumerate(scores[:TOP_K], start=1):
            row = {
                'query_index': qi,
                'query_name': qname,
                'candidate_rank': rank,
                'candidate_name': name,
                'overall_score': f'{sc:.2f}',
                'weight_pattern': ai.get('weight_pattern', ''),
                'token_overlap': ai.get('token_overlap', ''),
                'core_ngram': ai.get('core_ngram',''),
                'core_levenshtein': ai.get('core_levenshtein',''),
                'keywords': ai.get('keywords',''),
                'ngram': ai.get('ngram',''),
                'levenshtein': ai.get('levenshtein',''),
                'type_pattern': ai.get('type_pattern','')
            }
            writer.writerow(row)
print('Done. Results written to', OUT_CSV)
