#!/usr/bin/env python3
"""
Test script to verify JSON matched tags cache storage and retrieval.
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
        logging.FileHandler('test_cache_fix.log')
    ]
)

def test_cache_fix():
    """Test JSON matched tags cache storage and retrieval."""
    
    logging.info("🚀 Starting Cache Fix Test")
    logging.info(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Test URL
        test_url = "https://files.cultivera.com/435553542D5753353635/Interop/25/34/GFJZZ9ZJQKVBWQDR/Cultivera_ORD-11766_422044.json"
        
        # Start the Flask app
        app_url = "http://localhost:5001"
        
        logging.info("📡 Testing JSON matching with cache verification...")
        
        # Test JSON matching endpoint
        try:
            response = requests.post(
                f"{app_url}/api/json-match",
                json={"url": test_url},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logging.info(f"✅ JSON matching successful: {result.get('message', 'Unknown')}")
                
                # Check if JSON matched tags were created
                matched_tags = result.get('json_matched_tags', result.get('matched_tags', []))
                logging.info(f"📊 Found {len(matched_tags)} matched tags in response")
                
                # Check the source of each tag
                json_matches = [tag for tag in matched_tags if isinstance(tag, dict) and tag.get('Source') == 'JSON Match']
                excel_matches = [tag for tag in matched_tags if isinstance(tag, dict) and tag.get('Source') == 'Excel Match (Strict)']
                
                logging.info(f"🎯 JSON Match products: {len(json_matches)}")
                logging.info(f"📋 Excel Match products: {len(excel_matches)}")
                
                # Test available tags endpoint
                try:
                    response = requests.get(f"{app_url}/api/available-tags", timeout=10)
                    
                    if response.status_code == 200:
                        available_tags = response.json()
                        logging.info(f"✅ Available tags endpoint successful: {len(available_tags)} tags")
                        
                        # Check if JSON matched tags are in available tags
                        json_matched_in_available = [tag for tag in available_tags if isinstance(tag, dict) and tag.get('Source') == 'JSON Match']
                        logging.info(f"🎯 JSON Match products in available tags: {len(json_matched_in_available)}")
                        
                        if json_matched_in_available:
                            logging.info("✅ SUCCESS: JSON matched products are available in the web interface!")
                            for i, tag in enumerate(json_matched_in_available[:3]):
                                logging.info(f"   {i+1}. {tag.get('Product Name*', tag.get('ProductName', 'Unknown'))}")
                        else:
                            logging.warning("❌ JSON matched products are NOT available in the web interface")
                            
                            # Check filter status
                            try:
                                response = requests.get(f"{app_url}/api/get-filter-status", timeout=10)
                                if response.status_code == 200:
                                    filter_status = response.json()
                                    logging.info(f"📊 Filter status: {filter_status}")
                                else:
                                    logging.error(f"❌ Filter status endpoint failed: {response.status_code}")
                            except Exception as e:
                                logging.error(f"❌ Filter status request failed: {e}")
                    else:
                        logging.error(f"❌ Available tags endpoint failed: {response.status_code}")
                        
                except Exception as e:
                    logging.error(f"❌ Available tags request failed: {e}")
                
            else:
                logging.error(f"❌ JSON matching failed: {response.status_code}")
                logging.error(f"Response: {response.text}")
                
        except Exception as e:
            logging.error(f"❌ JSON matching request failed: {e}")
        
        logging.info("🏁 Cache Fix Test Complete")
        return True
        
    except Exception as e:
        logging.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_cache_fix()
    sys.exit(0 if success else 1)
