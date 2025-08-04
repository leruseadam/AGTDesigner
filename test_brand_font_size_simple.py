#!/usr/bin/env python3
"""
Simple test to verify that product brands with more than 20 letters get forced to font size 14 in horizontal templates.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.generation.font_sizing import get_thresholded_font_size

def test_brand_font_size_simple():
    """Simple test of brand font sizing."""
    
    print("=== Simple Brand Font Size Test ===\n")
    
    # Test cases
    test_cases = [
        ("Short", 5, "Should be 16pt (normal sizing)"),
        ("Medium Brand", 12, "Should be 14pt (multi-word rule)"),
        ("Very Long Brand Name That Exceeds Twenty Letters", 42, "Should be 14pt (>20 letters rule)"),
        ("Exactly Twenty Letters Here", 25, "Should be 14pt (>20 letters rule)"),
        ("Twenty One Letters Here!", 21, "Should be 14pt (>20 letters rule)"),
    ]
    
    print("Testing horizontal template brand font sizing:")
    print("-" * 60)
    
    all_passed = True
    
    for brand_name, letter_count, description in test_cases:
        font_size = get_thresholded_font_size(brand_name, orientation='horizontal', field_type='brand')
        
        print(f"Brand: '{brand_name}'")
        print(f"  Letters: {letter_count}")
        print(f"  Font size: {font_size.pt}pt")
        print(f"  Description: {description}")
        
        # Check if the rule is working correctly
        if letter_count > 20:
            if font_size.pt == 14:
                print(f"  Status: ✅ PASS (>20 letters → 14pt)")
            else:
                print(f"  Status: ❌ FAIL (got {font_size.pt}pt, expected 14pt)")
                all_passed = False
        elif len(brand_name.split()) > 1 and len(brand_name) > 9:
            if font_size.pt == 14:
                print(f"  Status: ✅ PASS (multi-word rule)")
            else:
                print(f"  Status: ❌ FAIL (got {font_size.pt}pt, expected 14pt)")
                all_passed = False
        else:
            print(f"  Status: ✅ Normal sizing")
        
        print()
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! The brand font size fix is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_brand_font_size_simple() 