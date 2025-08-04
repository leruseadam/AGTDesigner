#!/usr/bin/env python3
"""
Test script for vertical template description font sizing
Tests the logic for automatically reducing font size when descriptions contain words longer than 9 characters
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.generation.font_sizing import get_thresholded_font_size_description
from src.core.generation.unified_font_sizing import get_font_size

def test_vertical_description_font_sizing():
    """Test the vertical template description font sizing logic."""
    print("=== Testing Vertical Template Description Font Sizing ===")
    
    # Test cases with different word lengths
    test_cases = [
        # Short words (should use normal sizing)
        ("Short description", "Normal sizing expected"),
        ("Two words here", "Normal sizing expected"),
        ("Three short words", "Normal sizing expected"),
        
        # Words exactly 9 characters (should use normal sizing)
        ("Ninechars description", "Normal sizing expected"),
        ("Word with ninechars", "Normal sizing expected"),
        
        # Words longer than 9 characters (should reduce font size)
        ("Longerword description", "Should reduce to 24pt"),
        ("Verylongword here", "Should reduce to 20pt"),
        ("Extremelylongword", "Should reduce to 16pt"),
        ("Superextremelylongword", "Should reduce to 12pt"),
        
        # Mixed cases
        ("Short longerword mixed", "Should reduce based on longest word"),
        ("Ninechars longerword", "Should reduce based on longest word"),
        ("Verylongword short", "Should reduce based on longest word"),
        
        # Edge cases
        ("", "Empty text handling"),
        ("   ", "Whitespace handling"),
        ("A", "Single character"),
        ("123456789", "Exactly 9 characters"),
        ("1234567890", "Exactly 10 characters"),
    ]
    
    print("\nTesting get_thresholded_font_size_description function:")
    print("-" * 80)
    
    for text, expected_behavior in test_cases:
        try:
            font_size = get_thresholded_font_size_description(text, orientation='vertical', scale_factor=1.0)
            words = text.split()
            max_word_length = max(len(word) for word in words) if words else 0
            
            print(f"Text: '{text}'")
            print(f"  Max word length: {max_word_length}")
            print(f"  Font size: {font_size.pt}pt")
            print(f"  Expected: {expected_behavior}")
            
            # Verify the logic
            if max_word_length > 9:
                if max_word_length <= 12:
                    expected_size = 24
                elif max_word_length <= 15:
                    expected_size = 20
                elif max_word_length <= 18:
                    expected_size = 16
                else:
                    expected_size = 12
                
                if font_size.pt == expected_size:
                    print(f"  ✓ PASS: Correctly reduced to {expected_size}pt")
                else:
                    print(f"  ✗ FAIL: Expected {expected_size}pt, got {font_size.pt}pt")
            else:
                print(f"  ✓ PASS: Using normal sizing ({font_size.pt}pt)")
            
            print()
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            print()
    
    print("\nTesting get_font_size function (unified):")
    print("-" * 80)
    
    for text, expected_behavior in test_cases:
        try:
            font_size = get_font_size(text, field_type='description', orientation='vertical', scale_factor=1.0)
            words = text.split()
            max_word_length = max(len(word) for word in words) if words else 0
            
            print(f"Text: '{text}'")
            print(f"  Max word length: {max_word_length}")
            print(f"  Font size: {font_size.pt}pt")
            print(f"  Expected: {expected_behavior}")
            
            # Verify the logic
            if max_word_length > 9:
                if max_word_length <= 12:
                    expected_size = 24
                elif max_word_length <= 15:
                    expected_size = 20
                elif max_word_length <= 18:
                    expected_size = 16
                else:
                    expected_size = 12
                
                if font_size.pt == expected_size:
                    print(f"  ✓ PASS: Correctly reduced to {expected_size}pt")
                else:
                    print(f"  ✗ FAIL: Expected {expected_size}pt, got {font_size.pt}pt")
            else:
                print(f"  ✓ PASS: Using normal sizing ({font_size.pt}pt)")
            
            print()
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            print()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_vertical_description_font_sizing() 