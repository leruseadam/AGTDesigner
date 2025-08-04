#!/usr/bin/env python3
"""
Simple test to check double template brand centering.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from src.core.constants import FONT_SCHEME_DOUBLE
from docx.enum.text import WD_ALIGN_PARAGRAPH

def test_simple_brand_centering():
    """Simple test for brand centering in double template."""
    print("Testing Double Template Brand Centering")
    print("=" * 50)
    
    # Test data with actual brand names from the image
    test_record = {
        'Description': '30:2:1 Extra Relief Tincture - 1oz',
        'WeightUnits': '1oz',
        'ProductBrand': 'GREEN',
        'Price': '$38',
        'Lineage': 'CBD 300mg 20mg',
        'THC_CBD': 'THC: 20% CBD: 2%',
        'ProductStrain': 'Test Strain',
        'DOH': 'DOH',
        'ProductType': 'tincture'
    }
    
    # Test double template
    processor = TemplateProcessor('double', FONT_SCHEME_DOUBLE)
    result_doc = processor.process_records([test_record])
    
    if not result_doc:
        print("ERROR: Failed to process test record")
        return False
    
    # Check for brand centering
    brand_found = False
    brand_centered = False
    
    for table in result_doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph_text = paragraph.text.strip()
                    
                    # Look for the brand name "GREEN"
                    if 'GREEN' in paragraph_text:
                        brand_found = True
                        print(f"Found brand content: '{paragraph_text}'")
                        print(f"Alignment: {paragraph.alignment}")
                        
                        if paragraph.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                            brand_centered = True
                            print("✓ Brand content is CENTERED")
                        else:
                            print("✗ Brand content is NOT centered")
    
    if brand_found:
        if brand_centered:
            print("✓ SUCCESS: Brand content is properly centered")
            return True
        else:
            print("✗ FAILURE: Brand content is not centered")
            return False
    else:
        print("✗ FAILURE: Brand content not found")
        return False

if __name__ == "__main__":
    success = test_simple_brand_centering()
    if success:
        print("\n✓ Brand centering is working!")
    else:
        print("\n✗ Brand centering needs fixing!") 