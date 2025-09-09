#!/usr/bin/env python3
"""
Test script to verify QR code font sizing integration.
"""
from src.core.generation.unified_font_sizing import get_font_size, get_font_size_by_marker
from docx.shared import Pt

def test_qr_font_sizing():
    """Test QR code font sizing for different template types."""
    
    print("Testing QR Code Font Sizing Integration")
    print("=" * 50)
    
    # Test different template types
    template_types = ['mini', 'vertical', 'horizontal', 'double']
    
    for template_type in template_types:
        print(f"\n{template_type.upper()} Template:")
        print("-" * 20)
        
        # Test QR font sizing
        qr_font_size = get_font_size("Test Product Name", 'qr', template_type, 1.0)
        print(f"  QR font size: {qr_font_size.pt}pt")
        
        # Test with different product name lengths
        test_names = [
            "Short",
            "Medium Length Product",
            "Very Long Product Name That Should Test Font Sizing",
            "Extremely Long Product Name That Will Definitely Test The Font Sizing System And See How It Handles Very Long Text"
        ]
        
        for name in test_names:
            size = get_font_size(name, 'qr', template_type, 1.0)
            print(f"  '{name[:30]}...': {size.pt}pt")
    
    # Test marker-based font sizing
    print(f"\nMarker-Based Font Sizing:")
    print("-" * 30)
    
    for template_type in template_types:
        size = get_font_size_by_marker("Test Product", 'QR', template_type, 1.0)
        print(f"  {template_type}: {size.pt}pt")
    
    # Test with scale factors
    print(f"\nScale Factor Testing (vertical template):")
    print("-" * 45)
    
    scale_factors = [0.5, 1.0, 1.5, 2.0]
    for scale in scale_factors:
        size = get_font_size("Test Product", 'qr', 'vertical', scale)
        print(f"  Scale {scale}: {size.pt}pt")
    
    print(f"\n✅ QR Code font sizing test completed!")

if __name__ == "__main__":
    test_qr_font_sizing()
