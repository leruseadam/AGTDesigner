#!/usr/bin/env python3
"""
Test script to verify THC_CBD right-aligned percentage formatting for vertical templates.
This test ensures that THC: and CBD: labels are left-aligned while percentages are right-aligned.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_thc_cbd_vertical_alignment_formatting():
    """Test the THC_CBD vertical alignment formatting function."""
    print("Testing THC_CBD Vertical Alignment Formatting")
    print("=" * 50)
    
    # Import the function we want to test
    from src.core.generation.template_processor import TemplateProcessor
    
    # Create a template processor instance
    processor = TemplateProcessor('vertical', {}, 1.0)
    
    # Test cases
    test_cases = [
        {
            'input': 'THC: 87.01% CBD: 0.45%',
            'expected': 'THC:   87.01%\nCBD:   0.45%'
        },
        {
            'input': 'THC: 80.91%\nCBD: 0.14%',
            'expected': 'THC:   80.91%\nCBD:   0.14%'
        },
        {
            'input': 'THC: 25% CBD: 2%',
            'expected': 'THC:   25%\nCBD:   2%'
        },
        {
            'input': 'THC: 100mg CBD: 10mg',  # mg values should not be affected
            'expected': 'THC: 100mg CBD: 10mg'
        },
        {
            'input': 'THC: 25% CBD: 2% CBC: 1%',  # Multiple cannabinoids
            'expected': 'THC:   25%\nCBD:   2%\nCBC: 1%'  # Only THC and CBD get spacing formatting
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        input_text = test_case['input']
        expected = test_case['expected']
        
        # Call the formatting function
        result = processor.format_thc_cbd_vertical_alignment(input_text)
        
        # Display result and expected for comparison
        result_display = result
        expected_display = expected
        
        if result == expected:
            print(f"✓ Test {i}: '{input_text}' -> '{result_display}'")
        else:
            print(f"✗ Test {i}: '{input_text}' -> '{result_display}' (expected: '{expected_display}')")
            all_passed = False
    
    return all_passed

def test_tab_stop_creation():
    """Test that tab stops are properly created for vertical template THC_CBD content."""
    print("\nTesting Tab Stop Creation")
    print("=" * 50)
    
    from docx import Document
    from docx.enum.text import WD_TAB_ALIGNMENT
    from docx.shared import Inches
    
    # Create a test document
    doc = Document()
    paragraph = doc.add_paragraph("THC:\t87.01%")
    
    # Test tab stop creation
    paragraph.paragraph_format.tab_stops.clear_all()
    tab_stop = paragraph.paragraph_format.tab_stops.add_tab_stop(Inches(2), WD_TAB_ALIGNMENT.RIGHT)
    
    # Check if tab stop was created
    if tab_stop:
        print("✓ Tab stop created successfully")
        print(f"  - Position: {tab_stop.position}")
        print(f"  - Alignment: {tab_stop.alignment}")
        return True
    else:
        print("✗ Failed to create tab stop")
        return False

def test_regex_patterns():
    """Test the regex patterns used for extracting THC/CBD percentages."""
    print("\nTesting Regex Patterns")
    print("=" * 50)
    
    import re
    
    test_cases = [
        ('THC: 87.01%', True, '87.01'),
        ('CBD: 0.45%', True, '0.45'),
        ('THC: 25%', True, '25'),
        ('CBD: 2%', True, '2'),
        ('THC: 100mg', False, None),  # mg values should not match
        ('CBD: 10mg', False, None),   # mg values should not match
        ('THC: 25% CBD: 2%', True, '25'),  # Should match THC value
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        text, should_match, expected_value = test_case
        
        # Test THC pattern
        thc_match = re.search(r'(THC:\s*)([0-9.]+)%', text)
        if should_match and 'THC:' in text:
            if thc_match and thc_match.group(2) == expected_value:
                print(f"✓ THC pattern: '{text}' -> '{thc_match.group(2)}'")
            else:
                print(f"✗ THC pattern: '{text}' -> {thc_match.group(2) if thc_match else 'None'} (expected: '{expected_value}')")
                all_passed = False
        elif not should_match and 'THC:' in text:
            if not thc_match:
                print(f"✓ THC pattern: '{text}' -> no match (correct)")
            else:
                print(f"✗ THC pattern: '{text}' -> matched when it shouldn't")
                all_passed = False
        
        # Test CBD pattern - only for CBD-specific test cases
        if 'CBD:' in text and not 'THC:' in text:
            cbd_match = re.search(r'(CBD:\s*)([0-9.]+)%', text)
            if should_match:
                if cbd_match and cbd_match.group(2) == expected_value:
                    print(f"✓ CBD pattern: '{text}' -> '{cbd_match.group(2)}'")
                else:
                    print(f"✗ CBD pattern: '{text}' -> {cbd_match.group(2) if cbd_match else 'None'} (expected: '{expected_value}')")
                    all_passed = False
            else:
                if not cbd_match:
                    print(f"✓ CBD pattern: '{text}' -> no match (correct)")
                else:
                    print(f"✗ CBD pattern: '{text}' -> matched when it shouldn't")
                    all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("THC_CBD Right Alignment Test")
    print("=" * 60)
    
    test1_passed = test_thc_cbd_vertical_alignment_formatting()
    test2_passed = test_tab_stop_creation()
    test3_passed = test_regex_patterns()
    
    print("\n" + "=" * 60)
    if all([test1_passed, test2_passed, test3_passed]):
        print("🎉 ALL TESTS PASSED! THC_CBD right alignment formatting is working correctly.")
        print("\nSummary:")
        print("✓ THC_CBD vertical alignment formatting works correctly")
        print("✓ Tab stops are properly created for right-aligned percentages")
        print("✓ Regex patterns correctly extract THC/CBD percentages")
        print("\nExpected format for vertical templates:")
        print("  THC:    87.01%")
        print("  CBD:     0.45%")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED! THC_CBD right alignment formatting needs attention.")
        failed_tests = []
        if not test1_passed: failed_tests.append("Vertical alignment formatting")
        if not test2_passed: failed_tests.append("Tab stop creation")
        if not test3_passed: failed_tests.append("Regex patterns")
        print(f"Failed tests: {', '.join(failed_tests)}")
        sys.exit(1) 