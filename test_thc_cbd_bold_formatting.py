#!/usr/bin/env python3
"""
Test script to verify the new THC/CBD bold formatting.
This tests the format_thc_cbd_bold_labels function and ensures it produces
the correct format with bold labels and indented values.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.text_processing import format_thc_cbd_bold_labels

def test_thc_cbd_bold_formatting():
    """Test the new THC/CBD bold formatting function."""
    
    test_cases = [
        {
            'input': 'THC: 74.51% CBD: 0.15%',
            'expected': 'THC:\n  74.51%\nCBD:\n  0.15%',
            'description': 'Standard THC/CBD with percentages'
        },
        {
            'input': 'THC: 66.73% CBD: 0.17%',
            'expected': 'THC:\n  66.73%\nCBD:\n  0.17%',
            'description': 'Another THC/CBD with percentages'
        },
        {
            'input': 'THC:|BR|CBD:',
            'expected': 'THC:\n   \nCBD:\n   ',
            'description': 'Default placeholder format'
        },
        {
            'input': 'THC: 25% CBD: 2%',
            'expected': 'THC:\n  25%\nCBD:\n  2%',
            'description': 'Simple percentages'
        },
        {
            'input': 'THC: 100mg CBD: 10mg',
            'expected': 'THC:\n  100mg\nCBD:\n  10mg',
            'description': 'mg values instead of percentages'
        }
    ]
    
    print("Testing THC/CBD Bold Formatting")
    print("=" * 50)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        input_text = test_case['input']
        expected = test_case['expected']
        description = test_case['description']
        
        result = format_thc_cbd_bold_labels(input_text)
        
        if result == expected:
            print(f"✓ Test {i}: {description}")
            print(f"  Input: '{input_text}'")
            print(f"  Output: '{result}'")
        else:
            print(f"✗ Test {i}: {description}")
            print(f"  Input: '{input_text}'")
            print(f"  Expected: '{expected}'")
            print(f"  Got: '{result}'")
            all_passed = False
        
        print()
    
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    
    return all_passed

if __name__ == "__main__":
    test_thc_cbd_bold_formatting() 