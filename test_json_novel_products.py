#!/usr/bin/env python3
"""
Test script to test JSON matching with novel products and see how they're saved to the database.
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
        logging.FileHandler('test_json_novel_products.log')
    ]
)

def test_json_matching():
    """Test JSON matching with the provided URL."""
    
    # The URL to test
    test_url = "https://files.cultivera.com/435553542D5753353635/Interop/25/34/GFJZZ9ZJQKVBWQDR/Cultivera_ORD-11766_422044.json"
    
    try:
        # Import the JSON matcher
        from core.data.json_matcher import JSONMatcher
        from core.data.excel_processor import ExcelProcessor
        from core.data.product_database import ProductDatabase
        
        logging.info("=== JSON Matching Test with Novel Products ===")
        logging.info(f"Testing URL: {test_url}")
        
        # Initialize the Excel processor
        logging.info("Initializing Excel processor...")
        excel_processor = ExcelProcessor()
        
        # Initialize Product Database
        logging.info("Initializing Product Database...")
        product_db = ProductDatabase()
        
        # Initialize the JSON matcher with required parameters
        logging.info("Initializing JSON matcher...")
        json_matcher = JSONMatcher(excel_processor, product_db)
        
        # Test the fetch_and_match method
        logging.info("Testing fetch_and_match method...")
        matched_products = json_matcher.fetch_and_match(test_url)
        
        logging.info(f"✅ JSON matching completed successfully!")
        logging.info(f"📊 Results:")
        logging.info(f"   - Total products processed: {len(matched_products)}")
        
        # Analyze the results
        excel_matches = 0
        database_matches = 0
        novel_products = 0
        
        for i, product in enumerate(matched_products):
            source = product.get('Source', 'Unknown')
            product_name = product.get('Product Name*', 'Unknown')
            
            if 'JSON Match' in source:
                if 'Excel match' in source.lower():
                    excel_matches += 1
                    logging.info(f"   {i+1}. {product_name} (Excel Match)")
                elif 'database' in source.lower():
                    database_matches += 1
                    logging.info(f"   {i+1}. {product_name} (Database Match)")
                else:
                    novel_products += 1
                    logging.info(f"   {i+1}. {product_name} (Novel Product - Created from JSON)")
            else:
                novel_products += 1
                logging.info(f"   {i+1}. {product_name} (Novel Product)")
        
        logging.info(f"\n📈 Summary:")
        logging.info(f"   - Excel matches: {excel_matches}")
        logging.info(f"   - Database matches: {database_matches}")
        logging.info(f"   - Novel products created: {novel_products}")
        
        # Check if novel products were saved to database
        if novel_products > 0:
            logging.info(f"\n💾 Checking if novel products were saved to database...")
            
            # Check a few novel products to see if they're in the database
            novel_product_names = []
            for product in matched_products:
                if product.get('Source', '').startswith('JSON Match'):
                    product_name = product.get('Product Name*', '')
                    if product_name:
                        novel_product_names.append(product_name)
            
            # Check first few novel products
            for product_name in novel_product_names[:5]:
                db_info = product_db.get_product_info(product_name)
                if db_info:
                    logging.info(f"   ✅ '{product_name}' found in database")
                else:
                    logging.info(f"   ❌ '{product_name}' NOT found in database")
        
        # Show sample product details
        if matched_products:
            logging.info(f"\n🔍 Sample Product Details:")
            sample_product = matched_products[0]
            for key, value in sample_product.items():
                if key in ['Product Name*', 'Vendor', 'Product Type*', 'Product Strain', 'Lineage', 'Weight*', 'Price', 'Source']:
                    logging.info(f"   {key}: {value}")
        
        return matched_products
        
    except Exception as e:
        logging.error(f"❌ Error during JSON matching test: {e}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        return []

def test_database_integration():
    """Test database integration and see what's in the product database."""
    
    try:
        logging.info("\n=== Database Integration Test ===")
        
        from core.data.product_database import ProductDatabase
        product_db = ProductDatabase()
        
        # Get database stats using available methods
        all_strains = product_db.get_all_strains()
        strain_stats = product_db.get_strain_statistics()
        
        logging.info(f"📊 Database Statistics:")
        logging.info(f"   - Total strains: {len(all_strains)}")
        logging.info(f"   - Strain statistics: {strain_stats}")
        
        # Get some sample products from the database
        logging.info(f"\n🕒 Sample Products in Database:")
        
        # Try to get products by some common names
        sample_product_names = [
            "GSC Live Resin Cartridge",
            "Wedding Cake Live Resin Cartridge", 
            "Jet Fuel Gelato Live Resin Vaporizer"
        ]
        
        for product_name in sample_product_names:
            db_info = product_db.get_product_info(product_name)
            if db_info:
                logging.info(f"   ✅ Found: {product_name}")
                logging.info(f"      - Vendor: {db_info.get('Vendor/Supplier*', 'Unknown')}")
                logging.info(f"      - Type: {db_info.get('Product Type*', 'Unknown')}")
                logging.info(f"      - Strain: {db_info.get('Product Strain', 'Unknown')}")
            else:
                logging.info(f"   ❌ Not found: {product_name}")
            
    except Exception as e:
        logging.error(f"❌ Error during database integration test: {e}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")

def main():
    """Main test function."""
    logging.info("🚀 Starting JSON Novel Products Test")
    logging.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test JSON matching
    matched_products = test_json_matching()
    
    # Test database integration
    test_database_integration()
    
    logging.info("\n✅ Test completed!")
    
    if matched_products:
        logging.info(f"📋 Generated {len(matched_products)} products from JSON data")
        logging.info("Check the log file 'test_json_novel_products.log' for detailed results")
    else:
        logging.warning("⚠️ No products were generated from JSON data")

if __name__ == "__main__":
    main()
