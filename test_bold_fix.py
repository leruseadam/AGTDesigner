#!/usr/bin/env python3
"""
Test script to verify that the bold formatting fix is working correctly for mini templates.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor, get_font_scheme

def test_bold_formatting():
    """Test that all text in mini templates gets bolded correctly."""
    
    print("Testing Bold Formatting Fix for Mini Templates")
    print("=" * 50)
    
    # Test data
    test_records = [
        {
            'ProductName': 'Test Product 1',
            'Description': 'Test Description 1',
            'WeightUnits': '1.5g',
            'Price': '$25.99',
            'DOH': '100mg THC',
            'ProductBrand': 'Test Brand 1',
            'ProductType': 'edible',
            'Lineage': 'HYBRID',
            'ProductStrain': 'Test Strain 1'
        },
        {
            'ProductName': 'Test Product 2',
            'Description': 'Test Description 2',
            'WeightUnits': '2.0g',
            'Price': '$30.99',
            'DOH': '150mg THC',
            'ProductBrand': 'Test Brand 2',
            'ProductType': 'concentrate',
            'Lineage': 'SATIVA',
            'ProductStrain': 'Test Strain 2'
        }
    ]
    
    try:
        font_scheme = get_font_scheme('mini')
        processor = TemplateProcessor('mini', font_scheme, 1.0)
        
        print(f"Template type: {processor.template_type}")
        
        # Process the records
        result_doc = processor.process_records(test_records)
        
        if result_doc and result_doc.tables:
            table = result_doc.tables[0]
            print(f"Generated table dimensions: {len(table.rows)}x{len(table.columns)}")
            
            # Check the first few cells for bold formatting
            cells_to_check = [
                (0, 0),  # First cell
                (0, 1),  # Second cell
                (1, 0),  # First cell of second row
            ]
            
            for row, col in cells_to_check:
                if row < len(table.rows) and col < len(table.rows[row].cells):
                    cell = table.rows[row].cells[col]
                    print(f"\n=== Cell ({row}, {col}) ===")
                    print(f"Cell text: '{cell.text[:100]}...'")
                    
                    # Check font formatting for all runs in all paragraphs
                    bold_count = 0
                    total_runs = 0
                    
                    for para_idx, paragraph in enumerate(cell.paragraphs):
                        print(f"  Paragraph {para_idx}: '{paragraph.text[:50]}...'")
                        for run_idx, run in enumerate(paragraph.runs):
                            total_runs += 1
                            is_bold = run.font.bold
                            font_name = run.font.name
                            font_size = run.font.size
                            
                            print(f"    Run {run_idx}: '{run.text[:30]}...' - Bold: {is_bold}, Font: {font_name}, Size: {font_size}")
                            
                            if is_bold:
                                bold_count += 1
                    
                    print(f"  Bold formatting: {bold_count}/{total_runs} runs are bold")
                    
                    if bold_count == total_runs and total_runs > 0:
                        print("  ✅ All text is properly bolded!")
                    elif total_runs > 0:
                        print(f"  ❌ {total_runs - bold_count} runs are not bolded")
                    else:
                        print("  ⚠️  No runs found in cell")
        else:
            print("❌ No document or tables generated")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bold_formatting()
