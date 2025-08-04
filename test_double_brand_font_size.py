#!/usr/bin/env python3
"""
Test script to verify double template brand font sizing rule.
Tests that brand names with words longer than 9 characters get 8pt font in double template.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size
from docx.shared import Pt

def test_double_brand_font_sizing():
    """Test the new double template brand font sizing rule."""
    
    print("Testing double template brand font sizing rule...")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        # Brand names with words > 9 characters should get 8pt
        ("Supercalifragilisticexpialidocious", "Should be 8pt - single word > 9 chars"),
        ("VeryLongBrandName", "Should be 8pt - single word > 9 chars"),
        ("Short Brand", "Should use normal sizing - no words > 9 chars"),
        ("Short VeryLongBrandName", "Should be 8pt - has word > 9 chars"),
        ("VeryLongBrandName Short", "Should be 8pt - has word > 9 chars"),
        ("Multiple VeryLongBrandNames Here", "Should be 8pt - has words > 9 chars"),
        ("", "Should use default sizing - empty text"),
    ]
    
    for brand_name, description in test_cases:
        font_size = get_font_size(brand_name, 'brand', 'double', 1.0)
        expected_8pt = any(len(word) > 9 for word in brand_name.split()) if brand_name else False
        
        print(f"Brand: '{brand_name}'")
        print(f"Description: {description}")
        print(f"Font size: {font_size.pt}pt")
        print(f"Expected 8pt: {expected_8pt}")
        print(f"Test {'PASSED' if (expected_8pt and font_size.pt == 8) or (not expected_8pt and font_size.pt != 8) else 'FAILED'}")
        print("-" * 40)
    
    print("\nTesting other template types to ensure rule only applies to double...")
    print("=" * 60)
    
    # Test that the rule doesn't affect other template types
    long_brand = "VeryLongBrandName"
    other_templates = ['horizontal', 'vertical', 'mini']
    
    for template in other_templates:
        font_size = get_font_size(long_brand, 'brand', template, 1.0)
        print(f"Template: {template}, Brand: '{long_brand}', Font size: {font_size.pt}pt")
        print(f"Test {'PASSED' if font_size.pt != 8 else 'FAILED'} (should not be 8pt for {template})")
        print("-" * 40)

if __name__ == "__main__":
    test_double_brand_font_sizing() 