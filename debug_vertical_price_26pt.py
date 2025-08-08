#!/usr/bin/env python3
"""Debug script to identify why vertical price is showing 26pt instead of expected values."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size, FONT_SIZING_CONFIG
from src.core.generation.font_sizing import get_thresholded_font_size_price
from src.core.utils.common import calculate_text_complexity

def debug_vertical_price_font_sizing():
    """Debug the vertical price font sizing issue."""
    
    print("🔍 Debugging Vertical Price Font Sizing Issue")
    print("=" * 50)
    
    # Test prices with different lengths
    test_prices = [
        "$5.99",      # 5 chars
        "$10.99",     # 6 chars  
        "$15.99",     # 6 chars
        "$25.99",     # 6 chars
        "$100.99",    # 7 chars
        "$1000.99",   # 8 chars
        "$10000.99",  # 9 chars
        "$100000.99", # 10 chars
    ]
    
    print("\n📊 Testing Unified Font Sizing System:")
    print("-" * 40)
    
    for price in test_prices:
        # Get complexity
        complexity = calculate_text_complexity(price)
        
        # Get font size from unified system
        unified_size = get_font_size(price, 'price', 'vertical', 1.0)
        
        print(f"Price: '{price}' ({len(price)} chars, complexity: {complexity:.1f})")
        print(f"  → Unified system: {unified_size.pt}pt")
        
        # Check what threshold it should fall into
        config = FONT_SIZING_CONFIG.get('standard', {}).get('vertical', {}).get('price', [])
        print(f"  → Config thresholds: {config}")
        
        # Find which threshold it matches
        for threshold, size in config:
            if complexity <= threshold:
                print(f"  → Matches threshold: {complexity:.1f} <= {threshold} → {size}pt")
                break
        
        print()
    
    print("\n📊 Testing Old Font Sizing System:")
    print("-" * 40)
    
    for price in test_prices:
        complexity = calculate_text_complexity(price)
        try:
            old_size = get_thresholded_font_size_price(price, 'vertical', 1.0)
            print(f"Price: '{price}' ({len(price)} chars, complexity: {complexity:.1f})")
            print(f"  → Old system: {old_size.pt}pt")
            
            # Check old system thresholds
            if complexity < 10:
                expected = 30
            elif complexity < 20:
                expected = 28
            elif complexity < 30:
                expected = 26
            else:
                expected = 14
            print(f"  → Expected (old): {expected}pt")
            print()
        except Exception as e:
            print(f"Price: '{price}' - Error: {e}")
            print()

if __name__ == "__main__":
    debug_vertical_price_font_sizing() 