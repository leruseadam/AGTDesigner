#!/usr/bin/env python3
"""Test script to directly test the app's font sizing function."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app's font sizing function
from app import _get_template_specific_font_size

def test_app_price_font():
    """Test the app's price font sizing function directly."""
    
    print("🔍 Testing App's Price Font Sizing Function")
    print("=" * 50)
    
    # Test with different prices
    test_prices = [
        "$5.99",
        "$10.99", 
        "$15.99",
        "$25.99",
        "$29.99",
        "$100.99",
    ]
    
    print("📊 Testing App's _get_template_specific_font_size:")
    print("-" * 50)
    
    for price in test_prices:
        try:
            # Call the app's function directly
            font_size = _get_template_specific_font_size(price, "PRICE", "vertical", 1.0)
            print(f"'{price}' → {font_size.pt}pt")
        except Exception as e:
            print(f"'{price}' → Error: {e}")
    
    print()
    print("💡 If you're seeing 26pt in the actual application, it might be:")
    print("1. A different price text than what we're testing")
    print("2. Font size being overridden after calculation")
    print("3. Cached font size from previous runs")
    print("4. A different font sizing function being used")

if __name__ == "__main__":
    test_app_price_font() 