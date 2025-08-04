#!/usr/bin/env python3
"""
Test script to verify double template brand centering for non-classic types.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from src.core.constants import FONT_SCHEME_DOUBLE
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

def test_double_brand_centering():
    """Test that double template centers brand names for non-classic types."""
    print("Testing Double Template Brand Centering")
    print("=" * 50)
    
    # Print alignment constants for reference
    print(f"WD_ALIGN_PARAGRAPH.CENTER = {WD_ALIGN_PARAGRAPH.CENTER}")
    print(f"WD_ALIGN_PARAGRAPH.LEFT = {WD_ALIGN_PARAGRAPH.LEFT}")
    print(f"WD_ALIGN_PARAGRAPH.RIGHT = {WD_ALIGN_PARAGRAPH.RIGHT}")
    print(f"WD_ALIGN_PARAGRAPH.JUSTIFY = {WD_ALIGN_PARAGRAPH.JUSTIFY}")
    print()
    
    # Test records with different product types
    test_records = [
        # Non-classic type (should be centered)
        {
            'Description': 'Test Edible Product',
            'WeightUnits': '100mg',
            'ProductBrand': 'Test Brand',
            'Price': '$10.00',
            'Lineage': 'Test Lineage',
            'THC_CBD': 'THC: 10mg CBD: 5mg',
            'ProductStrain': 'Test Strain',
            'ProductType': 'edible (solid)',
            'DOH': 'YES'
        },
        # Classic type (should not be centered)
        {
            'Description': 'Test Flower Product',
            'WeightUnits': '1g',
            'ProductBrand': 'Test Brand',
            'Price': '$25.00',
            'Lineage': 'Sativa',
            'THC_CBD': 'THC: 20% CBD: 2%',
            'ProductStrain': 'Test Strain',
            'ProductType': 'flower',
            'DOH': 'YES'
        }
    ]
    
    # Test double template
    processor = TemplateProcessor('double', FONT_SCHEME_DOUBLE)
    
    for i, record in enumerate(test_records):
        print(f"\nTest Record {i+1}: {record['ProductType']}")
        print(f"Product Brand: {record['ProductBrand']}")
        
        # Process the record
        result_doc = processor.process_records([record])
        
        if not result_doc:
            print("ERROR: Failed to process test record")
            continue
        
        # Check paragraph alignment for brand content
        found_brand_paragraph = False
        brand_alignment = None
        
        for table in result_doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        # Look for paragraphs containing the brand name
                        if record['ProductBrand'] in paragraph.text:
                            found_brand_paragraph = True
                            brand_alignment = paragraph.alignment
                            print(f"  Found brand paragraph with alignment: {brand_alignment}")
                            print(f"  Paragraph text: '{paragraph.text}'")
                            
                            # Check if paragraph has any runs and their properties
                            if paragraph.runs:
                                print(f"  Number of runs: {len(paragraph.runs)}")
                                for j, run in enumerate(paragraph.runs):
                                    print(f"    Run {j}: '{run.text}' (font: {run.font.name}, size: {run.font.size})")
                            
                            # Check for any remaining markers in the text
                            if 'PRODUCTBRAND_CENTER_START' in paragraph.text or 'PRODUCTBRAND_START' in paragraph.text:
                                print(f"  WARNING: Found unprocessed markers in text!")
                            
                            break
                    if found_brand_paragraph:
                        break
                if found_brand_paragraph:
                    break
            if found_brand_paragraph:
                break
        
        # Verify the correct alignment is used
        if record['ProductType'] == 'edible (solid)':  # Non-classic type
            if brand_alignment == WD_ALIGN_PARAGRAPH.CENTER:
                print(f"  ✓ CORRECT: Non-classic type brand is centered")
            else:
                print(f"  ✗ ERROR: Non-classic type brand should be centered, but got: {brand_alignment}")
        else:  # Classic type
            if brand_alignment == WD_ALIGN_PARAGRAPH.LEFT:
                print(f"  ✓ CORRECT: Classic type brand is left-aligned")
            else:
                print(f"  ✗ ERROR: Classic type brand should be left-aligned, but got: {brand_alignment}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_double_brand_centering() 