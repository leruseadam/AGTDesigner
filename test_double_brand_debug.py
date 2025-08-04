#!/usr/bin/env python3
"""
Test script to debug double template brand issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from src.core.constants import FONT_SCHEME_DOUBLE
from docx import Document
from io import BytesIO

def test_double_brand():
    """Test double template brand processing."""
    print("Testing Double Template Brand Processing")
    print("=" * 50)
    
    # Create test records with brand information
    test_records = [
        {
            'ProductName': 'Test Product 1',
            'ProductBrand': 'Test Brand 1',
            'Product Type*': 'concentrate',
            'Description': 'Test Description 1',
            'Price': '$25.00',
            'Lineage': 'SATIVA',
            'THC_CBD': 'THC: 20% CBD: 2%',
            'WeightUnits': '1g'
        },
        {
            'ProductName': 'Test Product 2',
            'ProductBrand': 'Test Brand 2',
            'Product Type*': 'edible (solid)',
            'Description': 'Test Description 2',
            'Price': '$30.00',
            'Lineage': 'HYBRID',
            'THC_CBD': 'THC: 15% CBD: 5%',
            'WeightUnits': '2g'
        }
    ]
    
    # Test double template
    processor = TemplateProcessor('double', FONT_SCHEME_DOUBLE)
    
    print("Processing test records...")
    result_doc = processor.process_records(test_records)
    
    if not result_doc:
        print("ERROR: Failed to process test records")
        return
    
    print(f"Document created successfully with {len(result_doc.tables)} tables")
    
    # Examine the document content
    for table_idx, table in enumerate(result_doc.tables):
        print(f"\nTable {table_idx + 1}:")
        for row_idx, row in enumerate(table.rows):
            for col_idx, cell in enumerate(row.cells):
                cell_text = cell.text.strip()
                if cell_text:
                    print(f"  Cell ({row_idx}, {col_idx}): '{cell_text}'")
                    
                    # Check for brand markers
                    if 'PRODUCTBRAND_CENTER_START' in cell_text:
                        print(f"    -> Contains PRODUCTBRAND_CENTER_START marker")
                    if 'PRODUCTBRAND_CENTER_END' in cell_text:
                        print(f"    -> Contains PRODUCTBRAND_CENTER_END marker")
                    
                    # Check for brand content
                    if 'Test Brand' in cell_text:
                        print(f"    -> Contains brand content: 'Test Brand'")
    
    # Save the document for inspection
    output_path = "test_double_brand_output.docx"
    result_doc.save(output_path)
    print(f"\nDocument saved to: {output_path}")

if __name__ == "__main__":
    test_double_brand() 