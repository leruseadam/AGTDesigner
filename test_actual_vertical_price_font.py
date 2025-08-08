#!/usr/bin/env python3
"""Test script to check actual vertical price font sizing in the application."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size, FONT_SIZING_CONFIG
from src.core.utils.common import calculate_text_complexity

def test_actual_vertical_price_font():
    """Test the actual vertical price font sizing."""
    
    print("🔍 Testing Actual Vertical Price Font Sizing")
    print("=" * 50)
    
    # Test with a price that should give 26pt according to old system
    test_price = "$29.99"  # This has complexity around 20-30, which would give 26pt in old system
    
    # Get complexity
    complexity = calculate_text_complexity(test_price)
    
    # Get font size from unified system
    unified_size = get_font_size(test_price, 'price', 'vertical', 1.0)
    
    print(f"Test Price: '{test_price}'")
    print(f"Character count: {len(test_price)}")
    print(f"Complexity: {complexity:.1f}")
    print(f"Unified system font size: {unified_size.pt}pt")
    
    # Check what threshold it should fall into
    config = FONT_SIZING_CONFIG.get('standard', {}).get('vertical', {}).get('price', [])
    print(f"Config thresholds: {config}")
    
    # Find which threshold it matches
    for threshold, size in config:
        if complexity <= threshold:
            print(f"Matches threshold: {complexity:.1f} <= {threshold} → {size}pt")
            break
    
    print()
    
    # Test with different prices to see the pattern
    test_prices = [
        "$5.99",      # Should be 30pt
        "$10.99",     # Should be 28pt  
        "$15.99",     # Should be 28pt
        "$25.99",     # Should be 28pt
        "$29.99",     # Should be 14pt (complexity > 8)
        "$100.99",    # Should be 14pt
    ]
    
    print("📊 Testing Multiple Prices:")
    print("-" * 30)
    
    for price in test_prices:
        complexity = calculate_text_complexity(price)
        unified_size = get_font_size(price, 'price', 'vertical', 1.0)
        
        print(f"'{price}' ({len(price)} chars, complexity: {complexity:.1f}) → {unified_size.pt}pt")
    
    print()
    print("💡 Analysis:")
    print("- If you're seeing 26pt, it might be from:")
    print("  1. An old cached font size")
    print("  2. A different font sizing function being used")
    print("  3. Post-processing overriding the font size")
    print("  4. A different price text than expected")

if __name__ == "__main__":
    test_actual_vertical_price_font() 