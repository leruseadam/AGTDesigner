#!/usr/bin/env python3
"""
Test script to verify that the double template now properly uses brand names 
instead of descriptions for edibles.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.tag_generator import process_chunk
from src.core.generation.docx_formatting import apply_lineage_colors
from docx import Document
from io import BytesIO

def test_double_template_brand_fix():
    """Test that double template uses brand names for edibles."""
    print("Testing Double Template Brand Fix")
    
    # Create test data for edibles
    test_records = [
        {
            "Product Name*": "HOT SHOTZ Edible",
            "Description": "Huckleberriez CBN Shot",
            "Product Brand": "HOT SHOTZ",
            "Product Type*": "Edible (Liquid)",
            "Price": "$18",
            "Lineage": "HYBRID",
            "Ratio": "100mg THC / 5mg CBN",
            "WeightUnits": "2oz",
            "Product Strain": "CBD Blend",
            "DOH": "NO",
            "JointRatio": ""
        },
        {
            "Product Name*": "CONSTELLATION CANNABIS Edible",
            "Description": "Constellation Cannabis Shot",
            "Product Brand": "CONSTELLATION CANNABIS",
            "Product Type*": "Edible (Liquid)",
            "Price": "$18",
            "Lineage": "HYBRID",
            "Ratio": "50mg THC / 50mg CBC",
            "WeightUnits": "2oz",
            "Product Strain": "CBD Blend",
            "DOH": "NO",
            "JointRatio": ""
        }
    ]
    
    # Test the process_chunk function
    try:
        # Get template path
        from src.core.generation.tag_generator import get_template_path
        template_path = get_template_path('double')
        print(f"Template path: {template_path}")
        
        # Process the chunk
        result = process_chunk((
            test_records,
            template_path,
            None,  # font_scheme
            'double',  # orientation
            1.0  # scale_factor
        ))
        
        if result:
            print("✓ Template processing successful")
            
            # Load the document to check content
            doc = Document(BytesIO(result))
            
            # Check if brand names appear in the document
            doc_text = ""
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        doc_text += cell.text + " "
            
            print(f"Document text: {doc_text[:200]}...")
            
            # Check for brand names in markers
            if "DESC_STARTHOT SHOTZ" in doc_text:
                print("✓ Brand name HOT SHOTZ found in document markers")
                print("✓ Double template is now using brand names instead of descriptions for edibles")
                return True
            else:
                print("✗ Brand names not found in document markers")
                print(f"Looking for: DESC_STARTHOT SHOTZ")
                print(f"Found in text: {doc_text}")
                return False
        else:
            print("✗ Template processing failed")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_double_template_brand_fix()
    if success:
        print("\n✓ Double template brand fix test PASSED")
    else:
        print("\n✗ Double template brand fix test FAILED")
        sys.exit(1) 