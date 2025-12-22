import logging
import sys, os
# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.data.product_database import ProductDatabase

logging.basicConfig(level=logging.DEBUG)

def run_test():
    try:
        db = ProductDatabase(store_name='AGT_Bothell')
        product = {
            'Product Name*': 'TEST PRODUCT XYZ',
            'ProductName': 'TEST PRODUCT XYZ',
            'Product Type*': 'Flower',
            'Vendor/Supplier*': 'Test Vendor',
            'Vendor': 'Test Vendor',
            'Product Brand': 'Test Brand',
            'Price': '$0.00',
            'Lineage': 'HYBRID',
            'Weight*': '1',
            'Units': 'g'
        }
        pid = db.add_or_update_product(product)
        print('Result product_id:', pid)
    except Exception as e:
        print('Exception:', e)

if __name__ == '__main__':
    run_test()
