#!/usr/bin/env python3
"""
Test script to verify Flask session management fixes.
This script tests the ExcelProcessor initialization and session management.
"""

import os
import sys
import logging
import time
import requests
import json
from pathlib import Path

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_health_endpoint(base_url="http://localhost:9090"):
    """Test the health endpoint to check ExcelProcessor status."""
    try:
        logger.info("Testing health endpoint...")
        response = requests.get(f"{base_url}/api/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            logger.info("Health check successful")
            logger.info(f"Overall status: {health_data.get('status', 'unknown')}")
            logger.info(f"Data loaded: {health_data.get('application', {}).get('data_loaded', False)}")
            
            if 'application' in health_data:
                app_data = health_data['application']
                logger.info(f"ExcelProcessor error: {app_data.get('excel_processor_error', 'None')}")
                logger.info(f"Data shape: {app_data.get('data_shape', 'None')}")
                logger.info(f"Selected tags count: {app_data.get('selected_tags_count', 0)}")
            
            if 'warnings' in health_data and health_data['warnings']:
                logger.warning(f"Warnings: {health_data['warnings']}")
            
            return health_data
        else:
            logger.error(f"Health check failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error testing health endpoint: {e}")
        return None

def test_status_endpoint(base_url="http://localhost:9090"):
    """Test the status endpoint."""
    try:
        logger.info("Testing status endpoint...")
        response = requests.get(f"{base_url}/api/status", timeout=10)
        
        if response.status_code == 200:
            status_data = response.json()
            logger.info("Status check successful")
            logger.info(f"Server: {status_data.get('server', 'unknown')}")
            logger.info(f"Data loaded: {status_data.get('data_loaded', False)}")
            logger.info(f"Data shape: {status_data.get('data_shape', 'None')}")
            logger.info(f"Selected tags count: {status_data.get('selected_tags_count', 0)}")
            
            if 'error' in status_data:
                logger.error(f"Status error: {status_data['error']}")
            
            return status_data
        else:
            logger.error(f"Status check failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error testing status endpoint: {e}")
        return None

def test_available_tags_endpoint(base_url="http://localhost:9090"):
    """Test the available tags endpoint."""
    try:
        logger.info("Testing available tags endpoint...")
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        
        if response.status_code == 200:
            tags_data = response.json()
            if isinstance(tags_data, list):
                logger.info(f"Available tags check successful: {len(tags_data)} tags found")
                if tags_data:
                    logger.info(f"First tag: {tags_data[0]}")
                return tags_data
            else:
                logger.error(f"Unexpected response format: {type(tags_data)}")
                return None
        else:
            logger.error(f"Available tags check failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error testing available tags endpoint: {e}")
        return None

def test_selected_tags_endpoint(base_url="http://localhost:9090"):
    """Test the selected tags endpoint."""
    try:
        logger.info("Testing selected tags endpoint...")
        response = requests.get(f"{base_url}/api/selected-tags", timeout=10)
        
        if response.status_code == 200:
            tags_data = response.json()
            if isinstance(tags_data, list):
                logger.info(f"Selected tags check successful: {len(tags_data)} tags selected")
                return tags_data
            else:
                logger.error(f"Unexpected response format: {type(tags_data)}")
                return None
        else:
            logger.error(f"Selected tags check failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error testing selected tags endpoint: {e}")
        return None

def test_excel_processor_initialization():
    """Test ExcelProcessor initialization directly."""
    try:
        logger.info("Testing ExcelProcessor initialization...")
        
        # Import the functions
        from app import get_excel_processor, get_session_excel_processor
        
        # Test global ExcelProcessor
        logger.info("Testing global ExcelProcessor...")
        global_processor = get_excel_processor()
        
        if global_processor is None:
            logger.error("Global ExcelProcessor is None")
            return False
        
        logger.info(f"Global ExcelProcessor initialized successfully")
        logger.info(f"Has df attribute: {hasattr(global_processor, 'df')}")
        logger.info(f"df is None: {global_processor.df is None}")
        logger.info(f"df is empty: {global_processor.df.empty if global_processor.df is not None else 'N/A'}")
        logger.info(f"Has selected_tags attribute: {hasattr(global_processor, 'selected_tags')}")
        
        # Test session ExcelProcessor
        logger.info("Testing session ExcelProcessor...")
        session_processor = get_session_excel_processor()
        
        if session_processor is None:
            logger.error("Session ExcelProcessor is None")
            return False
        
        logger.info(f"Session ExcelProcessor initialized successfully")
        logger.info(f"Has df attribute: {hasattr(session_processor, 'df')}")
        logger.info(f"df is None: {session_processor.df is None}")
        logger.info(f"df is empty: {session_processor.df.empty if session_processor.df is not None else 'N/A'}")
        logger.info(f"Has selected_tags attribute: {hasattr(session_processor, 'selected_tags')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing ExcelProcessor initialization: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main test function."""
    logger.info("Starting Flask session management tests...")
    
    # Test ExcelProcessor initialization directly
    logger.info("=" * 50)
    logger.info("Testing ExcelProcessor initialization directly...")
    init_success = test_excel_processor_initialization()
    
    if not init_success:
        logger.error("ExcelProcessor initialization test failed")
        return
    
    # Test API endpoints (if server is running)
    logger.info("=" * 50)
    logger.info("Testing API endpoints...")
    
    base_url = "http://localhost:9090"
    
    # Test health endpoint
    health_data = test_health_endpoint(base_url)
    
    # Test status endpoint
    status_data = test_status_endpoint(base_url)
    
    # Test available tags endpoint
    available_tags = test_available_tags_endpoint(base_url)
    
    # Test selected tags endpoint
    selected_tags = test_selected_tags_endpoint(base_url)
    
    # Summary
    logger.info("=" * 50)
    logger.info("Test Summary:")
    logger.info(f"ExcelProcessor initialization: {'PASS' if init_success else 'FAIL'}")
    logger.info(f"Health endpoint: {'PASS' if health_data else 'FAIL'}")
    logger.info(f"Status endpoint: {'PASS' if status_data else 'FAIL'}")
    logger.info(f"Available tags endpoint: {'PASS' if available_tags is not None else 'FAIL'}")
    logger.info(f"Selected tags endpoint: {'PASS' if selected_tags is not None else 'FAIL'}")
    
    if health_data and health_data.get('status') == 'healthy':
        logger.info("✅ All tests passed! Flask session management is working correctly.")
    else:
        logger.warning("⚠️ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 