#!/usr/bin/env python3
"""
Test raw Jinja2 rendering for brand to see if the issue is in rendering or post-processing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from docx import Document
from docxtpl import DocxTemplate
from io import BytesIO

def test_raw_jinja2_brand():
    """Test raw Jinja2 rendering for brand."""
    
    print("Raw Jinja2 Brand Test")
    print("=" * 40)
    
    # Create a single test record
    test_record = {
        'Description': 'Raw Product',
        'Price': '$15',
        'Lineage': 'HYBRID',
        'Ratio_or_THC_CBD': 'THC: 22%',
        'ProductBrand': 'RAW_BRAND_TEST',
        'ProductStrain': 'Raw Strain',
        'ProductType': 'flower',
        'JointRatio': '3.5g'
    }
    
    # Initialize template processor
    processor = TemplateProcessor('double', 'standard', scale_factor=1.0)
    
    # Get the template buffer
    template_buffer = processor._expanded_template_buffer
    template_buffer.seek(0)
    
    # Create DocxTemplate and build context
    doc = DocxTemplate(template_buffer)
    context = {}
    for i in range(1, 13):  # Double template has 12 labels (4x3 grid)
        if i == 1:
            context[f'Label{i}'] = processor._build_label_context(test_record, doc)
        else:
            context[f'Label{i}'] = {}
    
    print("Context before rendering:")
    print(f"  ProductBrand: '{context['Label1'].get('ProductBrand', 'N/A')}'")
    print(f"  Description: '{context['Label1'].get('Description', 'N/A')}'")
    
    # Render the template
    doc.render(context)
    
    # Save the raw rendered document
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    rendered_doc = Document(buffer)
    
    # Save the result
    output_path = "test_raw_jinja2_brand_output.docx"
    rendered_doc.save(output_path)
    print(f"✅ Generated raw document: {output_path}")
    
    # Analyze the content
    print("\nRaw Jinja2 Document Analysis:")
    print("=" * 40)
    
    # Check all tables
    for table_idx, table in enumerate(rendered_doc.tables):
        print(f"\nTable {table_idx + 1}:")
        for row_idx, row in enumerate(table.rows):
            for col_idx, cell in enumerate(row.cells):
                cell_text = cell.text.strip()
                if cell_text:
                    print(f"\nCell ({row_idx},{col_idx}):")
                    
                    # Split by lines and analyze each paragraph
                    lines = cell_text.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip():
                            print(f"  Line {i+1}: '{line.strip()}'")
                            
                            # Check for brand content
                            if 'RAW_BRAND_TEST' in line:
                                print(f"    ✓ FOUND FULL BRAND at line {i+1}")
                            elif 'RAW_BRAND' in line:
                                print(f"    ⚠ FOUND PARTIAL BRAND at line {i+1}")
                            elif 'BRAND_TEST' in line:
                                print(f"    ⚠ FOUND PARTIAL BRAND at line {i+1}")
                            elif 'Raw Product' in line:
                                print(f"    ✓ FOUND DESCRIPTION at line {i+1}")

if __name__ == "__main__":
    test_raw_jinja2_brand() 