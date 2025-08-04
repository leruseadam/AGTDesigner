#!/usr/bin/env python3
"""
Test script to debug price font sizing in double template.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size, get_font_size_by_marker
from src.core.utils.common import calculate_text_complexity
from docx.shared import Pt

def test_price_font_sizing():
    """Test price font sizing for double template."""
    
    print("Testing Price Font Sizing for Double Template")
    print("=" * 50)
    
    # Test prices from the screenshot
    test_prices = ["$12", "$27", "$4", "$110", "$75", "$7"]
    
    for price in test_prices:
        print(f"\nPrice: '{price}'")
        print("-" * 20)
        
        # Test complexity calculation
        complexity = calculate_text_complexity(price, 'standard')
        print(f"Complexity: {complexity}")
        
        # Test unified font sizing
        font_size = get_font_size(price, 'price', 'double', 1.0, 'standard')
        print(f"Unified font size: {font_size.pt}pt")
        
        # Test marker-based font sizing
        marker_font_size = get_font_size_by_marker(price, 'PRICE', 'double', 1.0)
        print(f"Marker font size: {marker_font_size.pt}pt")
        
        # Check if they match
        if font_size.pt == marker_font_size.pt:
            print("✓ Font sizes match")
        else:
            print("✗ Font sizes don't match!")

def test_double_template_config():
    """Test the double template price configuration."""
    
    print("\n\nDouble Template Price Configuration")
    print("=" * 40)
    
    config = [
        (10, 20), (20, 18), (30, 16), (40, 14), (float('inf'), 12)
    ]
    
    print("Thresholds:")
    for threshold, size in config:
        print(f"  Complexity < {threshold}: {size}pt")
    
    # Test with different complexity values
    test_complexities = [5, 10, 15, 25, 35, 45]
    
    print("\nTest Results:")
    for comp in test_complexities:
        for threshold, size in config:
            if comp < threshold:
                print(f"  Complexity {comp} < {threshold}: {size}pt")
                break

if __name__ == "__main__":
    test_price_font_sizing()
    test_double_template_config() 