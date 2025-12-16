#!/usr/bin/env python3
"""
Test script to verify the CBD classic type fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd

def test_cbd_classic_type_fix():
    """Test the CBD classic type fix."""
    print("=== TESTING CBD CLASSIC TYPE FIX ===")
    
    # Import the function we fixed
    from src.core.data.excel_processor import optimized_lineage_assignment
    from src.core.constants import CLASSIC_TYPES
    
    # Create test data
    test_data = {
        'Product Type*': ['Flower', 'Flower', 'Pre-roll', 'Edible (Solid)', 'Vape Cartridge'],
        'Product Strain': ['CBD Blend', 'Blue Dream', 'CBD Blend', 'CBD Blend', 'CBD Blend'],
        'Lineage': ['', 'HYBRID', '', '', ''],
        'Product Name*': ['CBD Flower - Charlotte\'s Web', 'THC Flower - Blue Dream', 'CBD Pre-Roll', 'CBD Gummies', 'CBD Vape Cart']
    }
    
    df = pd.DataFrame(test_data)
    
    print("Test data:")
    for i, row in df.iterrows():
        print(f"  {i+1}. {row['Product Name*']}")
        print(f"     Type: {row['Product Type*']}, Strain: {row['Product Strain']}, Original Lineage: '{row['Lineage']}'")
    
    # Apply the lineage assignment function
    product_types = df['Product Type*'].astype(str)
    lineages = df['Lineage'].astype(str)
    classic_types = [ct.lower() for ct in CLASSIC_TYPES]
    
    result_lineages = optimized_lineage_assignment(df, product_types, lineages, classic_types)
    
    print("\nResults after lineage assignment:")
    for i, (original_lineage, new_lineage) in enumerate(zip(df['Lineage'], result_lineages)):
        row = df.iloc[i]
        product_type = row['Product Type*']
        is_classic = product_type.lower() in classic_types
        
        print(f"  {i+1}. {row['Product Name*']}")
        print(f"     Type: {product_type} ({'Classic' if is_classic else 'Non-Classic'})")
        print(f"     Original Lineage: '{original_lineage}' -> New Lineage: '{new_lineage}'")
        
        # Verify expected results
        if row['Product Name*'] == 'CBD Flower - Charlotte\'s Web':
            expected = 'CBD'
            if new_lineage == expected:
                print(f"     ✅ CORRECT: CBD flower got CBD lineage (classic styling)")
            else:
                print(f"     ❌ WRONG: Expected {expected}, got {new_lineage}")
        
        elif row['Product Name*'] == 'CBD Pre-Roll':
            expected = 'CBD'
            if new_lineage == expected:
                print(f"     ✅ CORRECT: CBD pre-roll got CBD lineage (classic styling)")
            else:
                print(f"     ❌ WRONG: Expected {expected}, got {new_lineage}")
        
        elif row['Product Name*'] == 'THC Flower - Blue Dream':
            expected = 'HYBRID'
            if new_lineage == expected:
                print(f"     ✅ CORRECT: THC flower kept original lineage")
            else:
                print(f"     ❌ WRONG: Expected {expected}, got {new_lineage}")
        
        elif row['Product Name*'] == 'CBD Gummies':
            # Edibles should be more conservative
            if new_lineage in ['CBD', 'MIXED']:
                print(f"     ✅ ACCEPTABLE: Edible got {new_lineage} (non-classic styling)")
            else:
                print(f"     ❌ WRONG: Edible got unexpected lineage {new_lineage}")
        
        elif row['Product Name*'] == 'CBD Vape Cart':
            expected = 'CBD'
            if new_lineage == expected:
                print(f"     ✅ CORRECT: CBD vape cart got CBD lineage (classic styling)")
            else:
                print(f"     ❌ WRONG: Expected {expected}, got {new_lineage}")

def test_styling_implications():
    """Test what the styling implications are."""
    print("\n=== STYLING IMPLICATIONS ===")
    
    from src.core.constants import CLASSIC_TYPES
    
    test_results = [
        ('CBD Flower', 'Flower', 'CBD', True),
        ('CBD Pre-Roll', 'Pre-roll', 'CBD', True),
        ('THC Flower', 'Flower', 'HYBRID', True),
        ('CBD Gummies', 'Edible (Solid)', 'MIXED', False),
        ('CBD Vape Cart', 'Vape Cartridge', 'CBD', True)
    ]
    
    print("Expected styling after fix:")
    for product_name, product_type, lineage, is_classic in test_results:
        if is_classic:
            styling = "Classic styling (shows lineage)"
            color = get_lineage_color(lineage)
        else:
            styling = "Non-classic styling (shows brand)"
            color = "blue"
        
        print(f"  {product_name}:")
        print(f"    Type: {product_type} ({'Classic' if is_classic else 'Non-Classic'})")
        print(f"    Lineage: {lineage}")
        print(f"    Styling: {styling}")
        print(f"    Color: {color}")

def get_lineage_color(lineage):
    """Get the color for a lineage."""
    colors = {
        'SATIVA': 'red',
        'INDICA': 'purple',
        'HYBRID': 'green', 
        'HYBRID/SATIVA': 'red',
        'HYBRID/INDICA': 'purple',
        'CBD': 'yellow',
        'MIXED': 'blue',
        'PARAPHERNALIA': 'pink'
    }
    return colors.get(lineage, 'unknown')

if __name__ == "__main__":
    test_cbd_classic_type_fix()
    test_styling_implications()
    print("\n=== CBD CLASSIC TYPE FIX TEST COMPLETE ===")
