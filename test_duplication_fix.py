#!/usr/bin/env python3
"""
Simple test script to verify the duplication fix works.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.generation.template_processor import TemplateProcessor

def test_duplication_fix():
    """Test if the duplication fix actually works."""
    
    # Test record that should show the duplication
    test_record = {
        'ProductName': 'Grape Moonshot',
        'ProductBrand': 'CONSTELLATION CANNABIS',
        'Product Type*': 'edible (solid)',
        'Description': 'Grape Moonshot -1.7oz',
        'WeightUnits': '1.7oz',
        'Price': '$15',
        'THC': '100.0%',
        'CBD': '0%',
        'Lineage': 'MIXED'
    }
    
    print("=== TESTING DUPLICATION FIX ===")
    print(f"Test record: {test_record}")
    
    # Test with horizontal template
    from src.core.generation.template_processor import get_font_scheme
    font_scheme = get_font_scheme('horizontal')
    processor = TemplateProcessor('horizontal', font_scheme)
    
    try:
        # Generate the document
        print("Generating document...")
        records = [test_record]
        documents = processor.process_records(records)
        
        if documents:
            print(f"Generated document successfully")
            
            # Check the first document
            doc = documents[0] if hasattr(documents, '__len__') else documents
            
            if doc.tables:
                table = doc.tables[0]
                print(f"Document has {len(table.rows)} rows and {len(table.columns)} columns")
                
                # Check all cells for duplication
                duplication_found = False
                for row_idx, row in enumerate(table.rows):
                    for col_idx, cell in enumerate(row.cells):
                        cell_text = ' '.join([p.text for p in cell.paragraphs])
                        if 'CONSTELLATION CANNABISCONSTELLATION CANNABIS' in cell_text:
                            print(f"❌ DUPLICATION FOUND in cell ({row_idx}, {col_idx}): '{cell_text}'")
                            duplication_found = True
                        elif 'CONSTELLATION CANNABIS' in cell_text:
                            print(f"✅ Cell ({row_idx}, {col_idx}) has correct content: '{cell_text}'")
                
                if not duplication_found:
                    print("✅ SUCCESS: No duplication found in generated document!")
                    print("The duplication fix is working!")
                else:
                    print("❌ FAILURE: Duplication was still created during document generation")
                    print("The duplication fix did not work.")
            else:
                print("❌ Generated document has no tables")
        else:
            print("❌ No documents generated")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_duplication_fix()
