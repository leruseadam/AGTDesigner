#!/usr/bin/env python3
import os
import json
import sys
import logging
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.data.product_database import ProductDatabase
from src.core.data.excel_processor import ExcelProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    store = 'AGT_Bothell'
    cache_dir = os.path.join('uploads', 'cache')
    cache_file = os.path.join(cache_dir, f'available_tags_{store}.json')

    # Backup existing cache
    if os.path.exists(cache_file):
        bak = cache_file + '.bak'
        logger.info(f'Backing up {cache_file} -> {bak}')
        os.replace(cache_file, bak)

    # Load all products from DB
    db = ProductDatabase(store_name=store)
    products = db.get_all_products()
    if not products:
        logger.warning('No products found in DB to rebuild tags')
        return

    # Convert to DataFrame
    df = pd.DataFrame(products)

    # Normalize DataFrame column names to match ExcelProcessor expectations
    # Many DB columns have quotes in names; attempt to use common names
    # For safety, rename keys that exist
    rename_map = {}
    for col in df.columns:
        new = col.replace('"', '').strip()
        rename_map[col] = new
    df.rename(columns=rename_map, inplace=True)

    ep = ExcelProcessor(store_name=store)
    ep.df = df

    # Get available tags and write cache
    tags = ep.get_available_tags()
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, 'w') as fh:
        json.dump(tags, fh)
    logger.info(f'Wrote {len(tags)} tags to {cache_file}')


if __name__ == '__main__':
    main()
