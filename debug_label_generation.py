#!/usr/bin/env python3
"""
Debug script to test the actual label generation process and see what template is being used.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor, get_font_scheme

def debug_label_generation():
    """Debug the actual label generation process."""
    
    print("Debug Label Generation Process")
    print("=" * 50)
    
    # Test data similar to what you might have
    test_records = [
        {
            'ProductName': 'Grape Moonshot',
            'Description': 'Grape Moonshot',  # Add Description field
            'WeightUnits': '1.7oz',
            'Price': '$15',
            'DOH': '100mg THC',
            'ProductBrand': 'Test Brand',
            'ProductType': 'edible',
            'Lineage': 'HYBRID',
            'ProductStrain': 'Grape Moonshot'
        },
        {
            'ProductName': 'Tropical Punch Moonshot',
            'Description': 'Tropical Punch Moonshot',  # Add Description field
            'WeightUnits': '1.7oz',
            'Price': '$15',
            'DOH': '100mg THC',
            'ProductBrand': 'Test Brand',
            'ProductType': 'edible',
            'Lineage': 'HYBRID',
            'ProductStrain': 'Tropical Punch Moonshot'
        }
    ]
    
    # Test with mini template
    print("\n--- Testing MINI template label generation ---")
    
    try:
        font_scheme = get_font_scheme('mini')
        processor = TemplateProcessor('mini', font_scheme, 1.0)
        
        print(f"Template type: {processor.template_type}")
        print(f"Chunk size: {processor.chunk_size}")
        
        # Process the test records
        result = processor.process_records(test_records)
        
        if result:
            print(f"Generated document type: {type(result)}")
            
            # If it's a Document object, check its content
            if hasattr(result, 'tables') and result.tables:
                table = result.tables[0]
                print(f"Generated table dimensions: {len(table.rows)}x{len(table.columns)}")
                
                # Check first few cells
                for i in range(min(3, len(table.rows) * len(table.columns))):
                    row = i // len(table.columns)
                    col = i % len(table.columns)
                    cell = table.cell(row, col)
                    print(f"Cell {i+1} ({row+1},{col+1}): '{cell.text}'")
                    
                    # Check for template variables
                    if '{{Label' in cell.text:
                        print(f"  ⚠️  WARNING: Template variable found: {cell.text}")
                    elif cell.text.strip():
                        print(f"  ✅ Content: {cell.text}")
                    else:
                        print(f"  ⚪ Empty cell")
        else:
            print("No document generated")
            
    except Exception as e:
        print(f"Error with mini template: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_label_generation()
