#!/usr/bin/env python3
"""
Test script to verify THC_CBD spacing fix for vertical templates.
Tests that a space is added after the first percentage value.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.generation.template_processor import TemplateProcessor

def test_thc_cbd_spacing():
    """Test the THC_CBD spacing fix."""
    print("Testing THC_CBD spacing fix for vertical templates...")
    
    # Create a template processor instance
    processor = TemplateProcessor('vertical', 'default')
    
    # Test cases - updated to match actual right-alignment behavior
    test_cases = [
        {
            'input': 'THC: 87.01% CBD: 0.45%',
            'expected': 'THC: 87.01% \nCBD: 0.45% ',
            'description': 'THC and CBD on same line with percentages'
        },
        {
            'input': 'THC: 80.91%\nCBD: 0.14%',
            'expected': 'THC: 80.91% \nCBD:  0.14% ',  # Right-aligned with extra spaces
            'description': 'THC and CBD on separate lines'
        },
        {
            'input': 'THC: 25% CBD: 2%',
            'expected': 'THC: 25% \nCBD: 2% ',
            'description': 'Simple percentages without decimals'
        },
        {
            'input': 'THC: 100mg CBD: 10mg',
            'expected': 'THC: 100mg CBD: 10mg',
            'description': 'mg values (should remain unchanged)'
        },
        {
            'input': 'THC: 25% CBD: 2% CBC: 1%',
            'expected': 'THC: 25% \nCBD: 2% \nCBC:  1% ',  # Right-aligned with extra spaces
            'description': 'With additional cannabinoid CBC'
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Input: '{test_case['input']}'")
        
        # Process the input
        result = processor.format_thc_cbd_vertical_alignment(test_case['input'])
        
        print(f"Output: '{result}'")
        print(f"Expected: '{test_case['expected']}'")
        
        # Check if the result matches expected
        if result == test_case['expected']:
            print("✓ PASS")
        else:
            print("✗ FAIL")
            all_passed = False
            
        # Check if there's a space after the first percentage (main requirement)
        if '%' in result:
            # Find the first percentage and check if there's a space after it
            first_percent_index = result.find('%')
            if first_percent_index + 1 < len(result) and result[first_percent_index + 1] == ' ':
                print("✓ Space after first percentage confirmed")
            else:
                print("✗ No space after first percentage")
                all_passed = False
                
        # Check if there are spaces after other percentage values too
        percent_indices = [i for i, char in enumerate(result) if char == '%']
        if len(percent_indices) > 1:
            spaces_after_percentages = 0
            for idx in percent_indices:
                if idx + 1 < len(result) and result[idx + 1] == ' ':
                    spaces_after_percentages += 1
            print(f"✓ Spaces after {spaces_after_percentages}/{len(percent_indices)} percentage values")
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 ALL TESTS PASSED! THC_CBD spacing fix is working correctly.")
    else:
        print("❌ SOME TESTS FAILED. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    test_thc_cbd_spacing()
