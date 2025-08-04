#!/usr/bin/env python3
"""
Test script to verify that Double template price font sizing is working correctly.
This tests that prices are not being pinned to 20pt font.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size

def test_double_template_price_font_sizing():
    """Test that Double template price font sizing works correctly."""
    
    test_cases = [
        {
            'price': '$9.99',
            'expected_range': (20, 24),  # Should be around 22pt for short prices
            'description': 'Short price'
        },
        {
            'price': '$29.99',
            'expected_range': (18, 22),  # Should be around 20pt for medium prices
            'description': 'Medium price'
        },
        {
            'price': '$129.99',
            'expected_range': (14, 18),  # Should be around 16pt for longer prices
            'description': 'Longer price'
        },
        {
            'price': '$1,299.99',
            'expected_range': (12, 16),  # Should be around 14pt for very long prices
            'description': 'Very long price'
        }
    ]
    
    print("Testing Double Template Price Font Sizing")
    print("=" * 50)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        price = test_case['price']
        expected_min, expected_max = test_case['expected_range']
        description = test_case['description']
        
        # Get font size for Double template price
        font_size = get_font_size(price, 'price', 'double')
        size_pt = font_size.pt
        
        print(f"\nTest {i}: {description}")
        print(f"  Price: '{price}'")
        print(f"  Font Size: {size_pt}pt")
        print(f"  Expected Range: {expected_min}-{expected_max}pt")
        
        if expected_min <= size_pt <= expected_max:
            print(f"  ✓ PASS - Font size {size_pt}pt is within expected range")
        else:
            print(f"  ✗ FAIL - Font size {size_pt}pt is outside expected range")
            all_passed = False
        
        # Check that it's not pinned to 20pt
        if size_pt == 20:
            print(f"  ⚠️  WARNING - Font size is pinned to 20pt")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED - Double template price font sizing is working correctly")
    else:
        print("❌ SOME TESTS FAILED - Double template price font sizing needs attention")
    
    return all_passed

if __name__ == "__main__":
    test_double_template_price_font_sizing() 