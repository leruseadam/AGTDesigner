#!/usr/bin/env python3
"""
Test script to check if novel products are being created correctly.
"""

import sys
import os
import logging
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_novel_products.log')
    ]
)

def test_novel_products():
    """Test novel product creation."""
    
    logging.info("🚀 Starting Novel Products Test")
    logging.info(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Import the JSON matcher
        from src.core.data.json_matcher import JSONMatcher
        from src.core.data.product_database import ProductDatabase
        from src.core.data.excel_processor import ExcelProcessor
        
        # Initialize the Excel processor and JSON matcher
        excel_processor = ExcelProcessor()
        json_matcher = JSONMatcher(excel_processor)
        
        # Create a test JSON item that definitely doesn't exist in Excel data
        test_json_item = {
            "product_name": "SUPER RARE TEST PRODUCT 999999",
            "vendor": "TEST VENDOR",
            "brand": "TEST BRAND",
            "inventory_type": "concentrate",
            "unit_weight": "1.0",
            "strain_name": "TEST STRAIN",
            "quantity": "1",
            "price": "$999.99"
        }
        
        logging.info("=== Testing Novel Product Creation ===")
        logging.info(f"Test JSON item: {test_json_item}")
        
        # Try to create a product from this JSON item
        product = json_matcher._create_product_from_json(test_json_item, "TEST VENDOR")
        
        logging.info(f"✅ Created product: {product}")
        logging.info(f"Product Source: {product.get('Source', 'No Source')}")
        logging.info(f"Product Name: {product.get('Product Name*', 'No Name')}")
        
        # Check if it's marked as a JSON Match
        if product.get('Source') == 'JSON Match':
            logging.info("✅ Product correctly marked as 'JSON Match'")
        else:
            logging.warning(f"❌ Product source is '{product.get('Source')}' instead of 'JSON Match'")
        
        # Now test with the actual JSON data to see what's happening
        logging.info("\n=== Testing with Actual JSON Data ===")
        
        # The URL to test
        test_url = "https://files.cultivera.com/435553542D5753353635/Interop/25/34/GFJZZ9ZJQKVBWQDR/Cultivera_ORD-11766_422044.json"
        
        # Fetch the JSON data
        import requests
        response = requests.get(test_url)
        response.raise_for_status()
        json_data = response.json()
        
        logging.info(f"✅ Fetched JSON data with {len(json_data.get('inventory_transfer_items', []))} items")
        
        # Check what products are in the JSON data
        json_products = json_data.get('inventory_transfer_items', [])
        for i, item in enumerate(json_products[:5]):  # Check first 5 items
            product_name = item.get('product_name', 'Unknown')
            logging.info(f"JSON Product {i+1}: {product_name}")
        
        # Now test the matching process
        logging.info("\n=== Testing JSON Matching Process ===")
        
        # Initialize product database
        product_db = ProductDatabase()
        
        # Test the fetch_and_match method
        matched_products = json_matcher.fetch_and_match(test_url)
        
        logging.info(f"✅ JSON matching completed: {len(matched_products)} products")
        
        # Check the sources of the matched products
        sources = {}
        for product in matched_products:
            source = product.get('Source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        logging.info("=== Product Sources Analysis ===")
        for source, count in sources.items():
            logging.info(f"Source '{source}': {count} products")
        
        # Check if any products are marked as JSON Match
        json_match_products = [p for p in matched_products if p.get('Source') == 'JSON Match']
        excel_match_products = [p for p in matched_products if 'Excel Match' in p.get('Source', '')]
        
        logging.info(f"✅ JSON Match products: {len(json_match_products)}")
        logging.info(f"✅ Excel Match products: {len(excel_match_products)}")
        
        if json_match_products:
            logging.info("✅ Found novel products created from JSON!")
            for i, product in enumerate(json_match_products[:3]):
                logging.info(f"  Novel Product {i+1}: {product.get('Product Name*', 'Unknown')}")
        else:
            logging.warning("❌ No novel products found - all products matched to Excel data")
            logging.info("This means the JSON matching system is finding matches for all products in your Excel data")
        
        logging.info(f"\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        logging.error(f"❌ Test failed with error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_novel_products()
    sys.exit(0 if success else 1)
