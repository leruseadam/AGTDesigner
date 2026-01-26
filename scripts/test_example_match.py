import logging
from pprint import pprint

logging.basicConfig(level=logging.INFO)

from src.core.data.enhanced_json_matcher import EnhancedJSONMatcher, MatchStrategy

example = {
    'product_name': 'Hawaiian Runtz Liquid Diamond Vaporizer 1.0g',
    'vendor': 'TRIGONAL INDUSTRIES',
    'inventory_type': 'Concentrate for Inhalation',
    'unit_weight': 1.0,
    'unit_weight_uom': 'g'
}

matcher = EnhancedJSONMatcher(None)
results = matcher.match_products([example], strategy=MatchStrategy.HYBRID)

print('\n=== MATCH RESULTS ===')
if not results or results[0] is None:
    print('No match returned')
else:
    best = results[0]
    print('Score:', getattr(best, 'score', None))
    md = getattr(best, 'match_data', {})
    print('DB Product Name:', md.get('Product Name*'))
    print('DB Product Type:', md.get('Product Type*'))
    print('DB Vendor:', md.get('Vendor/Supplier*') or md.get('Vendor'))
    print('Match Factors:')
    pprint(getattr(best, 'match_factors', {}))
