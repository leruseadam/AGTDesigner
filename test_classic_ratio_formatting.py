#!/usr/bin/env python3
"""
Test script to see how format_classic_ratio works with different inputs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
import re

def test_format_classic_ratio():
    """Test the format_classic_ratio method with different inputs."""
    
    # Create a template processor instance
    processor = TemplateProcessor('vertical', None)
    
    test_inputs = [
        "THC 10mg CBD 5mg CBG 2mg",
        "THC 10% CBD 5%",
        "10% THC 5% CBD",
        "THC: 10% CBD: 5%",
        "THC 15mg CBD 3mg",
        "15mg THC 3mg CBD",
        "THC 20%",
        "CBD 10%",
        "Some other text",
        ""
    ]
    
    print("Testing format_classic_ratio method:")
    print("=" * 50)
    
    for test_input in test_inputs:
        result = processor.format_classic_ratio(test_input, {})
        print(f"Input:  '{test_input}'")
        print(f"Output: '{result}'")
        print(f"Repr:   {repr(result)}")
        print("-" * 30)
    
    # Test the regex patterns directly
    print("\nTesting regex patterns directly:")
    print("=" * 50)
    
    text = "THC 10mg CBD 5mg CBG 2mg"
    
    thc_patterns = [
        r'THC[:\s]*([0-9.]+)%?',
        r'([0-9.]+)%?\s*THC',
        r'([0-9.]+)\s*THC'
    ]
    
    cbd_patterns = [
        r'CBD[:\s]*([0-9.]+)%?',
        r'([0-9.]+)%?\s*CBD',
        r'([0-9.]+)\s*CBD'
    ]
    
    print(f"Testing text: '{text}'")
    
    thc_value = None
    cbd_value = None
    
    # Extract THC value
    for i, pattern in enumerate(thc_patterns):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            thc_value = match.group(1)
            print(f"THC pattern {i+1} matched: {thc_value}")
            break
        else:
            print(f"THC pattern {i+1} no match")
    
    # Extract CBD value
    for i, pattern in enumerate(cbd_patterns):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cbd_value = match.group(1)
            print(f"CBD pattern {i+1} matched: {cbd_value}")
            break
        else:
            print(f"CBD pattern {i+1} no match")
    
    print(f"Final THC: {thc_value}, CBD: {cbd_value}")

if __name__ == "__main__":
    test_format_classic_ratio() 