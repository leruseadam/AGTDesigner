#!/usr/bin/env python3
"""
Debug brand context building in double template.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from docx import Document

def test_brand_context_debug():
    """Debug brand context building in double template."""
    
    print("Brand Context Debug Test")
    print("=" * 40)
    
    # Create test records with different brand names
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
    
    # Initialize template processor
    processor = TemplateProcessor('double', 'standard', scale_factor=1.0)
    
    # Debug context building for each record
    print("Context Building Debug:")
    print("=" * 40)
    
    for i, record in enumerate(test_records):
        print(f"\nRecord {i+1}:")
        print(f"  Input ProductBrand: '{record.get('ProductBrand', 'N/A')}'")
        
        # Build context for this record
        from docxtpl import DocxTemplate
        from io import BytesIO
        
        # Get the template buffer
        template_buffer = processor._expanded_template_buffer
        template_buffer.seek(0)
        doc = DocxTemplate(template_buffer)
        
        # Build context
        context = processor._build_label_context(record, doc)
        print(f"  Context ProductBrand: '{context.get('ProductBrand', 'N/A')}'")
        print(f"  Context Description: '{context.get('Description', 'N/A')}'")
        print(f"  Context DescAndWeight: '{context.get('DescAndWeight', 'N/A')}'")
    
    # Now process the records normally
    print("\nProcessing records...")
    result = processor.process_records(test_records)
    
    if result is None:
        print("❌ Failed to process records")
        return
    
    # Save the result
    output_path = "test_brand_context_debug_output.docx"
    result.save(output_path)
    print(f"✅ Generated document: {output_path}")
    
    # Analyze the content
    print("\nGenerated Document Analysis:")
    print("=" * 40)
    
    doc = Document(output_path)
    
    # Check all tables
    for table_idx, table in enumerate(doc.tables):
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
                            if 'BRAND_ONE' in line:
                                print(f"    ✓ FOUND BRAND_ONE at line {i+1}")
                            elif 'BRAND_TWO' in line:
                                print(f"    ✓ FOUND BRAND_TWO at line {i+1}")
                            elif 'Product 1' in line:
                                print(f"    ✓ FOUND PRODUCT_1 at line {i+1}")
                            elif 'Product 2' in line:
                                print(f"    ✓ FOUND PRODUCT_2 at line {i+1}")

if __name__ == "__main__":
    test_brand_context_debug() 