#!/usr/bin/env python3
"""
Test script to verify edible lineage fix
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

def test_edible_lineage():
    """Test that edibles get proper lineage assignment."""
    try:
        # Load the Excel file
        default_file = get_default_upload_file()
        if not default_file:
            logger.error("No default file found")
            return False
            
        logger.info(f"Loading file: {default_file}")
        
        # Create Excel processor and load file
        processor = ExcelProcessor()
        success = processor.load_file(default_file)
        
        if not success:
            logger.error("Failed to load file")
            return False
            
        logger.info(f"File loaded successfully. Shape: {processor.df.shape}")
        
        # Check lineage distribution for edibles
        edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule", "rso/co2 tankers"}
        
        # Filter for edible products
        edible_mask = processor.df["Product Type*"].str.strip().str.lower().isin(edible_types)
        edible_df = processor.df[edible_mask].copy()
        
        logger.info(f"Found {len(edible_df)} edible products")
        
        if len(edible_df) > 0:
            # Show lineage distribution
            lineage_counts = edible_df["Lineage"].value_counts()
            logger.info("Lineage distribution for edibles:")
            for lineage, count in lineage_counts.items():
                logger.info(f"  {lineage}: {count}")
            
            # Show some examples
            logger.info("\nSample edible products and their lineages:")
            sample_edibles = edible_df[["ProductName", "Product Type*", "Lineage", "Description"]].head(10)
            for _, row in sample_edibles.iterrows():
                logger.info(f"  {row['ProductName']} ({row['Product Type*']}) -> {row['Lineage']}")
            
            # Check for problematic assignments
            cbd_edibles = edible_df[edible_df["Lineage"] == "CBD"]
            if len(cbd_edibles) > 0:
                logger.info(f"\nCBD lineage edibles ({len(cbd_edibles)}):")
                for _, row in cbd_edibles.head(5).iterrows():
                    logger.info(f"  {row['ProductName']} ({row['Product Type*']})")
            
            mixed_edibles = edible_df[edible_df["Lineage"] == "MIXED"]
            if len(mixed_edibles) > 0:
                logger.info(f"\nMIXED lineage edibles ({len(mixed_edibles)}):")
                for _, row in mixed_edibles.head(5).iterrows():
                    logger.info(f"  {row['ProductName']} ({row['Product Type*']})")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_edible_lineage()
    if success:
        logger.info("✅ Edible lineage test completed successfully")
    else:
        logger.error("❌ Edible lineage test failed") 