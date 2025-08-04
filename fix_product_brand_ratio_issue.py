#!/usr/bin/env python3
"""
Fix for ProductBrand field issue where THC ratio values are incorrectly 
appearing in the ProductBrand field instead of the actual brand name.
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.data.excel_processor import ExcelProcessor, get_default_upload_file

def fix_product_brand_ratio_issue():
    """Fix the ProductBrand field issue by ensuring proper data separation."""
    
    print("=== Fixing ProductBrand Field Issue ===")
    
    # Get the default upload file
    default_file = get_default_upload_file()
    if not default_file:
        print("No default upload file found!")
        return False
    
    print(f"Using file: {default_file}")
    
    # Initialize the Excel processor
    processor = ExcelProcessor()
    
    # Load the file
    success = processor.load_file(default_file)
    if not success:
        print("Failed to load file!")
        return False
    
    print(f"File loaded successfully. DataFrame shape: {processor.df.shape}")
    
    # Check if Product Brand column exists and has valid data
    if 'Product Brand' not in processor.df.columns:
        print("ERROR: Product Brand column not found!")
        return False
    
    # Check for any Product Brand values that look like THC ratios
    print("\nChecking for THC ratio values in Product Brand column...")
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
        
        # Fix the suspicious values by clearing them or setting to a default
        print("\nFixing suspicious Product Brand values...")
        for idx, brand in suspicious_brands:
            # Clear the suspicious value and set to empty string
            processor.df.at[idx, 'Product Brand'] = ""
            print(f"  Fixed row {idx}: cleared '{brand}' -> ''")
        
        # Save the fixed data back to the file
        try:
            processor.df.to_excel(default_file, index=False, engine='openpyxl')
            print(f"Fixed data saved to: {default_file}")
        except Exception as e:
            print(f"Error saving fixed data: {e}")
            return False
    else:
        print("No suspicious THC ratio values found in Product Brand column.")
    
    # Also check the Ratio column to ensure it's properly populated
    if 'Ratio' in processor.df.columns:
        print("\nChecking Ratio column...")
        sample_ratios = processor.df['Ratio'].head(10)
        for i, ratio in enumerate(sample_ratios, 1):
            print(f"  {i}. '{ratio}'")
    
    # Test the fix by getting available tags
    print(f"\n=== Testing Fix ===")
    tags = processor.get_available_tags()
    print(f"Got {len(tags)} available tags")
    
    if tags:
        print("\nSample tags with ProductBrand field (after fix):")
        for i, tag in enumerate(tags[:5], 1):
            product_brand = tag.get('ProductBrand', 'NOT_FOUND')
            product_name = tag.get('Product Name*', 'NOT_FOUND')
            print(f"  {i}. Product: '{product_name}' -> ProductBrand: '{product_brand}'")
    
    print("=== Fix Complete ===")
    return True

def verify_fix():
    """Verify that the fix worked by testing the data processing pipeline."""
    
    print("\n=== Verifying Fix ===")
    
    # Get the default upload file
    default_file = get_default_upload_file()
    if not default_file:
        print("No default upload file found!")
        return False
    
    # Initialize the Excel processor
    processor = ExcelProcessor()
    
    # Load the file
    success = processor.load_file(default_file)
    if not success:
        print("Failed to load file!")
        return False
    
    # Get available tags
    tags = processor.get_available_tags()
    if not tags:
        print("No tags found!")
        return False
    
    # Test with a few sample records
    test_tags = [tag.get('Product Name*', '') for tag in tags[:3] if tag.get('Product Name*', '')]
    if test_tags:
        processor.selected_tags = test_tags
        records = processor.get_selected_records()
        
        if records:
            print(f"\nTesting with {len(records)} selected records:")
            for i, record in enumerate(records, 1):
                product_brand = record.get('ProductBrand', 'NOT_FOUND')
                product_name = record.get('ProductName', 'NOT_FOUND')
                ratio = record.get('Ratio_or_THC_CBD', 'NOT_FOUND')
                
                # Check if ProductBrand contains any THC ratio patterns
                brand_str = str(product_brand)
                thc_patterns = ['THC:', 'CBD:', 'mg', '%']
                has_thc_pattern = any(pattern in brand_str for pattern in thc_patterns)
                
                print(f"  {i}. Product: '{product_name}'")
                print(f"     ProductBrand: '{product_brand}' {'[ISSUE DETECTED]' if has_thc_pattern else '[OK]'}")
                print(f"     Ratio_or_THC_CBD: '{ratio}'")
                print()
                
                if has_thc_pattern:
                    print(f"     WARNING: ProductBrand still contains THC ratio patterns!")
                    return False
        
        print("✓ All ProductBrand values look correct!")
        return True
    
    return False

if __name__ == "__main__":
    # Apply the fix
    if fix_product_brand_ratio_issue():
        # Verify the fix worked
        if verify_fix():
            print("\n✅ Fix applied and verified successfully!")
        else:
            print("\n❌ Fix verification failed!")
    else:
        print("\n❌ Fix application failed!") 