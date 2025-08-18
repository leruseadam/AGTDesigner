#!/usr/bin/env python3
"""
Debug script to see what's happening in template expansion.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
import re

def debug_expansion():
    """Debug the template expansion decision logic."""
    
    try:
        print("Debugging template expansion...")
        
        # Create processor
        processor = TemplateProcessor('horizontal', {}, 1.0)
        
        print(f"Template type: {processor.template_type}")
        print(f"Chunk size: {processor.chunk_size}")
        
        # Check the template path
        template_path = processor._get_template_path()
        print(f"Template path: {template_path}")
        
        # Read the template content
        with open(template_path, 'rb') as f:
            from io import BytesIO
            buffer = BytesIO(f.read())
        
        # Check if template needs expansion
        from docx import Document
        doc = Document(buffer)
        text = doc.element.body.xml
        
        print(f"\nTemplate XML length: {len(text)}")
        print(f"Template XML preview: {text[:500]}...")
        
        # Check for Label placeholders
        matches = re.findall(r'Label(\d+)\.', text)
        print(f"\nRegex matches: {matches}")
        
        # Get unique labels
        unique_labels = set(matches)
        print(f"Unique labels: {unique_labels}")
        print(f"Number of unique labels: {len(unique_labels)}")
        
        # Check required labels
        if processor.template_type == 'mini':
            required_labels = 20  # 4x5 grid
        elif processor.template_type == 'double':
            required_labels = 12  # 4x3 grid
        elif processor.template_type == 'inventory':
            required_labels = 4   # 2x2 grid
        else:
            required_labels = 9   # 3x3 grid
        
        print(f"Required labels for {processor.template_type}: {required_labels}")
        
        # Check expansion decision
        needs_expansion = len(unique_labels) < required_labels
        print(f"Needs expansion: {needs_expansion}")
        print(f"  {len(unique_labels)} < {required_labels} = {needs_expansion}")
        
        # Check if template should expand
        if processor.template_type == 'double':
            print("Double template: Always expand to 4x3 grid")
        elif needs_expansion:
            print(f"Template needs expansion: {len(unique_labels)} < {required_labels}")
            if processor.template_type == 'mini':
                print("  Should call: _expand_template_to_4x5_fixed_scaled()")
            elif processor.template_type == 'inventory':
                print("  Should call: _expand_template_to_2x2_inventory()")
            elif processor.template_type == 'double':
                print("  Should call: _expand_template_to_4x3_fixed_double()")
            else:
                print("  Should call: _expand_template_to_3x3_fixed()")
        else:
            print("Template does not need expansion")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in debug expansion: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_expansion()
