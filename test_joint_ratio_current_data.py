#!/usr/bin/env python3
"""
Test script to check JointRatio issues with current data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd

def test_joint_ratio_current_data():
    """Test JointRatio processing with current data."""
    
    print("=== JointRatio Current Data Test ===")
    
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
                print("\n=== Pre-roll JointRatio Analysis ===")
                preroll_data = processor.df[preroll_mask]
                
                # Check JointRatio values
                joint_ratio_values = preroll_data['JointRatio'].tolist()
                print(f"JointRatio values for pre-rolls:")
                for i, value in enumerate(joint_ratio_values[:10]):  # Show first 10
                    print(f"  {i+1}. '{value}' (type: {type(value)})")
                    
                    # Check for issues
                    if pd.isna(value):
                        print(f"    ❌ PROBLEM: JointRatio is NaN")
                    elif str(value).lower() == 'nan':
                        print(f"    ❌ PROBLEM: JointRatio is 'nan' string")
                    elif str(value).strip() == '':
                        print(f"    ⚠️  JointRatio is empty string")
                    else:
                        print(f"    ✓ JointRatio looks good")
                
                # Check for NaN values
                nan_count = preroll_data['JointRatio'].isna().sum()
                print(f"\nNaN values in JointRatio: {nan_count}")
                
                # Check for empty strings
                empty_count = (preroll_data['JointRatio'] == '').sum()
                print(f"Empty strings in JointRatio: {empty_count}")
                
                # Test getting selected records for pre-rolls
                print(f"\n=== Testing Selected Pre-roll Records ===")
                preroll_names = preroll_data['Product Name*'].head(3).tolist()
                print(f"Testing with pre-rolls: {preroll_names}")
                
                processor.select_tags(preroll_names)
                selected_records = processor.get_selected_records()
                
                print(f"Selected {len(selected_records)} records")
                for i, record in enumerate(selected_records):
                    joint_ratio = record.get('JointRatio', '')
                    weight_units = record.get('WeightUnits', '')
                    product_name = record.get('ProductName', '')
                    product_type = record.get('ProductType', '')
                    
                    print(f"  Record {i+1}: {product_name}")
                    print(f"    Product Type: {product_type}")
                    print(f"    JointRatio: '{joint_ratio}' (type: {type(joint_ratio)})")
                    print(f"    WeightUnits: '{weight_units}' (type: {type(weight_units)})")
                    
                    # Check for issues
                    if pd.isna(joint_ratio) or str(joint_ratio).lower() == 'nan':
                        print(f"    ❌ PROBLEM: JointRatio is NaN or 'nan' in processed record")
                    elif str(joint_ratio).strip() == '':
                        print(f"    ⚠️  JointRatio is empty in processed record")
                    else:
                        print(f"    ✓ JointRatio is valid in processed record")
                    
                    # Check if WeightUnits is empty for pre-rolls
                    if product_type.lower() in ['pre-roll', 'infused pre-roll']:
                        if str(weight_units).strip() == '':
                            print(f"    ❌ PROBLEM: WeightUnits is empty for pre-roll")
                        else:
                            print(f"    ✓ WeightUnits has value for pre-roll")
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

if __name__ == "__main__":
    test_joint_ratio_current_data() 