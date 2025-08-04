#!/usr/bin/env python3
"""
Debug script to investigate ProductBrand field issue where THC ratio values 
are appearing in the ProductBrand field instead of the actual brand name.
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.data.excel_processor import ExcelProcessor, get_default_upload_file

def debug_product_brand_issue():
    """Debug the ProductBrand field issue."""
    
    print("=== ProductBrand Field Debug ===")
    
    # Get the default upload file
    default_file = get_default_upload_file()
    if not default_file:
        print("No default upload file found!")
        return
    
    print(f"Using file: {default_file}")
    
    # Initialize the Excel processor
    processor = ExcelProcessor()
    
    # Load the file
    success = processor.load_file(default_file)
    if not success:
        print("Failed to load file!")
        return
    
    print(f"File loaded successfully. DataFrame shape: {processor.df.shape}")
    
    # Check the columns
    print(f"\nAvailable columns: {list(processor.df.columns)}")
    
    # Check if Product Brand column exists
    if 'Product Brand' in processor.df.columns:
        print(f"\nProduct Brand column found!")
        
        # Show some sample values
        print("\nSample Product Brand values:")
        sample_brands = processor.df['Product Brand'].head(10)
        for i, brand in enumerate(sample_brands, 1):
            print(f"  {i}. '{brand}' (type: {type(brand)})")
        
        # Check for any values that look like THC ratios
        print("\nChecking for THC ratio values in Product Brand:")
        thc_patterns = ['THC:', 'CBD:', 'mg', '%']
        suspicious_brands = []
        
        for idx, brand in enumerate(processor.df['Product Brand']):
            if pd.isna(brand):
                continue
            brand_str = str(brand).strip()
            if any(pattern in brand_str for pattern in thc_patterns):
                suspicious_brands.append((idx, brand_str))
        
        if suspicious_brands:
            print(f"Found {len(suspicious_brands)} suspicious Product Brand values:")
            for idx, brand in suspicious_brands[:10]:  # Show first 10
                print(f"  Row {idx}: '{brand}'")
        else:
            print("No suspicious THC ratio values found in Product Brand column.")
    
    # Check the Ratio column
    if 'Ratio' in processor.df.columns:
        print(f"\nRatio column found!")
        print("\nSample Ratio values:")
        sample_ratios = processor.df['Ratio'].head(10)
        for i, ratio in enumerate(sample_ratios, 1):
            print(f"  {i}. '{ratio}' (type: {type(ratio)})")
    
    # Check Ratio_or_THC_CBD column
    if 'Ratio_or_THC_CBD' in processor.df.columns:
        print(f"\nRatio_or_THC_CBD column found!")
        print("\nSample Ratio_or_THC_CBD values:")
        sample_ratios = processor.df['Ratio_or_THC_CBD'].head(10)
        for i, ratio in enumerate(sample_ratios, 1):
            print(f"  {i}. '{ratio}' (type: {type(ratio)})")
    
    # Get available tags to see how ProductBrand is being processed
    print(f"\n=== Testing get_available_tags ===")
    tags = processor.get_available_tags()
    print(f"Got {len(tags)} available tags")
    
    if tags:
        print("\nSample tags with ProductBrand field:")
        for i, tag in enumerate(tags[:5], 1):
            product_brand = tag.get('ProductBrand', 'NOT_FOUND')
            product_name = tag.get('Product Name*', 'NOT_FOUND')
            print(f"  {i}. Product: '{product_name}' -> ProductBrand: '{product_brand}'")
    
    # Test get_selected_records with a few sample records
    print(f"\n=== Testing get_selected_records ===")
    if tags:
        # Select first 3 tags for testing
        test_tags = [tag.get('Product Name*', '') for tag in tags[:3] if tag.get('Product Name*', '')]
        if test_tags:
            processor.selected_tags = test_tags
            records = processor.get_selected_records()
            print(f"Got {len(records)} selected records")
            
            if records:
                print("\nSample processed records:")
                for i, record in enumerate(records[:3], 1):
                    product_brand = record.get('ProductBrand', 'NOT_FOUND')
                    product_name = record.get('ProductName', 'NOT_FOUND')
                    ratio = record.get('Ratio_or_THC_CBD', 'NOT_FOUND')
                    print(f"  {i}. Product: '{product_name}'")
                    print(f"     ProductBrand: '{product_brand}'")
                    print(f"     Ratio_or_THC_CBD: '{ratio}'")
                    print()
    
    print("=== Debug Complete ===")

if __name__ == "__main__":
    debug_product_brand_issue() 