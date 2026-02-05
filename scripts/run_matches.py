import csv
import os
import sys

# ensure project root is on sys.path so `src` imports resolve
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.core.data.advanced_matcher import AdvancedMatcher, MatchResult

csv_path='scripts/debug/all_mappings_cultivera.csv'
matcher=AdvancedMatcher()

candidates=[]
with open(csv_path, newline='', encoding='utf-8') as f:
    r=csv.DictReader(f)
    for row in r:
        candidates.append({'product_name':row['product_name'],'inventory_type':row.get('inventory_type',''),'inventory_category':row.get('inventory_category','')})

cult_items=[
 'Pure Prana Pulse AIO Disposable - Rainbow Belts Live Resin - Hybrid - 1mL',
 'Pure Prana Pulse AIO Disposable - Skunk #1 Live Resin - Hybrid - 1mL',
 'Pure Prana Pulse AIO Disposable - GMO Live Resin - Indica Dominant - 1mL',
 'Honey Tree LR AIO Disposable Vape - Gelato 47 - Hybrid - 1mL',
 'Pure Terp Crystal - Purple Kush Live Resin - Indica Dominant - 1g'
]


def score_and_print(query):
    scores=[]
    for c in candidates:
        ai=matcher.calculate_ai_powered_scores(query, c['product_name'], c, {})
        mr=MatchResult(item={'Product Name*': c['product_name']}, overall_score=0.0, fuzzy_score=ai.get('core_ngram', ai.get('ngram',0)), semantic_score=ai.get('keywords',0), phonetic_score=ai.get('soundex',0), vendor_match=False, brand_match=False, type_match=False, weight_match=False, strain_match=False)
        overall=matcher.calculate_overall_score_with_ai(mr, ai)
        scores.append((overall, c['product_name'], ai))
    scores.sort(key=lambda x: x[0], reverse=True)
    print('\n=== Query:', query)
    for i,(sc,name,ai) in enumerate(scores[:5],1):
        print(f'\nTop {i}: {name}\n  Overall: {sc:.2f}\n  AI components:')
        for k in sorted(ai.keys()):
            print(f'    {k}: {ai[k]}')

for q in cult_items:
    score_and_print(q)
