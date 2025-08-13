#!/usr/bin/env python3
"""
Debug script to examine the expanded template after expansion to see what placeholders it contains.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
from docx import Document

def debug_expanded_template():
    """Debug the expanded template after expansion to see what placeholders it contains."""
    
    print("Debug Expanded Template After Expansion")
    print("=" * 50)
    
    try:
        font_scheme = get_font_scheme('mini')
        processor = TemplateProcessor('mini', font_scheme, 1.0)
        
        print(f"Template type: {processor.template_type}")
        
        # The template should already be expanded from initialization
        # Just check the current expanded template buffer
        
        # Check the expanded template buffer
        if hasattr(processor, '_expanded_template_buffer'):
            processor._expanded_template_buffer.seek(0)
            doc = Document(processor._expanded_template_buffer)
            
            if doc.tables:
                table = doc.tables[0]
                print(f"Expanded template table dimensions: {len(table.rows)}x{len(table.columns)}")
                
                # Check a few cells to see what placeholders they contain
                cells_to_check = [
                    (0, 0),  # First cell
                    (0, 1),  # Second cell
                    (1, 0),  # First cell of second row
                    (2, 0),  # First cell of third row
                ]
                
                for row, col in cells_to_check:
                    if row < len(table.rows) and col < len(table.rows[row].cells):
                        cell = table.rows[row].cells[col]
                        print(f"\n=== Cell ({row}, {col}) ===")
                        print(f"Cell text: '{cell.text}'")
                        
                        # Check for template variables
                        if '{{Label' in cell.text:
                            print("✅ Template variables found")
                            # Extract all template variables
                            import re
                            variables = re.findall(r'\{\{Label(\d+)\.(\w+)\}\}', cell.text)
                            print(f"Template variables: {variables}")
                        else:
                            print("❌ No template variables found")
                            
                        # Check paragraph structure
                        print(f"Paragraphs in cell: {len(cell.paragraphs)}")
                        for i, para in enumerate(cell.paragraphs):
                            if para.text.strip():  # Only show non-empty paragraphs
                                print(f"  Paragraph {i}: '{para.text}'")
                                print(f"    Runs in paragraph {i}: {len(para.runs)}")
                                for j, run in enumerate(para.runs):
                                    print(f"      Run {j}: '{run.text}'")
            else:
                print("❌ No tables found in expanded template")
        else:
            print("❌ No expanded template buffer found")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_expanded_template() 