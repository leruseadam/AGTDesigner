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
results=matcher.match_products(items)
print('Total match result objects returned:', len(results))
print('\nTop 20 results:')
for i,m in enumerate(results[:20]):
    name = (m.match_data.get('Product Name*') if m.match_data else '')
    vendor = (m.match_data.get('Vendor/Supplier*') or m.match_data.get('Vendor') or '') if m.match_data else ''
    print(f"{i+1}. score={m.score:.3f} confidence={m.confidence:.3f} product='{str(name)[:80]}' vendor='{vendor}' strategy={m.strategy_used}")

high_conf = [m for m in results if m.score>=0.6]
print('\nHigh-confidence matches (score>=0.6):', len(high_conf))
print('Done')
