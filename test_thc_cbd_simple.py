#!/usr/bin/env python3
"""
Simple test to verify THC_CBD formatting function.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor

def test_simple():
    processor = TemplateProcessor('vertical', {}, 1.0)
    
    # Test the function
    result = processor.format_thc_cbd_vertical_alignment('THC: 87.01% CBD: 0.45%')
    
    print(f"Input: 'THC: 87.01% CBD: 0.45%'")
    print(f"Output: '{result}'")
    contains_tabs = '\t' in result
    contains_newlines = '\n' in result
    print(f"Contains tabs: {contains_tabs}")
    print(f"Contains newlines: {contains_newlines}")
    
    # Check if it contains the expected elements
    has_thc_spaces = 'THC:   ' in result
    has_cbd_spaces = 'CBD:   ' in result
    has_newline = '\n' in result
    
    print(f"Has THC spaces: {has_thc_spaces}")
    print(f"Has CBD spaces: {has_cbd_spaces}")
    print(f"Has newline: {has_newline}")
    
    if has_thc_spaces and has_cbd_spaces and has_newline:
        print("✓ Function is working correctly!")
        return True
    else:
        print("✗ Function is not working correctly!")
        return False

if __name__ == "__main__":
    test_simple() 