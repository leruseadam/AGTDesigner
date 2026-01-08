import logging
import sys
import os
import time

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd

from src.core.data.excel_processor import ExcelProcessor
from src.core.data.product_database import ProductDatabase

logging.basicConfig(level=logging.DEBUG)


def run_test():
    ep = ExcelProcessor(store_name='AGT_Bothell')

    # Minimal row that mirrors fields used by background integration
    product = {
        'Product Name*': 'TEST BG PRODUCT 123',
        'ProductName': 'TEST BG PRODUCT 123',
        'Product Type*': 'Flower',
        'Vendor/Supplier*': 'BG Vendor',
        'Vendor': 'BG Vendor',
        'Product Brand': 'BG Brand',
        'Product Strain': 'BG Strain 001',
        'Price': '$0.00',
        'Lineage': 'HYBRID',
        'Weight*': '1',
        'Units': 'g'
    }

    ep.df = pd.DataFrame([product])

    # Force synchronous integration for test
    ep._schedule_product_db_integration(force_sync=True)

    db = ProductDatabase(store_name='AGT_Bothell')
    results = db.get_products_by_names(['TEST BG PRODUCT 123'])
    print('DB lookup results:', results)


if __name__ == '__main__':
    run_test()
