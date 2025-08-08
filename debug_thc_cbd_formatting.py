#!/usr/bin/env python3
"""
Debug script to see exactly what THC_CBD formatting is producing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor

def debug_thc_cbd_formatting():
    """Debug the THC_CBD formatting to see what's actually happening."""
    print("Debugging THC_CBD Formatting")
    print("=" * 40)
    
    # Create a template processor instance
    processor = TemplateProcessor('vertical', 'default', 1.0)
    
    # Test case that matches the image
    test_case = "THC: 74.51% CBD: 0.15%"
    print(f"Input: '{test_case}'")
    
    # Format the THC/CBD content
    formatted = processor.format_thc_cbd_vertical_alignment(test_case)
    
    print(f"\nFormatted output:")
    print(f"Raw: {repr(formatted)}")
    print(f"\nLines:")
    lines = formatted.split('\n')
    for i, line in enumerate(lines):
        if line.strip() == '':
            print(f"  Line {i}: [empty]")
        else:
            print(f"  Line {i}: '{line}'")
    
    # Also test the individual group formatting
    print(f"\nTesting individual group formatting:")
    
    thc_group = processor._format_thc_cbd_simple("THC: 74.51%", 5)
    print(f"THC group: {repr(thc_group)}")
    
    cbd_group = processor._format_thc_cbd_simple("CBD: 0.15%", 5)
    print(f"CBD group: {repr(cbd_group)}")

if __name__ == "__main__":
    debug_thc_cbd_formatting() 