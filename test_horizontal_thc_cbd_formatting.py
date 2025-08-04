#!/usr/bin/env python3
"""
Test script to verify horizontal template THC/CBD formatting keeps percentages on same line.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.text_processing import format_thc_cbd_bold_labels

def test_horizontal_formatting():
    """Test that horizontal template keeps THC/CBD on same line."""
    
    print("Testing horizontal template THC/CBD formatting...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        ("THC: 74.51% CBD: 0.15%", "horizontal"),
        ("THC: 80.28% CBD: 0.0%", "horizontal"),
        ("THC: 66.73% CBD: 0.17%", "horizontal"),
        ("THC:|BR|CBD:", "horizontal"),
        ("THC: 100mg CBD: 10mg", "horizontal"),
    ]
    
    for input_text, template_type in test_cases:
        result = format_thc_cbd_bold_labels(input_text, template_type)
        print(f"Input: {input_text}")
        print(f"Template: {template_type}")
        print(f"Output: {repr(result)}")
        print(f"Formatted: {result}")
        print("-" * 30)
    
    # Also test vertical template to ensure it still works correctly
    print("\nTesting vertical template formatting (should have line breaks)...")
    print("=" * 50)
    
    vertical_test = "THC: 74.51% CBD: 0.15%"
    vertical_result = format_thc_cbd_bold_labels(vertical_test, "vertical")
    print(f"Input: {vertical_test}")
    print(f"Template: vertical")
    print(f"Output: {repr(vertical_result)}")
    print(f"Formatted:\n{vertical_result}")

if __name__ == "__main__":
    test_horizontal_formatting() 