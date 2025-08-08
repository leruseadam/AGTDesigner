#!/usr/bin/env python3
"""
Test script to verify the upload fix works correctly.
This script tests that uploaded files are properly loaded instead of default files.
"""

import os
import sys
import tempfile
import pandas as pd
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def create_test_excel_file():
    """Create a test Excel file with sample data."""
    # Create test data
    test_data = {
        'Product Name*': ['Test Product 1', 'Test Product 2', 'Test Product 3'],
        'Product Type*': ['Flower', 'Concentrate', 'Edible'],
        'Product Brand': ['Test Brand 1', 'Test Brand 2', 'Test Brand 3'],
        'Vendor': ['Test Vendor 1', 'Test Vendor 2', 'Test Vendor 3'],
        'Lineage': ['SATIVA', 'INDICA', 'HYBRID'],
        'Weight*': ['3.5g', '1g', '100mg'],
        'Quantity*': ['1', '1', '1']
    }
    
    df = pd.DataFrame(test_data)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    
    print(f"Created test Excel file: {temp_file.name}")
    return temp_file.name

def test_upload_fix():
    """Test that the upload fix works correctly."""
    print("=== TESTING UPLOAD FIX ===")
    
    # Create test Excel file
    test_file = create_test_excel_file()
    
    try:
        # Import the ExcelProcessor
        from src.core.data.excel_processor import ExcelProcessor
        
        # Test 1: Create processor and load test file
        print("\n--- Test 1: Loading uploaded file ---")
        processor = ExcelProcessor()
        
        # Set the uploaded file path to prevent default loading
        processor._last_loaded_file = test_file
        print(f"Set _last_loaded_file to: {test_file}")
        
        # Load the file
        success = processor.pythonanywhere_fast_load(test_file)
        print(f"Load success: {success}")
        
        if success and processor.df is not None:
            print(f"DataFrame shape: {processor.df.shape}")
            print(f"DataFrame columns: {list(processor.df.columns)}")
            print(f"First few rows:")
            print(processor.df.head())
            
            # Test that we loaded the correct file
            if processor._last_loaded_file == test_file:
                print("✓ SUCCESS: Correct file loaded")
            else:
                print(f"✗ ERROR: Wrong file loaded. Expected {test_file}, got {processor._last_loaded_file}")
                return False
        else:
            print("✗ ERROR: Failed to load file")
            return False
        
        # Test 2: Get available tags
        print("\n--- Test 2: Getting available tags ---")
        tags = processor.get_available_tags()
        print(f"Available tags count: {len(tags)}")
        
        if len(tags) > 0:
            print("✓ SUCCESS: Available tags retrieved")
            print(f"First tag: {tags[0]}")
        else:
            print("✗ ERROR: No available tags found")
            return False
        
        # Test 3: Verify the data matches our test file
        print("\n--- Test 3: Verifying data content ---")
        expected_products = ['Test Product 1', 'Test Product 2', 'Test Product 3']
        found_products = [tag.get('Product Name*', '') for tag in tags]
        
        print(f"Expected products: {expected_products}")
        print(f"Found products: {found_products}")
        
        if set(found_products) == set(expected_products):
            print("✓ SUCCESS: All expected products found")
        else:
            print("✗ ERROR: Products don't match expected data")
            return False
        
        print("\n=== ALL TESTS PASSED ===")
        return True
        
    except Exception as e:
        print(f"✗ ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test file
        try:
            os.unlink(test_file)
            print(f"Cleaned up test file: {test_file}")
        except Exception as e:
            print(f"Warning: Could not clean up test file: {e}")

if __name__ == "__main__":
    print("Starting upload fix tests...")
    
    # Run tests
    test_passed = test_upload_fix()
    
    if test_passed:
        print("\n🎉 ALL TESTS PASSED! Upload fix is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ TESTS FAILED! Upload fix needs attention.")
        sys.exit(1) 