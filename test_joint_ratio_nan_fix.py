#!/usr/bin/env python3
"""
Test script to identify and fix NaN issues in JointRatio.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd

def test_joint_ratio_nan_issues():
    """Test and fix NaN issues in JointRatio."""
    
    print("=== JointRatio NaN Issue Test ===")
    
    # Initialize processor
    processor = ExcelProcessor()
    
    # Check if there's a default file loaded
    if hasattr(processor, 'df') and processor.df is not None:
        print(f"Found loaded data: {len(processor.df)} rows")
        
        # Check for JointRatio column
        if 'JointRatio' in processor.df.columns:
            print(f"✓ JointRatio column exists")
            
            # Check for pre-roll products
            preroll_mask = processor.df["Product Type*"].str.strip().str.lower().isin(["pre-roll", "infused pre-roll"])
            preroll_count = preroll_mask.sum()
            print(f"Found {preroll_count} pre-roll products")
            
            if preroll_count > 0:
                print("\n=== Pre-roll JointRatio NaN Analysis ===")
                preroll_data = processor.df[preroll_mask]
                
                # Check for NaN values
                nan_count = preroll_data['JointRatio'].isna().sum()
                print(f"NaN values in JointRatio: {nan_count}")
                
                # Check for 'nan' string values
                nan_string_count = (preroll_data['JointRatio'].astype(str).str.lower() == 'nan').sum()
                print(f"'nan' string values in JointRatio: {nan_string_count}")
                
                # Check for empty strings
                empty_count = (preroll_data['JointRatio'] == '').sum()
                print(f"Empty strings in JointRatio: {empty_count}")
                
                # Show problematic records
                print(f"\n=== Problematic JointRatio Records ===")
                problematic_mask = (
                    preroll_data['JointRatio'].isna() | 
                    (preroll_data['JointRatio'].astype(str).str.lower() == 'nan') |
                    (preroll_data['JointRatio'] == '')
                )
                
                problematic_records = preroll_data[problematic_mask]
                print(f"Found {len(problematic_records)} problematic records")
                
                for i, (idx, row) in enumerate(problematic_records.head(10).iterrows()):
                    product_name = row.get('Product Name*', 'NO NAME')
                    joint_ratio = row.get('JointRatio', '')
                    ratio = row.get('Ratio', '')
                    weight = row.get('Weight*', '')
                    
                    print(f"  {i+1}. {product_name}")
                    print(f"     JointRatio: '{joint_ratio}' (type: {type(joint_ratio)})")
                    print(f"     Ratio: '{ratio}'")
                    print(f"     Weight: '{weight}'")
                    
                    # Check what the issue is
                    if pd.isna(joint_ratio):
                        print(f"     ❌ ISSUE: JointRatio is NaN")
                    elif str(joint_ratio).lower() == 'nan':
                        print(f"     ❌ ISSUE: JointRatio is 'nan' string")
                    elif str(joint_ratio).strip() == '':
                        print(f"     ⚠️  ISSUE: JointRatio is empty string")
                
                # Apply fix
                print(f"\n=== Applying NaN Fix ===")
                fix_joint_ratio_nan_issues(processor)
                
                # Test the fix
                print(f"\n=== Testing Fix ===")
                test_joint_ratio_after_fix(processor)
                
        else:
            print("❌ JointRatio column missing")
            
            # Check what columns exist
            print(f"Available columns: {processor.df.columns.tolist()}")
            
            # Check for Joint Ratio (with space)
            if 'Joint Ratio' in processor.df.columns:
                print("⚠️  Found 'Joint Ratio' column (with space) instead of 'JointRatio'")
    else:
        print("❌ No data loaded. Please load a file first.")
        print("You can load a file by running the application and uploading an Excel file.")

def fix_joint_ratio_nan_issues(processor):
    """Fix NaN issues in JointRatio column."""
    
    print("Applying JointRatio NaN fixes...")
    
    # Get pre-roll mask
    preroll_mask = processor.df["Product Type*"].str.strip().str.lower().isin(["pre-roll", "infused pre-roll"])
    
    # Fix 1: Replace NaN values with empty strings
    processor.df.loc[preroll_mask, 'JointRatio'] = processor.df.loc[preroll_mask, 'JointRatio'].fillna('')
    
    # Fix 2: Replace 'nan' string values with empty strings
    nan_string_mask = (processor.df.loc[preroll_mask, 'JointRatio'].astype(str).str.lower() == 'nan')
    processor.df.loc[preroll_mask & nan_string_mask, 'JointRatio'] = ''
    
    # Fix 3: For empty JointRatio, try to use Ratio as fallback
    empty_joint_ratio_mask = preroll_mask & (processor.df['JointRatio'] == '')
    for idx in processor.df[empty_joint_ratio_mask].index:
        ratio_value = processor.df.loc[idx, 'Ratio']
        if pd.notna(ratio_value) and str(ratio_value).strip() != '' and str(ratio_value).lower() != 'nan':
            processor.df.loc[idx, 'JointRatio'] = str(ratio_value).strip()
            print(f"  Fixed record {idx}: Used Ratio '{ratio_value}' as JointRatio fallback")
    
    # Fix 4: For still empty JointRatio, generate default from Weight
    still_empty_mask = preroll_mask & (processor.df['JointRatio'] == '')
    for idx in processor.df[still_empty_mask].index:
        weight_value = processor.df.loc[idx, 'Weight*']
        if pd.notna(weight_value) and str(weight_value).strip() != '' and str(weight_value).lower() != 'nan':
            try:
                weight_float = float(weight_value)
                default_joint_ratio = f"{weight_float}g x 1 Pack"
                processor.df.loc[idx, 'JointRatio'] = default_joint_ratio
                print(f"  Fixed record {idx}: Generated default JointRatio '{default_joint_ratio}' from Weight")
            except (ValueError, TypeError):
                pass
    
    print("✅ JointRatio NaN fixes applied")

def test_joint_ratio_after_fix(processor):
    """Test JointRatio after applying fixes."""
    
    # Get pre-roll mask
    preroll_mask = processor.df["Product Type*"].str.strip().str.lower().isin(["pre-roll", "infused pre-roll"])
    preroll_data = processor.df[preroll_mask]
    
    # Check for remaining issues
    nan_count = preroll_data['JointRatio'].isna().sum()
    nan_string_count = (preroll_data['JointRatio'].astype(str).str.lower() == 'nan').sum()
    empty_count = (preroll_data['JointRatio'] == '').sum()
    
    print(f"After fix:")
    print(f"  NaN values: {nan_count}")
    print(f"  'nan' string values: {nan_string_count}")
    print(f"  Empty strings: {empty_count}")
    
    if nan_count == 0 and nan_string_count == 0:
        print("✅ All NaN issues fixed!")
    else:
        print("❌ Some NaN issues remain")
    
    # Test getting selected records
    print(f"\n=== Testing Selected Records After Fix ===")
    preroll_names = preroll_data['Product Name*'].head(3).tolist()
    print(f"Testing with pre-rolls: {preroll_names}")
    
    processor.select_tags(preroll_names)
    selected_records = processor.get_selected_records()
    
    print(f"Selected {len(selected_records)} records")
    for i, record in enumerate(selected_records):
        joint_ratio = record.get('JointRatio', '')
        weight_units = record.get('WeightUnits', '')
        product_name = record.get('ProductName', '')
        
        print(f"  Record {i+1}: {product_name}")
        print(f"    JointRatio: '{joint_ratio}' (type: {type(joint_ratio)})")
        print(f"    WeightUnits: '{weight_units}' (type: {type(weight_units)})")
        
        # Check for issues
        if pd.isna(joint_ratio) or str(joint_ratio).lower() == 'nan':
            print(f"    ❌ PROBLEM: JointRatio still has NaN issues")
        elif str(joint_ratio).strip() == '':
            print(f"    ⚠️  JointRatio is empty (but not NaN)")
        else:
            print(f"    ✓ JointRatio is valid")

if __name__ == "__main__":
    test_joint_ratio_nan_issues() 