#!/usr/bin/env python3
"""
Debug script to see exactly what's happening with the matching logic.
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
        logging.FileHandler('debug_matching.log')
    ]
)

def debug_matching():
    """Debug the matching logic."""
    
    logging.info("🚀 Starting Matching Debug")
    logging.info(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Import the JSON matcher
        from src.core.data.json_matcher import JSONMatcher
        from src.core.data.excel_processor import ExcelProcessor
        
        # Initialize the Excel processor and JSON matcher
        excel_processor = ExcelProcessor()
        json_matcher = JSONMatcher(excel_processor)
        
        # Test with a specific product to see what's happening
        test_json_item = {
            "product_name": "GSC Live Resin Cartridge 1.0g",
            "vendor": "TRIGONAL INDUSTRIES",
            "brand": "Oleum",
            "inventory_type": "concentrate",
            "unit_weight": "1.0",
            "strain_name": "GSC",
            "quantity": "1",
            "price": "$40"
        }
        
        logging.info("=== Testing Specific Product Matching ===")
        logging.info(f"Test JSON item: {test_json_item}")
        
        # Get the product name and strain
        json_name = test_json_item.get("product_name", "").strip()
        json_strain = test_json_item.get("strain_name", "").strip()
        json_vendor = test_json_item.get("vendor", "").strip()
        json_brand = test_json_item.get("brand", "").strip()
        
        logging.info(f"JSON Name: {json_name}")
        logging.info(f"JSON Strain: {json_strain}")
        logging.info(f"JSON Vendor: {json_vendor}")
        logging.info(f"JSON Brand: {json_brand}")
        
        # Check what's in the Excel data
        if hasattr(excel_processor, 'df') and excel_processor.df is not None:
            logging.info(f"Excel data shape: {excel_processor.df.shape}")
            
            # Look for similar products
            excel_products = excel_processor.df[excel_processor.df['Product Name*'].str.contains('Live Resin', case=False, na=False)]
            logging.info(f"Found {len(excel_products)} Live Resin products in Excel")
            
            for i, (idx, row) in enumerate(excel_products.head(5).iterrows()):
                excel_name = row.get('Product Name*', '')
                excel_strain = row.get('Product Strain', '')
                excel_vendor = row.get('Vendor', '')
                excel_brand = row.get('Product Brand', '')
                
                logging.info(f"Excel Product {i+1}:")
                logging.info(f"  Name: {excel_name}")
                logging.info(f"  Strain: {excel_strain}")
                logging.info(f"  Vendor: {excel_vendor}")
                logging.info(f"  Brand: {excel_brand}")
                
                # Check for matches
                vendor_match = (json_vendor and excel_vendor and json_vendor in excel_vendor) or (json_vendor and excel_vendor and excel_vendor in json_vendor)
                brand_match = (json_brand and excel_brand and json_brand in excel_brand) or (json_brand and excel_brand and excel_brand in json_brand)
                
                logging.info(f"  Vendor Match: {vendor_match}")
                logging.info(f"  Brand Match: {brand_match}")
                
                # Check strain similarity
                if excel_strain and len(excel_strain) > 3:
                    strain_keywords = json_strain.split()
                    matching_keywords = sum(1 for keyword in strain_keywords[:3] if len(keyword) > 2 and keyword in excel_strain)
                    logging.info(f"  Strain Keywords: {strain_keywords}")
                    logging.info(f"  Matching Keywords: {matching_keywords}")
                    
                    if vendor_match or brand_match:
                        score = matching_keywords + (2 if vendor_match else 0) + (2 if brand_match else 0)
                        logging.info(f"  Score: {score}")
        else:
            logging.info("No Excel data available")
        
        logging.info(f"\n✅ Debug completed successfully!")
        return True
        
    except Exception as e:
        logging.error(f"❌ Debug failed with error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = debug_matching()
    sys.exit(0 if success else 1)
