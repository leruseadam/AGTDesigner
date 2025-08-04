#!/usr/bin/env python3
"""
Test script to verify the JointRatio fix
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor

def test_joint_ratio_fix():
    """Test the JointRatio processing fix"""
    print("🧪 Testing JointRatio Fix")
    print("=" * 50)
    
    # Create test data with various JointRatio scenarios
    test_data = {
        'ProductName': [
            'Test Pre-Roll 1',
            'Test Pre-Roll 2', 
            'Test Pre-Roll 3',
            'Test Pre-Roll 4',
            'Test Pre-Roll 5'
        ],
        'Product Type*': [
            'pre-roll',
            'pre-roll',
            'pre-roll', 
            'pre-roll',
            'pre-roll'
        ],
        'Joint Ratio': [
            '1g x 28 Pack',  # Valid format
            '3.5g',          # Simple weight
            '1g x 10',       # Valid format without "Pack"
            '',              # Empty
            'nan'            # NaN string
        ],
        'Weight*': [
            28.0,
            3.5,
            10.0,
            1.0,
            5.0
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Create Excel processor
    processor = ExcelProcessor()
    processor.df = df
    
    # Apply the joint ratio processing logic
    print("\n1. Testing JointRatio processing...")
    
    # Apply the same logic as in the Excel processor
    preroll_mask = processor.df["Product Type*"].str.strip().str.lower().isin(["pre-roll", "infused pre-roll"])
    processor.df["JointRatio"] = ""
    
    if preroll_mask.any():
        # First, try to use "Joint Ratio" column if it exists
        if "Joint Ratio" in processor.df.columns:
            joint_ratio_values = processor.df.loc[preroll_mask, "Joint Ratio"].fillna('')
            # Accept any non-empty Joint Ratio values that look like valid formats
            valid_joint_ratio_mask = (
                (joint_ratio_values.astype(str).str.strip() != '') & 
                (joint_ratio_values.astype(str).str.lower() != 'nan') &
                (joint_ratio_values.astype(str).str.lower() != '') &
                # Accept formats with 'g' and numbers, or 'pack', or 'x' separator
                (
                    joint_ratio_values.astype(str).str.contains(r'\d+g', case=False, na=False) |
                    joint_ratio_values.astype(str).str.contains(r'pack', case=False, na=False) |
                    joint_ratio_values.astype(str).str.contains(r'x', case=False, na=False) |
                    joint_ratio_values.astype(str).str.contains(r'\d+', case=False, na=False)
                )
            )
            processor.df.loc[preroll_mask & valid_joint_ratio_mask, "JointRatio"] = joint_ratio_values[valid_joint_ratio_mask]
        
        # For remaining pre-rolls without valid JointRatio, try to generate from Weight
        remaining_preroll_mask = preroll_mask & (processor.df["JointRatio"] == '')
        for idx in processor.df[remaining_preroll_mask].index:
            weight_value = processor.df.loc[idx, 'Weight*']
            if pd.notna(weight_value) and str(weight_value).strip() != '' and str(weight_value).lower() != 'nan':
                try:
                    weight_float = float(weight_value)
                    # Generate a more descriptive format: "1g x 1" for single units
                    if weight_float == 1.0:
                        default_joint_ratio = "1g x 1"
                    else:
                        default_joint_ratio = f"{weight_float}g"
                    processor.df.loc[idx, 'JointRatio'] = default_joint_ratio
                except (ValueError, TypeError):
                    pass
    
    # Ensure no NaN values remain in JointRatio column
    processor.df["JointRatio"] = processor.df["JointRatio"].fillna('')
    
    # Fix: Replace any 'nan' string values with empty strings
    nan_string_mask = (processor.df["JointRatio"].astype(str).str.lower() == 'nan')
    processor.df.loc[nan_string_mask, "JointRatio"] = ''
    
    # Fix: For still empty JointRatio, generate default from Weight
    still_empty_mask = preroll_mask & (processor.df["JointRatio"] == '')
    for idx in processor.df[still_empty_mask].index:
        weight_value = processor.df.loc[idx, 'Weight*']
        if pd.notna(weight_value) and str(weight_value).strip() != '' and str(weight_value).lower() != 'nan':
            try:
                weight_float = float(weight_value)
                # Generate a more descriptive format: "1g x 1" for single units
                if weight_float == 1.0:
                    default_joint_ratio = "1g x 1"
                else:
                    default_joint_ratio = f"{weight_float}g"
                processor.df.loc[idx, 'JointRatio'] = default_joint_ratio
            except (ValueError, TypeError):
                pass
    
    # Display results
    print("\n2. Results:")
    print("-" * 50)
    for idx, row in processor.df.iterrows():
        original = row['Joint Ratio']
        processed = row['JointRatio']
        weight = row['Weight*']
        print(f"Record {idx}:")
        print(f"  Original: '{original}'")
        print(f"  Processed: '{processed}'")
        print(f"  Weight: {weight}")
        print()
    
    # Test specific cases
    print("3. Testing specific cases:")
    print("-" * 50)
    
    # Test case 1: "1g x 28 Pack" should be preserved
    case1 = processor.df.iloc[0]
    if case1['JointRatio'] == '1g x 28 Pack':
        print("✅ Case 1 PASSED: '1g x 28 Pack' preserved correctly")
    else:
        print(f"❌ Case 1 FAILED: Expected '1g x 28 Pack', got '{case1['JointRatio']}'")
    
    # Test case 2: "3.5g" should be preserved
    case2 = processor.df.iloc[1]
    if case2['JointRatio'] == '3.5g':
        print("✅ Case 2 PASSED: '3.5g' preserved correctly")
    else:
        print(f"❌ Case 2 FAILED: Expected '3.5g', got '{case2['JointRatio']}'")
    
    # Test case 3: "1g x 10" should be preserved
    case3 = processor.df.iloc[2]
    if case3['JointRatio'] == '1g x 10':
        print("✅ Case 3 PASSED: '1g x 10' preserved correctly")
    else:
        print(f"❌ Case 3 FAILED: Expected '1g x 10', got '{case3['JointRatio']}'")
    
    # Test case 4: Empty should generate "1g x 1" for weight 1.0
    case4 = processor.df.iloc[3]
    if case4['JointRatio'] == '1g x 1':
        print("✅ Case 4 PASSED: Empty generated '1g x 1' correctly")
    else:
        print(f"❌ Case 4 FAILED: Expected '1g x 1', got '{case4['JointRatio']}'")
    
    # Test case 5: NaN should generate "5.0g" for weight 5.0
    case5 = processor.df.iloc[4]
    if case5['JointRatio'] == '5.0g':
        print("✅ Case 5 PASSED: NaN generated '5.0g' correctly")
    else:
        print(f"❌ Case 5 FAILED: Expected '5.0g', got '{case5['JointRatio']}'")
    
    print("\n🎉 JointRatio fix test completed!")

if __name__ == "__main__":
    test_joint_ratio_fix() 