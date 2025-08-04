#!/usr/bin/env python3
"""
Script to check what THC/CBD columns are actually available in the data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd

def check_thc_cbd_columns():
    """Check what THC/CBD columns are available and their values."""
    
    print("Checking THC/CBD columns in actual data")
    print("=" * 60)
    
    # Create Excel processor
    processor = ExcelProcessor()
    
    # Get the default file
    from src.core.data.excel_processor import get_default_upload_file
    default_file = get_default_upload_file()
    
    if not default_file:
        print("❌ No default file found")
        return
    
    print(f"Found default file: {default_file}")
    
    # Load the file
    success = processor.load_file(default_file)
    if not success:
        print("❌ Failed to load file")
        return
    
    print(f"✅ File loaded successfully: {len(processor.df)} rows")
    
    # Find all THC/CBD related columns
    thc_cbd_columns = []
    for col in processor.df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['thc', 'cbd', 'cannabinoid']):
            thc_cbd_columns.append(col)
    
    print(f"\nFound {len(thc_cbd_columns)} THC/CBD related columns:")
    for col in thc_cbd_columns:
        print(f"  ✅ {col}")
    
    # Check classic types
    classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
    classic_mask = processor.df["Product Type*"].str.strip().str.lower().isin(classic_types)
    classic_df = processor.df[classic_mask]
    
    print(f"\nFound {len(classic_df)} classic type products")
    
    # Check sample values from THC/CBD columns for classic types
    print("\nSample values from THC/CBD columns for classic types:")
    sample_classic = classic_df.head(10)
    
    for i, (idx, row) in enumerate(sample_classic.iterrows()):
        product_name = row.get('Product Name*', f'Row {idx}')
        product_type = row.get('Product Type*', 'Unknown')
        
        print(f"\n  Product {i+1}: {product_name} ({product_type})")
        
        # Check each THC/CBD column
        for col in thc_cbd_columns:
            value = row.get(col, '')
            if pd.notna(value) and str(value).strip():
                print(f"    {col}: '{value}'")
    
    # Check which columns have the most non-empty values
    print("\nColumn usage statistics:")
    for col in thc_cbd_columns:
        non_empty_count = classic_df[col].notna().sum()
        total_count = len(classic_df)
        percentage = (non_empty_count / total_count) * 100 if total_count > 0 else 0
        print(f"  {col}: {non_empty_count}/{total_count} ({percentage:.1f}%)")
    
    # Check for specific columns that might be used for THC/CBD values
    potential_thc_columns = ['Total THC', 'THCA', 'THC test result', 'THC Per Serving']
    potential_cbd_columns = ['CBDA', 'CBD test result']
    
    print("\nPotential THC columns:")
    for col in potential_thc_columns:
        if col in processor.df.columns:
            non_empty_count = classic_df[col].notna().sum()
            total_count = len(classic_df)
            percentage = (non_empty_count / total_count) * 100 if total_count > 0 else 0
            print(f"  {col}: {non_empty_count}/{total_count} ({percentage:.1f}%)")
            
            # Show sample values
            sample_values = classic_df[col].dropna().head(3).tolist()
            if sample_values:
                print(f"    Sample values: {sample_values}")
    
    print("\nPotential CBD columns:")
    for col in potential_cbd_columns:
        if col in processor.df.columns:
            non_empty_count = classic_df[col].notna().sum()
            total_count = len(classic_df)
            percentage = (non_empty_count / total_count) * 100 if total_count > 0 else 0
            print(f"  {col}: {non_empty_count}/{total_count} ({percentage:.1f}%)")
            
            # Show sample values
            sample_values = classic_df[col].dropna().head(3).tolist()
            if sample_values:
                print(f"    Sample values: {sample_values}")
    
    print("\n" + "=" * 60)
    print("Column check completed!")

if __name__ == "__main__":
    check_thc_cbd_columns() 