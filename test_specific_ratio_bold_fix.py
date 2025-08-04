#!/usr/bin/env python3
"""
Test script to specifically verify that "50mg THC 50mg CBC" content is properly bolded.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.generation.template_processor import TemplateProcessor
from src.core.data.excel_processor import ExcelProcessor

def test_specific_ratio_bold_formatting():
    """Test that specific ratio values like '50mg THC 50mg CBC' are properly bolded."""
    
    print("Testing specific ratio value bold formatting...")
    
    # Create test data with the specific ratio format from the image
    test_records = [
        {
            'Product Name*': '1:1 Tropical Punch Moonshot',
            'Product Type*': 'Edible',
            'Lineage': 'HYBRID',
            'Product Brand': 'CONSTELLATION CANNABIS',
            'Vendor/Supplier*': 'JOURNEYMAN',
            'Weight*': '1.7',
            'Weight Unit* (grams/gm or ounces/oz)': 'oz',
            'Price* (Tier Name for Bulk)': '$18',
            'Ratio': '50mg THC 50mg CBC',  # This is the specific format from the image
            'Product Strain': 'Tropical Punch'
        },
        {
            'Product Name*': 'Peach Mango Moonshot',
            'Product Type*': 'Edible',
            'Lineage': 'HYBRID',
            'Product Brand': 'CONSTELLATION CANNABIS',
            'Vendor/Supplier*': 'JOURNEYMAN',
            'Weight*': '0.06',
            'Weight Unit* (grams/gm or ounces/oz)': 'oz',
            'Price* (Tier Name for Bulk)': '$15',
            'Ratio': '100mg THC',  # This should be bolded
            'Product Strain': 'Peach Mango'
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
                output_file = f'test_specific_ratio_bold_{template_type}.docx'
                doc.save(output_file)
                print(f"✅ Generated {output_file}")
                
                # Check if specific ratio content is present and should be bold
                ratio_found = False
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                for run in paragraph.runs:
                                    text = run.text
                                    # Check for the specific ratio patterns from the image
                                    if any(pattern in text for pattern in [
                                        '50mg THC 50mg CBC',  # The specific problematic content
                                        '100mg THC',  # The working content
                                        'mg THC', 'mg CBC', 'mg CBD'
                                    ]):
                                        ratio_found = True
                                        if run.font.bold:
                                            print(f"  ✅ Ratio content '{text}' is bold")
                                        else:
                                            print(f"  ❌ Ratio content '{text}' is NOT bold")
                                        
                                        # Also check if this is the specific problematic content
                                        if '50mg THC 50mg CBC' in text:
                                            if run.font.bold:
                                                print(f"  ✅ SPECIFIC FIX: '50mg THC 50mg CBC' is now bold!")
                                            else:
                                                print(f"  ❌ SPECIFIC ISSUE: '50mg THC 50mg CBC' is still not bold!")
                
                if not ratio_found:
                    print("  ⚠️  No specific ratio content found in document")
                    
            else:
                print(f"❌ Failed to generate document for {template_type} template")
                
        except Exception as e:
            print(f"❌ Error testing {template_type} template: {e}")
    
    print("\nTest completed. Check the generated files to verify bold formatting.")

if __name__ == "__main__":
    test_specific_ratio_bold_formatting() 