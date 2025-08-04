#!/usr/bin/env python3
"""
Test script to verify THC_CBD line spacing is properly applied across all templates.
This test ensures that the unified font sizing system is working correctly for THC_CBD content.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_line_spacing_by_marker

def test_thc_cbd_line_spacing():
    """Test THC_CBD line spacing across all templates."""
    print("Testing THC_CBD Line Spacing Across All Templates")
    print("=" * 50)
    
    templates = ['vertical', 'horizontal', 'double', 'mini']
    expected_spacing = {
        'vertical': 1.25,
        'horizontal': 1.35,
        'double': 1.4,
        'mini': 1.3
    }
    
    all_passed = True
    
    for template in templates:
        actual = get_line_spacing_by_marker('THC_CBD', template)
        expected = expected_spacing[template]
        
        if actual == expected:
            print(f"✓ {template.upper()} template: {actual} (expected: {expected})")
        else:
            print(f"✗ {template.upper()} template: {actual} (expected: {expected})")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ ALL TESTS PASSED: THC_CBD line spacing is working correctly!")
        return True
    else:
        print("✗ SOME TESTS FAILED: THC_CBD line spacing needs attention.")
        return False

def test_other_markers_not_affected():
    """Test that other markers still get their expected line spacing."""
    print("\nTesting Other Markers Line Spacing")
    print("=" * 50)
    
    # Test RATIO marker (should still be 2.4)
    ratio_spacing = get_line_spacing_by_marker('RATIO', 'vertical')
    if ratio_spacing == 2.4:
        print("✓ RATIO marker: 2.4 (correct)")
    else:
        print(f"✗ RATIO marker: {ratio_spacing} (expected: 2.4)")
        return False
    
    # Test default marker (should be 1.0)
    default_spacing = get_line_spacing_by_marker('DESCRIPTION', 'vertical')
    if default_spacing == 1.0:
        print("✓ DESCRIPTION marker: 1.0 (correct)")
    else:
        print(f"✗ DESCRIPTION marker: {default_spacing} (expected: 1.0)")
        return False
    
    print("✓ Other markers not affected by THC_CBD changes")
    return True

if __name__ == "__main__":
    print("THC_CBD Line Spacing Fix Test")
    print("=" * 50)
    
    test1_passed = test_thc_cbd_line_spacing()
    test2_passed = test_other_markers_not_affected()
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! THC_CBD line spacing fix is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED! THC_CBD line spacing fix needs attention.")
        sys.exit(1) 