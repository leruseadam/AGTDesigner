import sys, os, json, requests
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.data.json_matcher import JSONMatcher
from src.core.data.product_database import ProductDatabase

URL = 'https://api-trace.getbamboo.com/shared/manifests/json/4jtd4tktnbrv1mtxjzhh47rphbw25rjqgrdAysrllbkf4654j26A4A5bgrrhc9jsjy6f4wdfmzndgl6n4r2w455gnn7cwvcgnr7h3tb5h35A5nk3g8tA4Atwgr2w47cqjbwvgsdfjf32cpj8'

print('Fetching manifest...')
resp = requests.get(URL, timeout=30)
resp.raise_for_status()
manifest = resp.json()

items = manifest.get('inventory_transfer_items') or manifest.get('items') or []
print(f'Found {len(items)} items')

# Use AGT_Bothell database (based on manifest to_license_name)
store_name = 'AGT_Bothell'
print(f'Loading product DB for store: {store_name}')
json_matcher = JSONMatcher(excel_processor=None)

results = []
for idx, item in enumerate(items):
    try:
        name = item.get('product_name') or item.get('inventory_name') or item.get('name') or f'JSON Item {idx+1}'
        match, confidence, reason = json_matcher.intelligent_match_product(item)
        if match:
            matched_name = match.get('Product Name*') or match.get('ProductName') or match.get('original_name') or match.get('Product Name') or 'UNKNOWN'
        else:
            matched_name = None
        results.append({
            'index': idx,
            'json_name': name,
            'matched_name': matched_name,
            'confidence': float(confidence or 0.0),
            'reason': reason,
        })
        print(f"{idx+1:03d}: '{name[:80]}' -> {matched_name} (conf={confidence:.3f}) reason={reason}")
    except Exception as e:
        print(f"Error matching item {idx}: {e}")
        results.append({
            'index': idx,
            'json_name': item,
            'error': str(e)
        })

out_path = '/tmp/bamboo_manifest_matches.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f'Wrote results to {out_path}')
