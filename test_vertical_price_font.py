#!/usr/bin/env python3
"""Test script to debug vertical price font sizing."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size
from src.core.generation.font_sizing import get_thresholded_font_size_price

def test_vertical_price_font_sizing():
    """Test vertical price font sizing with different price lengths."""
    
    print("🔍 Testing Vertical Price Font Sizing")
    print("=" * 50)
    
    # Test prices of different lengths
    test_prices = [
        "$9.99",           # 5 chars
        "$19.99",          # 7 chars  
        "$29.99",          # 7 chars
        "$129.99",         # 8 chars
        "$1,299.99",       # 10 chars
        "$12,999.99",      # 12 chars
        "$129,999.99",     # 14 chars
        "$1,299,999.99",   # 16 chars
    ]
    
    print("\n📊 Testing Unified Font Sizing System:")
    print("-" * 40)
    
    for price in test_prices:
        # Test unified font sizing
        unified_size = get_font_size(price, 'price', 'vertical', 1.0, 'standard')
        print(f"Price: '{price}' ({len(price)} chars) -> {unified_size.pt}pt")
    
    print("\n📊 Testing Old Font Sizing System:")
    print("-" * 40)
    
    for price in test_prices:
        # Test old font sizing
        old_size = get_thresholded_font_size_price(price, 'vertical', 1.0)
        print(f"Price: '{price}' ({len(price)} chars) -> {old_size.pt}pt")
    
    print("\n🔍 Checking which function is being called:")
    print("-" * 40)
    
    # Test a specific price
    test_price = "$29.99"
    print(f"Testing price: '{test_price}'")
    
    # Check both systems
    unified_result = get_font_size(test_price, 'price', 'vertical', 1.0, 'standard')
    old_result = get_thresholded_font_size_price(test_price, 'vertical', 1.0)
    
    print(f"Unified system result: {unified_result.pt}pt")
    print(f"Old system result: {old_result.pt}pt")
    
    if unified_result.pt == old_result.pt:
        print("⚠️  Both systems return the same result!")
    else:
        print("✅ Systems return different results")
    
    print("\n🔍 Checking font sizing configuration:")
    print("-" * 40)
    
    # Import the configuration
    from src.core.generation.unified_font_sizing import FONT_SIZING_CONFIG
    
    vertical_price_config = FONT_SIZING_CONFIG.get('standard', {}).get('vertical', {}).get('price', [])
    print(f"Vertical price configuration: {vertical_price_config}")
    
    # Test each threshold
    for threshold, size in vertical_price_config:
        print(f"Threshold: {threshold} -> Size: {size}pt")
    
    print("\n🔍 Testing complexity calculation:")
    print("-" * 40)
    
    for price in test_prices:
        # Calculate complexity (character count for price)
        complexity = len(price)
        print(f"Price: '{price}' -> Complexity: {complexity}")
        
        # Find which threshold it matches
        for threshold, size in vertical_price_config:
            if complexity < threshold:
                print(f"  -> Matches threshold {threshold} -> {size}pt")
                break
        else:
            print(f"  -> No threshold matched, using fallback")

if __name__ == "__main__":
    test_vertical_price_font_sizing() 