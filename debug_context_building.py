#!/usr/bin/env python3
"""
Debug script to examine the context building process for template processing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

from src.core.generation.template_processor import TemplateProcessor

def debug_context_building():
    """Debug the context building process."""
    
    print("Debugging Context Building Process")
    print("=" * 50)
    
    # Test data with ProductBrand
    test_record = {
        'ProductStrain': 'Test Strain Product',
        'ProductBrand': 'Test Brand Name',
        'Lineage': 'HYBRID',
        'Price': '$25.00',
        'Description': 'Test description',
        'Ratio_or_THC_CBD': 'THC: 20% CBD: 5%',
        'ProductType': 'FLOWER'  # Add ProductType to see if it affects lineage
    }
    
    print("Test Record:")
    for key, value in test_record.items():
        print(f"  {key}: {repr(value)}")
    
    print("\nCreating TemplateProcessor...")
    processor = TemplateProcessor('double', 'default', 1.0)
    
    print("\nBuilding context manually...")
    
    # Let's examine the context building step by step
    try:
        # Process the record
        result = processor.process_records([test_record])
        print("✅ Document generated successfully!")
        
        # Now let's examine what context was actually built
        print("\n=== CONTEXT ANALYSIS ===")
        
        # Check the generated document content
        for table in result.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if paragraph.text.strip():
                            print(f"\nParagraph: {repr(paragraph.text)}")
                            for run in paragraph.runs:
                                if run.text.strip():
                                    font_size_pt = run.font.size.pt if run.font.size else 'No font size'
                                    print(f"  Run: {repr(run.text)} - Font: {font_size_pt}pt")
                                    
                                    # Identify what each piece of content represents
                                    if 'Test Strain Product' in run.text:
                                        print(f"    -> ProductStrain content")
                                    elif 'Test Brand Name' in run.text:
                                        print(f"    -> ProductBrand_Center content")
                                    elif 'HYBRID' in run.text:
                                        print(f"    -> Lineage content")
                                    elif '$25.00' in run.text:
                                        print(f"    -> Price content")
                                    elif 'Test description' in run.text:
                                        print(f"    -> Description content")
                                    elif 'THC:' in run.text or '20%' in run.text or 'CBD:' in run.text or '5%' in run.text:
                                        print(f"    -> THC_CBD content")
                                    else:
                                        print(f"    -> Unknown content")
        
        print("\n=== MISSING FIELDS ANALYSIS ===")
        print("Looking for expected fields in output...")
        
        # Check what we got vs what we expected
        expected_fields = ['Lineage', 'ProductStrain', 'Price', 'Description', 'THC_CBD', 'ProductBrand_Center']
        found_fields = []
        
        for table in result.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if paragraph.text.strip():
                            for run in paragraph.runs:
                                if run.text.strip():
                                    if 'Test Strain Product' in run.text:
                                        found_fields.append('ProductStrain')
                                    elif 'Test Brand Name' in run.text:
                                        found_fields.append('ProductBrand_Center')
                                    elif 'HYBRID' in run.text:
                                        found_fields.append('Lineage')
                                    elif '$25.00' in run.text:
                                        found_fields.append('Price')
                                    elif 'Test description' in run.text:
                                        found_fields.append('Description')
                                    elif 'THC:' in run.text or '20%' in run.text or 'CBD:' in run.text or '5%' in run.text:
                                        found_fields.append('THC_CBD')
        
        print(f"Expected fields: {expected_fields}")
        print(f"Found fields: {found_fields}")
        
        missing_fields = [field for field in expected_fields if field not in found_fields]
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        else:
            print("✅ All expected fields found!")
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_context_building() 