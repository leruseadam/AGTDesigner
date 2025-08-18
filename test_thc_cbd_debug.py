#!/usr/bin/env python3
"""
Debug script to test THC/CBD font sizing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size, get_font_size_by_marker

def test_thc_cbd_font_sizing():
    """Test THC/CBD font sizing for horizontal templates"""
    
    test_text = "THC: 74.5% CBD: 0.1%"
    
    print("=== TESTING THC/CBD FONT SIZING ===")
    print(f"Test text: '{test_text}'")
    print()
    
    # Test direct font size
    print("1. Direct font size:")
    font_size = get_font_size(test_text, 'thc_cbd', 'horizontal', 1.0)
    print(f"   get_font_size('{test_text}', 'thc_cbd', 'horizontal', 1.0) = {font_size.pt}pt")
    print()
    
    # Test marker-based font size
    print("2. Marker-based font size:")
    font_size_marker = get_font_size_by_marker(test_text, 'THC_CBD', 'horizontal', 1.0)
    print(f"   get_font_size_by_marker('{test_text}', 'THC_CBD', 'horizontal', 1.0) = {font_size_marker.pt}pt")
    print()
    
    # Test RATIO_OR_THC_CBD marker
    print("3. RATIO_OR_THC_CBD marker:")
    font_size_ratio = get_font_size_by_marker(test_text, 'RATIO_OR_THC_CBD', 'horizontal', 1.0)
    print(f"   get_font_size_by_marker('{test_text}', 'RATIO_OR_THC_CBD', 'horizontal', 1.0) = {font_size_ratio.pt}pt")
    print()
    
    # Test different text lengths
    print("4. Different text lengths:")
    short_text = "THC: 20%"
    long_text = "THC: 74.5% CBD: 0.1% Terpenes: 2.1%"
    
    short_size = get_font_size(short_text, 'thc_cbd', 'horizontal', 1.0)
    long_size = get_font_size(long_text, 'thc_cbd', 'horizontal', 1.0)
    
    print(f"   Short text '{short_text}': {short_size.pt}pt")
    print(f"   Long text '{long_text}': {long_size.pt}pt")
    print()
    
    print("=== END TEST ===")

if __name__ == "__main__":
    test_thc_cbd_font_sizing()
