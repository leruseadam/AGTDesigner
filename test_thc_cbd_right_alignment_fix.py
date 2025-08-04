#!/usr/bin/env python3
"""
Test script to verify THC/CBD percentage right-alignment fix.
Tests that percentage values are properly right-aligned so the '%' symbols align vertically.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.generation.template_processor import TemplateProcessor

def test_thc_cbd_right_alignment():
    """Test the THC/CBD right-alignment formatting."""
    print("=== Testing THC/CBD Percentage Right-Alignment ===")
    
    # Create a template processor instance
    processor = TemplateProcessor('vertical', {}, 1.0)
    
    # Test cases with different percentage lengths
    test_cases = [
        # Same line format - both percentages have same length (4 chars: "21.0" and "0.25")
        {
            'input': 'THC: 21.0% CBD: 0.25%',
            'expected_alignment': 'THC: 21.0%\nCBD: 0.25%'  # No alignment needed - same length
        },
        # Different percentage lengths - "24.0" (4 chars) vs "0.0" (3 chars)
        {
            'input': 'THC: 24.0% CBD: 0.0%',
            'expected_alignment': 'THC: 24.0%\nCBD:  0.0%'  # CBD percentage should be right-aligned
        },
        # Same line format - both percentages have same length (4 chars: "25.0" and "0.25")
        {
            'input': 'THC: 25.0% CBD: 0.25%',
            'expected_alignment': 'THC: 25.0%\nCBD: 0.25%'  # No alignment needed - same length
        },
        
        # Different percentage lengths - "5.0" (3 chars) vs "15.0" (4 chars)
        {
            'input': 'THC: 5.0% CBD: 15.0%',
            'expected_alignment': 'THC:  5.0%\nCBD: 15.0%'  # THC percentage should be right-aligned
        },
        # Different percentage lengths - "100.0" (5 chars) vs "0.1" (2 chars)
        {
            'input': 'THC: 100.0% CBD: 0.1%',
            'expected_alignment': 'THC: 100.0%\nCBD:   0.1%'  # CBD percentage should be right-aligned
        },
        # Different percentage lengths - "0.1" (2 chars) vs "100.0" (5 chars)
        {
            'input': 'THC: 0.1% CBD: 100.0%',
            'expected_alignment': 'THC:   0.1%\nCBD: 100.0%'  # THC percentage should be right-aligned
        },
        
        # Mixed format with additional cannabinoids - "25.0" (4 chars) vs "2.0" (3 chars)
        {
            'input': 'THC: 25.0% CBD: 2.0% CBC: 1.0%',
            'expected_alignment': 'THC: 25.0%\nCBD:  2.0%\nCBC: 1.0%'  # Only THC/CBD should be right-aligned
        },
        
        # Edge cases - both percentages have same length (1 char: "0" and "0")
        {
            'input': 'THC: 0% CBD: 0%',
            'expected_alignment': 'THC: 0%\nCBD: 0%'  # No alignment needed - same length
        },
        # Edge cases - both percentages have same length (1 char: "1" and "1")
        {
            'input': 'THC: 1% CBD: 1%',
            'expected_alignment': 'THC: 1%\nCBD: 1%'  # No alignment needed - same length
        },
    ]
    
    print("\nTesting format_thc_cbd_vertical_alignment function:")
    print("-" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        input_text = test_case['input']
        expected = test_case['expected_alignment']
        
        try:
            result = processor.format_thc_cbd_vertical_alignment(input_text)
            
            print(f"Test {i}:")
            print(f"  Input: '{input_text}'")
            print(f"  Expected: '{expected}'")
            print(f"  Result: '{result}'")
            
            # Check if the result matches expected alignment
            if result == expected:
                print(f"  ✓ PASS: Right-alignment working correctly")
            else:
                print(f"  ✗ FAIL: Expected '{expected}', got '{result}'")
                
                # Show visual comparison
                print(f"  Expected alignment:")
                for line in expected.split('\n'):
                    print(f"    '{line}'")
                print(f"  Actual alignment:")
                for line in result.split('\n'):
                    print(f"    '{line}'")
            
            print()
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            print()
    
    # Test with actual data from the image
    print("\nTesting with actual data from the image:")
    print("-" * 80)
    
    image_data = [
        'THC: 21.0% CBD: 0.25%',
        'THC: 24.0% CBD: 0.0%',
        'THC: 25.0% CBD: 0.25%',
    ]
    
    for i, data in enumerate(image_data, 1):
        try:
            result = processor.format_thc_cbd_vertical_alignment(data)
            
            print(f"Image Data {i}:")
            print(f"  Original: '{data}'")
            print(f"  Formatted: '{result}'")
            
            # Show the alignment visually
            print(f"  Visual alignment:")
            for line in result.split('\n'):
                print(f"    '{line}'")
            
            print()
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            print()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_thc_cbd_right_alignment() 