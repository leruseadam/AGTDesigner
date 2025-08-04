#!/usr/bin/env python3
"""
Test the full ratio processing pipeline
"""

import pandas as pd
import tempfile
import os
from src.core.generation.text_processing import format_ratio_multiline

def test_full_ratio_pipeline():
    """Test the complete ratio processing pipeline."""
    
    print("Testing Full Ratio Processing Pipeline")
    print("=" * 60)
    
    # Test the format_ratio_multiline function directly
    test_ratio = "230mg CBD 50mg THC 10mg CBG 10mg CBN"
    print(f"Original ratio: '{test_ratio}'")
    
    formatted_ratio = format_ratio_multiline(test_ratio)
    print(f"Formatted ratio: '{formatted_ratio}'")
    
    if '\n' in formatted_ratio:
        print("✅ Line breaks added by format_ratio_multiline")
        lines = formatted_ratio.split('\n')
        print(f"  Split into {len(lines)} lines:")
        for i, line in enumerate(lines, 1):
            print(f"    Line {i}: '{line}'")
    else:
        print("❌ No line breaks in formatted ratio")
        return False
    
    # Test with actual data processing
    print("\n" + "=" * 60)
    print("Testing with Excel Processor")
    print("=" * 60)
    
    # Create test data
    test_data = {
        'Product Name*': ['Test Product'],
        'Product Type*': ['concentrate'],  # Use classic type
        'Description': ['Test description'],
        'Lineage': ['Test lineage'],
        'Product Strain': ['Test strain'],
        'Ratio': ['230mg CBD 50mg THC 10mg CBG 10mg CBN'],  # Add mg values
        'Product Brand': ['Test Brand'],
        'Vendor': ['Test Vendor'],
        'Price': ['$10'],
        'Weight*': ['1'],
        'Units': ['oz']
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
            return False
        
        # Get all available tags and select them
        available_tags = processor.get_available_tags()
        if available_tags:
            tag_names = [tag['displayName'] for tag in available_tags]
            processor.select_tags(tag_names)
        
        # Get the processed records
        records = processor.get_selected_records('vertical')
        
        if not records:
            print("❌ No records found")
            return False
        
        print(f"Found {len(records)} records")
        
        for i, record in enumerate(records, 1):
            print(f"\nRecord {i}: {record.get('ProductName', 'Unknown')}")
            original_ratio = record.get('Ratio', '')
            print(f"Original Ratio from file: '{original_ratio}'")
            
            # Test the format_ratio_multiline function on the record
            if original_ratio:
                formatted_ratio = format_ratio_multiline(original_ratio)
                print(f"Formatted Ratio: '{formatted_ratio}'")
                
                if '\n' in formatted_ratio:
                    print("✅ Line breaks found in formatted ratio")
                    lines = formatted_ratio.split('\n')
                    print(f"  Split into {len(lines)} lines:")
                    for j, line in enumerate(lines, 1):
                        print(f"    Line {j}: '{line}'")
                else:
                    print("❌ No line breaks found in formatted ratio")
            else:
                print("❌ No ratio content found")
        
        # Test template processing (without requiring template files)
        print("\n" + "=" * 60)
        print("Testing Template Processing Logic")
        print("=" * 60)
        
        for i, record in enumerate(records, 1):
            print(f"\nProcessing Record {i}: {record.get('ProductName', 'Unknown')}")
            
            # Debug: print all available fields
            print(f"  Available fields: {list(record.keys())}")
            
            # Simulate the template processing logic
            ratio_val = record.get('Ratio', '')
            if ratio_val:
                cleaned_ratio = ratio_val.strip()
                product_type = record.get('ProductType', '').strip().lower()
                classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
                
                print(f"  Product Type: '{product_type}'")
                print(f"  Is Classic Type: {product_type in classic_types}")
                print(f"  Contains 'mg': {'mg' in cleaned_ratio.lower()}")
                
                if product_type in classic_types and 'mg' in cleaned_ratio.lower():
                    # This should trigger format_ratio_multiline
                    final_ratio = format_ratio_multiline(cleaned_ratio)
                    print(f"  Final Ratio (after format_ratio_multiline): '{final_ratio}'")
                    
                    if '\n' in final_ratio:
                        print("  ✅ Line breaks preserved in final ratio")
                    else:
                        print("  ❌ Line breaks lost in final ratio")
                else:
                    print(f"  Final Ratio (no processing): '{cleaned_ratio}'")
            else:
                print("  ❌ No ratio value found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up temporary file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)

if __name__ == "__main__":
    success = test_full_ratio_pipeline()
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!") 