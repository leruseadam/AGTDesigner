#!/usr/bin/env python3
"""
Debug script to see exactly what's happening with double template THC_CBD font sizing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size, get_font_size_by_marker
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def debug_double_thc_cbd_font():
    """Debug the double template THC_CBD font sizing."""
    print("Debugging Double Template THC_CBD Font Sizing")
    print("=" * 50)
    
    # Test cases for double template
    test_cases = [
        "THC: 21.5% CBD: 0.25%",
        "THC: 15.2% CBD: 1.8%",
        "THC: 8.7% CBD: 12.3%",
        "THC: 25.1% CBD: 0.1%",
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: '{test_text}'")
        
        # Test using get_font_size directly
        print(f"  Using get_font_size directly:")
        font_size_direct = get_font_size(test_text, 'thc_cbd', 'double', 1.0)
        print(f"    Font size: {font_size_direct.pt}pt")
        
        # Test using get_font_size_by_marker
        print(f"  Using get_font_size_by_marker:")
        font_size_marker = get_font_size_by_marker(test_text, 'THC_CBD', 'double', 1.0)
        print(f"    Font size: {font_size_marker.pt}pt")
        
        # Check if it's 8pt
        if font_size_direct.pt == 8 or font_size_marker.pt == 8:
            print(f"  ⚠ WARNING: Still getting 8pt font!")
        else:
            print(f"  ✓ PASS: Not using 8pt font")

if __name__ == "__main__":
    debug_double_thc_cbd_font() 