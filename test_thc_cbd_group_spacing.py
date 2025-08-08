#!/usr/bin/env python3
"""
Test script to verify THC_CBD group formatting with proper spacing between groups.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor

def test_thc_cbd_group_formatting():
    """Test that THC_CBD formatting creates proper groups with spacing between them."""
    print("Testing THC_CBD Group Formatting")
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
        
        # Check the structure
        lines = formatted.split('\n')
        
        # Find THC and CBD groups
        thc_group_start = None
        cbd_group_start = None
        
        for j, line in enumerate(lines):
            if 'THC:' in line and not '%' in line:  # Label line
                thc_group_start = j
            elif 'CBD:' in line and not '%' in line:  # Label line
                cbd_group_start = j
                break
        
        if thc_group_start is not None and cbd_group_start is not None:
            # Check if there's proper spacing between groups
            gap_lines = lines[thc_group_start + 2:cbd_group_start]  # Skip THC label and percentage lines
            
            # Should have at least one empty line between groups
            has_empty_line = any(line.strip() == '' for line in gap_lines)
            
            if has_empty_line:
                print(f"✓ PASS: Proper spacing found between THC and CBD groups")
                print(f"  Formatted structure:")
                for k, line in enumerate(lines):
                    if line.strip() == '':
                        print(f"    Line {k}: [empty]")
                    else:
                        print(f"    Line {k}: '{line}'")
            else:
                print(f"✗ FAIL: No proper spacing found between THC and CBD groups")
                print(f"  Formatted: {repr(formatted)}")
                all_passed = False
        else:
            print(f"⚠ WARNING: Could not find both THC and CBD groups in formatted output")
            print(f"  Formatted: {repr(formatted)}")
    
    return all_passed

def test_group_structure():
    """Test that THC and CBD groups have proper structure (label + percentage together)."""
    print("\nTesting Group Structure")
    print("=" * 40)
    
    processor = TemplateProcessor('vertical', 'default', 1.0)
    
    # Test individual group formatting
    test_cases = [
        ("THC: 21.5%", "THC group"),
        ("CBD: 0.25%", "CBD group"),
    ]
    
    all_passed = True
    
    for test_input, description in test_cases:
        print(f"\nTesting {description}: '{test_input}'")
        
        # Use the new group formatting function
        formatted = processor._format_thc_cbd_group(test_input, 5)  # max_percentage_width = 5
        
        lines = formatted.split('\n')
        
        if len(lines) >= 2:
            label_line = lines[0]
            percentage_line = lines[1]
            
            # Check that label is on first line
            if 'THC:' in label_line or 'CBD:' in label_line:
                print(f"✓ PASS: Label on first line: '{label_line}'")
            else:
                print(f"✗ FAIL: Label not on first line: '{label_line}'")
                all_passed = False
            
            # Check that percentage is on second line with indentation
            if '%' in percentage_line and percentage_line.strip().startswith(('21.5', '0.25')):
                print(f"✓ PASS: Percentage on second line with indentation: '{percentage_line}'")
            else:
                print(f"✗ FAIL: Percentage not properly formatted: '{percentage_line}'")
                all_passed = False
        else:
            print(f"✗ FAIL: Group not properly structured")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("THC_CBD Group Spacing Test")
    print("=" * 40)
    
    test1_passed = test_thc_cbd_group_formatting()
    test2_passed = test_group_structure()
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! THC_CBD group formatting is working correctly.")
    else:
        print("\n❌ SOME TESTS FAILED! THC_CBD group formatting needs attention.")
    
    print(f"\nTest Results:")
    print(f"  Group Spacing Test: {'PASS' if test1_passed else 'FAIL'}")
    print(f"  Group Structure Test: {'PASS' if test2_passed else 'FAIL'}") 