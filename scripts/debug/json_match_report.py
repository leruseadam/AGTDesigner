#!/usr/bin/env python3
"""
Simple report tool to evaluate JSON->product-type mappings

Usage:
  python scripts/debug/json_match_report.py /path/to/inventory.json --output mismatches.csv

This will scan products in the JSON (list or dict with values) and report rows where the mapped
type differs from an existing `Product Type*` or `product_type` field.
"""
import sys
import os
import json
import csv
from src.core.data.json_matcher import map_inventory_type_to_product_type


def extract_fields(record):
    inventory_type = record.get('inventory_type') or record.get('inventoryType') or record.get('Inventory Type') or record.get('inventory_type_name') or record.get('type') or ''
    inventory_category = record.get('inventory_category') or record.get('inventoryCategory') or record.get('category') or ''
    product_name = record.get('product_name') or record.get('Product Name*') or record.get('productName') or record.get('inventory_name') or ''
    source_type = record.get('Product Type*') or record.get('product_type') or record.get('productType') or ''
    return inventory_type, inventory_category, product_name, source_type


def iter_products(data):
    # Accept either a list of products, or a dict with 'products' or 'items' keys
    if isinstance(data, list):
        for r in data:
            yield r
        return
    if isinstance(data, dict):
        for key in ('products', 'items', 'inventory', 'results'):
            if key in data and isinstance(data[key], list):
                for r in data[key]:
                    yield r
                return
        # fallback: iterate values if they are dicts
        for v in data.values():
            if isinstance(v, dict) and ('product' in v or 'product_name' in v or 'inventory_type' in v):
                yield v


def main():
    if len(sys.argv) < 2:
        print('Usage: json_match_report.py /path/to/inventory.json [--output out.csv]')
        sys.exit(2)

    path = sys.argv[1]
    out_path = None
    if '--output' in sys.argv:
        try:
            out_path = sys.argv[sys.argv.index('--output') + 1]
        except IndexError:
            out_path = 'mismatches.csv'

    if not os.path.exists(path):
        print('Path not found:', path)
        sys.exit(1)

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rows = []
    for rec in iter_products(data):
        inventory_type, inventory_category, product_name, source_type = extract_fields(rec)
        mapped = map_inventory_type_to_product_type(inventory_type, inventory_category, product_name)
        rows.append({
            'product_name': product_name,
            'inventory_type': inventory_type,
            'inventory_category': inventory_category,
            'source_type': source_type,
            'mapped_type': mapped
        })

    # If out_path specified, write CSV of mismatches (where source_type exists and differs)
    if out_path:
        with open(out_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['product_name', 'inventory_type', 'inventory_category', 'source_type', 'mapped_type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                if r['source_type'] and r['source_type'].strip().lower() != r['mapped_type'].strip().lower():
                    writer.writerow(r)
        print(f'Wrote mismatches to {out_path}')
    else:
        # Print all rows
        for r in rows:
            print(r)


if __name__ == '__main__':
    main()
