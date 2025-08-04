#!/usr/bin/env python3
"""
Debug script to test tag matching
"""
import os
import sys
import pandas as pd
import logging

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_tag_matching():
    """Debug tag matching issues"""
    try:
        # Load the Excel file
        default_file = get_default_upload_file()
        if not default_file:
            logger.error("No default file found")
            return False
            
        logger.info(f"Loading file: {default_file}")
        excel_processor = ExcelProcessor()
        
        if not excel_processor.load_file(default_file):
            logger.error("Failed to load file")
            return False
            
        logger.info(f"Successfully loaded file with {len(excel_processor.df)} records")
        
        # Get available tags
        available_tags = excel_processor.get_available_tags()
        logger.info(f"Available tags count: {len(available_tags)}")
        
        # Show first 10 available tags
        logger.info("First 10 available tags:")
        for i, tag in enumerate(available_tags[:10]):
            logger.info(f"  {i+1}. {tag['Product Name*']}")
        
        # Test with some sample selected tags
        sample_selected_tags = [
            available_tags[0]['Product Name*'] if available_tags else "Test Tag 1",
            available_tags[1]['Product Name*'] if len(available_tags) > 1 else "Test Tag 2"
        ]
        
        logger.info(f"Testing with selected tags: {sample_selected_tags}")
        
        # Normalize selected tags and DataFrame values (same logic as in app.py)
        selected_tags = set(tag.strip().lower() for tag in sample_selected_tags)
        df_tags = excel_processor.df['ProductName'].dropna().apply(lambda x: x.strip().lower())
        
        logger.info(f"Normalized selected tags: {selected_tags}")
        logger.info(f"First 10 normalized DataFrame tags: {df_tags.head(10).tolist()}")
        
        # Check for matches
        records_df = excel_processor.df[df_tags.isin(selected_tags)]
        
        logger.info(f"Found {len(records_df)} matching records")
        
        if records_df.empty:
            logger.error("No matches found!")
            logger.info("This is the same error as in the web app")
            
            # Show some sample ProductName values for debugging
            logger.info("Sample ProductName values from DataFrame:")
            for i, name in enumerate(excel_processor.df['ProductName'].head(10)):
                logger.info(f"  {i+1}. '{name}' -> normalized: '{name.strip().lower() if pd.notna(name) else 'N/A'}'")
        else:
            logger.info("✅ Tag matching is working correctly")
            
        return True
        
    except Exception as e:
        logger.error(f"Error in debug_tag_matching: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    debug_tag_matching() 