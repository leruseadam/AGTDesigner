import os
import sys
import json
import requests

# ensure repo root in path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.core.data.enhanced_json_matcher import EnhancedJSONMatcher

URL = "https://files.cultivera.com/435553542D5753313835/Interop/25/44/HHPBSZMVT6QT56JS/Cultivera_ORD-28444_422044.json"

print(f"Fetching {URL}...")
resp = requests.get(URL, timeout=30)
resp.raise_for_status()
obj = resp.json()

items = obj.get('inventory_transfer_items') or obj.get('inventory_items') or []
print(f"Found {len(items)} inventory items")

# Instantiate matcher
matcher = EnhancedJSONMatcher(excel_processor=None)

# function to pretty print matches

def dump_matches(item, matches):
    name = item.get('product_name') or item.get('inventory_name') or item.get('name')
    print('\n=== ITEM: ' + (name[:200] if name else '<no name>') + ' ===')
    # show extracted name and weight
    try:
        product_name = matcher.product_matcher._get_product_name(item) or name
    except Exception:
        product_name = name
    print('Normalized Name:', product_name)
    try:
        extracted_weight = matcher._extract_weight(product_name or '')
    except Exception:
        extracted_weight = None
    print('Extracted weight (g):', extracted_weight)

    for i, m in enumerate(matches[:8]):
        md = m.match_data
        db_name = md.get('Product Name*') or md.get('Product Name') or md.get('ProductName') or md.get('Product') or '<no db name>'
        print(f"\nCandidate {i+1}: {db_name}")
        print(f"  score={m.score:.4f} confidence={m.confidence:.4f}")
        try:
            mf = getattr(m, 'match_factors', {}) or {}
            for k, v in mf.items():
                print(f"    {k}: {v}")
        except Exception as e:
            print('   (no factors)')
        # show db weights if present
        try:
            db_w = md.get('WeightWithUnits') or md.get('CombinedWeight') or md.get('Weight*') or md.get('Units')
            print('    db_weight:', db_w)
        except Exception:
            pass


# find problematic items containing 'Skunk #1' or 'Pure Prana Pulse AIO Disposable - Skunk #1'
candidates = [it for it in items if it.get('product_name') and 'skunk #1' in it.get('product_name').lower()]
if not candidates:
    # fallback: look for 'Pure Prana' items
    candidates = [it for it in items if it.get('product_name') and 'pure prana' in it.get('product_name').lower()]

print(f"Diagnostic candidates: {len(candidates)}")

if not candidates and items:
    # pick first few items
    candidates = items[:3]

for item in candidates:
    # run matcher
    try:
        matches = matcher.match_products([item])
    except Exception as e:
        print('Matcher error:', e)
        # try fuzzy via internal methods
        matches = []
    dump_matches(item, matches)

print('\nDiagnostics complete')
