#!/usr/bin/env python3
"""
Simple test to verify ratio content bold formatting.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.generation.template_processor import TemplateProcessor

def test_simple_ratio_bold():
    """Simple test of ratio content bold formatting."""
    
    print("Testing simple ratio content bold formatting...")
    
    # Create test data with simple ratio format
    test_records = [
        {
            'Product Name*': 'Simple Test Product',
            'Product Type*': 'Edible',
            'Lineage': 'HYBRID',
            'Product Brand': 'TEST BRAND',
            'Vendor/Supplier*': 'TEST VENDOR',
            'Weight*': '1.0',
            'Weight Unit* (grams/gm or ounces/oz)': 'oz',
            'Price* (Tier Name for Bulk)': '$10',
            'Ratio': 'THC: 25%\nCBD: 2%',  # Use 'Ratio' field
            'Product Strain': 'Test Strain'
        }
    ]
    
    # Test mini template (which has ratio markers)
    template_type = 'mini'
    
    try:
        # Create template processor
        processor = TemplateProcessor(template_type, {}, scale_factor=1.0)
        
        # Process the test records
        doc = processor.process_records(test_records)
        
        if doc:
            # Save the document
            output_file = f'test_simple_ratio_bold_{template_type}.docx'
            doc.save(output_file)
            print(f"✅ Generated {output_file}")
            
            # Check if ratio content is present and bold
            ratio_found = False
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                text = run.text
                                # Check for ratio patterns
                                if any(pattern in text for pattern in [
                                    'THC: 25%', 'CBD: 2%', 'THC:', 'CBD:'
                                ]):
                                    ratio_found = True
                                    if run.font.bold:
                                        print(f"✅ Ratio content '{text}' is bold")
                                    else:
                                        print(f"❌ Ratio content '{text}' is NOT bold")
                                    
                                    # Check if this is multi-line content
                                    if '\n' in text:
                                        if run.font.bold:
                                            print(f"✅ MULTI-LINE RATIO: '{text[:30]}...' is bold")
                                        else:
                                            print(f"❌ MULTI-LINE ISSUE: '{text[:30]}...' is NOT bold")
            
            if not ratio_found:
                print("⚠️  No ratio content found in document")
                # Let's examine what content is actually in the document
                print("\nDocument content:")
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                if paragraph.text.strip():
                                    print(f"  '{paragraph.text}'")
                    
        else:
            print(f"❌ Failed to generate document for {template_type} template")
            
    except Exception as e:
        print(f"❌ Error testing {template_type} template: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nSimple test completed.")

if __name__ == "__main__":
    test_simple_ratio_bold() 