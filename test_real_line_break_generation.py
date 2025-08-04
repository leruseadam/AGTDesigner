#!/usr/bin/env python3
"""
Test script to verify line break conversion works in real document generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from src.core.data.excel_processor import ExcelProcessor
import tempfile
import shutil

def test_real_line_break_generation():
    """Test line break conversion in real document generation."""
    
    print("=== Testing Real Document Generation with Line Breaks ===")
    
    # Create test data with ratio content that should have line breaks
    test_records = [
        {
            'Product Name*': 'Test Edible Product',
            'Product Brand': 'Test Brand',
            'Product Type*': 'edible (solid)',
            'Lineage': 'MIXED',
            'Price': '$25.99',
            'Ratio': '100mg THC 50mg CBD 5mg CBG',
            'Description': 'Test description',
            'Weight Units': '4oz'
        },
        {
            'Product Name*': 'Test RSO Product',
            'Product Brand': 'Test Brand',
            'Product Type*': 'rso/co2 tankers',
            'Lineage': 'MIXED',
            'Price': '$45.99',
            'Ratio': '200mg THC 100mg CBD 10mg CBG',
            'Description': 'Test RSO description',
            'Weight Units': '1g'
        }
    ]
    
    # Create template processor
    processor = TemplateProcessor('vertical', {}, 1.0)
    
    try:
        # Process the records
        print("Processing test records...")
        doc = processor.process_records(test_records)
        
        if doc:
            print("✅ Document generated successfully!")
            
            # Check the content for line breaks
            print("\nChecking for line breaks in generated content...")
            
            for table_idx, table in enumerate(doc.tables):
                print(f"\nTable {table_idx + 1}:")
                for row_idx, row in enumerate(table.rows):
                    for cell_idx, cell in enumerate(row.cells):
                        cell_text = cell.text.strip()
                        if cell_text:
                            print(f"  Cell ({row_idx}, {cell_idx}): '{cell_text}'")
                            
                            # Check if this cell contains line breaks
                            if '\n' in cell_text:
                                print(f"    ✅ Contains line breaks!")
                                lines = cell_text.split('\n')
                                for i, line in enumerate(lines):
                                    print(f"      Line {i+1}: '{line}'")
                            
                            # Check for |BR| markers (should not be present)
                            if '|BR|' in cell_text:
                                print(f"    ❌ Still contains |BR| markers!")
            
            # Save the document for inspection
            output_path = "test_line_break_output.docx"
            doc.save(output_path)
            print(f"\n✅ Document saved to: {output_path}")
            print("You can open this file in Word to verify the line breaks are working correctly.")
            
        else:
            print("❌ Failed to generate document")
            
    except Exception as e:
        print(f"❌ Error during document generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_line_break_generation() 