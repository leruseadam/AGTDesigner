#!/usr/bin/env python3
"""
Test script to verify Vape Cartridge lineage alignment logic.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.constants import CLASSIC_TYPES

def test_vape_cartridge_classification():
    """Test if Vape Cartridge is properly classified as a classic type."""
    print("Testing Vape Cartridge classification...")
    print(f"CLASSIC_TYPES: {CLASSIC_TYPES}")
    
    # Test various vape cartridge product type variations
    test_cases = [
        "vape cartridge",
        "Vape Cartridge", 
        "VAPE CARTRIDGE",
        "Vape cartridge",
        "vape Cartridge"
    ]
    
    for product_type in test_cases:
        is_classic = product_type.lower() in CLASSIC_TYPES
        print(f"Product Type: '{product_type}' -> is_classic: {is_classic}")
    
    # Test the specific check used in the code
    product_type = "Vape Cartridge"
    is_classic_product = product_type and product_type.lower() in CLASSIC_TYPES
    print(f"\nSpecific test: '{product_type}' -> is_classic_product: {is_classic_product}")
    
    return is_classic_product

def test_lineage_alignment_logic():
    """Test the lineage alignment logic for Vape Cartridge products."""
    print("\nTesting lineage alignment logic...")
    
    # Simulate the logic from template_processor.py
    product_type = "Vape Cartridge"
    
    # First check (lines 2483-2484)
    is_classic_product = product_type and product_type.lower() in CLASSIC_TYPES
    print(f"First check - product_type: '{product_type}', is_classic_product: {is_classic_product}")
    
    # Second check (lines 2750-2751) - fallback logic
    if product_type:
        is_classic_product_fallback = product_type.lower() in CLASSIC_TYPES
        print(f"Fallback check - product_type: '{product_type}', is_classic_product: {is_classic_product_fallback}")
    
    # Test with different product type formats
    test_formats = [
        "Vape Cartridge",
        "vape cartridge", 
        "VAPE CARTRIDGE",
        "Vape cartridge"
    ]
    
    print("\nTesting different product type formats:")
    for fmt in test_formats:
        is_classic = fmt.lower() in CLASSIC_TYPES
        print(f"  '{fmt}' -> is_classic: {is_classic}")

if __name__ == "__main__":
    print("=== Vape Cartridge Lineage Alignment Test ===")
    
    # Test classification
    is_classic = test_vape_cartridge_classification()
    
    # Test alignment logic
    test_lineage_alignment_logic()
    
    print(f"\n=== Result ===")
    print(f"Vape Cartridge should be treated as classic type: {is_classic}")
    print(f"Expected lineage alignment: {'LEFT' if is_classic else 'CENTER'}")
