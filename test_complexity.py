#!/usr/bin/env python3
"""
Test text complexity calculation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.utils.common import calculate_text_complexity

def test_complexity():
    """Test text complexity calculation"""
    
    test_vendor = "Test Vendor Company"
    
    print("=== Testing Text Complexity ===")
    print(f"Test vendor text: '{test_vendor}'")
    print(f"Text length: {len(test_vendor)} characters")
    print(f"Word count: {len(test_vendor.split())} words")
    
    # Test different complexity types
    for complexity_type in ['standard', 'description', 'mini']:
        comp = calculate_text_complexity(test_vendor, complexity_type)
        print(f"Complexity ({complexity_type}): {comp}")
    
    # Test what font size this should get
    print(f"\n=== Font Size Analysis ===")
    
    # Vendor config: [(10, 8), (20, 7), (30, 6), (40, 5), (50, 4), (inf, 3)]
    config = [(10, 8), (20, 7), (30, 6), (40, 5), (50, 4), (float('inf'), 3)]
    
    for complexity_type in ['standard', 'description', 'mini']:
        comp = calculate_text_complexity(test_vendor, complexity_type)
        print(f"\nComplexity type: {complexity_type}")
        print(f"Calculated complexity: {comp}")
        
        # Find which threshold this falls into
        for threshold, size in config:
            if comp < threshold:
                print(f"  Falls into threshold {threshold} -> {size}pt font")
                break
        else:
            print(f"  Falls into final threshold -> 3pt font")

if __name__ == "__main__":
    test_complexity() 