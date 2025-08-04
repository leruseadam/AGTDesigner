#!/usr/bin/env python3
"""
Simple test to save the generated document and examine the output.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_save_output():
    """Save the generated document to examine the output."""
    
    print("Saving Generated Document")
    print("=" * 30)
    
    # Test data
    test_records = [
        {
            'Product Name*': 'Test Product 1',
            'ProductBrand': 'Test Brand 1',
            'Product Brand': 'Test Brand 1',
            'Price': '$25.00',
            'Description': 'Test description 1',
            'Lineage': 'HYBRID',
            'THC_CBD': 'THC: 20% CBD: 2%',
            'WeightUnits': '3.5g',
            'ProductType': 'flower',
            'Product Strain': 'Test Strain 1'
        }
    ]
    
    try:
        print("\n1. Creating template processor...")
        double_processor = TemplateProcessor('double', {}, 1.0)
        
        print("\n2. Processing records...")
        result = double_processor.process_records(test_records)
        assert result is not None, "Template processing failed"
        
        print("\n3. Saving document...")
        output_path = "test_output_double_template.docx"
        result.save(output_path)
        print(f"   Document saved to: {output_path}")
        
        print("\n4. Examining first cell content...")
        table = result.tables[0]
        first_cell = table.cell(0, 0)
        
        print(f"   Cell text: '{first_cell.text}'")
        print(f"   Cell text length: {len(first_cell.text)}")
        
        # Split by lines
        lines = first_cell.text.split('\n')
        print(f"   Number of lines: {len(lines)}")
        for i, line in enumerate(lines):
            if line.strip():
                print(f"   Line {i}: '{line}'")
        
        print("\n5. Checking for brand content...")
        if 'Test Brand 1' in first_cell.text:
            print("   ✓ Brand content 'Test Brand 1' is present")
        else:
            print("   ❌ Brand content 'Test Brand 1' is missing")
        
        print("\n6. Summary...")
        print(f"   Document saved to: {output_path}")
        print("   Please open this file to see the actual output.")
        print("   The brand content should be visible in the document.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_save_output()
    sys.exit(0 if success else 1) 