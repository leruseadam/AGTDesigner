#!/usr/bin/env python3
"""
Test script to debug table generation issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor

def test_table_generation():
    """Test basic table generation to see what's happening."""
    
    # Test data - just a few records
    test_records = [
        {
            'ProductName': 'Test Product 1',
            'ProductType': 'Flower',
            'Lineage': 'SATIVA',
            'ProductVendor': 'Test Vendor 1',
            'Price': '$25.00',
            'Description': 'Test Description 1'
        },
        {
            'ProductName': 'Test Product 2', 
            'ProductType': 'Flower',
            'Lineage': 'INDICA',
            'ProductVendor': 'Test Vendor 2',
            'Price': '$30.00',
            'Description': 'Test Description 2'
        },
        {
            'ProductName': 'Test Product 3',
            'ProductType': 'Flower', 
            'Lineage': 'HYBRID',
            'ProductVendor': 'Test Vendor 3',
            'Price': '$35.00',
            'Description': 'Test Description 3'
        }
    ]
    
    try:
        print("Testing horizontal template...")
        processor = TemplateProcessor('horizontal', {}, 1.0)
        
        # Process the records
        result_doc = processor.process_records(test_records)
        
        if result_doc:
            print(f"✓ Document generated successfully")
            print(f"  Tables: {len(result_doc.tables)}")
            print(f"  Paragraphs: {len(result_doc.tables)}")
            
            if result_doc.tables:
                for i, table in enumerate(result_doc.tables):
                    print(f"  Table {i}: {len(table.rows)} rows x {len(table.columns)} columns")
                    
                    # Check cell content
                    for row_idx, row in enumerate(table.rows):
                        for col_idx, cell in enumerate(row.cells):
                            cell_text = cell.text.strip()
                            if cell_text:
                                print(f"    Cell ({row_idx},{col_idx}): '{cell_text[:100]}...'")
                            else:
                                print(f"    Cell ({row_idx},{col_idx}): Empty")
                
                # Save the document for inspection
                result_doc.save("test_table_issue_result.docx")
                print("✓ Result document saved as: test_table_issue_result.docx")
            else:
                print("❌ No tables in generated document")
                return False
        else:
            print("❌ Document generation failed - returned None")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error in table generation test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_table_generation()
