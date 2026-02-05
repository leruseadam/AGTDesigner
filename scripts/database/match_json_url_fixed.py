#!/usr/bin/env python3
"""
Fetch a JSON URL and run EnhancedJSONMatcher.fetch_and_match on it.
If any JSON items are unmatched, produce a guaranteed faux match result so every
input has a match (score/confidence marked low). Outputs CSV to outputs/match_results.csv
"""
import os
import sys
import csv
import logging
from pathlib import Path

# allow running from repo root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

URL = os.environ.get('JSON_URL') or ('https://files.cultivera.com/435553542D5753313835/Interop/26/04/1SYBBSFRY4J4WAK3/Cultivera_ORD-30063_422044.json')

logging.basicConfig(level=logging.INFO)

try:
    from src.core.data.enhanced_json_matcher import EnhancedJSONMatcher
except Exception as e:
    logging.error('Failed to import EnhancedJSONMatcher: %s', e)
    raise

import pandas as pd
import requests


# Minimal ExcelProcessor stub expected by EnhancedJSONMatcher
class _ExcelProcessorStub:
    def __init__(self):
        # Provide an empty DataFrame to avoid ML/model building
        self.df = pd.DataFrame()
        self._store_name = 'AGT_Bothell'


def ensure_match_for_item(item, match_entry):
    if match_entry:
        return match_entry
    # Build a faux match result with low confidence
    faux = {
        'matched_name': f"FAUX_MATCH: {item.get('product_name') or item.get('product') or item.get('product_name', '')}",
        'strategy': 'faux',
        'score': 0.01,
        'confidence': 0.10,
        'match_data': {},
        'faux': True
    }
    return faux


def main(url: str):
    m = EnhancedJSONMatcher(_ExcelProcessorStub())
    logging.info('Running fetch_and_match on %s', url)

    # Fetch original JSON items so we can preserve original names and ordering
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:
        logging.warning('Failed to fetch original JSON payload separately: %s', e)
        payload = None

    # Normalize json_items list from payload
    json_items = []
    if isinstance(payload, list):
        json_items = payload
    elif isinstance(payload, dict):
        json_items = payload.get('inventory_transfer_items') or payload.get('items') or payload.get('products') or payload.get('inventory') or []

    results = m.fetch_and_match(url)

    # results is a list of matched product dicts or structures - normalize
    outdir = Path('outputs')
    outdir.mkdir(exist_ok=True)
    out_csv = outdir / 'match_results.csv'

    with out_csv.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=['index','JSON_Item_Name','Product Name*','matched_name','strategy','score','confidence','faux'])
        writer.writeheader()

        # If fetch_and_match returned fewer entries than JSON items, we need to also fetch the JSON items
        # For simplicity, EnhancedJSONMatcher returns matched_products length equal to JSON items when successful
        for i, entry in enumerate(results):
            # Try to extract common fields
            if not entry:
                # we don't have the original JSON item here; create minimal record
                faux = {'matched_name': 'FAUX_MATCH_MISSING_ENTRY', 'strategy':'faux','score':0.01,'confidence':0.1,'faux':True}
                writer.writerow({'index': i, 'JSON_Item_Name': '', 'Product Name*': faux['matched_name'], 'matched_name': faux['matched_name'], 'strategy': faux['strategy'], 'score': faux['score'], 'confidence': faux['confidence'], 'faux': True})
                continue

            # Prefer canonical product name fields
            matched_name = None
            if isinstance(entry, dict):
                matched_name = entry.get('Product Name*') or entry.get('ProductName') or entry.get('matched_name') or entry.get('name') or entry.get('displayName')
                if not matched_name and isinstance(entry.get('match_data'), dict):
                    matched_name = entry['match_data'].get('Product Name*') or entry['match_data'].get('product_name') or entry['match_data'].get('name')

            strategy = entry.get('Match_Algorithm') or entry.get('strategy') or entry.get('strategy_used') or entry.get('method') or 'unknown'
            score = float(entry.get('Match_Score') or entry.get('score') or entry.get('confidence') or 0.0)
            confidence = float(entry.get('confidence') or entry.get('Match_Score') or entry.get('score') or 0.0)
            faux_flag = bool(entry.get('faux', False))

            # Determine original JSON item name (preserve order if possible)
            json_name = ''
            if i < len(json_items):
                ji = json_items[i]
                if isinstance(ji, dict):
                    json_name = ji.get('product_name') or ji.get('inventory_name') or ji.get('name') or ''
                else:
                    json_name = str(ji)
            else:
                json_name = entry.get('JSON_Item_Name') or entry.get('json_name') or entry.get('product_name') or entry.get('inventory_name') or ''

            # If no matched name, generate a faux match
            if not matched_name:
                faux = ensure_match_for_item({'product_name': json_name}, None)
                matched_name = faux['matched_name']
                strategy = faux['strategy']
                score = faux['score']
                confidence = faux['confidence']
                faux_flag = True

            # Also mark as faux if score is very low
            SCORE_THRESHOLD = float(os.environ.get('MATCH_SCORE_THRESHOLD', 0.20))
            if (score or 0.0) < SCORE_THRESHOLD:
                faux_flag = True

            writer.writerow({'index': i, 'JSON_Item_Name': json_name, 'Product Name*': matched_name, 'matched_name': matched_name, 'strategy': strategy, 'score': float(score), 'confidence': float(confidence), 'faux': bool(faux_flag)})

    logging.info('Wrote results to %s', out_csv)


if __name__ == '__main__':
    main(URL)
