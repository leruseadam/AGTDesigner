#!/usr/bin/env python3
"""
Debug script to identify dropdown population issues
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add the src directory to the path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from core.data.excel_processor import ExcelProcessor, get_default_upload_file

def test_dropdown_population():
    """Test the dropdown population to identify issues"""
    print("=== Testing Dropdown Population ===")
    
    # Initialize processor
    processor = ExcelProcessor()
    
    # Try to load default file
    default_file = get_default_upload_file()
    if default_file and os.path.exists(default_file):
        print(f"Loading default file: {default_file}")
        success = processor.load_file(default_file)
        if not success:
            print("❌ Failed to load default file")
            return
    else:
        print("❌ No default file found")
        return
    
    print(f"✅ File loaded successfully")
    print(f"DataFrame shape: {processor.df.shape}")
    print(f"Columns: {list(processor.df.columns)}")
    
    # Test filter options generation
    print("\n=== Testing Filter Options ===")
    try:
        filter_options = processor.get_dynamic_filter_options({})
        
        for filter_type, options in filter_options.items():
            print(f"\n{filter_type.upper()} ({len(options)} options):")
            if len(options) > 20:
                print(f"  First 10: {options[:10]}")
                print(f"  Last 10: {options[-10:]}")
                print(f"  Total: {len(options)} options")
            else:
                print(f"  All: {options}")
                
            # Check for potential issues
            if len(options) > 100:
                print(f"  ⚠️  WARNING: {filter_type} has {len(options)} options - this might cause UI issues")
            
            # Check for empty or null values
            empty_count = sum(1 for opt in options if not opt or opt.strip() == '')
            if empty_count > 0:
                print(f"  ⚠️  WARNING: {filter_type} has {empty_count} empty/null values")
                
            # Check for very long option names that might cause display issues
            long_options = [opt for opt in options if opt and len(str(opt)) > 50]
            if long_options:
                print(f"  ⚠️  WARNING: {filter_type} has {len(long_options)} very long options (>50 chars)")
                print(f"     Examples: {long_options[:3]}")
                
    except Exception as e:
        print(f"❌ Error generating filter options: {e}")
        import traceback
        traceback.print_exc()

def test_specific_columns():
    """Test specific columns that might be causing issues"""
    print("\n=== Testing Specific Columns ===")
    
    processor = ExcelProcessor()
    default_file = get_default_upload_file()
    
    if default_file and os.path.exists(default_file):
        success = processor.load_file(default_file)
        if success:
            df = processor.df
            
            # Test vendor column
            if 'Vendor' in df.columns:
                vendors = df['Vendor'].dropna().unique()
                print(f"Vendor unique values: {len(vendors)}")
                print(f"Sample vendors: {vendors[:10].tolist()}")
                
                # Check for very long vendor names
                long_vendors = [v for v in vendors if len(str(v)) > 50]
                if long_vendors:
                    print(f"⚠️  Long vendor names found: {long_vendors[:5]}")
            
            # Test Product Brand column
            if 'Product Brand' in df.columns:
                brands = df['Product Brand'].dropna().unique()
                print(f"Product Brand unique values: {len(brands)}")
                print(f"Sample brands: {brands[:10].tolist()}")
                
                # Check for very long brand names
                long_brands = [b for b in brands if len(str(b)) > 50]
                if long_brands:
                    print(f"⚠️  Long brand names found: {long_brands[:5]}")
            
            # Test Product Type column
            if 'Product Type*' in df.columns:
                types = df['Product Type*'].dropna().unique()
                print(f"Product Type unique values: {len(types)}")
                print(f"Sample types: {types[:10].tolist()}")
            
            # Test Lineage column
            if 'Lineage' in df.columns:
                lineages = df['Lineage'].dropna().unique()
                print(f"Lineage unique values: {len(lineages)}")
                print(f"Sample lineages: {lineages[:10].tolist()}")

def test_weight_formatting():
    """Test weight formatting which might be causing issues"""
    print("\n=== Testing Weight Formatting ===")
    
    processor = ExcelProcessor()
    default_file = get_default_upload_file()
    
    if default_file and os.path.exists(default_file):
        success = processor.load_file(default_file)
        if success:
            df = processor.df
            
            # Test weight formatting on first 10 rows
            for i, (_, row) in enumerate(df.head(10).iterrows()):
                row_dict = row.to_dict()
                formatted_weight = processor._format_weight_units(row_dict)
                print(f"Row {i}: {formatted_weight}")

def test_dropdown_overflow():
    """Test for potential dropdown overflow issues"""
    print("\n=== Testing Dropdown Overflow Issues ===")
    
    processor = ExcelProcessor()
    default_file = get_default_upload_file()
    
    if default_file and os.path.exists(default_file):
        success = processor.load_file(default_file)
        if success:
            df = processor.df
            
            # Check for columns that might have too many unique values
            problematic_columns = []
            
            for col in df.columns:
                unique_count = df[col].dropna().nunique()
                if unique_count > 200:  # Threshold for potential UI issues
                    problematic_columns.append((col, unique_count))
            
            if problematic_columns:
                print("⚠️  Columns with potentially too many unique values for dropdowns:")
                for col, count in problematic_columns:
                    print(f"  - {col}: {count} unique values")
                    
                    # Show some sample values
                    sample_values = df[col].dropna().unique()[:10]
                    print(f"    Sample values: {sample_values.tolist()}")
            else:
                print("✅ No columns with excessive unique values found")

if __name__ == "__main__":
    test_dropdown_population()
    test_specific_columns()
    test_weight_formatting()
    test_dropdown_overflow() 