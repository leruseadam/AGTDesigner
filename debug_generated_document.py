#!/usr/bin/env python3
"""
Debug script to examine the actual content of the generated document and see what fields are present.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor

def debug_generated_document():
    """Debug the generated document content."""
    
    print("Debugging generated document content...")
    
    # Create a test record
    test_record = {
        'ProductStrain': 'TEST_STRAIN_123',
        'Lineage': 'TEST_LINEAGE',
        'ProductBrand': 'TEST_BRAND',
        'ProductVendor': 'TEST_VENDOR',
        'Description': 'Test Description',
        'WeightUnits': '1g',
        'Ratio_or_THC_CBD': 'THC: 15% CBD: 2%',
        'Price': '$25.00',
        'ProductType': 'flower'
    }
    
    try:
        # Create template processor
        processor = TemplateProcessor('double', 'default')
        
        # Process the test record
        print("Processing test record...")
        result = processor.process_records([test_record])
        
        if result:
            print("Generated output document")
            
            # Examine the document content
            print("\n=== DOCUMENT CONTENT ANALYSIS ===")
            
            for table_idx, table in enumerate(result.tables):
                print(f"\n--- TABLE {table_idx + 1} ---")
                for row_idx, row in enumerate(table.rows):
                    print(f"  ROW {row_idx + 1}:")
                    for cell_idx, cell in enumerate(row.cells):
                        print(f"    CELL {cell_idx + 1}:")
                        for para_idx, paragraph in enumerate(cell.paragraphs):
                            if paragraph.text.strip():
                                print(f"      Paragraph {para_idx + 1}: '{paragraph.text}'")
                                # Check font sizes for each run
                                for run_idx, run in enumerate(paragraph.runs):
                                    if run.text.strip():
                                        font_size = run.font.size
                                        font_size_str = f"{font_size.pt}pt" if font_size else "No font size"
                                        print(f"        Run {run_idx + 1}: '{run.text}' (Font: {font_size_str})")
            
            print("\n=== END DOCUMENT ANALYSIS ===")
            
        else:
            print("❌ FAIL: No output generated")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_generated_document() 