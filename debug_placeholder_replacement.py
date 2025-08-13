#!/usr/bin/env python3
"""
Debug script to test the manual placeholder replacement method directly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
import re

def debug_placeholder_replacement():
    """Debug the manual placeholder replacement method."""
    
    print("Debug Placeholder Replacement")
    print("=" * 50)
    
    # Test data
    test_records = [
        {
            'ProductName': 'Grape Moonshot',
            'Description': 'Grape Moonshot',
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
        
        # Create full context
        context = {}
        for i, record in enumerate(test_records):
            label_context = processor._build_label_context(record, None)
            context[f'Label{i+1}'] = label_context
        
        print(f"\n=== Full Context ===")
        for label_key, label_context in context.items():
            print(f"{label_key}: {list(label_context.keys())}")
        
        # Test the regex pattern
        test_text = "{{Label1.DOH }}"
        print(f"\n=== Testing Regex Pattern ===")
        print(f"Test text: {repr(test_text)}")
        
        # Test the exact pattern from the code
        pattern = r'\{\{Label(\d+)\.DOH\s*\}\}'
        matches = re.findall(pattern, test_text)
        print(f"Pattern: {pattern}")
        print(f"Matches: {matches}")
        
        # Test manual replacement
        print(f"\n=== Testing Manual Replacement ===")
        
        # Load the expanded template
        processor.force_re_expand_template()
        processor._expanded_template_buffer.seek(0)
        from docx import Document
        doc = Document(processor._expanded_template_buffer)
        
        # Check first cell before replacement
        first_cell = doc.tables[0].cell(0, 0)
        print(f"First cell before replacement: {repr(first_cell.text)}")
        
        # Apply manual replacement
        doc = processor._manual_replace_placeholders(doc, context)
        
        # Check first cell after replacement
        first_cell = doc.tables[0].cell(0, 0)
        print(f"First cell after replacement: {repr(first_cell.text)}")
        
        # Check if DOH placeholder was replaced
        if '{{Label1.DOH' in first_cell.text:
            print("❌ DOH placeholder still present")
        else:
            print("✅ DOH placeholder replaced")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_placeholder_replacement()
