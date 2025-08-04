#!/usr/bin/env python3
"""
Test font size calculation for vendor text
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size, get_font_size_by_marker
from docx.shared import Pt

def test_vendor_font_sizing():
    """Test font size calculation for vendor text"""
    
    test_vendor = "Test Vendor Company"
    
    print("=== Testing Vendor Font Size Calculation ===")
    print(f"Test vendor text: '{test_vendor}'")
    print(f"Text length: {len(test_vendor)} characters")
    
    # Test different template types
    for template_type in ['horizontal', 'vertical', 'double', 'mini']:
        print(f"\n--- {template_type.upper()} template ---")
        
        # Test using get_font_size directly
        font_size = get_font_size(test_vendor, 'vendor', template_type, 1.0)
        print(f"  get_font_size('vendor'): {font_size.pt}pt")
        
        # Test using get_font_size_by_marker
        marker_font_size = get_font_size_by_marker(test_vendor, 'PRODUCTVENDOR', template_type, 1.0)
        print(f"  get_font_size_by_marker('PRODUCTVENDOR'): {marker_font_size.pt}pt")
        
        # Check if the size is reasonable
        if marker_font_size.pt < 6:
            print(f"  ⚠️  Font size {marker_font_size.pt}pt is very small!")
        elif marker_font_size.pt < 8:
            print(f"  ⚠️  Font size {marker_font_size.pt}pt is small but should be visible")
        else:
            print(f"  ✅ Font size {marker_font_size.pt}pt should be clearly visible")

def test_font_config():
    """Test the font configuration directly"""
    print("\n=== Testing Font Configuration ===")
    
    from src.core.generation.unified_font_sizing import FONT_SIZING_CONFIG
    
    for template_type in ['horizontal', 'vertical', 'double', 'mini']:
        print(f"\n--- {template_type.upper()} template config ---")
        if template_type in FONT_SIZING_CONFIG['standard']:
            vendor_config = FONT_SIZING_CONFIG['standard'][template_type].get('vendor', [])
            print(f"  Vendor font config: {vendor_config}")
        else:
            print(f"  No config found for {template_type}")

if __name__ == "__main__":
    test_font_config()
    test_vendor_font_sizing() 