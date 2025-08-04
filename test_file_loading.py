#!/usr/bin/env python3
"""
Test script to check Excel file loading functionality.
"""

import os
import sys
import time
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.data.excel_processor import ExcelProcessor

def test_file_loading():
    """Test loading the carts.xlsx file directly."""
    print("=== Excel File Loading Test ===\n")
    
    # Check if the file exists
    file_path = "uploads/carts.xlsx"
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"Testing file: {file_path}")
    print(f"File size: {os.path.getsize(file_path) / (1024*1024):.2f} MB")
    
    try:
        # Create a new ExcelProcessor instance
        print("Creating ExcelProcessor instance...")
        processor = ExcelProcessor()
        
        # Disable product database integration for faster loading
        if hasattr(processor, 'enable_product_db_integration'):
            processor.enable_product_db_integration(False)
            print("Product database integration disabled")
        
        # Load the file
        print("Loading file...")
        start_time = time.time()
        success = processor.load_file(file_path)
        load_time = time.time() - start_time
        
        print(f"Load time: {load_time:.2f} seconds")
        print(f"Load success: {success}")
        
        if success:
            print(f"DataFrame shape: {processor.df.shape if processor.df is not None else 'None'}")
            print(f"DataFrame empty: {processor.df.empty if processor.df is not None else 'N/A'}")
            
            if processor.df is not None and not processor.df.empty:
                print("✅ File loaded successfully!")
                print(f"Number of rows: {len(processor.df)}")
                print(f"Number of columns: {len(processor.df.columns)}")
                print(f"Sample columns: {list(processor.df.columns[:5])}")
                return True
            else:
                print("❌ DataFrame is empty after loading")
                return False
        else:
            print("❌ File loading failed")
            return False
            
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("Starting Excel file loading test...\n")
    
    result = test_file_loading()
    
    print(f"\n=== Test Result ===")
    if result:
        print("✅ Excel file loading test passed!")
    else:
        print("❌ Excel file loading test failed!")

if __name__ == "__main__":
    main() 