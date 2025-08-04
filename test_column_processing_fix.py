#!/usr/bin/env python3
"""
Test script to verify column processing fix
"""

import os
import sys
import pandas as pd
import logging

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_column_processing():
    """Test that all columns are preserved during processing."""
    try:
        # Load the Excel file
        default_file = get_default_upload_file()
        if not default_file:
            logger.error("No default file found")
            return False
            
        logger.info(f"Loading file: {default_file}")
        excel_processor = ExcelProcessor()
        
        # First, let's see what columns are in the original file
        logger.info("Reading original file to check columns...")
        original_df = pd.read_excel(default_file)
        logger.info(f"Original file has {len(original_df.columns)} columns: {original_df.columns.tolist()}")
        
        # Now load with the processor
        if not excel_processor.load_file(default_file):
            logger.error("Failed to load file with processor")
            return False
            
        logger.info(f"Processor loaded file with {len(excel_processor.df.columns)} columns: {excel_processor.df.columns.tolist()}")
        
        # Check if all original columns are preserved
        original_columns = set(original_df.columns)
        processed_columns = set(excel_processor.df.columns)
        
        missing_columns = original_columns - processed_columns
        if missing_columns:
            logger.error(f"❌ Missing columns after processing: {missing_columns}")
            return False
        else:
            logger.info("✅ All original columns preserved!")
            
        # Check if we have the required columns
        required_columns = [
            'Product Name*', 'ProductName', 'Description',
            'Product Type*', 'Lineage', 'Product Brand', 'Vendor/Supplier*',
            'Weight*', 'Weight Unit* (grams/gm or ounces/oz)', 'Units',
            'Price* (Tier Name for Bulk)', 'Price',
            'DOH Compliant (Yes/No)', 'DOH',
            'Concentrate Type', 'Ratio',
            'Joint Ratio', 'JointRatio',
            'Product Strain',
            'Quantity*', 'Quantity Received*', 'Quantity', 'qty'
        ]
        
        missing_required = [col for col in required_columns if col not in processed_columns]
        if missing_required:
            logger.warning(f"⚠️  Missing required columns: {missing_required}")
        else:
            logger.info("✅ All required columns present!")
            
        return True
        
    except Exception as e:
        logger.error(f"Error testing column processing: {e}")
        return False

if __name__ == "__main__":
    success = test_column_processing()
    if success:
        print("✅ Column processing test passed!")
    else:
        print("❌ Column processing test failed!")
        sys.exit(1) 