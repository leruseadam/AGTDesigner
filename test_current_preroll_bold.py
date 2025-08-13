#!/usr/bin/env python3
"""
Test script to check current preroll bold formatting status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor, get_font_scheme

def test_current_preroll_bold():
    """Test if preroll descriptions are currently getting bold formatting."""
    
    print("Testing current preroll bold formatting status...")
    
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
    
    # Test with vertical template
    print("\n1. Testing with vertical template...")
    try:
        font_scheme = get_font_scheme('vertical')
        processor = TemplateProcessor('vertical', font_scheme, scale_factor=1.0)
        doc = processor.process_records([test_record])
        
        if doc:
            print("✅ Template processing successful")
            
            # Show all text content in the document
            print("\nAll text content in document:")
            for i, paragraph in enumerate(doc.paragraphs):
                if paragraph.text.strip():
                    print(f"  Paragraph {i+1}: '{paragraph.text}'")
                    
                    # Check formatting of each run
                    for j, run in enumerate(paragraph.runs):
                        if run.text.strip():
                            print(f"    Run {j+1}: '{run.text}' - Font: {run.font.name}, Bold: {run.font.bold}")
            
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
        print(f"❌ Error testing vertical template: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with horizontal template
    print("\n2. Testing with horizontal template...")
    try:
        font_scheme = get_font_scheme('horizontal')
        processor = TemplateProcessor('horizontal', font_scheme, scale_factor=1.0)
        doc = processor.process_records([test_record])
        
        if doc:
            print("✅ Template processing successful")
            
            # Show all text content in the document
            print("\nAll text content in document:")
            for i, paragraph in enumerate(doc.paragraphs):
                if paragraph.text.strip():
                    print(f"  Paragraph {i+1}: '{paragraph.text}'")
                    
                    # Check formatting of each run
                    for j, run in enumerate(paragraph.runs):
                        if run.text.strip():
                            print(f"    Run {j+1}: '{run.text}' - Font: {run.font.name}, Bold: {run.font.bold}")
            
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
    test_current_preroll_bold()
