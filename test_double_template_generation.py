#!/usr/bin/env python3
"""
Test script to generate a double template and see what font size is actually being used.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def test_double_template_generation():
    """Test double template generation to see actual font sizes."""
    print("Testing Double Template Generation")
    print("=" * 40)
    
    # Create a template processor for double template
    processor = TemplateProcessor('double', 'default', 1.0)
    
    # Test data
    test_data = {
        'Ratio_or_THC_CBD': 'THC: 21.5% CBD: 0.25%',
        'ProductBrand': 'Test Brand Name',
        'Price': '$25.00',
        'Description': 'Test Description',
        'Lineage': 'HYBRID',
        'Ratio': '1:1',
        'ProductVendor': 'Test Vendor'
    }
    
    print("Test data:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    print("\nGenerating template...")
    
    try:
        # Generate the template
        result = processor.process_records([test_data])
        
        print("Template generation completed successfully!")
        print(f"Result type: {type(result)}")
        
        # Check if we can access the document
        if hasattr(result, 'paragraphs'):
            print(f"Document has {len(result.paragraphs)} paragraphs")
        
        if hasattr(result, 'tables'):
            print(f"Document has {len(result.tables)} tables")
            
            # Look for THC_CBD content in tables and check font sizes
            for table_idx, table in enumerate(result.tables):
                print(f"\nTable {table_idx}:")
                for row_idx, row in enumerate(table.rows):
                    for cell_idx, cell in enumerate(row.cells):
                        if cell.text and ('THC' in cell.text or 'CBD' in cell.text):
                            print(f"  Cell [{row_idx},{cell_idx}]: '{cell.text}'")
                            for paragraph in cell.paragraphs:
                                for run in paragraph.runs:
                                    if run.text and ('THC' in run.text or 'CBD' in run.text):
                                        font_size = run.font.size.pt if run.font.size else "No font size"
                                        print(f"    Run: '{run.text}' - Font size: {font_size}pt")
        
    except Exception as e:
        print(f"Error generating template: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_double_template_generation() 