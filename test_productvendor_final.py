#!/usr/bin/env python3
"""
Final test to verify ProductVendor is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from docx import Document

def test_productvendor_final():
    """Final test to verify ProductVendor is working correctly"""
    print("=== Final ProductVendor Test ===")
    
    # Create a test Excel file with vendor data
    test_data = {
        'ProductName': ['Test Product 1'],
        'Vendor': ['Test Vendor Company'],
        'ProductStrain': ['Test Strain'],
        'Lineage': ['Sativa']
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
            
            # Check if Vendor is present
            if 'Vendor' in first_record:
                vendor_value = first_record['Vendor']
                print(f"✅ Vendor found: '{vendor_value}'")
            else:
                print("❌ Vendor not found in record")
            
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
                
                # Save the document to check its content
                output_path = "test_productvendor_final_output.docx"
                output_doc.save(output_path)
                
                # Check the output document
                output_doc_check = Document(output_path)
                
                # Check all tables for ProductVendor content
                found_vendor = False
                found_markers = False
                
                for table_idx, table in enumerate(output_doc_check.tables):
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
                else:
                    print("🎉 SUCCESS: ProductVendor markers are preserved in the output!")
                
                # Clean up
                os.remove(output_path)
            else:
                print("❌ No output document returned from processing")
        
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
    test_productvendor_final() 