#!/usr/bin/env python3
"""
Test script to verify that the default file is not loaded after reset.
This tests the fix for the issue where default file still remains after upload.
"""

import os
import sys
import pandas as pd
import tempfile
import time
from pathlib import Path

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def create_test_file():
    """Create a test Excel file with specific data."""
    test_data = [
        {
            'Product Name*': 'Test Product Upload',
            'Description': 'Test Product Upload Description',
            'Product Type*': 'Flower',
            'Product Strain': 'Test Strain',
            'Lineage': 'HYBRID',
            'Vendor/Supplier*': 'Test Vendor',
            'Product Brand': 'Test Brand',
            'Weight*': '3.5',
            'Weight Unit* (grams/gm or ounces/oz)': 'grams',
            'Quantity*': '1',
            'Price* (Tier Name for Bulk)': 'Test Price',
            'DOH Compliant (Yes/No)': 'Yes'
        }
    ]
    
    df = pd.DataFrame(test_data)
    return df

def test_default_file_prevention():
    """Test that the default file is not loaded after reset."""
    print("Testing default file prevention after reset...")
    
    # Import the functions
    from app import reset_excel_processor, get_excel_processor, force_reload_excel_processor
    
    # Step 1: Get initial processor (should load default file)
    print("\n1. Getting initial processor (should load default file)...")
    processor1 = get_excel_processor()
    
    if processor1.df is None or processor1.df.empty:
        print("❌ Initial processor has no data")
        return False
    
    print(f"✅ Initial processor loaded with {len(processor1.df)} products")
    print(f"   Last loaded file: {getattr(processor1, '_last_loaded_file', 'None')}")
    
    # Step 2: Reset the processor
    print("\n2. Resetting the processor...")
    reset_excel_processor()
    print("✅ Processor reset complete")
    
    # Step 3: Get processor again (should NOT load default file)
    print("\n3. Getting processor after reset (should NOT load default file)...")
    processor2 = get_excel_processor()
    
    if processor2 is None:
        print("❌ Processor after reset is None")
        return False
    
    if processor2.df is None:
        print("❌ Processor after reset has no DataFrame")
        return False
    
    if not processor2.df.empty:
        print(f"❌ Processor after reset still has data: {len(processor2.df)} products")
        print(f"   Last loaded file: {getattr(processor2, '_last_loaded_file', 'None')}")
        return False
    
    print("✅ Processor after reset has empty DataFrame (no default file loaded)")
    
    # Step 4: Test with a new file upload
    print("\n4. Testing with new file upload...")
    
    # Create test file
    df = create_test_file()
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        test_file_path = tmp.name
    
    try:
        # Force reload with new file
        force_reload_excel_processor(test_file_path)
        
        # Get processor again
        processor3 = get_excel_processor()
        
        if processor3 is None:
            print("❌ Processor after file upload is None")
            return False
        
        if processor3.df is None or processor3.df.empty:
            print("❌ Processor after file upload has no data")
            return False
        
        print(f"✅ Processor after file upload has {len(processor3.df)} products")
        print(f"   Last loaded file: {getattr(processor3, '_last_loaded_file', 'None')}")
        
        # Verify it's the uploaded file, not the default file
        expected_name = 'Test Product Upload'
        actual_names = list(processor3.df['ProductName'])
        
        if expected_name not in actual_names:
            print(f"❌ Uploaded file data not found")
            print(f"   Expected: {expected_name}")
            print(f"   Actual: {actual_names}")
            return False
        
        print("✅ Uploaded file data verified")
        
        # Step 5: Test that default file is not automatically loaded again
        print("\n5. Testing that default file is not automatically loaded again...")
        
        # Reset again
        reset_excel_processor()
        
        # Get processor again
        processor4 = get_excel_processor()
        
        if processor4 is None:
            print("❌ Processor after second reset is None")
            return False
        
        if not processor4.df.empty:
            print(f"❌ Processor after second reset still has data: {len(processor4.df)} products")
            return False
        
        print("✅ Processor after second reset has empty DataFrame (no default file loaded)")
        
        print("\n🎉 All default file prevention tests passed!")
        return True
        
    finally:
        # Clean up
        try:
            os.unlink(test_file_path)
        except Exception as e:
            print(f"Warning: Could not clean up temporary file: {e}")

def test_upload_process():
    """Test the complete upload process to ensure default file is not loaded."""
    print("\nTesting complete upload process...")
    
    # Import the functions
    from app import reset_excel_processor, get_excel_processor, force_reload_excel_processor
    
    # Create test file
    df = create_test_file()
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        test_file_path = tmp.name
    
    try:
        # Step 1: Reset processor (simulating upload start)
        print("1. Resetting processor (simulating upload start)...")
        reset_excel_processor()
        
        # Step 2: Get processor (should be empty, no default file)
        print("2. Getting processor after reset...")
        processor1 = get_excel_processor()
        
        if processor1 is None:
            print("❌ Processor after reset is None")
            return False
        
        if not processor1.df.empty:
            print(f"❌ Processor not empty after reset: {len(processor1.df)} products")
            return False
        
        print("✅ Processor empty after reset")
        
        # Step 3: Force reload with new file (simulating upload completion)
        print("3. Force reloading with new file...")
        force_reload_excel_processor(test_file_path)
        
        # Step 4: Get processor again
        print("4. Getting processor after file upload...")
        processor2 = get_excel_processor()
        
        if processor2 is None:
            print("❌ Processor after file upload is None")
            return False
        
        if processor2.df is None or processor2.df.empty:
            print("❌ Processor empty after file upload")
            return False
        
        print(f"✅ Processor has {len(processor2.df)} products after upload")
        
        # Verify it's the uploaded file
        expected_name = 'Test Product Upload'
        actual_names = list(processor2.df['ProductName'])
        
        if expected_name not in actual_names:
            print(f"❌ Uploaded file data not found")
            return False
        
        print("✅ Uploaded file data verified")
        
        print("\n🎉 Upload process test passed!")
        return True
        
    finally:
        # Clean up
        try:
            os.unlink(test_file_path)
        except Exception as e:
            print(f"Warning: Could not clean up temporary file: {e}")

if __name__ == "__main__":
    print("=== Default File Prevention Test ===")
    
    # Test default file prevention
    test1_passed = test_default_file_prevention()
    
    # Test upload process
    test2_passed = test_upload_process()
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Default file prevention is working correctly.")
        print("✅ Default file will NOT be loaded after reset.")
        print("✅ Upload process will completely replace old data.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Default file prevention needs attention.")
        sys.exit(1) 