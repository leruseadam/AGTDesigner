#!/usr/bin/env python3
"""
Debug script to identify vendor field mapping issues in Excel files.
This script helps troubleshoot why some Excel files load organized by Brand instead of Vendor.
"""

import os
import sys
import pandas as pd
import logging

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.data.excel_processor import ExcelProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_excel_file(file_path):
    """Debug a specific Excel file to see vendor field mapping."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    
    logger.info(f"Debugging Excel file: {file_path}")
    
    # First, let's examine the raw Excel file
    logger.info("=== RAW EXCEL FILE ANALYSIS ===")
    try:
        # Read with pandas to see raw structure
        df_raw = pd.read_excel(file_path, engine='openpyxl')
        logger.info(f"Raw DataFrame shape: {df_raw.shape}")
        logger.info(f"Raw columns: {df_raw.columns.tolist()}")
        
        # Check for vendor-related columns
        vendor_columns = [col for col in df_raw.columns if 'vendor' in col.lower() or 'supplier' in col.lower()]
        logger.info(f"Vendor-related columns: {vendor_columns}")
        
        # Show sample data from vendor columns
        for col in vendor_columns:
            if col in df_raw.columns:
                sample_values = df_raw[col].dropna().unique()[:5]
                logger.info(f"Column '{col}' sample values: {sample_values}")
        
        # Check for brand columns
        brand_columns = [col for col in df_raw.columns if 'brand' in col.lower()]
        logger.info(f"Brand-related columns: {brand_columns}")
        
        # Show sample data from brand columns
        for col in brand_columns:
            if col in df_raw.columns:
                sample_values = df_raw[col].dropna().unique()[:5]
                logger.info(f"Column '{col}' sample values: {sample_values}")
                
    except Exception as e:
        logger.error(f"Error reading raw Excel file: {e}")
        return
    
    # Now test with our ExcelProcessor
    logger.info("\n=== EXCEL PROCESSOR ANALYSIS ===")
    try:
        processor = ExcelProcessor()
        
        # Test fast load
        logger.info("Testing fast load...")
        fast_success = processor.fast_load_file(file_path)
        logger.info(f"Fast load success: {fast_success}")
        
        if fast_success and processor.df is not None:
            logger.info(f"Fast load DataFrame shape: {processor.df.shape}")
            logger.info(f"Fast load columns: {processor.df.columns.tolist()}")
            
            # Check vendor columns after fast load
            vendor_cols_after = [col for col in processor.df.columns if 'vendor' in col.lower() or 'supplier' in col.lower()]
            logger.info(f"Vendor columns after fast load: {vendor_cols_after}")
            
            # Check if Vendor column exists
            if 'Vendor' in processor.df.columns:
                sample_vendors = processor.df['Vendor'].dropna().unique()[:10]
                logger.info(f"Vendor column sample values: {sample_vendors}")
            else:
                logger.warning("Vendor column not found after fast load")
        
        # Test regular load
        logger.info("\nTesting regular load...")
        regular_success = processor.load_file(file_path)
        logger.info(f"Regular load success: {regular_success}")
        
        if regular_success and processor.df is not None:
            logger.info(f"Regular load DataFrame shape: {processor.df.shape}")
            logger.info(f"Regular load columns: {processor.df.columns.tolist()}")
            
            # Check vendor columns after regular load
            vendor_cols_after = [col for col in processor.df.columns if 'vendor' in col.lower() or 'supplier' in col.lower()]
            logger.info(f"Vendor columns after regular load: {vendor_cols_after}")
            
            # Check if Vendor column exists
            if 'Vendor' in processor.df.columns:
                sample_vendors = processor.df['Vendor'].dropna().unique()[:10]
                logger.info(f"Vendor column sample values: {sample_vendors}")
            else:
                logger.warning("Vendor column not found after regular load")
        
        # Test getting available tags
        logger.info("\n=== TESTING AVAILABLE TAGS ===")
        if processor.df is not None:
            tags = processor.get_available_tags()
            logger.info(f"Number of available tags: {len(tags)}")
            
            if tags:
                # Check first few tags for vendor field
                logger.info("First 3 tags vendor field analysis:")
                for i, tag in enumerate(tags[:3]):
                    logger.info(f"Tag {i+1}:")
                    logger.info(f"  Product: {tag.get('Product Name*', 'Unknown')}")
                    logger.info(f"  Vendor: '{tag.get('vendor', 'MISSING')}'")
                    logger.info(f"  Vendor (uppercase): '{tag.get('Vendor', 'MISSING')}'")
                    logger.info(f"  Vendor/Supplier*: '{tag.get('Vendor/Supplier*', 'MISSING')}'")
                    logger.info(f"  Brand: '{tag.get('productBrand', 'MISSING')}'")
                    logger.info(f"  Brand (uppercase): '{tag.get('Product Brand', 'MISSING')}'")
                
                # Check if any tags are missing vendor
                missing_vendor = [tag for tag in tags if not tag.get('vendor')]
                if missing_vendor:
                    logger.warning(f"Found {len(missing_vendor)} tags with missing vendor field")
                    logger.warning("First few products with missing vendor:")
                    for tag in missing_vendor[:5]:
                        logger.warning(f"  - {tag.get('Product Name*', 'Unknown')}")
                else:
                    logger.info("All tags have vendor field populated")
        
    except Exception as e:
        logger.error(f"Error testing ExcelProcessor: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to run the debug script."""
    if len(sys.argv) != 2:
        print("Usage: python debug_vendor_field_issue.py <excel_file_path>")
        print("Example: python debug_vendor_field_issue.py uploads/my_file.xlsx")
        return
    
    file_path = sys.argv[1]
    debug_excel_file(file_path)

if __name__ == "__main__":
    main()
