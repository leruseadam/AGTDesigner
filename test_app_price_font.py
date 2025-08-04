#!/usr/bin/env python3
"""Test to check what font sizing the actual application is using."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app functions
from app import _get_template_specific_font_size

def test_app_price_font_sizing():
    """Test the actual application's price font sizing."""
    
    print("🔍 Testing Application's Price Font Sizing")
    print("=" * 50)
    
    # Test prices of different lengths
    test_prices = [
        "$9.99",           # 5 chars
        "$19.99",          # 6 chars  
        "$29.99",          # 6 chars
        "$129.99",         # 7 chars
        "$1,299.99",       # 9 chars
        "$12,999.99",      # 10 chars
        "$129,999.99",     # 11 chars
        "$1,299,999.99",   # 13 chars
    ]
    
    print("\n📊 Testing Application's Font Sizing:")
    print("-" * 40)
    
    for price in test_prices:
        # Test the actual application function
        app_size = _get_template_specific_font_size(price, 'PRICE', 'vertical', 1.0)
        print(f"Price: '{price}' ({len(price)} chars) -> {app_size.pt}pt")
    
    print("\n🔍 Testing with different orientations:")
    print("-" * 40)
    
    test_price = "$29.99"
    orientations = ['vertical', 'horizontal', 'mini']
    
    for orientation in orientations:
        app_size = _get_template_specific_font_size(test_price, 'PRICE', orientation, 1.0)
        print(f"Price: '{test_price}' ({orientation}) -> {app_size.pt}pt")
    
    print("\n🔍 Testing with different scale factors:")
    print("-" * 40)
    
    scale_factors = [0.5, 1.0, 1.5, 2.0]
    
    for scale_factor in scale_factors:
        app_size = _get_template_specific_font_size(test_price, 'PRICE', 'vertical', scale_factor)
        print(f"Price: '{test_price}' (scale: {scale_factor}) -> {app_size.pt}pt")

if __name__ == "__main__":
    test_app_price_font_sizing() 