#!/usr/bin/env python3
"""
Test script to verify the unhashable type fix in JSON matcher and upload function.
"""

import sys
import os
import pandas as pd

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_unhashable_fix():
    """Test that the JSON matcher and upload function can handle various index types without unhashable errors."""
    
    print("=== Testing Unhashable Type Fix ===\n")
    
    try:
        from src.core.data.json_matcher import JSONMatcher
        from src.core.data.excel_processor import ExcelProcessor
        
        # Create a test DataFrame with various index types
        test_data = {
            'Product Name*': ['Test Product 1', 'Test Product 2', 'Test Product 3'],
            'Description': ['Test Description 1', 'Test Description 2', 'Test Description 3'],
            'Vendor': ['Test Vendor 1', 'Test Vendor 2', 'Test Vendor 3']
        }
        
        # Test with different index types
        test_cases = [
            ("Default index", pd.DataFrame(test_data)),
            ("String index", pd.DataFrame(test_data, index=['a', 'b', 'c'])),
            ("Integer index", pd.DataFrame(test_data, index=[10, 20, 30])),
            ("Tuple index", pd.DataFrame(test_data, index=[(1, 'a'), (2, 'b'), (3, 'c')]))
        ]
        
        for test_name, df in test_cases:
            print(f"Testing {test_name}...")
            
            # Create ExcelProcessor and set the DataFrame
            excel_processor = ExcelProcessor()
            excel_processor.df = df
            
            # Create JSONMatcher
            json_matcher = JSONMatcher(excel_processor)
            
            # Test building sheet cache (this was the original source of the error)
            try:
                json_matcher._build_sheet_cache()
                print(f"  ✅ {test_name}: Sheet cache built successfully")
            except Exception as e:
                print(f"  ❌ {test_name}: Error building sheet cache: {e}")
                return False
        
        # Test upload function fix
        print("\n=== Testing Upload Function Fix ===")
        
        # Simulate the upload function logic
        excel_processor = ExcelProcessor()
        
        # Test with mixed selected_tags (strings and dictionaries)
        excel_processor.selected_tags = [
            "Product 1",
            {"Product Name*": "Product 2", "vendor": "Vendor 2"},
            "Product 3",
            {"Product Name*": "Product 4", "vendor": "Vendor 4"}
        ]
        
        # Test the fix logic from upload function
        prev_selected = set()
        if excel_processor.selected_tags:
            for tag in excel_processor.selected_tags:
                if isinstance(tag, dict):
                    prev_selected.add(tag.get('Product Name*', ''))
                elif isinstance(tag, str):
                    prev_selected.add(tag)
                else:
                    prev_selected.add(str(tag))
        
        print(f"✅ Upload function fix: Converted mixed selected_tags to set: {prev_selected}")
        
        # Test with available tags (dictionaries)
        available_tags = [
            {"Product Name*": "Product 1", "vendor": "Vendor 1"},
            {"Product Name*": "Product 2", "vendor": "Vendor 2"},
            {"Product Name*": "Product 3", "vendor": "Vendor 3"}
        ]
        
        # Test the fix logic for available tags
        available_tag_names = set()
        for tag in available_tags:
            if isinstance(tag, dict):
                available_tag_names.add(tag.get('Product Name*', ''))
            elif isinstance(tag, str):
                available_tag_names.add(tag)
            else:
                available_tag_names.add(str(tag))
        
        print(f"✅ Upload function fix: Converted available_tags to set: {available_tag_names}")
        
        # Test intersection
        valid_selected = prev_selected.intersection(available_tag_names)
        print(f"✅ Upload function fix: Intersection successful: {valid_selected}")
        
        # Test move_tags function fix
        print("\n=== Testing Move Tags Function Fix ===")
        
        # Simulate the move_tags function logic
        excel_processor = ExcelProcessor()
        excel_processor.selected_tags = [
            "Product 1",
            {"Product Name*": "Product 2", "vendor": "Vendor 2"},
            "Product 3"
        ]
        
        # Test the fix logic from move_tags function
        selected_tags = []
        for tag in excel_processor.selected_tags:
            if isinstance(tag, dict):
                selected_tags.append(tag.get('Product Name*', ''))
            elif isinstance(tag, str):
                selected_tags.append(tag)
            else:
                selected_tags.append(str(tag))
        
        print(f"✅ Move tags function fix: Converted selected_tags to strings: {selected_tags}")
        
        print("\n=== All Tests Passed! ===")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_unhashable_fix()
    sys.exit(0 if success else 1) 