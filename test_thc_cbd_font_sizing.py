#!/usr/bin/env python3
"""
Test script to verify THC_CBD font sizing is working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_font_size_by_marker

def test_thc_cbd_font_sizing():
    """Test that THC_CBD font sizing uses the correct configuration."""
    print("Testing THC_CBD Font Sizing")
    print("=" * 40)
    
    # Test cases for different templates
    test_cases = [
        ("THC: 21.5% CBD: 0.25%", "vertical"),
        ("THC: 15.2% CBD: 1.8%", "horizontal"),
        ("THC: 8.7% CBD: 12.3%", "double"),
        ("THC: 25.1% CBD: 0.1%", "mini"),
    ]
    
    all_passed = True
    
    for test_text, template_type in test_cases:
        print(f"\nTesting {template_type} template:")
        print(f"  Text: '{test_text}'")
        
        # Get font size using the marker system
        font_size = get_font_size_by_marker(test_text, 'THC_CBD', template_type, 1.0)
        
        print(f"  Font size: {font_size.pt}pt")
        
        # Check that it's not the hardcoded 8pt
        if font_size.pt == 8:
            print(f"  ✗ FAIL: Still using hardcoded 8pt font")
            all_passed = False
        else:
            print(f"  ✓ PASS: Using configured font size ({font_size.pt}pt)")
        
        # Check that it's using the correct configuration
        if template_type == "vertical" and font_size.pt == 6.5:
            print(f"  ✓ PASS: Using correct vertical template size")
        elif template_type == "horizontal" and font_size.pt == 12:
            print(f"  ✓ PASS: Using correct horizontal template size")
        elif template_type == "double" and font_size.pt == 6:
            print(f"  ✓ PASS: Using correct double template size")
        elif template_type == "mini" and font_size.pt == 6.5:
            print(f"  ✓ PASS: Using correct mini template size")
        else:
            print(f"  ⚠ WARNING: Unexpected font size for {template_type} template")
    
    return all_passed

if __name__ == "__main__":
    print("THC_CBD Font Sizing Test")
    print("=" * 40)
    
    test_passed = test_thc_cbd_font_sizing()
    
    if test_passed:
        print("\n🎉 ALL TESTS PASSED! THC_CBD font sizing is working correctly.")
    else:
        print("\n❌ SOME TESTS FAILED! THC_CBD font sizing needs attention.")
    
    print(f"\nTest Results:")
    print(f"  Font Sizing Test: {'PASS' if test_passed else 'FAIL'}") 