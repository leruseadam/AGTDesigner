#!/usr/bin/env python3
"""
Test script to verify that Alcohol/Ethanol Extract gets normalized to rso/co2 tankers.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd

def test_product_type_normalization():
    """Test that Alcohol/Ethanol Extract gets normalized correctly."""
    
    # Create test data
    test_data = {
        'Product Name*': [
            'Test Alcohol/Ethanol Extract',
            'Test alcohol/ethanol extract', 
            'Test Alcohol Ethanol Extract',
            'Test c02/ethanol extract',
            'Test CO2 Concentrate',
            'Test co2 concentrate',
            'Test Flower'
        ],
        'Product Type*': [
            'Alcohol/Ethanol Extract',
            'alcohol/ethanol extract',
            'Alcohol Ethanol Extract', 
            'c02/ethanol extract',
            'CO2 Concentrate',
            'co2 concentrate',
            'Flower'
        ],
        'Product Brand': ['Test Brand'] * 7,
        'Vendor': ['Test Vendor'] * 7,
        'Lineage': ['MIXED'] * 7,
        'Weight*': ['1'] * 7,
        'Units': ['g'] * 7,
        'Price': ['$10'] * 7
    }
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Create ExcelProcessor instance
    processor = ExcelProcessor()
    processor.df = df.copy()
    
    # Apply the normalization logic manually
    from src.core.constants import TYPE_OVERRIDES
    processor.df["Product Type*"] = processor.df["Product Type*"].replace(TYPE_OVERRIDES)
    
    print("Testing product type normalization:")
    print("=" * 50)
    
    for i, (original, normalized) in enumerate(zip(test_data['Product Type*'], processor.df['Product Type*'])):
        print(f"\nTest {i+1}:")
        print(f"  Original: '{original}'")
        print(f"  Normalized: '{normalized}'")
        
        if original in ['Alcohol/Ethanol Extract', 'alcohol/ethanol extract', 'Alcohol Ethanol Extract', 'c02/ethanol extract', 'CO2 Concentrate', 'co2 concentrate']:
            if normalized == 'rso/co2 tankers':
                print(f"  ✅ PASS: Correctly normalized to 'rso/co2 tankers'")
            else:
                print(f"  ❌ FAIL: Expected 'rso/co2 tankers', got '{normalized}'")
        elif original == 'Flower':
            if normalized == 'Flower':
                print(f"  ✅ PASS: Unchanged (not in TYPE_OVERRIDES)")
            else:
                print(f"  ❌ FAIL: Should remain unchanged")
    
    # Test that the normalized types are recognized as edible types
    print(f"\n" + "=" * 50)
    print("Testing edible type recognition:")
    
    edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule", "rso/co2 tankers"}
    
    for product_type in processor.df['Product Type*'].unique():
        is_edible = product_type.lower() in {et.lower() for et in edible_types}
        print(f"  '{product_type}': {'✅ Edible' if is_edible else '❌ Not Edible'}")

if __name__ == "__main__":
    test_product_type_normalization() 