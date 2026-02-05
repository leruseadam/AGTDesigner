#!/usr/bin/env python3
"""Debug matcher for a single JSON item index and print top candidates."""
import sys
import requests
from src.core.data.enhanced_json_matcher import EnhancedJSONMatcher, MatchStrategy

URL = 'https://files.cultivera.com/435553542D5753313835/Interop/26/04/1SYBBSFRY4J4WAK3/Cultivera_ORD-30063_422044.json'

def main(idx: int = 42):
    m = EnhancedJSONMatcher(None)
    resp = requests.get(URL, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    items = payload.get('inventory_transfer_items') or payload.get('items') or payload.get('products') or payload.get('inventory') or []
    print('Total items in JSON:', len(items))
    if idx < 0 or idx >= len(items):
        print('Index out of range')
        return
    item = items[idx]
    print('JSON item name:', item.get('product_name') or item.get('inventory_name') or item.get('name'))
    normalized_item = dict(item)
    if 'product_name' in normalized_item and 'inventory_name' not in normalized_item:
        normalized_item['inventory_name'] = normalized_item['product_name']

    matches = m._match_single_product(normalized_item, MatchStrategy.HYBRID)
    if not matches:
        print('No matches returned')
        return

    for i, mm in enumerate(matches[:10]):
        print('\nCandidate', i)
        print(' Score:', getattr(mm, 'score', None))
        md = getattr(mm, 'match_data', None)
        if isinstance(md, dict):
            print(' Product Name*:', md.get('Product Name*'))
            print(' Price:', md.get('Price') or md.get('Unit Price') or md.get('Wholesale Cost'))
            print(' Units/Weight:', md.get('Weight*'), md.get('Units'))
        print(' Match factors:', getattr(mm, 'match_factors', None))

if __name__ == '__main__':
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    main(idx)
