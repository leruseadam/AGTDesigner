#!/usr/bin/env python3
"""
Script to check actual data columns and THC/CBD values in the real data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd

def check_actual_data():
    """Check the actual data to see what columns and values are available."""
    
    print("Checking actual data columns and THC/CBD values")
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
    
    print(f"✅ File loaded successfully: {len(processor.df)} rows, {len(processor.df.columns)} columns")
    
    # Check all column names
    print("\nAll available columns:")
    for i, col in enumerate(processor.df.columns):
        print(f"  {i+1:2d}. {col}")
    
    # Look for THC/CBD related columns
    print("\nTHC/CBD related columns:")
    thc_cbd_columns = []
    for col in processor.df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['thc', 'cbd', 'cannabinoid', 'ai', 'aj', 'ak']):
            thc_cbd_columns.append(col)
            print(f"  ✅ {col}")
    
    if not thc_cbd_columns:
        print("  ❌ No THC/CBD related columns found")
    
    # Check for AI, AJ, AK columns specifically
    print("\nChecking for AI, AJ, AK columns:")
    ai_col = None
    aj_col = None
    ak_col = None
    
    for col in processor.df.columns:
        if col == 'AI':
            ai_col = col
            print(f"  ✅ Found AI column: {col}")
        elif col == 'AJ':
            aj_col = col
            print(f"  ✅ Found AJ column: {col}")
        elif col == 'AK':
            ak_col = col
            print(f"  ✅ Found AK column: {col}")
    
    if not ai_col:
        print("  ❌ AI column not found")
    if not aj_col:
        print("  ❌ AJ column not found")
    if not ak_col:
        print("  ❌ AK column not found")
    
    # Check sample values from these columns
    if ai_col or aj_col or ak_col:
        print("\nSample values from THC/CBD columns:")
        sample_rows = processor.df.head(5)
        
        for i, (idx, row) in enumerate(sample_rows.iterrows()):
            product_name = row.get('Product Name*', f'Row {idx}')
            product_type = row.get('Product Type*', 'Unknown')
            
            print(f"  Product {i+1}: {product_name} ({product_type})")
            
            if ai_col:
                ai_value = row.get(ai_col, '')
                print(f"    {ai_col}: '{ai_value}'")
            
            if aj_col:
                aj_value = row.get(aj_col, '')
                print(f"    {aj_col}: '{aj_value}'")
            
            if ak_col:
                ak_value = row.get(ak_col, '')
                print(f"    {ak_col}: '{ak_value}'")
            
            print()
    
    # Check classic types
    print("Checking classic types:")
    classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
    
    classic_mask = processor.df["Product Type*"].str.strip().str.lower().isin(classic_types)
    classic_count = classic_mask.sum()
    
    print(f"  Found {classic_count} classic type products")
    
    if classic_count > 0:
        classic_df = processor.df[classic_mask]
        print("\nSample classic type products:")
        
        for i, (idx, row) in enumerate(classic_df.head(3).iterrows()):
            product_name = row.get('Product Name*', f'Row {idx}')
            product_type = row.get('Product Type*', 'Unknown')
            ratio = row.get('Ratio', '')
            
            print(f"  {i+1}. {product_name} ({product_type})")
            print(f"     Ratio: '{ratio}'")
            
            if ai_col:
                ai_value = row.get(ai_col, '')
                print(f"     {ai_col}: '{ai_value}'")
            
            if aj_col:
                aj_value = row.get(aj_col, '')
                print(f"     {aj_col}: '{aj_value}'")
            
            if ak_col:
                ak_value = row.get(ak_col, '')
                print(f"     {ak_col}: '{ak_value}'")
            
            print()
    
    # Check Ratio_or_THC_CBD column
    if 'Ratio_or_THC_CBD' in processor.df.columns:
        print("Ratio_or_THC_CBD column values:")
        ratio_values = processor.df['Ratio_or_THC_CBD'].value_counts()
        for value, count in ratio_values.head(10).items():
            print(f"  '{value}': {count} products")
    else:
        print("❌ Ratio_or_THC_CBD column not found")
    
    print("\n" + "=" * 60)
    print("Data check completed!")

if __name__ == "__main__":
    check_actual_data() 