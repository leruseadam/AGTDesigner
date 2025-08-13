#!/usr/bin/env python3
"""
Debug script to check what's in the context for mini templates.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor, get_font_scheme

def debug_context_check():
    """Debug the context building for mini templates."""
    
    print("Debug Context Check for Mini Templates")
    print("=" * 50)
    
    # Test data
    test_records = [
        {
            'ProductName': 'Grape Moonshot',
            'WeightUnits': '1.7oz',
            'Price': '$15',
            'DOH': '100mg THC',
            'ProductBrand': 'Test Brand',
            'ProductType': 'edible',
            'Lineage': 'HYBRID',
            'ProductStrain': 'Grape Moonshot'
        }
    ]
    
    try:
        font_scheme = get_font_scheme('mini')
        processor = TemplateProcessor('mini', font_scheme, 1.0)
        
        print(f"Template type: {processor.template_type}")
        
        # Build context for the first record
        label_context = processor._build_label_context(test_records[0], None)
        
        print("\n=== Context for Label1 ===")
        for key, value in label_context.items():
            print(f"{key}: {repr(value)}")
        
        # Check if DOH field is present
        if 'DOH' in label_context:
            print(f"\n✅ DOH field found: {repr(label_context['DOH'])}")
        else:
            print("\n❌ DOH field NOT found")
        
        # Check if _DOH_IMAGE_PATH is present
        if '_DOH_IMAGE_PATH' in label_context:
            print(f"✅ _DOH_IMAGE_PATH found: {repr(label_context['_DOH_IMAGE_PATH'])}")
        else:
            print("❌ _DOH_IMAGE_PATH NOT found")
        
        # Create full context
        context = {}
        for i, record in enumerate(test_records):
            label_context = processor._build_label_context(record, None)
            context[f'Label{i+1}'] = label_context
        
        print(f"\n=== Full Context Keys ===")
        for label_key, label_context in context.items():
            print(f"{label_key}: {list(label_context.keys())}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_context_check()
