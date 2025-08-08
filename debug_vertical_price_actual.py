#!/usr/bin/env python3
"""Debug script to help identify the actual vertical price font size issue."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size, FONT_SIZING_CONFIG
from src.core.utils.common import calculate_text_complexity

def debug_vertical_price_actual():
    """Debug the actual vertical price font sizing."""
    
    print("🔍 Debugging Vertical Price Font Size Issue")
    print("=" * 50)
    
    # Ask user for the actual price they're seeing
    print("\n📝 Please provide the exact price text you're seeing with 26pt font:")
    print("(e.g., $29.99, $15.50, etc.)")
    
    # For now, let's test with common price formats
    test_prices = [
        "$29.99",
        "$15.50", 
        "$25.00",
        "$10.99",
        "$5.99",
        "$100.00",
        "$1,000.00",
        "$1,500.00",
    ]
    
    print("\n📊 Testing Common Price Formats:")
    print("-" * 40)
    
    for price in test_prices:
        complexity = calculate_text_complexity(price)
        font_size = get_font_size(price, 'price', 'vertical', 1.0)
        
        print(f"Price: '{price}' ({len(price)} chars)")
        print(f"  Complexity: {complexity:.1f}")
        print(f"  Font Size: {font_size.pt}pt")
        
        # Check thresholds
        config = FONT_SIZING_CONFIG.get('standard', {}).get('vertical', {}).get('price', [])
        for threshold, size in config:
            if complexity <= threshold:
                print(f"  → Matches: complexity {complexity:.1f} <= {threshold} → {size}pt")
                break
        
        print()
    
    print("💡 Troubleshooting Steps:")
    print("1. Check if the price text in your data matches any of the test prices above")
    print("2. If not, provide the exact price text you're seeing")
    print("3. Check if you're looking at a different template (horizontal, double, mini)")
    print("4. Check if there's any post-processing overriding the font size")
    print("5. Try clearing any cached data and regenerating the labels")

if __name__ == "__main__":
    debug_vertical_price_actual() 