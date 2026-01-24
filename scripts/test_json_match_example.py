import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.data.enhanced_json_matcher import EnhancedJSONMatcher

jm = EnhancedJSONMatcher(None)
json_item = {'product_name':'Pure Prana Pulse AIO Disposable - Skunk #1 Live Resin - Hybrid - 1mL','brand':None,'vendor':None,'inventory_type':'Concentrate for Inhalation'}
db_products = [{'Product Name*':'Alien Runtz Pure Live Resin Disposable Vape by Bodhi High - 1g','ProductBrand':'Bodhi High','Product Type*':'Vape Cartridge'}]

jn = jm._get_product_name(json_item)
print('json raw:', jn)
print('json normalized:', jm._normalize_text(jn))

dbn = db_products[0]['Product Name*']
print('db raw:', dbn)
print('db normalized:', jm._normalize_text(dbn))

matches = jm._fuzzy_match(json_item, db_products)
print('matches count:', len(matches))
for m in matches:
    print('score:', m.score)
    print('factors:', m.match_factors)
    print('match name:', m.match_data.get('Product Name*'))

exact = jm._exact_match(json_item, db_products)
print('exact matches:', len(exact))
