#!/usr/bin/env python3
"""
Test to verify dynamic font sizing is working in document generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from src.core.constants import FONT_SCHEME_DOUBLE
from src.core.generation.unified_font_sizing import get_font_size, get_font_size_by_marker
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

def test_dynamic_font_sizing():
    """Test that dynamic font sizing is working in document generation."""
    print("Testing Dynamic Font Sizing in Document Generation")
    print("=" * 60)
    
    # Test the font sizing function directly first
    print("1. Testing Font Sizing Function Directly:")
    brand_names = ['JOURNEYMAN', 'FAIRWINDS', 'GREEN', 'CQ', 'HOT SHOTZ']
    for brand in brand_names:
        font_size = get_font_size(brand, 'brand', 'double', 1.0)
        print(f"   {brand}: {font_size.pt}pt")
    
    print("\n2. Testing Document Generation:")
    
    # Test data with different brand name lengths
    test_records = [
        {
            'Description': 'Test Product 1',
            'WeightUnits': '1g',
            'ProductBrand': 'JOURNEYMAN',  # 9 letters
            'Price': '$18',
            'Lineage': 'Test Lineage',
            'THC_CBD': 'THC: 20% CBD: 2%',
            'ProductStrain': 'Test Strain',
            'DOH': 'DOH',
            'ProductType': 'edible (liquid)'
        },
        {
            'Description': 'Test Product 2',
            'WeightUnits': '1g',
            'ProductBrand': 'GREEN',  # 5 letters
            'Price': '$18',
            'Lineage': 'Test Lineage',
            'THC_CBD': 'THC: 20% CBD: 2%',
            'ProductStrain': 'Test Strain',
            'DOH': 'DOH',
            'ProductType': 'edible (liquid)'
        },
        {
            'Description': 'Test Product 3',
            'WeightUnits': '1g',
            'ProductBrand': 'CQ',  # 2 letters
            'Price': '$18',
            'Lineage': 'Test Lineage',
            'THC_CBD': 'THC: 20% CBD: 2%',
            'ProductStrain': 'Test Strain',
            'DOH': 'DOH',
            'ProductType': 'edible (liquid)'
        }
    ]
    
    # Process the records
    processor = TemplateProcessor('double', FONT_SCHEME_DOUBLE)
    result_doc = processor.process_records(test_records)
    
    if not result_doc:
        print("ERROR: Failed to process test records")
        return
    
    print("✅ Document processed successfully")
    
    # Check font sizes in the generated document
    print("\n3. Checking Font Sizes in Generated Document:")
    
    for table in result_doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph_text = paragraph.text.strip()
                    
                    # Check if this contains brand content
                    brand_names = ['JOURNEYMAN', 'FAIRWINDS', 'GREEN', 'CQ', 'HOT SHOTZ']
                    if any(brand in paragraph_text.upper() for brand in brand_names):
                        print(f"\nBrand content: '{paragraph_text}'")
                        
                        # Check centering
                        if paragraph.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                            print(f"  ✅ Centering: OK")
                        else:
                            print(f"  ❌ Centering: FAILED")
                        
                        # Check font sizes for each run
                        for run in paragraph.runs:
                            if run.text.strip():
                                font_size_pt = run.font.size.pt if run.font.size else 0
                                print(f"  Run '{run.text}': {font_size_pt}pt")
                                
                                # Check if this looks like a brand name
                                if any(brand in run.text.upper() for brand in brand_names):
                                    expected_size = get_font_size(run.text.strip(), 'brand', 'double', 1.0).pt
                                    if abs(font_size_pt - expected_size) < 0.1:
                                        print(f"    ✅ Font size matches expected ({expected_size}pt)")
                                    else:
                                        print(f"    ❌ Font size mismatch: got {font_size_pt}pt, expected {expected_size}pt")
    
    # Save the document
    output_path = "test_dynamic_font_sizing_output.docx"
    result_doc.save(output_path)
    print(f"\nDocument saved to: {output_path}")

if __name__ == "__main__":
    test_dynamic_font_sizing() 