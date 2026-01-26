#!/usr/bin/env python3
import logging
import json
from src.core.data.json_matcher import JSONMatcher

logging.basicConfig(level=logging.DEBUG, format='%(message)s')

URL = "https://files.cultivera.com/435553542D57533739/Interop/25/43/HCQJH01000C5PQZC/Cultivera_ORD-8799_422044.json"

def run(url=URL):
    print('Running diagnostic matcher for URL:', url)
    matcher = JSONMatcher(None)
    results = matcher.fetch_and_match_with_product_db(url)
    print('\n=== SUMMARY ===')
    print('Total matched items:', len(results))
    for idx, item in enumerate(results, 1):
        print('\n--- ITEM', idx, '---')
        if isinstance(item, dict):
            print('Name:', item.get('Product Name*'))
            print('Vendor:', item.get('Vendor/Supplier*'))
            print('Source:', item.get('Source'))
            if '_similarity_score' in item:
                print('Similarity:', item.get('_similarity_score'))
            if 'Weight*' in item or 'Units' in item:
                print('Weight:', item.get('Weight*'), item.get('Units'))
            # Print candidate details if present
            cand_key = None
            for k in item.keys():
                if k.startswith('_candidates') or k == 'candidates' or k == 'top_candidates':
                    cand_key = k
                    break
            if cand_key:
                print('Candidates (via', cand_key + '):')
                for c in item.get(cand_key, [])[:10]:
                    try:
                        name = c.get('Product Name*') or c.get('excel_name') or str(c)
                        vendor = c.get('Vendor/Supplier*') or c.get('excel_data', {}).get('Vendor/Supplier*') if isinstance(c, dict) else ''
                        score = c.get('_score') or c.get('score')
                        weight = c.get('Weight*') or (c.get('excel_data', {}).get('Weight*') if isinstance(c, dict) else None)
                        units = c.get('Units') or (c.get('excel_data', {}).get('Units') if isinstance(c, dict) else None)
                        print(' -', name, '| vendor:', vendor, '| score:', score, '| weight:', weight, units)
                    except Exception as e:
                        print(' - candidate print error:', e, 'raw:', c)
        else:
            print(item)

if __name__ == '__main__':
    run()
