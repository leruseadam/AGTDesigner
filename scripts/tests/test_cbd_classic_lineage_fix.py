#!/usr/bin/env python3
"""
Test script to verify CBD classic type lineage fix.
This script tests that CBD classic types like 'CBD Huckleberry Web' get CBD lineage.
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from src.core.data.excel_processor import optimized_lineage_assignment
from src.core.constants import CLASSIC_TYPES

def test_cbd_classic_lineage_fix():
    """Test that CBD classic types get CBD lineage instead of HYBRID."""
    print("=== TESTING CBD CLASSIC TYPE LINEAGE FIX ===")
    
    # Create test data that matches the products shown in the Word document
    test_data = {
        'Product Name*': [
            'CBD Huckleberry Web - 1g',
            'Terpgasm - 1g', 
            'GMO - 1g',
            'Zade - 1g',
            'Hash Burger - 1g',
            'Grapefruit - 1g',
            'CBD Pre-Roll',
            'THC Flower - Blue Dream',
            'CBD Concentrate',
            'CBD Gummies'  # This should remain as edible
        ],
        'Product Type*': [
            'Flower',
            'Flower', 
            'Flower',
            'Flower',
            'Flower',
            'Flower',
            'Pre-Roll',
            'Flower',
            'Concentrate',
            'Edible (Solid)'
        ],
        'Product Strain': [
            'CBD Blend',
            'Terpgasm',
            'GMO',
            'Zade',
            'Hash Burger',
            'Grapefruit',
            'CBD Blend',
            'Blue Dream',
            'CBD Blend',
            'CBD Blend'
        ],
        'Lineage': [
            'HYBRID',  # Should become CBD
            'HYBRID',  # Should stay HYBRID
            'SATIVA',  # Should stay SATIVA
            'HYBRID',  # Should stay HYBRID  
            'HYBRID',  # Should stay HYBRID
            'SATIVA',  # Should stay SATIVA
            '',        # Should become CBD (empty lineage)
            'HYBRID',  # Should stay HYBRID
            '',        # Should become CBD (empty lineage)
            'MIXED'    # Should stay MIXED (edible)
        ]
    }
    
    df = pd.DataFrame(test_data)
    
    print("Original test data:")
    for i, row in df.iterrows():
        print(f"  {i+1}. {row['Product Name*']} ({row['Product Type*']}) - Lineage: {row['Lineage']}")
    
    # Apply the optimized lineage assignment
    product_types = df['Product Type*'].str.strip().str.lower()
    lineages = df['Lineage'].astype(str)
    classic_types = [ct.lower() for ct in CLASSIC_TYPES]
    
    print(f"\nClassic types: {classic_types}")
    
    # Apply the lineage assignment function
    result_lineages = optimized_lineage_assignment(df, product_types, lineages, classic_types)
    
    print("\nResults after CBD detection fix:")
    all_correct = True
    
    for i, (original_lineage, new_lineage) in enumerate(zip(df['Lineage'], result_lineages)):
        row = df.iloc[i]
        product_type = row['Product Type*']
        product_name = row['Product Name*']
        is_classic = product_type.lower() in classic_types
        
        print(f"\n  {i+1}. {product_name}")
        print(f"     Type: {product_type} ({'Classic' if is_classic else 'Non-Classic'})")
        print(f"     Original Lineage: '{original_lineage}' -> New Lineage: '{new_lineage}'")
        
        # Check expected results
        if 'CBD' in product_name and is_classic:
            expected = 'CBD'
            if new_lineage == expected:
                print(f"     ✅ CORRECT: CBD classic type got CBD lineage")
            else:
                print(f"     ❌ WRONG: Expected {expected}, got {new_lineage}")
                all_correct = False
        elif product_name == 'Terpgasm - 1g':
            expected = 'HYBRID'
            if new_lineage == expected:
                print(f"     ✅ CORRECT: Non-CBD classic type kept/got HYBRID lineage")
            else:
                print(f"     ❌ WRONG: Expected {expected}, got {new_lineage}")
                all_correct = False
        elif product_name == 'GMO - 1g':
            expected = 'SATIVA'
            if new_lineage == expected:
                print(f"     ✅ CORRECT: Non-CBD classic type kept original lineage")
            else:
                print(f"     ❌ WRONG: Expected {expected}, got {new_lineage}")
                all_correct = False
        elif product_name == 'CBD Gummies':
            # Edibles should be handled differently
            if new_lineage in ['CBD', 'MIXED']:
                print(f"     ✅ ACCEPTABLE: Edible got {new_lineage} lineage")
            else:
                print(f"     ❌ WRONG: Edible got unexpected lineage {new_lineage}")
                all_correct = False
    
    print(f"\n=== SUMMARY ===")
    if all_correct:
        print("✅ ALL TESTS PASSED - CBD classic type lineage fix is working correctly!")
        print("🎉 CBD products like 'CBD Huckleberry Web' will now get CBD lineage")
    else:
        print("❌ SOME TESTS FAILED - Fix needs more work")
    
    return all_correct

def test_edge_cases():
    """Test edge cases for CBD detection."""
    print("\n=== TESTING EDGE CASES ===")
    
    edge_cases = {
        'Product Name*': [
            'High CBD Flower - Charlotte\'s Web',
            'CBD-Rich Pre-Roll',
            'CDB Typo Flower',  # Typo - should not get CBD
            'Subcbd Flower',    # Substring - should not get CBD
            'flower cbd test',  # Lowercase - should get CBD
            'Full Spectrum CBD Concentrate'
        ],
        'Product Type*': [
            'Flower',
            'Pre-Roll', 
            'Flower',
            'Flower',
            'Flower',
            'Concentrate'
        ],
        'Product Strain': [
            'Charlotte\'s Web',
            'High CBD',
            'CDB Strain',
            'Unknown',
            'Test Strain',
            'Full Spectrum'
        ],
        'Lineage': ['', '', '', '', '', '']
    }
    
    df = pd.DataFrame(edge_cases)
    product_types = df['Product Type*'].str.strip().str.lower()
    lineages = df['Lineage'].astype(str)
    classic_types = [ct.lower() for ct in CLASSIC_TYPES]
    
    result_lineages = optimized_lineage_assignment(df, product_types, lineages, classic_types)
    
    for i, (product_name, new_lineage) in enumerate(zip(df['Product Name*'], result_lineages)):
        print(f"  {i+1}. '{product_name}' -> '{new_lineage}'")
        
        # Check if CBD detection is working correctly
        if re.search(r'\bCBD\b', product_name, re.IGNORECASE):
            if new_lineage == 'CBD':
                print(f"     ✅ CORRECT: CBD detected and assigned")
            else:
                print(f"     ❌ WRONG: CBD should have been detected")
        else:
            if new_lineage != 'CBD':
                print(f"     ✅ CORRECT: No CBD detected, got default lineage")
            else:
                print(f"     ❌ WRONG: CBD detected where it shouldn't be")

if __name__ == "__main__":
    success = test_cbd_classic_lineage_fix()
    test_edge_cases()
    
    print(f"\n=== CBD CLASSIC TYPE LINEAGE FIX TEST COMPLETE ===")
    
    if success:
        print("🎯 The fix should now properly assign CBD lineage to classic products with 'CBD' in the name")
        print("📋 Products like 'CBD Huckleberry Web - 1g' will show yellow CBD lineage instead of green HYBRID")
        print("🔧 Make sure to restart the application to apply the changes")
    
    sys.exit(0 if success else 1)