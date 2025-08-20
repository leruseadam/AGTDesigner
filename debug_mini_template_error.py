#!/usr/bin/env python3
"""
Debug script to identify the issue with mini template generation.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_mini_template_methods():
    """Test each part of the mini template processing to identify the issue."""
    print("Testing mini template methods...")
    
    try:
        # Test 1: Import TemplateProcessor
        print("1. Testing import...")
        from core.generation.template_processor import TemplateProcessor
        print("   ✓ Import successful")
        
        # Test 2: Create processor
        print("2. Testing processor creation...")
        processor = TemplateProcessor(template_type='mini', font_scheme='Arial')
        print("   ✓ Processor created")
        
        # Test 3: Test template path
        print("3. Testing template path...")
        template_path = processor._get_template_path()
        print(f"   ✓ Template path: {template_path}")
        print(f"   ✓ Template exists: {template_path.exists()}")
        
        # Test 4: Test template expansion
        print("4. Testing template expansion...")
        expanded = processor._expand_template_if_needed()
        print("   ✓ Template expansion successful")
        
        # Test 5: Test mini template preserve design method
        print("5. Testing mini template preserve design method...")
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
        
        label_context = processor._build_label_context(test_record)
        context = {'Label1': label_context}
        
        result_doc = processor._expand_mini_template_preserve_design(None, context)
        print("   ✓ Mini template preserve design successful")
        
        print("\n🎉 All tests passed! Mini template processing is working.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mini_template_methods()
    sys.exit(0 if success else 1)
