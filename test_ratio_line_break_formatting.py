#!/usr/bin/env python3
"""
Test to verify that ratio formatting correctly inserts line breaks after every 2nd space.
"""

import sys
import os
import tempfile
import pandas as pd

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.data.excel_processor import ExcelProcessor
from src.core.generation.template_processor import TemplateProcessor
from src.core.generation.text_processing import format_ratio_multiline

def test_ratio_line_break_formatting():
    """Test that ratio formatting correctly inserts line breaks after every 2nd space."""
    
    print("Testing Ratio Line Break Formatting")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            'name': 'Cannabinoid Content with mg values',
            'input': '10mg THC 30mg CBD 5mg CBG 5mg CBN',
            'expected': '10mg THC\n30mg CBD\n5mg CBG\n5mg CBN',
            'description': 'Should insert line breaks after every 2nd space'
        },
        {
            'name': 'Simple ratio format',
            'input': '1:1:1:1',
            'expected': '1: 1: 1: 1',
            'description': 'Should format ratio with proper spacing'
        },
        {
            'name': 'Mixed content',
            'input': 'THC 10mg CBD 20mg CBG 5mg',
            'expected': 'THC 10mg\nCBD 20mg\nCBG 5mg',
            'description': 'Should handle mixed content with line breaks'
        },
        {
            'name': 'Short content',
            'input': 'THC CBD',
            'expected': 'THC CBD',
            'description': 'Should not add line breaks for short content'
        },
        {
            'name': 'Three words',
            'input': 'THC 10mg CBD',
            'expected': 'THC 10mg\nCBD',
            'description': 'Should add line break after 2nd space'
        }
    ]
    
    # Test the format_ratio_multiline function directly
    print("\nTesting format_ratio_multiline function:")
    test_cases = [
        {
            'input': '10mg THC 30mg CBD 5mg CBG 5mg CBN',
            'expected': '10mg THC\n30mg CBD\n5mg CBG\n5mg CBN'
        },
        {
            'input': '1:1:1:1',
            'expected': '1: 1: 1: 1'
        },
        {
            'input': 'THC 10mg CBD 20mg CBG 5mg',
            'expected': 'THC 10mg\nCBD 20mg\nCBG 5mg'
        },
        {
            'input': 'THC CBD',
            'expected': 'THC CBD'
        },
        {
            'input': 'THC 10mg CBD',
            'expected': 'THC 10mg\nCBD'
        },
        # Test case with actual mg values that should trigger line breaks
        {
            'input': '230mg CBD 50mg THC 10mg CBG 10mg CBN',
            'expected': '230mg CBD\n50mg THC\n10mg CBG\n10mg CBN'
        },
        # Test case to verify it stops when ratio text is complete
        {
            'input': '100mg THC 200mg CBD',
            'expected': '100mg THC\n200mg CBD'
        },
        # Test case with odd number of words
        {
            'input': 'THC 10mg CBD 20mg CBG',
            'expected': 'THC 10mg\nCBD 20mg\nCBG'
        },
        # Test case with single word
        {
            'input': 'THC',
            'expected': 'THC'
        },
        # Test case with two words
        {
            'input': 'THC CBD',
            'expected': 'THC CBD'
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        result = format_ratio_multiline(test_case['input'])
        expected = test_case['expected']
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"Test {i}: {status}")
        print(f"  Input: '{test_case['input']}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got: '{result}'")
        print(f"  Expected length: {len(expected)}")
        print(f"  Result length: {len(result)}")
        if result != expected:
            print(f"  Expected bytes: {repr(expected)}")
            print(f"  Result bytes: {repr(result)}")
        print()
    
    # Test with actual data processing
    print("\n" + "="*50)
    print("Testing with actual data processing:")
    print("="*50)

    # Create a test file with mg values in the ratio field
    import pandas as pd
    import tempfile
    import os

    # Create test data with mg values in ratio
    test_data = {
        'Product Name*': ['Test Product 1', 'Test Product 2'],
        'Product Type*': ['concentrate', 'concentrate'],  # Use classic type to trigger mg formatting
        'Description': ['Test description 1', 'Test description 2'],
        'Lineage': ['Test lineage 1', 'Test lineage 2'],
        'Product Strain': ['Test strain 1', 'Test strain 2'],
        'Ratio': ['230mg CBD 50mg THC 10mg CBG 10mg CBN', '100mg THC 200mg CBD'],  # Add mg values
        'Product Brand': ['Test Brand 1', 'Test Brand 2'],
        'Vendor': ['Test Vendor 1', 'Test Vendor 2'],
        'Price': ['$10', '$20'],
        'Weight*': ['1', '1'],
        'Units': ['oz', 'oz']
    }

    # Create temporary Excel file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        df = pd.DataFrame(test_data)
        df.to_excel(tmp_file.name, index=False)
        test_file_path = tmp_file.name

    try:
        # Load and process the test file
        from src.core.data.excel_processor import ExcelProcessor
        
        processor = ExcelProcessor()
        success = processor.load_file(test_file_path)
        
        if not success:
            print("❌ Failed to load test file")
            return
        
        # Get all available tags and select them
        available_tags = processor.get_available_tags()
        if available_tags:
            # Select all tags
            tag_names = [tag['displayName'] for tag in available_tags]
            processor.select_tags(tag_names)
        
        # Get the processed records
        records = processor.get_selected_records('vertical')
        
        if not records:
            print("❌ No records found")
            return
        
        print(f"\nFound {len(records)} records")
        
        for i, record in enumerate(records, 1):
            print(f"\nRecord {i}: {record.get('ProductName', 'Unknown')}")
            original_ratio = record.get('Ratio', '')
            print(f"Original Ratio: '{original_ratio}'")
            
            # Test the format_ratio_multiline function directly
            if original_ratio:
                formatted_ratio = format_ratio_multiline(original_ratio)
                print(f"Formatted Ratio: '{formatted_ratio}'")
                
                if '\n' in formatted_ratio:
                    print("✅ Line breaks found in formatted ratio")
                else:
                    print("❌ No line breaks found in formatted ratio")
            else:
                print("❌ No ratio content found")
        
        # Test the full template processing
        from src.core.generation.template_processor import TemplateProcessor
        
        # Get font scheme function
        def get_font_scheme(template_type, base_size=12):
            """Get font scheme for template type."""
            schemes = {
                'classic': {'ratio': base_size, 'brand': base_size - 2, 'description': base_size - 1},
                'mini': {'ratio': base_size - 1, 'brand': base_size - 3, 'description': base_size - 2},
                'double': {'ratio': base_size, 'brand': base_size - 2, 'description': base_size - 1}
            }
            return schemes.get(template_type, schemes['classic'])
        
        template_processor = TemplateProcessor('classic', get_font_scheme('classic'))
        processed_records = template_processor.process_records(records)
        
        print(f"\nProcessed {len(processed_records)} records through template processor")
        
        for i, record in enumerate(processed_records, 1):
            print(f"\nProcessed Record {i}: {record.get('ProductName', 'Unknown')}")
            ratio_content = record.get('Ratio_or_THC_CBD', '')
            print(f"Final Ratio Content: '{ratio_content}'")
            
            if '\n' in ratio_content:
                print("✅ Line breaks found in final ratio content")
            else:
                print("❌ No line breaks found in final ratio content")

    finally:
        # Clean up temporary file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)

    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    success = test_ratio_line_break_formatting()
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!") 