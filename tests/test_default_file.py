#!/usr/bin/env python3
"""
Test script to verify the default file works correctly.
"""

import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_default_file():
    """Test the default file to ensure it loads correctly."""
    try:
        from src.core.data.excel_processor import ExcelProcessor
        
        # Test file path
        test_file = "uploads/A Greener Today - Bothell_inventory_07-07-2025 10_19 AM.xlsx"
        
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            return False
        
        print(f"✅ Test file found: {test_file}")
        
        # Test loading the file
        excel_processor = ExcelProcessor()
        success = excel_processor.load_file(test_file)
        
        if success and excel_processor.df is not None:
            print(f"✅ File loaded successfully: {len(excel_processor.df)} records")
            print(f"✅ Columns: {list(excel_processor.df.columns)}")
            
            # Test getting available tags
            try:
                tags = excel_processor.get_available_tags()
                print(f"✅ Available tags: {len(tags)} tags")
                
                # Show first few tags
                if tags:
                    print("Sample tags:")
                    for i, tag in enumerate(tags[:5]):
                        print(f"  {i+1}. {tag.get('Product Name*', 'N/A')}")
                    if len(tags) > 5:
                        print(f"  ... and {len(tags) - 5} more")
                        
            except Exception as e:
                print(f"❌ Error getting available tags: {e}")
                return False
                
            # Test filter options
            try:
                filter_options = excel_processor.get_dynamic_filter_options({})
                print(f"✅ Filter options: {list(filter_options.keys())}")
                for key, values in filter_options.items():
                    print(f"  - {key}: {len(values)} options")
                    
            except Exception as e:
                print(f"❌ Error getting filter options: {e}")
                return False
                
            return True
        else:
            print("❌ Failed to load file")
            return False
            
    except Exception as e:
        print(f"❌ Error testing default file: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Default File ===\n")
    
    success = test_default_file()
    
    if success:
        print("\n✅ Default file test PASSED")
        print("The file should work correctly when deployed to production.")
    else:
        print("\n❌ Default file test FAILED")
        print("Please check the file format and try again.") 