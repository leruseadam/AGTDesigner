#!/usr/bin/env python3
"""
Test script to generate an actual mini template document with classic types.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
from docx import Document

def test_mini_template_generation():
    """Generate a mini template with classic types to verify weight units display."""
    
    print("Testing Mini Template Generation with Classic Types")
    print("=" * 60)
    
    # Test data for classic types
    test_records = [
        {
            'ProductType': 'flower',
            'WeightUnits': '3.5g',
            'Ratio': 'THC: 25%\nCBD: 2%',
            'Description': 'Blue Dream',
            'ProductBrand': 'Test Brand',
            'Price': '$45',
            'Lineage': 'HYBRID',
            'ProductStrain': 'Blue Dream'
        },
        {
            'ProductType': 'vape cartridge',
            'WeightUnits': '1g',
            'Ratio': 'THC: 85%\nCBD: 1%',
            'Description': 'Sour Diesel Cart',
            'ProductBrand': 'Test Brand',
            'Price': '$35',
            'Lineage': 'SATIVA',
            'ProductStrain': 'Sour Diesel'
        },
        {
            'ProductType': 'concentrate',
            'WeightUnits': '0.5g',
            'Ratio': 'THC: 90%\nCBD: 0.5%',
            'Description': 'OG Kush Wax',
            'ProductBrand': 'Test Brand',
            'Price': '$40',
            'Lineage': 'INDICA',
            'ProductStrain': 'OG Kush'
        }
    ]
    
    # Create mini template processor
    font_scheme = get_font_scheme('mini')
    processor = TemplateProcessor('mini', font_scheme, 1.0)
    
    print(f"Processing {len(test_records)} classic type records...")
    
    try:
        # Generate the document
        doc = processor.process_records(test_records)
        
        if doc:
            # Save the document
            output_filename = "test_mini_classic_types.docx"
            doc.save(output_filename)
            print(f"✓ Successfully generated mini template: {output_filename}")
            
            # Check the content
            print("\nDocument content analysis:")
            print("-" * 40)
            
            full_text = ""
            for paragraph in doc.paragraphs:
                full_text += paragraph.text + "\n"
            
            # Also check table content
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        full_text += cell.text + "\n"
            
            # Check for weight units in the document
            weight_units_found = []
            for record in test_records:
                if record['WeightUnits'] in full_text:
                    weight_units_found.append(record['WeightUnits'])
                    print(f"✓ Found weight units: {record['WeightUnits']}")
                else:
                    print(f"✗ Weight units NOT found: {record['WeightUnits']}")
            
            # Check for THC/CBD content (should NOT be present for classic types in mini)
            thc_cbd_found = []
            for record in test_records:
                if 'THC:' in full_text and 'CBD:' in full_text:
                    thc_cbd_found.append(record['Ratio'])
                    print(f"⚠ Found THC/CBD content: {record['Ratio'][:20]}...")
                else:
                    print(f"✓ No THC/CBD content found (as expected for mini classic types)")
            
            print(f"\nSummary:")
            print(f"  - Weight units found: {len(weight_units_found)}/{len(test_records)}")
            print(f"  - THC/CBD content found: {len(thc_cbd_found)}/{len(test_records)}")
            
            if len(weight_units_found) == len(test_records) and len(thc_cbd_found) == 0:
                print(f"✓ SUCCESS: All weight units found, no THC/CBD content (as expected)")
            else:
                print(f"✗ ISSUE: Some weight units missing or unexpected THC/CBD content")
                
        else:
            print("✗ Failed to generate document")
            
    except Exception as e:
        print(f"✗ Error generating document: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    test_mini_template_generation() 