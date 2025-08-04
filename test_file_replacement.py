#!/usr/bin/env python3
"""
Test script to verify that newly uploaded files properly replace old data.
This tests the fix for the issue where new lists load but don't replace old data.
"""

import os
import sys
import pandas as pd
import tempfile
import shutil
import time
from pathlib import Path

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.core.data.excel_processor import ExcelProcessor

def create_test_file_1():
    """Create first test Excel file with specific data."""
    test_data = [
        {
            'Product Name*': 'Test Flower 1',
            'Description': 'Test Flower 1 Description',
            'Product Type*': 'Flower',
            'Product Strain': 'OG Kush',
            'Lineage': 'HYBRID',
            'Vendor/Supplier*': 'Test Vendor 1',
            'Product Brand': 'Test Brand 1',
            'Weight*': '3.5',
            'Weight Unit* (grams/gm or ounces/oz)': 'grams',
            'Quantity*': '1',
            'Price* (Tier Name for Bulk)': 'Test Price',
            'DOH Compliant (Yes/No)': 'Yes'
        },
        {
            'Product Name*': 'Test Pre-roll 1',
            'Description': 'Test Pre-roll 1 Description',
            'Product Type*': 'Pre-roll',
            'Product Strain': 'Sour Diesel',
            'Lineage': 'SATIVA',
            'Vendor/Supplier*': 'Test Vendor 1',
            'Product Brand': 'Test Brand 1',
            'Weight*': '1.0',
            'Weight Unit* (grams/gm or ounces/oz)': 'grams',
            'Quantity*': '1',
            'Price* (Tier Name for Bulk)': 'Test Price',
            'DOH Compliant (Yes/No)': 'Yes'
        }
    ]
    
    df = pd.DataFrame(test_data)
    return df

def create_test_file_2():
    """Create second test Excel file with different data."""
    test_data = [
        {
            'Product Name*': 'Test Edible 2',
            'Description': 'Test Edible 2 Description',
            'Product Type*': 'Edibles',
            'Product Strain': 'N/A',
            'Lineage': 'N/A',
            'Vendor/Supplier*': 'Test Vendor 2',
            'Product Brand': 'Test Brand 2',
            'Weight*': '100',
            'Weight Unit* (grams/gm or ounces/oz)': 'mg',
            'Quantity*': '1',
            'Price* (Tier Name for Bulk)': 'Test Price',
            'DOH Compliant (Yes/No)': 'Yes'
        },
        {
            'Product Name*': 'Test Tincture 2',
            'Description': 'Test Tincture 2 Description',
            'Product Type*': 'Tinctures',
            'Product Strain': 'N/A',
            'Lineage': 'N/A',
            'Vendor/Supplier*': 'Test Vendor 2',
            'Product Brand': 'Test Brand 2',
            'Weight*': '30',
            'Weight Unit* (grams/gm or ounces/oz)': 'ml',
            'Quantity*': '1',
            'Price* (Tier Name for Bulk)': 'Test Price',
            'DOH Compliant (Yes/No)': 'Yes'
        }
    ]
    
    df = pd.DataFrame(test_data)
    return df

def test_file_replacement():
    """Test that newly uploaded files properly replace old data."""
    print("Testing file replacement functionality...")
    
    # Create test files
    df1 = create_test_file_1()
    df2 = create_test_file_2()
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp1:
        df1.to_excel(tmp1.name, index=False)
        file1_path = tmp1.name
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp2:
        df2.to_excel(tmp2.name, index=False)
        file2_path = tmp2.name
    
    try:
        # Test 1: Load first file
        print("\n1. Loading first file...")
        processor = ExcelProcessor()
        success1 = processor.load_file(file1_path)
        
        if not success1:
            print("❌ Failed to load first file")
            return False
        
        print(f"✅ First file loaded successfully")
        print(f"   Products: {len(processor.df)}")
        print(f"   Product names: {list(processor.df['ProductName'])}")
        
        # Verify first file data
        expected_names_1 = ['Test Flower 1', 'Test Pre-roll 1']
        actual_names_1 = list(processor.df['ProductName'])
        
        if actual_names_1 != expected_names_1:
            print(f"❌ First file data mismatch")
            print(f"   Expected: {expected_names_1}")
            print(f"   Actual: {actual_names_1}")
            return False
        
        print("✅ First file data verified")
        
        # Test 2: Load second file (should replace first file)
        print("\n2. Loading second file (should replace first file)...")
        success2 = processor.load_file(file2_path)
        
        if not success2:
            print("❌ Failed to load second file")
            return False
        
        print(f"✅ Second file loaded successfully")
        print(f"   Products: {len(processor.df)}")
        print(f"   Product names: {list(processor.df['ProductName'])}")
        
        # Verify second file data (should have replaced first file)
        expected_names_2 = ['Test Edible 2', 'Test Tincture 2']
        actual_names_2 = list(processor.df['ProductName'])
        
        if actual_names_2 != expected_names_2:
            print(f"❌ Second file data mismatch - old data not replaced")
            print(f"   Expected: {expected_names_2}")
            print(f"   Actual: {actual_names_2}")
            return False
        
        print("✅ Second file data verified - old data properly replaced")
        
        # Test 3: Verify that first file data is completely gone
        print("\n3. Verifying old data is completely replaced...")
        
        # Check that no products from first file remain
        first_file_products = ['Test Flower 1', 'Test Pre-roll 1']
        remaining_old_products = [name for name in first_file_products if name in actual_names_2]
        
        if remaining_old_products:
            print(f"❌ Old data still present: {remaining_old_products}")
            return False
        
        print("✅ Old data completely replaced")
        
        # Test 4: Check file path tracking
        print("\n4. Checking file path tracking...")
        last_loaded_file = getattr(processor, '_last_loaded_file', None)
        
        if last_loaded_file != file2_path:
            print(f"❌ File path not updated correctly")
            print(f"   Expected: {file2_path}")
            print(f"   Actual: {last_loaded_file}")
            return False
        
        print("✅ File path tracking working correctly")
        
        print("\n🎉 All file replacement tests passed!")
        return True
        
    finally:
        # Clean up temporary files
        try:
            os.unlink(file1_path)
            os.unlink(file2_path)
        except Exception as e:
            print(f"Warning: Could not clean up temporary files: {e}")

def test_force_reload_function():
    """Test the force_reload_excel_processor function specifically."""
    print("\nTesting force_reload_excel_processor function...")
    
    # Import the function
    from app import force_reload_excel_processor, get_excel_processor
    
    # Create test file
    df = create_test_file_2()
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        test_file_path = tmp.name
    
    try:
        # Test force reload
        print("Testing force_reload_excel_processor...")
        force_reload_excel_processor(test_file_path)
        
        # Get the updated processor
        processor = get_excel_processor()
        
        if processor.df is None or processor.df.empty:
            print("❌ Force reload failed - DataFrame is empty")
            return False
        
        print(f"✅ Force reload successful")
        print(f"   Products: {len(processor.df)}")
        print(f"   Product names: {list(processor.df['ProductName'])}")
        
        # Verify data
        expected_names = ['Test Edible 2', 'Test Tincture 2']
        actual_names = list(processor.df['ProductName'])
        
        if actual_names != expected_names:
            print(f"❌ Force reload data mismatch")
            print(f"   Expected: {expected_names}")
            print(f"   Actual: {actual_names}")
            return False
        
        print("✅ Force reload data verified")
        return True
        
    finally:
        # Clean up
        try:
            os.unlink(test_file_path)
        except Exception as e:
            print(f"Warning: Could not clean up temporary file: {e}")

if __name__ == "__main__":
    print("=== File Replacement Test ===")
    
    # Test basic file replacement
    test1_passed = test_file_replacement()
    
    # Test force reload function
    test2_passed = test_force_reload_function()
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! File replacement is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. File replacement needs attention.")
        sys.exit(1) 