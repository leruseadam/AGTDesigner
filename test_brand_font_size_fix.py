#!/usr/bin/env python3
"""
Test script to verify that product brands with more than 20 letters get forced to font size 14 in horizontal templates.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.generation.font_sizing import get_thresholded_font_size
from docx import Document
from docx.shared import Pt

def test_brand_font_size_fix():
    """Test that product brands with more than 20 letters get forced to font size 14 in horizontal templates."""
    
    print("=== Brand Font Size Fix Test ===\n")
    
    # Test cases with different brand name lengths
    test_cases = [
        ("Short Brand", 11),  # Less than 20 letters
        ("Medium Brand Name", 18),  # Less than 20 letters
        ("Very Long Brand Name That Exceeds Twenty Letters", 42),  # More than 20 letters
        ("Another Very Long Brand Name With Many Characters", 47),  # More than 20 letters
        ("Short", 5),  # Very short
        ("Exactly Twenty Letters Here", 25),  # Exactly 20 letters (should be 14)
        ("Twenty One Letters Here!", 21),  # 21 letters (should be 14)
    ]
    
    print("Testing horizontal template brand font sizing:")
    print("-" * 50)
    
    for brand_name, letter_count in test_cases:
        # Get font size for horizontal template
        font_size = get_thresholded_font_size(brand_name, orientation='horizontal', field_type='brand')
        
        # Check if the rule is working
        expected_size = 14 if letter_count > 20 else None
        rule_applied = letter_count > 20 and font_size.pt == 14
        
        print(f"Brand: '{brand_name}'")
        print(f"  Letters: {letter_count}")
        print(f"  Font size: {font_size.pt}pt")
        print(f"  Rule applied (>20 letters → 14pt): {'✅' if rule_applied else '❌'}")
        
        if expected_size:
            print(f"  Expected: {expected_size}pt")
            if font_size.pt == expected_size:
                print(f"  Status: ✅ PASS")
            else:
                print(f"  Status: ❌ FAIL (got {font_size.pt}pt, expected {expected_size}pt)")
        else:
            print(f"  Status: ✅ Normal sizing")
        print()
    
    # Test edge cases
    print("Edge Cases:")
    print("-" * 20)
    
    edge_cases = [
        ("", 0),  # Empty string
        ("A", 1),  # Single character
        ("12345678901234567890", 20),  # Exactly 20 characters
        ("123456789012345678901", 21),  # 21 characters
        ("   Spaces   Count   ", 20),  # 20 characters with spaces
    ]
    
    for brand_name, letter_count in edge_cases:
        font_size = get_thresholded_font_size(brand_name, orientation='horizontal', field_type='brand')
        print(f"'{brand_name}' ({letter_count} chars): {font_size.pt}pt")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_brand_font_size_fix() 