#!/usr/bin/env python3
"""
Test script to verify the mini template fix is working correctly.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.generation.template_processor import TemplateProcessor

def test_mini_template_processing():
    """Test that mini template processing works correctly."""
    print("Testing mini template processing...")
    
    try:
        # Create a template processor for mini template
        processor = TemplateProcessor(template_type='mini', font_scheme='Arial')
        print("✓ Template processor created successfully")
        
        # Test data
        test_record = {
            'ProductName': 'Test Product',
            'Product Type*': 'Flower',
            'Product Brand': 'Test Brand',
            'Description': 'Test Description',
            'Weight*': '3.5g',
            'Price': '$45.00',
            'Product Strain': 'Test Strain',
            'Lineage': 'Sativa',
            'DOH': 'Yes'
        }
        
        # Test building label context
        label_context = processor._build_label_context(test_record)
        print("✓ Label context built successfully")
        print(f"  - ProductBrand: {label_context.get('ProductBrand')}")
        print(f"  - DOH: {label_context.get('DOH')}")
        
        # Test mini template processing
        context = {'Label1': label_context}
        result_doc = processor._expand_mini_template_preserve_design(None, context)
        print("✓ Mini template processing completed successfully")
        
        # Check the result
        if result_doc and result_doc.tables:
            table = result_doc.tables[0]
            print(f"✓ Result document has {len(table.rows)}x{len(table.columns)} table")
            
            # Check first cell content
            first_cell = table.cell(0, 0)
            if first_cell.paragraphs:
                first_para = first_cell.paragraphs[0]
                print(f"✓ First cell has content: '{first_para.text[:50]}...'")
            else:
                print("⚠ First cell has no paragraphs")
        else:
            print("✗ Result document has no tables")
            return False
        
        print("\n🎉 Mini template fix test PASSED!")
        return True
        
    except Exception as e:
        print(f"✗ Error during mini template processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mini_template_processing()
    sys.exit(0 if success else 1)
