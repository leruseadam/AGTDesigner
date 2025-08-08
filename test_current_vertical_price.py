#!/usr/bin/env python3
"""Test current vertical price font sizing to see what's actually happening."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size, FONT_SIZING_CONFIG
from src.core.utils.common import calculate_text_complexity

def test_current_vertical_price():
    """Test the current vertical price font sizing."""
    
    print("🔍 Testing Current Vertical Price Font Sizing")
    print("=" * 50)
    
    # Test with different prices
    test_prices = [
        "$5.99",      # 5 chars - should be 30pt
        "$10.99",     # 6 chars - should be 28pt
        "$15.99",     # 7 chars - should be 28pt
        "$25.99",     # 8 chars - should be 28pt
        "$29.99",     # 9 chars - should be 14pt
        "$100.00",    # 10 chars - should be 14pt
        "$1,000.00",  # 12 chars - should be 14pt
    ]
    
    print("📊 Current Vertical Price Configuration:")
    print(f"Config: {FONT_SIZING_CONFIG['standard']['vertical']['price']}")
    print()
    
    print("📊 Testing Font Sizes:")
    print("-" * 50)
    
    for price in test_prices:
        complexity = calculate_text_complexity(price)
        font_size = get_font_size(price, 'price', 'vertical', 1.0)
        
        print(f"Price: '{price}' ({len(price)} chars, complexity: {complexity:.1f})")
        print(f"  → Font size: {font_size.pt}pt")
        print()
    
    print("💡 If you're seeing 26pt, it's NOT coming from the unified system.")
    print("   The unified system only returns: 30pt, 28pt, or 14pt for vertical price.")

if __name__ == "__main__":
    test_current_vertical_price() 