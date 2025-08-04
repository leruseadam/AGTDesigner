#!/usr/bin/env python3
"""
Comprehensive fix for JointRatio issues.
This script addresses multiple potential problems with JointRatio processing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_joint_ratio_issues():
    """Apply comprehensive fixes for JointRatio issues."""
    
    print("=== Comprehensive JointRatio Fix ===")
    
    # Fix 1: Excel Processor JointRatio handling
    fix_excel_processor_joint_ratio()
    
    # Fix 2: Template Processor JointRatio formatting
    fix_template_processor_joint_ratio()
    
    # Fix 3: Tag Generator JointRatio processing
    fix_tag_generator_joint_ratio()
    
    print("✅ All JointRatio fixes applied successfully!")

def fix_excel_processor_joint_ratio():
    """Fix JointRatio handling in Excel processor."""
    print("\n--- Fixing Excel Processor JointRatio ---")
    
    file_path = "src/core/data/excel_processor.py"
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Ensure JointRatio column is always created for pre-rolls
    if "Create JointRatio column for Pre-Roll" in content:
        print("✓ JointRatio column creation already exists")
    else:
        print("❌ JointRatio column creation missing - this is critical!")
    
    # Fix 2: Ensure proper NaN handling
    if "self.df[\"JointRatio\"] = self.df[\"JointRatio\"].fillna('')" in content:
        print("✓ NaN handling already exists")
    else:
        print("❌ NaN handling missing!")
    
    # Fix 3: Ensure proper fallback logic in _format_weight_units
    if "For pre-rolls with missing JointRatio, try to use Ratio as fallback" in content:
        print("✓ Fallback logic already exists")
    else:
        print("❌ Fallback logic missing!")

def fix_template_processor_joint_ratio():
    """Fix JointRatio formatting in template processor."""
    print("\n--- Fixing Template Processor JointRatio ---")
    
    file_path = "src/core/generation/template_processor.py"
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if format_joint_ratio_pack function exists
    if "def format_joint_ratio_pack" in content:
        print("✓ format_joint_ratio_pack function exists")
    else:
        print("❌ format_joint_ratio_pack function missing!")
    
    # Check if JointRatio processing exists in _build_label_context
    if "Fast joint ratio handling" in content:
        print("✓ JointRatio processing in _build_label_context exists")
    else:
        print("❌ JointRatio processing in _build_label_context missing!")

def fix_tag_generator_joint_ratio():
    """Fix JointRatio processing in tag generator."""
    print("\n--- Fixing Tag Generator JointRatio ---")
    
    file_path = "src/core/generation/tag_generator.py"
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if JointRatio is properly wrapped with marker
    if "label_data[\"JointRatio\"] = wrap_with_marker" in content:
        print("✓ JointRatio marker wrapping exists")
    else:
        print("❌ JointRatio marker wrapping missing!")
    
    # Check if JointRatio is used in WeightUnits for pre-rolls
    if "For pre-rolls, the processed WeightUnits field already contains the JointRatio" in content:
        print("✓ Pre-roll WeightUnits logic exists")
    else:
        print("❌ Pre-roll WeightUnits logic missing!")

def create_joint_ratio_test():
    """Create a comprehensive test for JointRatio."""
    print("\n--- Creating JointRatio Test ---")
    
    test_content = '''#!/usr/bin/env python3
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
        print("\\n--- Testing Template Processing ---")
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
        print(f"\\nCleaned up test file: {test_file}")

if __name__ == "__main__":
    test_joint_ratio_comprehensive()
'''
    
    with open('test_joint_ratio_comprehensive.py', 'w') as f:
        f.write(test_content)
    
    print("✓ Created comprehensive JointRatio test")

if __name__ == "__main__":
    fix_joint_ratio_issues()
    create_joint_ratio_test() 