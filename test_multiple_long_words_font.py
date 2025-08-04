#!/usr/bin/env python3
"""
Test script to verify that font sizing logic correctly handles multiple words with 10+ characters each.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.generation.unified_font_sizing import get_font_size
from docx.shared import Pt

def test_multiple_long_words_font_sizing():
    """Test that multiple words with 10+ characters each trigger the correct font sizing."""
    
    print("Testing multiple long words font sizing logic...")
    print("=" * 60)
    
    # Test cases for brand names
    brand_test_cases = [
        {
            'name': 'Single long word (should NOT trigger 8pt)',
            'text': 'CONSTELLATION',
            'expected_size': 'NOT 8pt',
            'should_trigger': False
        },
        {
            'name': 'Two long words (should trigger 8pt)',
            'text': 'CONSTELLATION CANNABIS',
            'expected_size': '8pt',
            'should_trigger': True
        },
        {
            'name': 'Three long words (should trigger 8pt)',
            'text': 'CONSTELLATION CANNABIS COMPANY',
            'expected_size': '8pt',
            'should_trigger': True
        },
        {
            'name': 'One long word + short word (should NOT trigger 8pt)',
            'text': 'CONSTELLATION ABC',
            'expected_size': 'NOT 8pt',
            'should_trigger': False
        },
        {
            'name': 'Short words only (should NOT trigger 8pt)',
            'text': 'ABC DEF GHI',
            'expected_size': 'NOT 8pt',
            'should_trigger': False
        }
    ]
    
    print("Testing brand font sizing (double template):")
    print("-" * 40)
    
    for case in brand_test_cases:
        font_size = get_font_size(case['text'], 'brand', 'double', 1.0)
        is_8pt = font_size.pt == 8
        status = "✅" if is_8pt == case['should_trigger'] else "❌"
        
        print(f"{status} {case['name']}")
        print(f"    Text: '{case['text']}'")
        print(f"    Font size: {font_size.pt}pt")
        print(f"    Expected: {case['expected_size']}")
        print(f"    Should trigger: {case['should_trigger']}")
        print(f"    Actually triggered: {is_8pt}")
        print()
    
    # Test cases for descriptions
    desc_test_cases = [
        {
            'name': 'Single long word (should NOT trigger 18pt)',
            'text': 'CONSTELLATION',
            'expected_size': 'NOT 18pt',
            'should_trigger': False
        },
        {
            'name': 'Two long words (should trigger 18pt)',
            'text': 'CONSTELLATION CANNABIS',
            'expected_size': '18pt',
            'should_trigger': True
        },
        {
            'name': 'One long word + short word (should NOT trigger 18pt)',
            'text': 'CONSTELLATION ABC',
            'expected_size': 'NOT 18pt',
            'should_trigger': False
        }
    ]
    
    print("Testing description font sizing (double template):")
    print("-" * 40)
    
    for case in desc_test_cases:
        font_size = get_font_size(case['text'], 'description', 'double', 1.0)
        is_18pt = font_size.pt == 18
        status = "✅" if is_18pt == case['should_trigger'] else "❌"
        
        print(f"{status} {case['name']}")
        print(f"    Text: '{case['text']}'")
        print(f"    Font size: {font_size.pt}pt")
        print(f"    Expected: {case['expected_size']}")
        print(f"    Should trigger: {case['should_trigger']}")
        print(f"    Actually triggered: {is_18pt}")
        print()
    
    print("Test completed!")

if __name__ == "__main__":
    test_multiple_long_words_font_sizing() 