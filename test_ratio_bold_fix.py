#!/usr/bin/env python3
"""
Test script to verify that ratio values and cannabinoid content are properly bolded.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.generation.template_processor import TemplateProcessor
from src.core.data.excel_processor import ExcelProcessor

def test_ratio_bold_formatting():
    """Test that ratio values and cannabinoid content are properly bolded."""
    
    print("Testing ratio value bold formatting...")
    
    # Create test data with various ratio formats
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
            'Ratio': '50mg THC 50mg CBC',
            'Product Strain': 'Tropical Punch'
        },
        {
            'Product Name*': '2:1 CBC Watermelon Lemonade Shot',
            'Product Type*': 'Edible',
            'Lineage': 'HYBRID',
            'Product Brand': 'CONSTELLATION CANNABIS',
            'Vendor/Supplier*': 'JOURNEYMAN',
            'Weight*': '0.07',
            'Weight Unit* (grams/gm or ounces/oz)': 'oz',
            'Price* (Tier Name for Bulk)': '$15',
            'Ratio': '100mg THC 50mg CBC',
            'Product Strain': 'Watermelon Lemonade'
        },
        {
            'Product Name*': '2:1 CBN Blueberry Lemonade Shot',
            'Product Type*': 'Edible',
            'Lineage': 'HYBRID',
            'Product Brand': 'CONSTELLATION CANNABIS',
            'Vendor/Supplier*': 'JOURNEYMAN',
            'Weight*': '0.07',
            'Weight Unit* (grams/gm or ounces/oz)': 'oz',
            'Price* (Tier Name for Bulk)': '$15',
            'Ratio': '100mg THC 50mg CBN',
            'Product Strain': 'Blueberry Lemonade'
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
                output_file = f'test_ratio_bold_{template_type}.docx'
                doc.save(output_file)
                print(f"✅ Generated {output_file}")
                
                # Check if ratio content is present and should be bold
                ratio_found = False
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                for run in paragraph.runs:
                                    text = run.text
                                    # Check for ratio patterns
                                    if any(pattern in text for pattern in [
                                        'mg THC', 'mg CBD', 'mg CBC', 'mg CBN',
                                        '1:1', '2:1', '3:1',
                                        'THC:', 'CBD:', 'CBC:', 'CBN:'
                                    ]):
                                        ratio_found = True
                                        if run.font.bold:
                                            print(f"  ✅ Ratio content '{text}' is bold")
                                        else:
                                            print(f"  ❌ Ratio content '{text}' is NOT bold")
                
                if not ratio_found:
                    print("  ⚠️  No ratio content found in document")
                    
            else:
                print(f"❌ Failed to generate document for {template_type} template")
                
        except Exception as e:
            print(f"❌ Error testing {template_type} template: {e}")
    
    print("\nTest completed. Check the generated files to verify bold formatting.")

if __name__ == "__main__":
    test_ratio_bold_formatting() 