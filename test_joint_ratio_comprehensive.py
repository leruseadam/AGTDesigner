#!/usr/bin/env python3
"""
Comprehensive JointRatio test.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
from src.core.generation.template_processor import TemplateProcessor
import pandas as pd

def test_joint_ratio_comprehensive():
    """Test JointRatio processing comprehensively."""
    
    print("=== Comprehensive JointRatio Test ===")
    
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
            '',  # Empty
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
    test_file = 'test_joint_ratio_comprehensive.xlsx'
    df.to_excel(test_file, index=False)
    
    print(f"Created test file: {test_file}")
    
    # Process with ExcelProcessor
    processor = ExcelProcessor()
    success = processor.load_file(test_file)
    
    if success:
        print("✓ File loaded successfully")
        
        # Check JointRatio column
        if 'JointRatio' in processor.df.columns:
            print("✓ JointRatio column exists")
            
            # Test JointRatio values
            joint_ratio_values = processor.df['JointRatio'].tolist()
            print("JointRatio values:")
            for i, value in enumerate(joint_ratio_values):
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
        else:
            print("❌ JointRatio column missing")
        
        # Test template processing
        print("\n--- Testing Template Processing ---")
        processor.select_tags(['Test Pre-Roll 1', 'Test Pre-Roll 2', 'Test Pre-Roll 3'])
        selected_records = processor.get_selected_records()
        
        if selected_records:
            print(f"✓ Got {len(selected_records)} selected records")
            
            # Test template processor
            template_processor = TemplateProcessor('vertical', {}, 1.0)
            
            for i, record in enumerate(selected_records):
                joint_ratio = record.get('JointRatio', '')
                weight_units = record.get('WeightUnits', '')
                product_name = record.get('ProductName', '')
                
                print(f"  Record {i+1}: {product_name}")
                print(f"    JointRatio: '{joint_ratio}'")
                print(f"    WeightUnits: '{weight_units}'")
                
                # Test format_joint_ratio_pack
                if hasattr(template_processor, 'format_joint_ratio_pack'):
                    formatted = template_processor.format_joint_ratio_pack(joint_ratio)
                    print(f"    Formatted: '{formatted}'")
                else:
                    print(f"    ❌ format_joint_ratio_pack method missing")
        else:
            print("❌ No selected records")
    else:
        print("❌ File loading failed")
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\nCleaned up test file: {test_file}")

if __name__ == "__main__":
    test_joint_ratio_comprehensive()
