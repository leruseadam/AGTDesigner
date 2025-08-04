#!/usr/bin/env python3
"""
Test to verify that price thresholds are working correctly for different price lengths.
"""

import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.DEBUG)

from src.core.generation.unified_font_sizing import get_font_size

def test_price_thresholds():
    """Test price thresholds for different price lengths."""
    
    test_prices = [
        ('$9.99', 5, 'Short price - should get 22pt'),
        ('$29.99', 6, 'Medium price - should get 20pt'),
        ('$129.99', 7, 'Longer price - should get 20pt'),
        ('$1,299.99', 9, 'Very long price - should get 18pt'),
        ('$12,999.99', 10, 'Extra long price - should get 18pt'),
        ('$129,999.99', 11, 'Super long price - should get 18pt'),
        ('$1,299,999.99', 13, 'Mega long price - should get 16pt'),
    ]
    
    print("Testing Price Thresholds for Double Template")
    print("=" * 60)
    
    for price, expected_length, description in test_prices:
        print(f"\n{description}")
        print(f"Price: '{price}'")
        print(f"Expected length: {expected_length}")
        
        font_size = get_font_size(price, 'price', 'double')
        size_pt = font_size.pt
        
        print(f"Font size: {size_pt}pt")
        
        # Check if the size is appropriate for the length
        if expected_length < 5:
            expected_size = 22
        elif expected_length < 8:
            expected_size = 20
        elif expected_length < 12:
            expected_size = 18
        elif expected_length < 16:
            expected_size = 16
        else:
            expected_size = 14
        
        if size_pt == expected_size:
            print(f"✓ Correct size ({size_pt}pt)")
        else:
            print(f"✗ Incorrect size - got {size_pt}pt, expected {expected_size}pt")

if __name__ == "__main__":
    test_price_thresholds() 