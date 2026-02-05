import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from src.core.data.advanced_matcher import AdvancedMatcher, MatchResult
import csv, json, requests, os, sys

matcher = AdvancedMatcher()
# load cultivera json
URL='https://files.cultivera.com/435553542D5753313835/Interop/25/44/HHPBSZMVT6QT56JS/Cultivera_ORD-28444_422044.json'
resp = requests.get(URL, timeout=30)
js = resp.json()
items = js.get('inventory_transfer_items') or []
# find query
query=None
for it in items:
    name = it.get('product_name','') or it.get('product','')
    if 'skunk #1' in name.lower():
        query=it
        break
if not query:
    print('query not found')
    sys.exit(1)
qname = query.get('product_name') or query.get('product')
# load candidates
candidates=[]
with open('scripts/debug/all_mappings_cultivera.csv', encoding='utf-8') as f:
    r = csv.DictReader(f)
    for row in r:
        candidates.append(row)
# find alien runtz
cand=None
for c in candidates:
    if 'alien runtz' in (c.get('product_name') or '').lower():
        cand=c
        break
if not cand:
    print('candidate not found')
    sys.exit(1)

try:
    ai = matcher.calculate_ai_powered_scores(qname, cand['product_name'], query, cand)
    mr = MatchResult(item=cand, overall_score=0.0, fuzzy_score=ai.get('core_ngram', ai.get('ngram',0)), semantic_score=ai.get('keywords',0), phonetic_score=ai.get('soundex',0), vendor_match=False, brand_match=False, type_match=False, weight_match=False, strain_match=False)
    mr.query_name = qname
    overall = matcher.calculate_overall_score_with_ai(mr, ai)
    print('Query:', qname)
    print('Candidate:', cand['product_name'])
    print('AI scores:', ai)
    print('Overall:', overall)
except Exception as e:
    import traceback
    print('ERROR during inspection:', e)
    traceback.print_exc()
