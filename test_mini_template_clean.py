#!/usr/bin/env python3
"""
Clean test script to verify mini template fix with fresh initialization.
This tests that the mini template uses its original structure without any corruption.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.generation.template_processor import TemplateProcessor
from docx import Document
import tempfile

def test_mini_template_clean():
    """Test mini template processing with fresh initialization."""
    print("Testing mini template processing with clean initialization...")
    
    try:
        # Force a completely fresh template processor
        processor = TemplateProcessor('mini', 'Arial')
        
        # Force re-initialization to clear any cached templates
        processor.force_re_expand_template()
        
        # Create test context with 2 labels
        context = {}
        for i in range(1, 3):
            context[f'Label{i}'] = {
                'ProductStrain': f'Test Strain {i}',
                'ProductBrand': f'Test Brand {i}',
                'VendorInfo': f'Test Vendor {i}',
                'Price': f'${i * 10}.00',
                'Ratio_or_THC_CBD': f'THC: {20 + i}% CBD: {i * 0.1}%',
                'Lineage': f'Test Lineage {i}'
            }
        
        # Add empty contexts for remaining labels
        for i in range(3, 21):
            context[f'Label{i}'] = {}
        
        print(f"Created context with {len(context)} labels")
        
        # Process the mini template
        result_doc = processor._expand_mini_template_preserve_design(None, context)
        
        # Save result
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            result_doc.save(tmp_file.name)
            print(f"Saved result to: {tmp_file.name}")
        
        # Verify the result
        if result_doc.tables:
            table = result_doc.tables[0]
            print(f"Result table: {len(table.rows)} rows x {len(table.columns)} columns")
            
            # Check first few cells
            for i in range(min(5, len(table.rows) * len(table.columns))):
                row = i // len(table.columns)
                col = i % len(table.columns)
                cell = table.cell(row, col)
                cell_text = cell.text.strip()
                
                print(f"\nCell {i+1}:")
                print(f"  Text: {cell_text[:100]}...")
                
                if i < 2:  # First two cells should have data
                    if "Test Strain" in cell_text and "Test Brand" in cell_text:
                        print("  ✅ Placeholders replaced with data")
                    else:
                        print("  ❌ Placeholders NOT replaced!")
                else:  # Other cells should have placeholders
                    if "{{Label" in cell_text:
                        print("  ⚠️  STILL HAS PLACEHOLDERS!")
                    else:
                        print("  ❌ Unexpected content!")
        else:
            print("❌ No tables found in result!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\nMini template clean test completed!")
    return True

if __name__ == "__main__":
    test_mini_template_clean()
