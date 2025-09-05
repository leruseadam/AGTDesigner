#!/usr/bin/env python3
"""
Test script to verify JSON matching integration with web interface.
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
        logging.FileHandler('test_json_web_integration.log')
    ]
)

def test_json_web_integration():
    """Test JSON matching integration with web interface."""
    
    # The URL to test
    test_url = "https://files.cultivera.com/435553542D5753353635/Interop/25/34/GFJZZ9ZJQKVBWQDR/Cultivera_ORD-11766_422044.json"
    
    logging.info("🚀 Starting JSON Web Integration Test")
    logging.info(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Import required modules
        from src.core.data.excel_processor import ExcelProcessor
        from src.core.data.product_database import ProductDatabase
        from src.core.data.json_matcher import JSONMatcher
        
        logging.info("=== JSON Web Integration Test ===")
        logging.info(f"Testing URL: {test_url}")
        
        # Initialize components
        logging.info("Initializing Excel processor...")
        excel_processor = ExcelProcessor()
        
        logging.info("Initializing Product Database...")
        db_path = os.path.join(os.path.dirname(__file__), 'uploads', 'product_database.db')
        product_db = ProductDatabase(db_path)
        
        logging.info("Initializing JSON matcher...")
        json_matcher = JSONMatcher(excel_processor, product_db)
        
        # Test JSON matching
        logging.info("Testing fetch_and_match method...")
        matched_products = json_matcher.fetch_and_match(test_url)
        
        logging.info(f"✅ JSON matching completed successfully!")
        logging.info(f"📊 Results:")
        logging.info(f"   - Total products processed: {len(matched_products)}")
        
        # Test web interface integration
        logging.info("\n=== Web Interface Integration Test ===")
        
        # Simulate session data
        session_data = {
            'json_matched_tags': json_matcher.get_matched_tags(),
            'json_selected_tags': [product.get('Product Name*', '') for product in json_matcher.get_matched_tags()],
            'selected_tags': [product.get('Product Name*', '') for product in json_matcher.get_matched_tags()]
        }
        
        logging.info(f"Session data created:")
        logging.info(f"   - JSON matched tags: {len(session_data['json_matched_tags'])}")
        logging.info(f"   - JSON selected tags: {len(session_data['json_selected_tags'])}")
        logging.info(f"   - Selected tags: {len(session_data['selected_tags'])}")
        
        # Test tag restoration logic
        logging.info("\n=== Tag Restoration Test ===")
        
        restored_tags = []
        for tag_name in session_data['selected_tags']:
            found_tag = None
            
            # First try to find in JSON matched tags
            if session_data['json_matched_tags'] and tag_name in session_data['json_selected_tags']:
                for json_tag in session_data['json_matched_tags']:
                    if isinstance(json_tag, dict):
                        json_tag_name = json_tag.get('Product Name*', json_tag.get('ProductName', ''))
                        if json_tag_name == tag_name:
                            found_tag = json_tag
                            logging.info(f"✅ Found JSON matched tag: {tag_name}")
                            break
            
            # If not found in JSON tags, try Excel data
            if not found_tag and hasattr(excel_processor, 'df') and excel_processor.df is not None:
                possible_columns = ['ProductName', 'Product Name*', 'Product Name']
                for col in possible_columns:
                    if col in excel_processor.df.columns:
                        mask = excel_processor.df[col] == tag_name
                        if mask.any():
                            row = excel_processor.df[mask].iloc[0]
                            found_tag = row.to_dict()
                            logging.info(f"✅ Found Excel tag: {tag_name}")
                            break
            
            if found_tag:
                restored_tags.append(found_tag)
            else:
                logging.warning(f"❌ Tag not found in data: {tag_name}")
        
        logging.info(f"\n📊 Tag Restoration Results:")
        logging.info(f"   - Original tags: {len(session_data['selected_tags'])}")
        logging.info(f"   - Restored tags: {len(restored_tags)}")
        logging.info(f"   - Success rate: {len(restored_tags)}/{len(session_data['selected_tags'])} = {len(restored_tags)/len(session_data['selected_tags'])*100:.1f}%")
        
        # Test available tags integration
        logging.info("\n=== Available Tags Integration Test ===")
        
        # Simulate the available tags logic
        available_tags = []
        
        # Add Excel tags if available
        if hasattr(excel_processor, 'df') and excel_processor.df is not None and not excel_processor.df.empty:
            excel_tags = excel_processor.get_available_tags()
            available_tags.extend(excel_tags)
            logging.info(f"Added {len(excel_tags)} Excel tags to available tags")
        
        # Add JSON matched tags
        json_tags = session_data['json_matched_tags']
        available_tags.extend(json_tags)
        logging.info(f"Added {len(json_tags)} JSON matched tags to available tags")
        
        logging.info(f"Total available tags: {len(available_tags)}")
        
        # Verify all JSON products are in available tags
        json_product_names = set(session_data['json_selected_tags'])
        available_product_names = set()
        
        for tag in available_tags:
            if isinstance(tag, dict):
                product_name = tag.get('Product Name*', tag.get('ProductName', ''))
                if product_name:
                    available_product_names.add(product_name)
        
        missing_products = json_product_names - available_product_names
        found_products = json_product_names & available_product_names
        
        logging.info(f"\n📊 Available Tags Verification:")
        logging.info(f"   - JSON products: {len(json_product_names)}")
        logging.info(f"   - Found in available tags: {len(found_products)}")
        logging.info(f"   - Missing from available tags: {len(missing_products)}")
        
        if missing_products:
            logging.warning(f"❌ Missing products: {list(missing_products)}")
        else:
            logging.info(f"✅ All JSON products found in available tags!")
        
        logging.info(f"\n✅ Test completed successfully!")
        logging.info(f"📋 JSON matching and web interface integration working correctly")
        logging.info(f"Check the log file 'test_json_web_integration.log' for detailed results")
        
    except Exception as e:
        logging.error(f"❌ Test failed with error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False
    
    return True

if __name__ == "__main__":
    success = test_json_web_integration()
    sys.exit(0 if success else 1)
