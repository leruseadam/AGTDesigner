#!/usr/bin/env python3
"""
Detailed test to examine uploaded data processing issues
"""

import os
import sys
import pandas as pd
import logging
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_uploaded_file_processing():
    """Test processing of uploaded files to identify issues."""
    try:
        # Test each uploaded file
        upload_dir = Path("uploads")
        excel_files = list(upload_dir.glob("*.xlsx"))
        
        for file_path in excel_files:
            logger.info(f"\n{'='*60}")
            logger.info(f"TESTING FILE: {file_path.name}")
            logger.info(f"{'='*60}")
            
            # 1. Read raw file
            logger.info("\n1. READING RAW FILE:")
            raw_df = pd.read_excel(file_path)
            logger.info(f"   Raw rows: {len(raw_df)}")
            logger.info(f"   Raw columns: {len(raw_df.columns)}")
            
            # Check for edibles specifically
            if 'Product Type*' in raw_df.columns:
                edible_mask = raw_df['Product Type*'].str.contains('edible', case=False, na=False)
                edible_count = edible_mask.sum()
                logger.info(f"   Raw edible products: {edible_count}")
                
                if edible_count > 0:
                    logger.info("   Sample edible products (raw):")
                    sample_edibles = raw_df[edible_mask].head(5)
                    for idx, row in sample_edibles.iterrows():
                        name = row.get('Product Name*', 'Unknown')
                        desc = row.get('Description', '')
                        lineage = row.get('Lineage', '')
                        logger.info(f"     - {name} | Lineage: {lineage} | Desc: {desc[:50]}...")
            
            # 2. Process with ExcelProcessor
            logger.info("\n2. PROCESSING WITH EXCELPROCESSOR:")
            processor = ExcelProcessor()
            success = processor.load_file(str(file_path))
            
            if success:
                logger.info(f"   Processed rows: {len(processor.df)}")
                logger.info(f"   Processed columns: {len(processor.df.columns)}")
                
                # Check processed edibles
                if 'Product Type*' in processor.df.columns:
                    processed_edible_mask = processor.df['Product Type*'].str.contains('edible', case=False, na=False)
                    processed_edible_count = processed_edible_mask.sum()
                    logger.info(f"   Processed edible products: {processed_edible_count}")
                    
                    if processed_edible_count > 0:
                        logger.info("   Sample edible products (processed):")
                        sample_processed = processor.df[processed_edible_mask].head(5)
                        for idx, row in sample_processed.iterrows():
                            name = row.get('ProductName', row.get('Product Name*', 'Unknown'))
                            desc = row.get('Description', '')
                            lineage = row.get('Lineage', '')
                            strain = row.get('Product Strain', '')
                            logger.info(f"     - {name} | Lineage: {lineage} | Strain: {strain} | Desc: {desc[:50]}...")
                
                # Check lineage distribution
                if 'Lineage' in processor.df.columns:
                    lineage_counts = processor.df['Lineage'].value_counts()
                    logger.info(f"   Lineage distribution: {dict(lineage_counts)}")
                
                # Check for any data corruption
                logger.info("\n3. DATA QUALITY CHECKS:")
                
                # Check for empty product names
                if 'ProductName' in processor.df.columns:
                    empty_names = processor.df['ProductName'].isna().sum()
                    logger.info(f"   Empty product names: {empty_names}")
                
                # Check for missing lineages
                if 'Lineage' in processor.df.columns:
                    missing_lineages = processor.df['Lineage'].isna().sum()
                    logger.info(f"   Missing lineages: {missing_lineages}")
                
                # Check for invalid lineages
                valid_lineages = ["SATIVA", "INDICA", "HYBRID", "HYBRID/SATIVA", "HYBRID/INDICA", "CBD", "MIXED", "PARAPHERNALIA"]
                if 'Lineage' in processor.df.columns:
                    invalid_lineages = [lineage for lineage in processor.df['Lineage'].unique() if lineage not in valid_lineages]
                    if invalid_lineages:
                        logger.warning(f"   Invalid lineages found: {invalid_lineages}")
                    else:
                        logger.info("   All lineages are valid")
                
                # Check for data type issues
                logger.info("\n4. DATA TYPE ANALYSIS:")
                for col in ['ProductName', 'Lineage', 'Product Strain', 'Description']:
                    if col in processor.df.columns:
                        dtype = processor.df[col].dtype
                        null_count = processor.df[col].isna().sum()
                        unique_count = processor.df[col].nunique()
                        logger.info(f"   {col}: dtype={dtype}, nulls={null_count}, unique={unique_count}")
                
            else:
                logger.error(f"   Failed to process file: {file_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

def test_specific_edible_issues():
    """Test specific issues with edible processing."""
    try:
        logger.info(f"\n{'='*60}")
        logger.info("TESTING SPECIFIC EDIBLE ISSUES")
        logger.info(f"{'='*60}")
        
        # Test with the default file
        default_file = get_default_upload_file()
        if not default_file:
            logger.error("No default file found")
            return False
        
        processor = ExcelProcessor()
        success = processor.load_file(default_file)
        
        if not success:
            logger.error("Failed to load default file")
            return False
        
        # Focus on edibles
        if 'Product Type*' in processor.df.columns:
            edible_mask = processor.df['Product Type*'].str.contains('edible', case=False, na=False)
            edible_df = processor.df[edible_mask].copy()
            
            logger.info(f"Total edible products: {len(edible_df)}")
            
            # Check lineage assignment
            if 'Lineage' in edible_df.columns:
                lineage_counts = edible_df['Lineage'].value_counts()
                logger.info(f"Edible lineage distribution: {dict(lineage_counts)}")
                
                # Check specific examples
                logger.info("\nSample CBD lineage edibles:")
                cbd_edibles = edible_df[edible_df['Lineage'] == 'CBD'].head(3)
                for idx, row in cbd_edibles.iterrows():
                    name = row.get('ProductName', 'Unknown')
                    desc = row.get('Description', '')
                    strain = row.get('Product Strain', '')
                    logger.info(f"  - {name} | Strain: {strain} | Desc: {desc[:50]}...")
                
                logger.info("\nSample MIXED lineage edibles:")
                mixed_edibles = edible_df[edible_df['Lineage'] == 'MIXED'].head(3)
                for idx, row in mixed_edibles.iterrows():
                    name = row.get('ProductName', 'Unknown')
                    desc = row.get('Description', '')
                    strain = row.get('Product Strain', '')
                    logger.info(f"  - {name} | Strain: {strain} | Desc: {desc[:50]}...")
            
            # Check for any edibles with wrong lineages
            if 'Lineage' in edible_df.columns:
                wrong_lineages = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA']
                wrong_edibles = edible_df[edible_df['Lineage'].isin(wrong_lineages)]
                if len(wrong_edibles) > 0:
                    logger.warning(f"Found {len(wrong_edibles)} edibles with wrong lineages:")
                    for idx, row in wrong_edibles.head(3).iterrows():
                        name = row.get('ProductName', 'Unknown')
                        lineage = row.get('Lineage', '')
                        logger.warning(f"  - {name} | Lineage: {lineage}")
                else:
                    logger.info("All edibles have correct lineages (CBD or MIXED)")
        
        return True
        
    except Exception as e:
        logger.error(f"Edible test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("=== DETAILED UPLOAD TEST START ===")
    
    # Test uploaded file processing
    logger.info("\n1. Testing uploaded file processing...")
    upload_ok = test_uploaded_file_processing()
    
    # Test specific edible issues
    logger.info("\n2. Testing specific edible issues...")
    edible_ok = test_specific_edible_issues()
    
    # Summary
    logger.info("\n=== TEST SUMMARY ===")
    logger.info(f"Upload processing: {'✅ OK' if upload_ok else '❌ FAILED'}")
    logger.info(f"Edible processing: {'✅ OK' if edible_ok else '❌ FAILED'}")
    
    if all([upload_ok, edible_ok]):
        logger.info("All tests passed - no obvious issues found")
    else:
        logger.warning("Some tests failed - review the logs above for details")

if __name__ == "__main__":
    main() 