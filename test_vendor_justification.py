#!/usr/bin/env python3
"""
Test script to verify Product Vendor justification fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor

def test_vendor_justification():
    """Test that Product Vendor justification is working correctly."""
    
    try:
        print("Testing Product Vendor justification fix...")
        processor = TemplateProcessor('horizontal', {}, 1.0)
        
        print(f"Template type: {processor.template_type}")
        print(f"Chunk size: {processor.chunk_size}")
        
        # Test data with vendor information
        test_records = [
            {
                'ProductName': 'Test Product 1',
                'ProductType': 'Flower',
                'Lineage': 'SATIVA',
                'ProductVendor': '1555 Industrial LLC',
                'Price': '$25.00',
                'Description': 'Test Description 1'
            },
            {
                'ProductName': 'Test Product 2', 
                'ProductType': 'Flower',
                'Lineage': 'INDICA',
                'ProductVendor': '1555 Industrial LLC',
                'Price': '$30.00',
                'Description': 'Test Description 2'
            },
            {
                'ProductName': 'Test Product 3',
                'ProductType': 'Flower', 
                'Lineage': 'HYBRID',
                'ProductVendor': '1555 Industrial LLC',
                'Price': '$35.00',
                'Description': 'Test Description 3'
            }
        ]
        
        # Process the records
        result_doc = processor.process_records(test_records)
        
        if result_doc:
            print(f"✓ Document generated successfully")
            print(f"  Tables: {len(result_doc.tables)}")
            
            if result_doc.tables:
                for i, table in enumerate(result_doc.tables):
                    print(f"  Table {i}: {len(table.rows)} rows x {len(table.columns)} columns")
                    
                    # Check cell content and alignment
                    for row_idx, row in enumerate(table.rows):
                        for col_idx, cell in enumerate(row.cells):
                            cell_text = cell.text.strip()
                            if cell_text:
                                print(f"    Cell ({row_idx},{col_idx}): '{cell_text[:100]}...'")
                                
                                # Check for vendor text and alignment
                                if '1555 Industrial LLC' in cell_text:
                                    print(f"      ✓ Found Product Vendor text")
                                    # Check paragraph alignment
                                    for para in cell.paragraphs:
                                        if '1555 Industrial LLC' in para.text:
                                            alignment = para.alignment
                                            print(f"      Paragraph alignment: {alignment}")
                                            if alignment == 3:  # WD_ALIGN_PARAGRAPH.JUSTIFY
                                                print(f"      ✓ Paragraph is justified (correct for vendor alignment)")
                                            else:
                                                print(f"      ❌ Paragraph alignment is not justified")
                            else:
                                print(f"    Cell ({row_idx},{col_idx}): Empty")
                
                # Save the document for inspection
                result_doc.save("test_vendor_justification_result.docx")
                print("✓ Result document saved as: test_vendor_justification_result.docx")
            else:
                print("❌ No tables in generated document")
                return False
        else:
            print("❌ Document generation failed - returned None")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error in vendor justification test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_vendor_justification()
