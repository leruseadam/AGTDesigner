#!/usr/bin/env python3
"""
Test script to verify the mini template generation fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_mini_template_fix():
    """Test that the mini template can be processed without the Label100 error."""
    
    # Create a test record
    test_record = {
        'ProductName': 'Test Product',
        'ProductBrand': 'Test Brand',
        'ProductStrain': 'Test Strain',
        'ProductVendor': 'Test Vendor',
        'Price': '$20',
        'THC': '15.02%',
        'CBD': '0.04%',
        'ProductType': 'flower',
        'Description': 'Test Description',
        'WeightUnits': '1g'
    }
    
    try:
        # Create template processor for mini template
        from src.core.generation.template_processor import get_font_scheme
        font_scheme = get_font_scheme('mini')
        processor = TemplateProcessor('mini', font_scheme)
        print(f"✓ Template processor created successfully")
        print(f"✓ Template type: {processor.template_type}")
        print(f"✓ Chunk size: {processor.chunk_size}")
        
        # Test processing a single record
        result = processor.process_records([test_record])
        
        if result:
            print("✓ Mini template processing completed successfully")
            print(f"✓ Generated document has {len(result.tables)} tables")
            return True
        else:
            print("✗ Mini template processing failed")
            return False
            
    except Exception as e:
        print(f"✗ Error during mini template processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing mini template generation fix...")
    success = test_mini_template_fix()
    
    if success:
        print("\n🎉 Mini template fix test PASSED!")
    else:
        print("\n❌ Mini template fix test FAILED!")
        sys.exit(1)
