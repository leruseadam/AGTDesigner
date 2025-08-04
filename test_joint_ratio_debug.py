#!/usr/bin/env python3
"""
Test script to debug JointRatio issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd

def test_joint_ratio_debug():
    """Test JointRatio processing to identify issues."""
    
    print("=== JointRatio Debug Test ===")
    
    # Create test data with various JointRatio scenarios
    test_data = {
        'Product Name*': [
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
            '1.0g x 1 Pack',
            '1.5g x 2 Pack',
            '2.0g x 3 Pack',
            '1.0g',
            '2.5g x 5 Pack'
        ],
        'Ratio': [
            'THC: 25% CBD: 2%',
            'THC: 30% CBD: 1%',
            'THC: 28% CBD: 3%',
            'THC: 22% CBD: 1%',
            'THC: 35% CBD: 2%'
        ],
        'Weight*': ['1.0', '1.5', '2.0', '1.0', '2.5'],
        'Units': ['g', 'g', 'g', 'g', 'g'],
        'Product Brand': ['Test Brand', 'Test Brand', 'Test Brand', 'Test Brand', 'Test Brand'],
        'Lineage': ['HYBRID', 'SATIVA', 'INDICA', 'HYBRID', 'SATIVA'],
        'Product Strain': ['Test Strain 1', 'Test Strain 2', 'Test Strain 3', 'Test Strain 4', 'Test Strain 5'],
        'Vendor': ['Test Vendor', 'Test Vendor', 'Test Vendor', 'Test Vendor', 'Test Vendor'],
        'Price': ['10.00', '15.00', '20.00', '10.00', '25.00']
    }
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Create Excel file
    test_file = 'test_joint_ratio_debug.xlsx'
    df.to_excel(test_file, index=False)
    
    print(f"Created test file: {test_file}")
    print(f"Test data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Test JointRatio values
    print("\n=== Original JointRatio Values ===")
    for i, value in enumerate(df['Joint Ratio']):
        print(f"  {i+1}. '{value}' (type: {type(value)}, length: {len(str(value))})")
    
    # Process with ExcelProcessor
    processor = ExcelProcessor()
    
    # Load the test file
    print(f"\n=== Loading test file ===")
    success = processor.load_file(test_file)
    print(f"Load success: {success}")
    
    if success:
        print(f"Processed data shape: {processor.df.shape}")
        print(f"Processed columns: {processor.df.columns.tolist()}")
        
        # Check JointRatio column
        if 'JointRatio' in processor.df.columns:
            print("\n=== Processed JointRatio Values ===")
            joint_ratio_values = processor.df['JointRatio'].tolist()
            for i, value in enumerate(joint_ratio_values):
                print(f"  {i+1}. '{value}' (type: {type(value)}, length: {len(str(value))})")
                
                # Check for NaN issues
                if pd.isna(value):
                    print(f"    ❌ PROBLEM: JointRatio is NaN")
                elif str(value).lower() == 'nan':
                    print(f"    ❌ PROBLEM: JointRatio is 'nan' string")
                elif str(value).strip() == '':
                    print(f"    ⚠️  JointRatio is empty string")
                else:
                    print(f"    ✓ JointRatio looks good")
        else:
            print("❌ PROBLEM: JointRatio column missing after processing")
        
        # Test getting selected records
        print(f"\n=== Testing Selected Records ===")
        processor.select_tags(['Test Pre-Roll 1', 'Test Pre-Roll 2', 'Test Pre-Roll 3'])
        selected_records = processor.get_selected_records()
        
        print(f"Selected {len(selected_records)} records")
        for i, record in enumerate(selected_records):
            joint_ratio = record.get('JointRatio', '')
            weight_units = record.get('WeightUnits', '')
            print(f"  Record {i+1}:")
            print(f"    JointRatio: '{joint_ratio}' (type: {type(joint_ratio)})")
            print(f"    WeightUnits: '{weight_units}' (type: {type(weight_units)})")
            
            # Check for issues
            if pd.isna(joint_ratio) or str(joint_ratio).lower() == 'nan':
                print(f"    ❌ PROBLEM: JointRatio is NaN or 'nan' in processed record")
            elif str(joint_ratio).strip() == '':
                print(f"    ⚠️  JointRatio is empty in processed record")
            else:
                print(f"    ✓ JointRatio is valid in processed record")
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\nCleaned up test file: {test_file}")

if __name__ == "__main__":
    test_joint_ratio_debug() 