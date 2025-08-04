#!/usr/bin/env python3
"""
Test single record brand processing in double template.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from docx import Document

def test_single_record_brand():
    """Test single record brand processing in double template."""
    
    print("Single Record Brand Test")
    print("=" * 40)
    
    # Create a single test record
    test_record = {
        'Description': 'Single Product',
        'Price': '$15',
        'Lineage': 'HYBRID',
        'Ratio_or_THC_CBD': 'THC: 22%',
        'ProductBrand': 'SINGLE_BRAND_TEST',
        'ProductStrain': 'Single Strain',
        'ProductType': 'flower',
        'JointRatio': '3.5g'
    }
    
    # Initialize template processor
    processor = TemplateProcessor('double', 'standard', scale_factor=1.0)
    
    # Process the single record
    print("Processing single record...")
    result = processor.process_records([test_record])
    
    if result is None:
        print("❌ Failed to process record")
        return
    
    # Save the result
    output_path = "test_single_record_brand_output.docx"
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
                            if 'SINGLE_BRAND_TEST' in line:
                                print(f"    ✓ FOUND FULL BRAND at line {i+1}")
                            elif 'SINGLE_BRAND' in line:
                                print(f"    ⚠ FOUND PARTIAL BRAND at line {i+1}")
                            elif 'BRAND_TEST' in line:
                                print(f"    ⚠ FOUND PARTIAL BRAND at line {i+1}")
                            elif 'Single Product' in line:
                                print(f"    ✓ FOUND DESCRIPTION at line {i+1}")

if __name__ == "__main__":
    test_single_record_brand() 