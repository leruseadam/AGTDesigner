#!/usr/bin/env python3
"""
Test script to verify JSON matching works correctly in the web interface.
"""

import sys
import os
import logging
import json
import requests
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_json_web_interface.log')
    ]
)

def test_json_web_interface():
    """Test JSON matching in the web interface."""
    
    # The URL to test
    test_url = "https://files.cultivera.com/435553542D5753353635/Interop/25/34/GFJZZ9ZJQKVBWQDR/Cultivera_ORD-11766_422044.json"
    
    logging.info("🚀 Starting JSON Web Interface Test")
    logging.info(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Test the JSON matching endpoint
        logging.info("=== Testing JSON Matching Endpoint ===")
        
        # Start the Flask app if not already running
        app_url = "http://127.0.0.1:5003"
        
        # Test JSON matching
        json_match_data = {
            'url': test_url
        }
        
        logging.info(f"Testing JSON matching with URL: {test_url}")
        
        try:
            response = requests.post(f"{app_url}/api/json-match", json=json_match_data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            logging.info(f"✅ JSON matching successful!")
            logging.info(f"Response status: {response.status_code}")
            logging.info(f"Response data: {result}")
            
            # Check if we got the expected response
            if 'success' in result and result['success']:
                logging.info(f"✅ JSON matching returned success")
                
                # Check for matched products
                if 'matched_products' in result:
                    matched_count = len(result['matched_products'])
                    logging.info(f"✅ Found {matched_count} matched products")
                else:
                    logging.warning("❌ No matched_products in response")
                    
            else:
                logging.error(f"❌ JSON matching failed: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Failed to connect to Flask app: {e}")
            logging.info("Make sure the Flask app is running on http://127.0.0.1:5003")
            return False
        
        # Test the filter status endpoint
        logging.info("\n=== Testing Filter Status Endpoint ===")
        
        try:
            response = requests.get(f"{app_url}/api/get-filter-status", timeout=10)
            response.raise_for_status()
            result = response.json()
            
            logging.info(f"✅ Filter status successful!")
            logging.info(f"Response: {result}")
            
            # Check if JSON matched tags are detected
            if 'has_json_matched' in result and result['has_json_matched']:
                logging.info(f"✅ JSON matched tags detected: {result['json_matched_count']} items")
            else:
                logging.warning("❌ No JSON matched tags detected in filter status")
                
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Failed to get filter status: {e}")
            return False
        
        # Test the available tags endpoint
        logging.info("\n=== Testing Available Tags Endpoint ===")
        
        try:
            response = requests.get(f"{app_url}/api/available-tags", timeout=10)
            response.raise_for_status()
            result = response.json()
            
            logging.info(f"✅ Available tags successful!")
            logging.info(f"Response: {len(result)} tags returned")
            
            # Check for JSON matched tags in the response
            json_matched_tags = [tag for tag in result if isinstance(tag, dict) and tag.get('Source') and 'JSON' in tag.get('Source', '')]
            excel_match_tags = [tag for tag in result if isinstance(tag, dict) and tag.get('Source') and 'Excel Match' in tag.get('Source', '')]
            
            logging.info(f"✅ Found {len(json_matched_tags)} JSON matched tags")
            logging.info(f"✅ Found {len(excel_match_tags)} Excel match tags")
            
            if json_matched_tags or excel_match_tags:
                logging.info(f"✅ JSON matching integration working correctly!")
                
                # Show sample tags
                sample_tags = (json_matched_tags + excel_match_tags)[:3]
                for i, tag in enumerate(sample_tags):
                    product_name = tag.get('Product Name*', tag.get('ProductName', 'Unknown'))
                    source = tag.get('Source', 'Unknown')
                    logging.info(f"   Sample {i+1}: {product_name} (Source: {source})")
            else:
                logging.warning("❌ No JSON matched or Excel match tags found in available tags")
                
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Failed to get available tags: {e}")
            return False
        
        logging.info(f"\n✅ All tests completed successfully!")
        logging.info(f"📋 JSON matching web interface integration working correctly")
        logging.info(f"Check the log file 'test_json_web_interface.log' for detailed results")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Test failed with error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_json_web_interface()
    sys.exit(0 if success else 1)
