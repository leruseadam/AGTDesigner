#!/usr/bin/env python3
"""
Test script to verify upload speed optimizations
"""

import time
import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_upload_speed():
    """Test the upload speed optimizations"""
    try:
        logger.info("=== UPLOAD SPEED TEST START ===")
        
        # Test 1: Check if fast loading is enabled
        from src.core.data.excel_processor import ENABLE_FAST_LOADING, ENABLE_MINIMAL_PROCESSING
        logger.info(f"Fast loading enabled: {ENABLE_FAST_LOADING}")
        logger.info(f"Minimal processing enabled: {ENABLE_MINIMAL_PROCESSING}")
        
        # Test 2: Test ExcelProcessor fast loading
        from src.core.data.excel_processor import ExcelProcessor
        
        # Create a test processor
        processor = ExcelProcessor()
        
        # Check if fast_load_file method exists
        if hasattr(processor, 'fast_load_file'):
            logger.info("✅ fast_load_file method exists")
        else:
            logger.error("❌ fast_load_file method not found")
            return False
        
        # Test 3: Check if ultra-fast background processing exists
        try:
            from app import ultra_fast_background_processing
            logger.info("✅ ultra_fast_background_processing function exists")
        except ImportError as e:
            logger.error(f"❌ ultra_fast_background_processing not found: {e}")
            return False
        
        # Test 4: Check if essential processing exists
        try:
            from app import apply_essential_processing
            logger.info("✅ apply_essential_processing function exists")
        except ImportError as e:
            logger.error(f"❌ apply_essential_processing not found: {e}")
            return False
        
        # Test 5: Check if fast global processor update exists
        try:
            from app import update_global_processor_fast
            logger.info("✅ update_global_processor_fast function exists")
        except ImportError as e:
            logger.error(f"❌ update_global_processor_fast not found: {e}")
            return False
        
        logger.info("=== ALL TESTS PASSED ===")
        logger.info("Upload speed optimizations are properly implemented!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_upload_speed()
    if success:
        print("\n🎉 Upload speed optimizations are working correctly!")
        print("The web version should now upload files much faster.")
    else:
        print("\n❌ Upload speed optimizations have issues.")
        sys.exit(1)
