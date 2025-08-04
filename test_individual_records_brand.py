#!/usr/bin/env python3
"""
Test individual record processing to see if the brand issue is with batch processing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from docx import Document

def test_individual_records_brand():
    """Test individual record processing to see if the brand issue is with batch processing."""
    
    print("Individual Records Brand Test")
    print("=" * 40)
    
    # Create test records
    test_records = [
        {
            'Description': 'Product 1',
            'Price': '$10',
            'Lineage': 'SATIVA',
            'Ratio_or_THC_CBD': 'THC: 20%',
            'ProductBrand': 'BRAND_ONE',
            'ProductStrain': 'Strain 1',
            'ProductType': 'flower',
            'JointRatio': '3.5g'
        },
        {
            'Description': 'Product 2',
            'Price': '$20',
            'Lineage': 'INDICA',
            'Ratio_or_THC_CBD': 'THC: 25%',
            'ProductBrand': 'BRAND_TWO',
            'ProductStrain': 'Strain 2',
            'ProductType': 'flower',
            'JointRatio': '1g'
        }
    ]
    
    # Process each record individually
    for i, record in enumerate(test_records):
        print(f"\n{'='*50}")
        print(f"Processing Record {i+1}: {record['ProductBrand']}")
        print(f"{'='*50}")
        
        # Initialize template processor for each record
        processor = TemplateProcessor('double', 'standard', scale_factor=1.0)
        
        # Process the single record
        result = processor.process_records([record])
        
        if result is None:
            print(f"❌ Failed to process record {i+1}")
            continue
        
        # Save the result
        output_path = f"test_individual_record_{i+1}_output.docx"
        result.save(output_path)
        print(f"✅ Generated document: {output_path}")
        
        # Analyze the content
        print(f"\nRecord {i+1} Analysis:")
        doc = Document(output_path)
        
        # Check all tables
        for table_idx, table in enumerate(doc.tables):
            for row_idx, row in enumerate(table.rows):
                for col_idx, cell in enumerate(row.cells):
                    cell_text = cell.text.strip()
                    if cell_text:
                        lines = cell_text.split('\n')
                        for line_idx, line in enumerate(lines):
                            if line.strip():
                                if record['ProductBrand'] in line:
                                    print(f"  Line {line_idx+1}: '{line.strip()}' ✓ CORRECT BRAND")
                                elif 'BRAND_ONE' in line and record['ProductBrand'] != 'BRAND_ONE':
                                    print(f"  Line {line_idx+1}: '{line.strip()}' ❌ WRONG BRAND (showing BRAND_ONE)")
                                elif 'BRAND_TWO' in line and record['ProductBrand'] != 'BRAND_TWO':
                                    print(f"  Line {line_idx+1}: '{line.strip()}' ❌ WRONG BRAND (showing BRAND_TWO)")

if __name__ == "__main__":
    test_individual_records_brand() 