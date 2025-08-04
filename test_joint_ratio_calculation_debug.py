#!/usr/bin/env python3
"""
Test script to debug JointRatio calculation issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd

def test_joint_ratio_calculation():
    """Test JointRatio calculation logic."""
    
    print("=== JointRatio Calculation Debug ===")
    
    # Initialize processor
    processor = ExcelProcessor()
    
    # Check if there's a default file loaded
    if hasattr(processor, 'df') and processor.df is not None:
        print(f"Found loaded data: {len(processor.df)} rows")
        
        # Check for pre-roll products
        preroll_mask = processor.df["Product Type*"].str.strip().str.lower().isin(["pre-roll", "infused pre-roll"])
        preroll_count = preroll_mask.sum()
        print(f"Found {preroll_count} pre-roll products")
        
        if preroll_count > 0:
            print("\n=== Pre-roll JointRatio Analysis ===")
            preroll_data = processor.df[preroll_mask]
            
            # Show sample pre-roll data
            print(f"\nSample pre-roll data:")
            for i, (idx, row) in enumerate(preroll_data.head(5).iterrows()):
                product_name = row.get('Product Name*', 'NO NAME')
                joint_ratio = row.get('JointRatio', '')
                ratio = row.get('Ratio', '')
                weight = row.get('Weight*', '')
                weight_units = row.get('WeightUnits', '')
                
                print(f"  {i+1}. {product_name}")
                print(f"     JointRatio: '{joint_ratio}'")
                print(f"     Ratio: '{ratio}'")
                print(f"     Weight*: '{weight}'")
                print(f"     WeightUnits: '{weight_units}'")
                
                # Test the _format_weight_units method
                try:
                    formatted_weight_units = processor._format_weight_units(row)
                    print(f"     _format_weight_units result: '{formatted_weight_units}'")
                except Exception as e:
                    print(f"     _format_weight_units error: {e}")
            
            # Test the format_joint_ratio_pack method
            print(f"\n=== Testing format_joint_ratio_pack ===")
            from src.core.generation.template_processor import TemplateProcessor
            
            # Create a template processor instance
            template_processor = TemplateProcessor('vertical', {}, 1.0)
            
            # Test various JointRatio formats
            test_cases = [
                "1g x 2 Pack",
                "1gx2Pack", 
                "1g x 2 pack",
                "1g",
                "0.5g x 3 Pack",
                "2g x 1 Pack",
                "1.5g x 4 Pack"
            ]
            
            for test_case in test_cases:
                try:
                    formatted = template_processor.format_joint_ratio_pack(test_case)
                    print(f"  Input: '{test_case}' -> Output: '{formatted}'")
                except Exception as e:
                    print(f"  Input: '{test_case}' -> Error: {e}")
            
            # Check what's actually in the JointRatio column
            print(f"\n=== JointRatio Column Analysis ===")
            joint_ratio_values = preroll_data['JointRatio'].value_counts()
            print(f"JointRatio value counts:")
            for value, count in joint_ratio_values.head(10).items():
                print(f"  '{value}': {count} records")
            
            # Check for problematic values
            print(f"\n=== Problematic JointRatio Values ===")
            problematic_mask = (
                preroll_data['JointRatio'].isna() |
                (preroll_data['JointRatio'].astype(str).str.lower() == 'nan') |
                (preroll_data['JointRatio'] == '') |
                (preroll_data['JointRatio'].astype(str).str.contains('THC:|CBD:', na=False))
            )
            
            problematic_records = preroll_data[problematic_mask]
            print(f"Found {len(problematic_records)} problematic records")
            
            for i, (idx, row) in enumerate(problematic_records.head(5).iterrows()):
                product_name = row.get('Product Name*', 'NO NAME')
                joint_ratio = row.get('JointRatio', '')
                ratio = row.get('Ratio', '')
                weight = row.get('Weight*', '')
                
                print(f"  {i+1}. {product_name}")
                print(f"     JointRatio: '{joint_ratio}' (type: {type(joint_ratio)})")
                print(f"     Ratio: '{ratio}'")
                print(f"     Weight*: '{weight}'")
                
                # Check what the issue is
                if pd.isna(joint_ratio):
                    print(f"     ❌ ISSUE: JointRatio is NaN")
                elif str(joint_ratio).lower() == 'nan':
                    print(f"     ❌ ISSUE: JointRatio is 'nan' string")
                elif str(joint_ratio).strip() == '':
                    print(f"     ⚠️  ISSUE: JointRatio is empty string")
                elif 'THC:' in str(joint_ratio) or 'CBD:' in str(joint_ratio):
                    print(f"     ❌ ISSUE: JointRatio contains THC/CBD format instead of pack format")
            
            # Test the actual processing pipeline
            print(f"\n=== Testing Processing Pipeline ===")
            sample_prerolls = preroll_data.head(3)
            
            for i, (idx, row) in enumerate(sample_prerolls.iterrows()):
                product_name = row.get('Product Name*', 'NO NAME')
                print(f"\nProcessing: {product_name}")
                
                # Test _format_weight_units
                try:
                    weight_units_result = processor._format_weight_units(row)
                    print(f"  _format_weight_units: '{weight_units_result}'")
                except Exception as e:
                    print(f"  _format_weight_units error: {e}")
                
                # Test format_joint_ratio_pack
                joint_ratio_value = row.get('JointRatio', '')
                try:
                    formatted_joint_ratio = template_processor.format_joint_ratio_pack(joint_ratio_value)
                    print(f"  format_joint_ratio_pack: '{formatted_joint_ratio}'")
                except Exception as e:
                    print(f"  format_joint_ratio_pack error: {e}")
                
                # Test the full pipeline by creating a record dict
                record_dict = row.to_dict()
                try:
                    # Simulate what happens in get_selected_records
                    from src.core.generation.tag_generator import wrap_with_marker
                    
                    # Test JointRatio wrapping
                    joint_ratio_for_wrapping = record_dict.get("JointRatio", "")
                    if pd.isna(joint_ratio_for_wrapping) or str(joint_ratio_for_wrapping).lower() == 'nan':
                        joint_ratio_for_wrapping = ""
                    
                    wrapped_joint_ratio = wrap_with_marker(str(joint_ratio_for_wrapping), "JOINT_RATIO")
                    print(f"  Wrapped JointRatio: '{wrapped_joint_ratio}'")
                    
                except Exception as e:
                    print(f"  Wrapping error: {e}")
                
        else:
            print("❌ No pre-roll products found")
            
    else:
        print("❌ No data loaded. Please load a file first.")

if __name__ == "__main__":
    test_joint_ratio_calculation() 