#!/usr/bin/env python3
"""
Test script to verify JointRatio works correctly in label generation.
"""

import pandas as pd
import tempfile
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.data.excel_processor import ExcelProcessor
from core.generation.template_processor import TemplateProcessor

def create_test_excel_for_label_generation():
    """Create a test Excel file for label generation testing."""
    print("Creating test Excel file for label generation...")
    
    # Sample data with various JointRatio scenarios
    data = {
        'Product Name*': [
            'Test Pre-Roll 1',
            'Test Pre-Roll 2', 
            'Test Pre-Roll 3',
            'Test Flower 1'
        ],
        'Product Type*': [
            'pre-roll',
            'infused pre-roll',
            'pre-roll',
            'flower'
        ],
        'Description': [
            'Test Pre-Roll Description 1',
            'Test Pre-Roll Description 2',
            'Test Pre-Roll Description 3',
            'Test Flower Description'
        ],
        'Joint Ratio': [
            '1g x 2 Pack',
            '0.5g x 3 Pack',
            '',  # Empty string
            ''   # Empty for non-pre-roll
        ],
        'Ratio': [
            '1g x 2 Pack',
            '0.5g x 3 Pack',
            '1g x 1 Pack',
            'THC: 25% CBD: 2%'
        ],
        'Lineage': ['HYBRID', 'SATIVA', 'INDICA', 'INDICA'],
        'Product Brand': ['Brand A', 'Brand B', 'Brand C', 'Brand D'],
        'Vendor/Supplier*': ['Vendor 1', 'Vendor 2', 'Vendor 3', 'Vendor 4'],
        'Weight*': ['2', '1.5', '1', '3.5'],
        'Weight Unit* (grams/gm or ounces/oz)': ['g', 'g', 'g', 'g'],
        'Price* (Tier Name for Bulk)': ['$15', '$12', '$10', '$45'],
        'DOH Compliant (Yes/No)': ['Yes', 'Yes', 'Yes', 'Yes'],
        'Product Strain': ['Strain A', 'Strain B', 'Strain C', 'Strain D']
    }
    
    df = pd.DataFrame(data)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        return tmp.name

def test_joint_ratio_in_label_generation():
    """Test JointRatio in the actual label generation process."""
    print("\n=== Testing JointRatio in Label Generation ===")
    
    # Create test file
    test_file = create_test_excel_for_label_generation()
    
    processor = ExcelProcessor()
    success = processor.load_file(test_file)
    
    if success:
        print("✓ File loaded successfully")
        
        # Get available tags and select them
        all_products = processor.get_available_tags()
        print(f"✓ Found {len(all_products)} available products")
        
        # Select all products for testing (use the first key from each tag)
        product_names = []
        for tag in all_products:
            # Get the first key which should be the product name
            if tag:
                first_key = list(tag.keys())[0]
                product_names.append(first_key)
        
        if product_names:
            processor.select_tags(product_names)
            print(f"✓ Selected {len(product_names)} products for testing")
            
            # Test label generation for different template types
            template_types = ['vertical', 'horizontal', 'double', 'mini']
            
            for template_type in template_types:
                print(f"\n--- Testing {template_type} template ---")
                
                try:
                    # Get selected records
                    records = processor.get_selected_records(template_type)
                    print(f"✓ Got {len(records)} records for {template_type} template")
                    
                    # Check JointRatio in each record
                    for i, record in enumerate(records):
                        product_name = record.get('ProductName', 'Unknown')
                        product_type = record.get('ProductType', '').lower()
                        joint_ratio = record.get('JointRatio', '')
                        
                        print(f"  Record {i}: {product_name} ({product_type})")
                        print(f"    JointRatio: '{joint_ratio}' (type: {type(joint_ratio)})")
                        
                        # Check if JointRatio is valid
                        if pd.isna(joint_ratio) or joint_ratio == 'nan' or joint_ratio == 'NaN':
                            print(f"    ✗ PROBLEM: JointRatio is NaN in {template_type} template")
                        elif product_type in ['pre-roll', 'infused pre-roll'] and not joint_ratio:
                            print(f"    ⚠️  WARNING: Pre-roll product has empty JointRatio")
                        else:
                            print(f"    ✓ JointRatio is valid")
                    
                    # Test template processing
                    if records:
                        try:
                            template_processor = TemplateProcessor(template_type)
                            # Test building label context for first record
                            first_record = records[0]
                            label_context = template_processor._build_label_context(first_record, None)
                            
                            joint_ratio_in_context = label_context.get('JointRatio', '')
                            print(f"  Template context JointRatio: '{joint_ratio_in_context}'")
                            
                            if pd.isna(joint_ratio_in_context) or joint_ratio_in_context == 'nan' or joint_ratio_in_context == 'NaN':
                                print(f"    ✗ PROBLEM: JointRatio is NaN in template context")
                            else:
                                print(f"    ✓ JointRatio is valid in template context")
                                
                        except Exception as e:
                            print(f"    ⚠️  Template processing error: {e}")
                    
                except Exception as e:
                    print(f"✗ Error processing {template_type} template: {e}")
        else:
            print("⚠️  No products found to test")
    
    # Clean up
    os.unlink(test_file)

def test_joint_ratio_edge_cases():
    """Test JointRatio with edge cases."""
    print("\n=== Testing JointRatio Edge Cases ===")
    
    # Create test file with edge cases
    data = {
        'Product Name*': [
            'Pre-Roll NaN Test',
            'Pre-Roll Empty Test',
            'Pre-Roll Valid Test'
        ],
        'Product Type*': [
            'pre-roll',
            'pre-roll',
            'pre-roll'
        ],
        'Description': [
            'Test Description 1',
            'Test Description 2',
            'Test Description 3'
        ],
        'Joint Ratio': [
            '',  # Empty string
            '',  # Empty string
            '1g x 2 Pack'  # Valid value
        ],
        'Ratio': [
            '1g x 1 Pack',
            '0.5g x 2 Pack',
            '1g x 2 Pack'
        ],
        'Lineage': ['HYBRID', 'SATIVA', 'INDICA'],
        'Product Brand': ['Brand A', 'Brand B', 'Brand C'],
        'Vendor/Supplier*': ['Vendor 1', 'Vendor 2', 'Vendor 3'],
        'Weight*': ['1', '1', '2'],
        'Weight Unit* (grams/gm or ounces/oz)': ['g', 'g', 'g'],
        'Price* (Tier Name for Bulk)': ['$10', '$8', '$15'],
        'DOH Compliant (Yes/No)': ['Yes', 'Yes', 'Yes'],
        'Product Strain': ['Strain A', 'Strain B', 'Strain C']
    }
    
    df = pd.DataFrame(data)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        test_file = tmp.name
    
    processor = ExcelProcessor()
    success = processor.load_file(test_file)
    
    if success:
        print("✓ File loaded successfully")
        
        # Check JointRatio values
        if 'JointRatio' in processor.df.columns:
            joint_ratio_values = processor.df['JointRatio'].tolist()
            print(f"JointRatio values: {joint_ratio_values}")
            
            # Check for any NaN values
            nan_count = processor.df['JointRatio'].isna().sum()
            print(f"NaN values: {nan_count}")
            
            if nan_count == 0:
                print("✓ No NaN values found - edge case handling works")
            else:
                print("✗ Found NaN values - edge case handling failed")
        
        # Test weight units formatting
        print("\nTesting weight units formatting...")
        for i, record in processor.df.iterrows():
            product_name = record['ProductName']
            product_type = record['Product Type*'].lower()
            joint_ratio = record['JointRatio']
            
            # Test the _format_weight_units method
            weight_units = processor._format_weight_units(record)
            
            print(f"  {product_name} ({product_type}):")
            print(f"    JointRatio: '{joint_ratio}'")
            print(f"    WeightUnits: '{weight_units}'")
            
            if product_type in ['pre-roll', 'infused pre-roll']:
                if joint_ratio and weight_units == str(joint_ratio):
                    print(f"    ✓ WeightUnits correctly uses JointRatio")
                elif not joint_ratio and weight_units == "THC:|BR|CBD:":
                    print(f"    ✓ WeightUnits correctly falls back to default")
                else:
                    print(f"    ✗ WeightUnits formatting issue")
    
    # Clean up
    os.unlink(test_file)

if __name__ == "__main__":
    test_joint_ratio_in_label_generation()
    test_joint_ratio_edge_cases() 