#!/usr/bin/env python3
"""Comprehensive debug script to identify the vertical price font size issue."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size, FONT_SIZING_CONFIG
from src.core.utils.common import calculate_text_complexity

def debug_vertical_price_comprehensive():
    """Comprehensive debug of vertical price font sizing."""
    
    print("🔍 Comprehensive Vertical Price Font Size Debug")
    print("=" * 60)
    
    print("📊 Unified Font Sizing System Status:")
    print(f"  - Vertical price config: {FONT_SIZING_CONFIG['standard']['vertical']['price']}")
    print(f"  - This should return: 30pt (≤5 chars), 28pt (6-8 chars), 14pt (9+ chars)")
    print()
    
    print("🧪 Testing Different Price Formats:")
    print("-" * 60)
    
    test_cases = [
        ("$5.99", "Short price"),
        ("$10.99", "Medium price"),
        ("$15.99", "Medium price"),
        ("$25.99", "Medium price"),
        ("$29.99", "Medium price"),
        ("$100.00", "Long price"),
        ("$1,000.00", "Very long price"),
        ("$29.50", "Another medium price"),
        ("$15.50", "Another medium price"),
    ]
    
    for price, description in test_cases:
        complexity = calculate_text_complexity(price)
        font_size = get_font_size(price, 'price', 'vertical', 1.0)
        
        print(f"Price: '{price}' ({len(price)} chars, complexity: {complexity:.1f}) - {description}")
        print(f"  → Unified system returns: {font_size.pt}pt")
        print()
    
    print("🔍 Possible Causes for 26pt Issue:")
    print("-" * 60)
    print("1. You're looking at a different template (horizontal/double instead of vertical)")
    print("2. You're looking at a different field (not price)")
    print("3. There's some caching or old data")
    print("4. You're looking at a different price than what we're testing")
    print("5. There's some other code path being used")
    print()
    
    print("💡 Next Steps:")
    print("-" * 60)
    print("1. Check what template you're actually using")
    print("2. Check what field you're looking at")
    print("3. Check the exact price text you're seeing")
    print("4. Clear any caches and regenerate")
    print("5. Check if you're looking at a different template type")

if __name__ == "__main__":
    debug_vertical_price_comprehensive() 