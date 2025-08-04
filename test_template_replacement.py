#!/usr/bin/env python3
"""
Test script to verify that template replacement is working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from docx import Document
from src.core.generation.template_processor import get_font_scheme, TemplateProcessor

def test_template_replacement():
    """Test that template replacement is working correctly."""
    
    print("Testing Template Replacement")
    print("=" * 50)
    
    # Create a simple test record
    test_record = {
        'ProductType': 'flower',
        'WeightUnits': '3.5g',
        'Ratio': 'THC: 25%\nCBD: 2%',
        'Description': 'Blue Dream',
        'ProductBrand': 'Test Brand',
        'Price': '$45',
        'Lineage': 'HYBRID',
        'ProductStrain': 'Blue Dream'
    }
    
    # Create mini template processor
    font_scheme = get_font_scheme('mini')
    processor = TemplateProcessor('mini', font_scheme, 1.0)
    
    print(f"Processing test record...")
    
    try:
        # Generate the document
        doc = processor.process_records([test_record])
        
        if doc:
            # Save the document
            output_filename = "test_template_replacement.docx"
            doc.save(output_filename)
            print(f"✓ Successfully generated document: {output_filename}")
            
            # Check the content
            print("\nDocument content analysis:")
            print("-" * 40)
            
            full_text = ""
            for paragraph in doc.paragraphs:
                full_text += paragraph.text + "\n"
            
            print(f"Full document text: {repr(full_text)}")
            
            # Check for specific content
            if '3.5g' in full_text:
                print(f"✓ Found weight units: 3.5g")
            else:
                print(f"✗ Weight units NOT found: 3.5g")
            
            if 'Blue Dream' in full_text:
                print(f"✓ Found description: Blue Dream")
            else:
                print(f"✗ Description NOT found: Blue Dream")
            
            if 'Test Brand' in full_text:
                print(f"✓ Found brand: Test Brand")
            else:
                print(f"✗ Brand NOT found: Test Brand")
            
            if '$45' in full_text:
                print(f"✓ Found price: $45")
            else:
                print(f"✗ Price NOT found: $45")
            
            if 'HYBRID' in full_text:
                print(f"✓ Found lineage: HYBRID")
            else:
                print(f"✗ Lineage NOT found: HYBRID")
            
            # Check for THC/CBD content (should NOT be present for classic types in mini)
            if 'THC:' in full_text or 'CBD:' in full_text:
                print(f"⚠ Found THC/CBD content (unexpected for mini classic types)")
            else:
                print(f"✓ No THC/CBD content found (as expected for mini classic types)")
                
        else:
            print("✗ Failed to generate document")
            
    except Exception as e:
        print(f"✗ Error generating document: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_template_replacement() 