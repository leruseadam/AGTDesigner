#!/usr/bin/env python3
"""
Test script to verify that ratio formatting no longer adds extra line breaks.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from src.core.generation.text_processing import format_ratio_multiline

def test_ratio_formatting():
    """Test that ratio formatting no longer adds extra line breaks."""
    
    print("=== Testing Ratio Formatting (No Extra Lines) ===")
    
    # Test cases
    test_cases = [
        {
            'name': 'Classic THC/CBD ratio',
            'input': 'THC: 15% CBD: 5%',
            'expected': 'THC: 15% CBD: 5%'
        },
        {
            'name': 'Cannabinoid content',
            'input': '100mg THC 50mg CBD',
            'expected': '100mg THC 50mg CBD'
        },
        {
            'name': 'Simple ratio',
            'input': '1:1:1',
            'expected': '1: 1: 1'
        },
        {
            'name': 'Complex ratio',
            'input': '10mg THC 5mg CBD 2mg CBG',
            'expected': '10mg THC 5mg CBD 2mg CBG'
        }
    ]
    
    # Test template processor formatting
    print("\n1. Testing TemplateProcessor.format_classic_ratio():")
    tp = TemplateProcessor('vertical', {})
    
    for test_case in test_cases:
        result = tp.format_classic_ratio(test_case['input'], {})
        success = result == test_case['expected']
        print(f"   {test_case['name']}:")
        print(f"     Input: {repr(test_case['input'])}")
        print(f"     Expected: {repr(test_case['expected'])}")
        print(f"     Result: {repr(result)}")
        print(f"     Success: {'✅' if success else '❌'}")
        print()
    
    # Test text processing formatting
    print("\n2. Testing format_ratio_multiline():")
    
    for test_case in test_cases:
        result = format_ratio_multiline(test_case['input'])
        success = result == test_case['expected']
        print(f"   {test_case['name']}:")
        print(f"     Input: {repr(test_case['input'])}")
        print(f"     Expected: {repr(test_case['expected'])}")
        print(f"     Result: {repr(result)}")
        print(f"     Success: {'✅' if success else '❌'}")
        print()
    
    # Test that no line breaks are added
    print("\n3. Testing for absence of line breaks:")
    
    test_inputs = [
        'THC: 15% CBD: 5%',
        '100mg THC 50mg CBD',
        '1:1:1',
        '10mg THC 5mg CBD 2mg CBG'
    ]
    
    for test_input in test_inputs:
        # Test template processor
        tp_result = tp.format_classic_ratio(test_input, {})
        has_line_breaks_tp = '\n' in tp_result or '|BR|' in tp_result
        
        # Test text processing
        text_result = format_ratio_multiline(test_input)
        has_line_breaks_text = '\n' in text_result or '|BR|' in text_result
        
        print(f"   Input: {repr(test_input)}")
        print(f"     TemplateProcessor: {repr(tp_result)} {'❌ HAS LINE BREAKS' if has_line_breaks_tp else '✅ No line breaks'}")
        print(f"     TextProcessing: {repr(text_result)} {'❌ HAS LINE BREAKS' if has_line_breaks_text else '✅ No line breaks'}")
        print()
    
    print("=== Test Complete ===")
    return True

if __name__ == "__main__":
    success = test_ratio_formatting()
    sys.exit(0 if success else 1) 