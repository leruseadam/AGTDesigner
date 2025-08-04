#!/usr/bin/env python3
"""
Debug script to test DocxTemplate rendering directly
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.generation.template_processor import TemplateProcessor
from src.core.constants import FONT_SCHEME_DOUBLE
from docxtpl import DocxTemplate
from io import BytesIO

def debug_rendering():
    """Debug the DocxTemplate rendering process."""
    print("Debugging DocxTemplate rendering...")
    
    try:
        # Create template processor for double template
        processor = TemplateProcessor('double', FONT_SCHEME_DOUBLE)
        
        # Force re-expand template
        processor.force_re_expand_template()
        
        # Get the expanded template buffer
        buffer = processor._expanded_template_buffer
        buffer.seek(0)
        
        # Create DocxTemplate
        doc = DocxTemplate(buffer)
        
        # Create test context
        context = {
            'Label1': {
                'ProductBrand': 'Test Brand',
                'DescAndWeight': 'Test Description - 3.5g',
                'Price': '$25.00',
                'Ratio_or_THC_CBD': 'THC: 22% CBD: 1%',
                'DOH': 'YES',
                'Lineage': '•  Sativa',
                'ProductStrain': 'Test Strain 1'
            }
        }
        
        # Fill empty labels
        for i in range(2, 13):
            context[f'Label{i}'] = {}
        
        print("Context for rendering:")
        print(f"  Label1.ProductBrand: {context['Label1']['ProductBrand']}")
        print(f"  Label1.Price: {context['Label1']['Price']}")
        
        # Try to render
        print("\nAttempting to render template...")
        try:
            doc.render(context)
            print("✅ Template rendered successfully!")
            
            # Get the rendered document
            rendered_doc = doc.get_docx()
            
            # Check the content
            print("\nChecking rendered content...")
            for table in rendered_doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        cell_text = cell.text.strip()
                        if cell_text:
                            print(f"  Cell content: {repr(cell_text)}")
                            
                            # Check if placeholders were replaced
                            if '{{Label' in cell_text:
                                print(f"    ❌ Still contains placeholders!")
                            else:
                                print(f"    ✅ Placeholders replaced!")
            
        except Exception as render_error:
            print(f"❌ Rendering failed: {render_error}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_rendering()
    sys.exit(0 if success else 1) 