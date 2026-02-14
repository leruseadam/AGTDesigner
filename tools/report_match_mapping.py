import sys,os,requests,json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.data.enhanced_json_matcher import EnhancedJSONMatcher

url='https://files.cultivera.com/435553542D5753363133/Interop/25/35/6XPJPXVK8N4NPTZ9/Cultivera_ORD-38588_422044.json'
print('Fetching JSON...')
r=requests.get(url,timeout=30)
payload=r.json()
items=payload.get('inventory_transfer_items',[]) or payload.get('items',[])
print('JSON items:',len(items))
matcher=EnhancedJSONMatcher(None)

from pprint import pprint

for item in items:
    name = item.get('product_name') or item.get('inventory_name') or ''
    token = name.strip()
    # get top matches for this item
    matches = matcher._match_single_product(item, matcher.MatchStrategy.HYBRID if hasattr(matcher,'MatchStrategy') else None)
    top = matches[0] if matches else None
    matched_db_name = ''
    matched_db_json = ''
    matched_id = ''
    score = 0.0
    strat = ''
    if top and top.match_data:
        md = top.match_data
        matched_db_name = md.get('Product Name*') or md.get('ProductName') or ''
        matched_db_json = md.get('JSON') or md.get('json') or ''
        matched_id = md.get('id') or md.get('ID') or ''
        score = top.score
        strat = str(top.strategy_used)
    print('---')
    print('JSON:', token)
    print('Top match score:', score, 'strategy:', strat)
    print('DB name:', matched_db_name)
    print('DB JSON column:', matched_db_json)
    print('Exact JSON match?', str(token) == str(matched_db_json))

print('Done')
