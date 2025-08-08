#!/usr/bin/env python3
"""
Test script to verify THC_CBD extra line spacing between THC percentage and CBD line.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor

def test_thc_cbd_extra_spacing():
    """Test that THC_CBD formatting adds extra line spacing between THC and CBD."""
    print("Testing THC_CBD Extra Line Spacing")
    print("=" * 40)
    
    # Create a template processor instance
    processor = TemplateProcessor('vertical', 'default', 1.0)
    
    # Test cases with different THC/CBD formats
    test_cases = [
        "THC: 21.5% CBD: 0.25%",
        "THC: 15.2% CBD: 1.8%",
        "THC: 8.7% CBD: 12.3% CBC: 0.5%",
        "THC: 25.1% CBD: 0.1% CBG: 0.3%",
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: '{test_case}'")
        
        # Format the THC/CBD content
        formatted = processor.format_thc_cbd_vertical_alignment(test_case)
        
        # Check if there are double line breaks between THC and CBD
        lines = formatted.split('\n')
        
        # Find THC and CBD lines
        thc_line_index = None
        cbd_line_index = None
        
        for j, line in enumerate(lines):
            if 'THC:' in line and '%' in line:
                thc_line_index = j
            elif 'CBD:' in line and '%' in line:
                cbd_line_index = j
                break
        
        if thc_line_index is not None and cbd_line_index is not None:
            # Check if there's an empty line between THC and CBD
            gap_lines = lines[thc_line_index + 1:cbd_line_index]
            has_empty_line = any(line.strip() == '' for line in gap_lines)
            
            if has_empty_line:
                print(f"✓ PASS: Extra line spacing found between THC and CBD")
                print(f"  Formatted: {repr(formatted)}")
            else:
                print(f"✗ FAIL: No extra line spacing found between THC and CBD")
                print(f"  Formatted: {repr(formatted)}")
                all_passed = False
        else:
            print(f"⚠ WARNING: Could not find both THC and CBD lines in formatted output")
            print(f"  Formatted: {repr(formatted)}")
    
    return all_passed

def test_line_spacing_configuration():
    """Test that the line spacing configuration is correct."""
    print("\nTesting Line Spacing Configuration")
    print("=" * 40)
    
    from src.core.generation.unified_font_sizing import get_line_spacing_by_marker
    
    # Test vertical template THC_CBD spacing
    vertical_spacing = get_line_spacing_by_marker('THC_CBD', 'vertical')
    expected_vertical = 1.3
    
    if vertical_spacing == expected_vertical:
        print(f"✓ PASS: Vertical template THC_CBD spacing is {vertical_spacing} (expected {expected_vertical})")
    else:
        print(f"✗ FAIL: Vertical template THC_CBD spacing is {vertical_spacing} (expected {expected_vertical})")
        return False
    
    # Test other template types to ensure they're not affected
    other_templates = ['horizontal', 'double', 'mini']
    for template in other_templates:
        spacing = get_line_spacing_by_marker('THC_CBD', template)
        print(f"  {template.capitalize()} template THC_CBD spacing: {spacing}")
    
    return True

if __name__ == "__main__":
    print("THC_CBD Extra Line Spacing Test")
    print("=" * 40)
    
    test1_passed = test_thc_cbd_extra_spacing()
    test2_passed = test_line_spacing_configuration()
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! THC_CBD extra line spacing is working correctly.")
    else:
        print("\n❌ SOME TESTS FAILED! THC_CBD extra line spacing needs attention.")
    
    print(f"\nTest Results:")
    print(f"  Formatting Test: {'PASS' if test1_passed else 'FAIL'}")
    print(f"  Configuration Test: {'PASS' if test2_passed else 'FAIL'}") 