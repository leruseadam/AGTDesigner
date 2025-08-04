#!/usr/bin/env python3
"""
Simple test to see debug output for font sizing.
"""

import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.DEBUG)

from src.core.generation.unified_font_sizing import get_font_size

def test_debug_font_sizing():
    """Test font sizing with debug output."""
    
    price = '$29.99'
    print(f"Testing price: '{price}'")
    
    font_size = get_font_size(price, 'price', 'double')
    print(f"Result: {font_size.pt}pt")

if __name__ == "__main__":
    test_debug_font_sizing() 