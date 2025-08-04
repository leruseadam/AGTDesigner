#!/usr/bin/env python3
"""
Test script to check default file loading functionality.
Run this on PythonAnywhere to see what's happening with file loading.
"""

import os
import sys
import logging

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_default_file_loading():
    """Test the default file loading functionality."""
    print("=== Testing Default File Loading ===")
    
    try:
        # Import the function
        from src.core.data.excel_processor import get_default_upload_file
        
        print("✓ Successfully imported get_default_upload_file")
        
        # Call the function
        print("Calling get_default_upload_file()...")
        default_file = get_default_upload_file()
        
        if default_file:
            print(f"✓ Default file found: {default_file}")
            
            # Check if file exists
            if os.path.exists(default_file):
                print(f"✓ File exists and is accessible")
                file_size = os.path.getsize(default_file)
                mod_time = os.path.getmtime(default_file)
                print(f"  Size: {file_size:,} bytes")
                print(f"  Modified: {mod_time}")
            else:
                print(f"✗ File does not exist: {default_file}")
        else:
            print("✗ No default file found")
            
        return default_file
        
    except Exception as e:
        print(f"✗ Error testing default file loading: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_excel_processor_loading():
    """Test loading a file with the Excel processor."""
    print("\n=== Testing Excel Processor Loading ===")
    
    try:
        # Import the Excel processor
        from src.core.data.excel_processor import ExcelProcessor
        
        print("✓ Successfully imported ExcelProcessor")
        
        # Create an instance
        processor = ExcelProcessor()
        print("✓ ExcelProcessor instance created")
        
        # Try to load a file
        default_file = get_default_upload_file()
        if default_file and os.path.exists(default_file):
            print(f"Attempting to load: {default_file}")
            
            success = processor.load_file(default_file)
            
            if success:
                print("✓ File loaded successfully")
                if processor.df is not None:
                    print(f"  Rows: {len(processor.df)}")
                    print(f"  Columns: {list(processor.df.columns)}")
                else:
                    print("✗ DataFrame is None")
            else:
                print("✗ File loading failed")
        else:
            print("✗ No file to load")
            
        return success
        
    except Exception as e:
        print(f"✗ Error testing Excel processor: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the tests."""
    print("=== Default File Loading Test ===")
    
    # Test 1: Default file detection
    default_file = test_default_file_loading()
    
    # Test 2: Excel processor loading
    if default_file:
        success = test_excel_processor_loading()
    else:
        print("\nSkipping Excel processor test - no file to load")
        success = False
    
    # Summary
    print("\n=== TEST SUMMARY ===")
    print(f"Default file found: {'✓' if default_file else '✗'}")
    print(f"File loading successful: {'✓' if success else '✗'}")
    
    if not default_file:
        print("\nRECOMMENDATION: Upload a file through the web interface")
    elif not success:
        print("\nRECOMMENDATION: Check the file format and try again")

if __name__ == "__main__":
    main() 