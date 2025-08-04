#!/usr/bin/env python3
"""
Test script to debug vendor extraction logic in JSON matching
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor

def test_vendor_extraction():
    """Test the vendor extraction logic with sample data"""
    
    # Create a mock JSON matcher
    matcher = JSONMatcher(None)
    
    # Test cases from the Cultivera JSON
    test_cases = [
        "Medically Compliant - Dank Czar Rosin All-In-One - GMO - 1g",
        "Medically Compliant - Only B's - Amnesia Haze - 14g",
        "Medically Compliant - Flavour Bar - Blue Razz - 1g",
        "Flavour Stix - Blue Razz - 0.75g",
        "Zwish Infused Blunt - Passion Fruit Guava - 1g"
    ]
    
    print("Testing vendor extraction logic:")
    print("=" * 60)
    
    for test_case in test_cases:
        extracted_vendor = matcher._extract_vendor(test_case)
        print(f"Product: {test_case}")
        print(f"Extracted vendor: '{extracted_vendor}'")
        print("-" * 40)
    
    # Test cases from Excel data
    excel_cases = [
        "Banana OG Distillate Cartridge by Hustler's Ambition - 1g",
        "Gelato #41 Distillate Cartridge by Hustler's Ambition - 1g",
        "Orange Zee Distillate Cartridge by Hustler's Ambition - 1g"
    ]
    
    print("\nTesting vendor extraction from Excel format:")
    print("=" * 60)
    
    for test_case in excel_cases:
        extracted_vendor = matcher._extract_vendor(test_case)
        print(f"Product: {test_case}")
        print(f"Extracted vendor: '{extracted_vendor}'")
        print("-" * 40)

def test_key_term_extraction():
    """Test the key term extraction logic"""
    
    matcher = JSONMatcher(None)
    
    test_cases = [
        "Medically Compliant - Dank Czar Rosin All-In-One - GMO - 1g",
        "Banana OG Distillate Cartridge by Hustler's Ambition - 1g"
    ]
    
    print("\nTesting key term extraction:")
    print("=" * 60)
    
    for test_case in test_cases:
        key_terms = matcher._extract_key_terms(test_case)
        print(f"Product: {test_case}")
        print(f"Key terms: {key_terms}")
        print("-" * 40)

def test_normalization():
    """Test the normalization logic"""
    
    matcher = JSONMatcher(None)
    
    test_cases = [
        "Medically Compliant - Dank Czar Rosin All-In-One - GMO - 1g",
        "Banana OG Distillate Cartridge by Hustler's Ambition - 1g"
    ]
    
    print("\nTesting normalization:")
    print("=" * 60)
    
    for test_case in test_cases:
        normalized = matcher._normalize(test_case)
        print(f"Original: {test_case}")
        print(f"Normalized: '{normalized}'")
        print("-" * 40)

if __name__ == "__main__":
    test_vendor_extraction()
    test_key_term_extraction()
    test_normalization() 