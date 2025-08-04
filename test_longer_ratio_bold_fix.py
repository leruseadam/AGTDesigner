#!/usr/bin/env python3
"""
Test script to verify that longer THC/CBD ratio values are properly bolded.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.generation.template_processor import TemplateProcessor
from src.core.data.excel_processor import ExcelProcessor

def test_longer_ratio_bold_formatting():
    """Test that longer THC/CBD ratio values are properly bolded."""
    
    print("Testing longer ratio value bold formatting...")
    
    # Create test data with longer ratio formats
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
            'Ratio': '50mg THC 50mg CBC 25mg CBG 10mg CBN',
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
            'Ratio': '100mg THC 50mg CBC 25mg CBG 15mg CBN 10mg THCV',
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
            'Ratio': '100mg THC 50mg CBN 30mg CBC 20mg CBG 15mg CBD 5mg THCV',
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
                output_file = f'test_longer_ratio_bold_{template_type}.docx'
                doc.save(output_file)
                print(f"✅ Generated {output_file}")
                
                # Check if longer ratio content is present and should be bold
                ratio_found = False
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                for run in paragraph.runs:
                                    text = run.text
                                    # Check for longer ratio patterns
                                    if any(pattern in text for pattern in [
                                        'mg THC', 'mg CBD', 'mg CBC', 'mg CBG', 'mg CBN', 'mg THCV',
                                        '50mg THC 50mg CBC 25mg CBG 10mg CBN',
                                        '100mg THC 50mg CBC 25mg CBG 15mg CBN 10mg THCV',
                                        '100mg THC 50mg CBN 30mg CBC 20mg CBG 15mg CBD 5mg THCV'
                                    ]):
                                        ratio_found = True
                                        if run.font.bold:
                                            print(f"  ✅ Longer ratio content '{text[:50]}...' is bold")
                                        else:
                                            print(f"  ❌ Longer ratio content '{text[:50]}...' is NOT bold")
                
                if not ratio_found:
                    print("  ⚠️  No longer ratio content found in document")
                    
            else:
                print(f"❌ Failed to generate document for {template_type} template")
                
        except Exception as e:
            print(f"❌ Error testing {template_type} template: {e}")
    
    print("\nTest completed. Check the generated files to verify bold formatting.")

if __name__ == "__main__":
    test_longer_ratio_bold_formatting() 