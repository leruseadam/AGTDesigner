#!/usr/bin/env python3
"""
Test ProductVendor output with real data using the Excel processor
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from docx import Document

def test_productvendor_with_real_data():
    """Test ProductVendor output using the actual Excel processor"""
    print("=== Testing ProductVendor with Real Data ===")
    
    # Create a test Excel file with vendor data
    test_data = {
        'ProductName': ['Test Product 1', 'Test Product 2'],
        'Vendor': ['Test Vendor Company', 'Another Vendor'],
        'ProductStrain': ['Test Strain 1', 'Test Strain 2'],
        'Lineage': ['Sativa', 'Indica']
    }
    
    test_df = pd.DataFrame(test_data)
    test_file = "test_vendor_data.xlsx"
    test_df.to_excel(test_file, index=False)
    
    try:
        # Import and initialize the Excel processor
        from src.core.data.excel_processor import ExcelProcessor
        
        # Create processor and load the test file
        processor = ExcelProcessor()
        processor.load_file(test_file)
        
        # Set selected tags
        processor.selected_tags = ['Test Product 1']
        
        # Get records for horizontal template (which has ProductVendor placeholder)
        records = processor.get_selected_records('horizontal')
        
        print(f"✅ Got {len(records)} records from processor")
        
        if records:
            # Check the first record
            first_record = records[0]
            print(f"First record keys: {list(first_record.keys())}")
            
            # Check if ProductVendor is present
            if 'ProductVendor' in first_record:
                vendor_value = first_record['ProductVendor']
                print(f"✅ ProductVendor found: '{vendor_value}'")
                
                # Check if it has markers
                if 'PRODUCTVENDOR_START' in vendor_value and 'PRODUCTVENDOR_END' in vendor_value:
                    print("✅ ProductVendor has proper markers")
                else:
                    print("❌ ProductVendor missing markers")
            else:
                print("❌ ProductVendor not found in record")
            
            # Now test with TemplateProcessor
            print("\n=== Testing with TemplateProcessor ===")
            
            from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
            
            # Create processor
            font_scheme = get_font_scheme('horizontal')
            processor_tp = TemplateProcessor('horizontal', font_scheme)
            
            # Process records
            output_doc = processor_tp.process_records(records)
            
            if output_doc:
                print(f"✅ Processing completed, output is a Document object")
                
                # Check the output document directly
                
                # Check all tables for ProductVendor content
                found_vendor = False
                found_markers = False
                
                for table_idx, table in enumerate(output_doc.tables):
                    for row_idx, row in enumerate(table.rows):
                        for col_idx, cell in enumerate(row.cells):
                            cell_text = cell.text
                            if 'Test Vendor Company' in cell_text:
                                found_vendor = True
                                print(f"✅ Found vendor text in table {table_idx}, cell [{row_idx},{col_idx}]: '{cell_text}'")
                            
                            if 'PRODUCTVENDOR_START' in cell_text and 'PRODUCTVENDOR_END' in cell_text:
                                found_markers = True
                                print(f"✅ Found ProductVendor markers in table {table_idx}, cell [{row_idx},{col_idx}]: '{cell_text}'")
                
                if not found_vendor:
                    print("❌ No vendor text found in output document")
                
                if not found_markers:
                    print("❌ No ProductVendor markers found in output document")
                    print("   This indicates markers are being stripped during post-processing")
                
                # No cleanup needed for Document object
            else:
                print("❌ No output path returned from processing")
        
        else:
            print("❌ No records returned from processor")
    
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_productvendor_with_real_data() 