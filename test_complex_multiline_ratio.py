#!/usr/bin/env python3
"""
Test complex multi-line ratio content bold formatting.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.generation.template_processor import TemplateProcessor

def test_complex_multiline_ratio():
    """Test complex multi-line ratio content bold formatting."""
    
    print("Testing complex multi-line ratio content bold formatting...")
    
    # Create test data with complex multi-line ratio formats
    test_records = [
        {
            'Product Name*': 'Complex Multi-Line Test Product',
            'Product Type*': 'Edible',
            'Lineage': 'HYBRID',
            'Product Brand': 'TEST BRAND',
            'Vendor/Supplier*': 'TEST VENDOR',
            'Weight*': '1.0',
            'Weight Unit* (grams/gm or ounces/oz)': 'oz',
            'Price* (Tier Name for Bulk)': '$10',
            'Ratio': 'THC: 100mg\nCBD: 50mg\nCBC: 25mg\nCBG: 10mg',  # Complex multi-line
            'Product Strain': 'Test Strain'
        },
        {
            'Product Name*': 'BR Marker Test Product',
            'Product Type*': 'Edible',
            'Lineage': 'HYBRID',
            'Product Brand': 'TEST BRAND',
            'Vendor/Supplier*': 'TEST VENDOR',
            'Weight*': '1.0',
            'Weight Unit* (grams/gm or ounces/oz)': 'oz',
            'Price* (Tier Name for Bulk)': '$10',
            'Ratio': 'THC: 100mg|BR|CBD: 50mg|BR|CBC: 25mg',  # BR marker format
            'Product Strain': 'Test Strain 2'
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
            output_file = f'test_complex_multiline_ratio_{template_type}.docx'
            doc.save(output_file)
            print(f"✅ Generated {output_file}")
            
            # Check if complex multi-line ratio content is present and bold
            ratio_found = False
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                text = run.text
                                # Check for complex ratio patterns
                                if any(pattern in text for pattern in [
                                    'THC: 100mg', 'CBD: 50mg', 'CBC: 25mg', 'CBG: 10mg',
                                    'THC:', 'CBD:', 'CBC:', 'CBG:'
                                ]):
                                    ratio_found = True
                                    if run.font.bold:
                                        print(f"✅ Complex ratio content '{text}' is bold")
                                    else:
                                        print(f"❌ Complex ratio content '{text}' is NOT bold")
                                    
                                    # Check if this is multi-line content
                                    if '\n' in text:
                                        if run.font.bold:
                                            print(f"✅ COMPLEX MULTI-LINE RATIO: '{text[:50]}...' is bold")
                                        else:
                                            print(f"❌ COMPLEX MULTI-LINE ISSUE: '{text[:50]}...' is NOT bold")
            
            if not ratio_found:
                print("⚠️  No complex ratio content found in document")
                    
        else:
            print(f"❌ Failed to generate document for {template_type} template")
            
    except Exception as e:
        print(f"❌ Error testing {template_type} template: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nComplex multi-line test completed.")

if __name__ == "__main__":
    test_complex_multiline_ratio() 