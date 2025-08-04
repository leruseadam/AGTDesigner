#!/usr/bin/env python3
"""
Test script to verify that multi-line THC/CBD ratio values are properly bolded.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.generation.template_processor import TemplateProcessor
from src.core.data.excel_processor import ExcelProcessor

def test_multiline_ratio_bold_formatting():
    """Test that multi-line THC/CBD ratio values are properly bolded."""
    
    print("Testing multi-line ratio value bold formatting...")
    
    # Create test data with multi-line ratio formats
    test_records = [
        {
            'Product Name*': 'Multi-Line Test Product 1',
            'Product Type*': 'Edible',
            'Lineage': 'HYBRID',
            'Product Brand': 'CONSTELLATION CANNABIS',
            'Vendor/Supplier*': 'JOURNEYMAN',
            'Weight*': '1.7',
            'Weight Unit* (grams/gm or ounces/oz)': 'oz',
            'Price* (Tier Name for Bulk)': '$18',
            'Ratio': 'THC: 25%\nCBD: 2%',  # Multi-line format
            'Product Strain': 'Test Strain'
        },
        {
            'Product Name*': 'Multi-Line Test Product 2',
            'Product Type*': 'Edible',
            'Lineage': 'HYBRID',
            'Product Brand': 'CONSTELLATION CANNABIS',
            'Vendor/Supplier*': 'JOURNEYMAN',
            'Weight*': '0.07',
            'Weight Unit* (grams/gm or ounces/oz)': 'oz',
            'Price* (Tier Name for Bulk)': '$15',
            'Ratio': '100mg THC\n50mg CBD\n25mg CBC',  # Multi-line format
            'Product Strain': 'Test Strain 2'
        },
        {
            'Product Name*': 'Multi-Line Test Product 3',
            'Product Type*': 'Edible',
            'Lineage': 'HYBRID',
            'Product Brand': 'CONSTELLATION CANNABIS',
            'Vendor/Supplier*': 'JOURNEYMAN',
            'Weight*': '0.07',
            'Weight Unit* (grams/gm or ounces/oz)': 'oz',
            'Price* (Tier Name for Bulk)': '$15',
            'Ratio': 'THC: 100mg|BR|CBD: 50mg|BR|CBC: 25mg',  # BR marker format
            'Product Strain': 'Test Strain 3'
        }
    ]
    
    # Test all template types
    template_types = ['vertical', 'horizontal', 'mini', 'double']
    
    for template_type in template_types:
        print(f"\nTesting {template_type} template...")
        
        try:
            # Create template processor
            processor = TemplateProcessor(template_type, {}, scale_factor=1.0)
            
            # Process the test records
            doc = processor.process_records(test_records)
            
            if doc:
                # Save the document
                output_file = f'test_multiline_ratio_bold_{template_type}.docx'
                doc.save(output_file)
                print(f"✅ Generated {output_file}")
                
                # Check if multi-line ratio content is present and should be bold
                ratio_found = False
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                for run in paragraph.runs:
                                    text = run.text
                                    # Check for multi-line ratio patterns
                                    if any(pattern in text for pattern in [
                                        'THC: 25%', 'CBD: 2%', '100mg THC', '50mg CBD', '25mg CBC',
                                        'THC: 100mg', 'CBD: 50mg', 'CBC: 25mg'
                                    ]):
                                        ratio_found = True
                                        if run.font.bold:
                                            print(f"  ✅ Multi-line ratio content '{text}' is bold")
                                        else:
                                            print(f"  ❌ Multi-line ratio content '{text}' is NOT bold")
                                        
                                        # Also check if this is multi-line content
                                        if '\n' in text or '|BR|' in text:
                                            if run.font.bold:
                                                print(f"  ✅ MULTI-LINE FIX: '{text[:30]}...' is bold")
                                            else:
                                                print(f"  ❌ MULTI-LINE ISSUE: '{text[:30]}...' is NOT bold")
                
                if not ratio_found:
                    print("  ⚠️  No multi-line ratio content found in document")
                    
            else:
                print(f"❌ Failed to generate document for {template_type} template")
                
        except Exception as e:
            print(f"❌ Error testing {template_type} template: {e}")
    
    print("\nTest completed. Check the generated files to verify bold formatting.")

if __name__ == "__main__":
    test_multiline_ratio_bold_formatting() 