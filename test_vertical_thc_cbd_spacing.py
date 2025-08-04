#!/usr/bin/env python3
"""
Test script to verify vertical template THC_CBD line spacing is set to 1.25.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.unified_font_sizing import get_line_spacing_by_marker

def test_vertical_thc_cbd_spacing():
    """Test that vertical template THC_CBD uses 1.25 spacing."""
    
    print("Testing Vertical Template THC_CBD Line Spacing")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            'marker': 'THC_CBD',
            'template': 'vertical',
            'expected': 1.25,
            'description': 'Vertical template THC_CBD should use 1.25 spacing'
        },
        {
            'marker': 'THC_CBD',
            'template': 'horizontal',
            'expected': 2.0,
            'description': 'Horizontal template THC_CBD should use 2.0 spacing'
        },
        {
            'marker': 'THC_CBD',
            'template': 'mini',
            'expected': 2.0,
            'description': 'Mini template THC_CBD should use 2.0 spacing'
        },
        {
            'marker': 'THC_CBD',
            'template': 'double',
            'expected': 2.0,
            'description': 'Double template THC_CBD should use 2.0 spacing'
        },
        {
            'marker': 'RATIO',
            'template': 'vertical',
            'expected': 2.4,
            'description': 'Vertical template RATIO should use 2.4 spacing'
        },
        {
            'marker': 'DESCRIPTION',
            'template': 'vertical',
            'expected': 1.0,
            'description': 'Vertical template DESCRIPTION should use 1.0 spacing'
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        marker = test_case['marker']
        template = test_case['template']
        expected = test_case['expected']
        description = test_case['description']
        
        # Get the actual spacing
        actual = get_line_spacing_by_marker(marker, template)
        
        # Check if it matches expected
        if actual == expected:
            print(f"✅ PASS: {description}")
            print(f"   Marker: {marker}, Template: {template}, Spacing: {actual}")
        else:
            print(f"❌ FAIL: {description}")
            print(f"   Marker: {marker}, Template: {template}")
            print(f"   Expected: {expected}, Actual: {actual}")
            all_passed = False
        
        print()
    
    if all_passed:
        print("🎉 All tests passed! Vertical template THC_CBD now uses 1.25 spacing.")
    else:
        print("💥 Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    test_vertical_thc_cbd_spacing() 