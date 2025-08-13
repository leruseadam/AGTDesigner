#!/usr/bin/env python3
"""
Detailed test script to debug preroll description processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)

def test_detailed_preroll():
    """Test preroll description processing with detailed logging."""
    
    print("Testing detailed preroll description processing...")
    
    # Create a test record for preroll
    test_record = {
        'ProductName': 'Test Pre-Roll',
        'Product Type*': 'pre-roll',
        'Description': 'Blueberry Infused Pre-Roll',
        'WeightUnits': '0.5g x 2 Pack',
        'ProductBrand': 'Test Brand',
        'Price': '$15.00',
        'Lineage': 'HYBRID',
        'DOH': 'YES',
        'Ratio': '0.5g x 2 Pack',
        'JointRatio': '0.5g x 2 Pack',
        'THC': '15.5%',
        'CBD': '0.1%'
    }
    
    print(f"Test record: {test_record}")
    
    # Test with horizontal template
    print("\n1. Testing with horizontal template...")
    try:
        font_scheme = get_font_scheme('horizontal')
        processor = TemplateProcessor('horizontal', font_scheme, scale_factor=1.0)
        
        # Check what template path is being used
        print(f"Template path: {processor._template_path}")
        print(f"Template exists: {processor._template_path.exists()}")
        
        # Process the record
        doc = processor.process_records([test_record])
        
        if doc:
            print("✅ Template processing successful")
            
            # Show all text content in the document
            print("\nAll text content in document:")
            for i, paragraph in enumerate(doc.paragraphs):
                if paragraph.text.strip():
                    print(f"  Paragraph {i+1}: '{paragraph.text}'")
                    
                    # Show runs
                    for j, run in enumerate(paragraph.runs):
                        if run.text.strip():
                            print(f"    Run {j+1}: '{run.text}' - Font: {run.font.name}, Bold: {run.font.bold}")
            
            # Check tables
            print(f"\nDocument has {len(doc.tables)} tables")
            for i, table in enumerate(doc.tables):
                print(f"  Table {i+1}: {len(table.rows)} rows, {len(table.columns)} columns")
                for row_idx, row in enumerate(table.rows):
                    for col_idx, cell in enumerate(row.cells):
                        if cell.text.strip():
                            print(f"    Cell ({row_idx+1}, {col_idx+1}): '{cell.text}'")
                        
                        # Check for inner tables
                        if cell.tables:
                            print(f"    Cell ({row_idx+1}, {col_idx+1}) has {len(cell.tables)} inner tables")
                            for inner_idx, inner_table in enumerate(cell.tables):
                                print(f"      Inner table {inner_idx+1}: {len(inner_table.rows)} rows, {len(inner_table.columns)} columns")
                                for inner_row_idx, inner_row in enumerate(inner_table.rows):
                                    for inner_col_idx, inner_cell in enumerate(inner_row.cells):
                                        if inner_cell.text.strip():
                                            print(f"        Inner cell ({inner_row_idx+1}, {inner_col_idx+1}): '{inner_cell.text}'")
            
            # Check if the document contains the preroll description
            found_description = False
            for paragraph in doc.paragraphs:
                if 'Blueberry Infused Pre-Roll' in paragraph.text:
                    found_description = True
                    print(f"\n✅ Found description paragraph: '{paragraph.text}'")
                    
                    # Check formatting of each run
                    for i, run in enumerate(paragraph.runs):
                        print(f"    Run {i+1}: '{run.text}' - Font: {run.font.name}, Bold: {run.font.bold}")
                        
                        # Check if this run contains the description
                        if 'Blueberry' in run.text or 'Pre-Roll' in run.text:
                            if run.font.bold:
                                print(f"      ✅ Description text is BOLD")
                            else:
                                print(f"      ❌ Description text is NOT BOLD")
                        
            if not found_description:
                print("\n❌ Preroll description not found in document")
                
        else:
            print("❌ Template processing failed")
            
    except Exception as e:
        print(f"❌ Error testing horizontal template: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_detailed_preroll()
