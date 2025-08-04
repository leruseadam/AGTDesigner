#!/usr/bin/env python3
"""
Test to debug font sizing issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size, get_font_size_by_marker
from docx.shared import Pt

def test_font_sizing():
    """Test font sizing for brand names."""
    print("Testing Font Sizing for Brand Names")
    print("=" * 50)
    
    # Test brand names from the screenshot
    brand_names = ['JOURNEYMAN', 'FAIRWINDS', 'GREEN', 'CQ', 'HOT SHOTZ']
    
    for brand in brand_names:
        print(f"\nBrand: {brand}")
        
        # Test with get_font_size directly
        font_size_direct = get_font_size(brand, 'brand', 'double', 1.0)
        print(f"  get_font_size('brand', 'double'): {font_size_direct} ({font_size_direct.pt}pt)")
        
        # Test with get_font_size_by_marker
        font_size_marker = get_font_size_by_marker(brand, 'PRODUCTBRAND', 'double', 1.0)
        print(f"  get_font_size_by_marker('PRODUCTBRAND', 'double'): {font_size_marker} ({font_size_marker.pt}pt)")
        
        # Test with PRODUCTBRAND_CENTER marker
        font_size_center = get_font_size_by_marker(brand, 'PRODUCTBRAND_CENTER', 'double', 1.0)
        print(f"  get_font_size_by_marker('PRODUCTBRAND_CENTER', 'double'): {font_size_center} ({font_size_center.pt}pt)")
        
        # Check if the font size is reasonable (should be 8-16pt)
        if font_size_direct.pt > 20:
            print(f"  ⚠️  WARNING: Font size {font_size_direct.pt}pt is too large!")
        elif font_size_direct.pt < 6:
            print(f"  ⚠️  WARNING: Font size {font_size_direct.pt}pt is too small!")
        else:
            print(f"  ✅ Font size {font_size_direct.pt}pt is reasonable")

if __name__ == "__main__":
    test_font_sizing() 