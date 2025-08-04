#!/usr/bin/env python3
"""
Debug script to understand why Double template prices are being pinned to 20pt.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size
from src.core.utils.common import calculate_text_complexity

def debug_double_price_font():
    """Debug Double template price font sizing."""
    
    test_prices = ['$9.99', '$29.99', '$129.99', '$1,299.99']
    
    print("Debugging Double Template Price Font Sizing")
    print("=" * 60)
    
    for price in test_prices:
        print(f"\nPrice: '{price}'")
        print(f"Length: {len(price)} characters")
        
        # Test complexity calculation
        standard_comp = calculate_text_complexity(price, 'standard')
        print(f"Standard complexity: {standard_comp}")
        
        # Test character count
        char_count = len(price)
        print(f"Character count: {char_count}")
        
        # Get font size
        font_size = get_font_size(price, 'price', 'double')
        size_pt = font_size.pt
        print(f"Font size: {size_pt}pt")
        
        # Check the thresholds
        print("Double template price thresholds:")
        print("  [(5, 22), (8, 20), (12, 18), (16, 16), (float('inf'), 14)]")
        print(f"  Complexity {char_count} should match threshold...")
        
        if char_count < 5:
            expected = 22
        elif char_count < 8:
            expected = 20
        elif char_count < 12:
            expected = 18
        elif char_count < 16:
            expected = 16
        else:
            expected = 14
        
        print(f"  Expected: {expected}pt, Got: {size_pt}pt")
        
        if size_pt == expected:
            print(f"  ✓ Correct")
        else:
            print(f"  ✗ Incorrect - should be {expected}pt")

if __name__ == "__main__":
    debug_double_price_font() 