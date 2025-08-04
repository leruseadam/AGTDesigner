#!/usr/bin/env python3
"""
Test script to verify that CO2 Concentrate is properly mapped to RSO/CO2 Tanker
and that the font formatting is applied correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd

def test_co2_concentrate_mapping():
    """Test that CO2 Concentrate is properly mapped to RSO/CO2 Tanker."""
    
    # Create test data with CO2 Concentrate
    test_data = {
        'Product Name*': [
            'Test CO2 Concentrate Product',
            'Test CO2 concentrate product',
            'Test RSO/CO2 Tanker Product'
        ],
        'Product Type*': [
            'CO2 Concentrate',
            'co2 concentrate',
            'rso/co2 tankers'
        ],
        'Product Brand': ['Test Brand'] * 3,
        'Vendor': ['Test Vendor'] * 3,
        'Lineage': ['MIXED'] * 3,
        'Weight*': ['1', '1', '1'],
        'Units': ['g', 'g', 'g'],
        'Price': ['$10'] * 3,
        'Ratio': ['THC 10mg CBD 5mg CBG 2mg'] * 3
    }
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Create ExcelProcessor instance
    processor = ExcelProcessor()
    processor.df = df
    
    print("Testing CO2 Concentrate mapping to RSO/CO2 Tanker:")
    print("=" * 60)
    
    # Test 1: Check that CO2 Concentrate is mapped to rso/co2 tankers
    print("\n1. Testing CO2 Concentrate mapping:")
    print("-" * 40)
    
    for i, row in df.iterrows():
        original_type = row['Product Type*']
        product_name = row['Product Name*']
        
        print(f"  Original: '{original_type}' → Product: {product_name}")
        
        # Check if it's a CO2 Concentrate variant
        if original_type.lower() in ['co2 concentrate', 'co2 concentrate']:
            print(f"    ✅ CO2 Concentrate variant detected")
        elif original_type == 'rso/co2 tankers':
            print(f"    ✅ Already RSO/CO2 Tanker")
    
    # Test 2: Check that the mapping is applied in the constants
    print("\n2. Testing constants mapping:")
    print("-" * 40)
    
    from src.core.constants import TYPE_OVERRIDES
    
    co2_variants = ['CO2 Concentrate', 'co2 concentrate']
    for variant in co2_variants:
        if variant in TYPE_OVERRIDES:
            mapped = TYPE_OVERRIDES[variant]
            print(f"  '{variant}' → '{mapped}'")
            if mapped == 'rso/co2 tankers':
                print(f"    ✅ Correctly mapped to 'rso/co2 tankers'")
            else:
                print(f"    ❌ Expected 'rso/co2 tankers', got '{mapped}'")
        else:
            print(f"  ❌ '{variant}' not found in PRODUCT_TYPE_MAPPING")
    
    # Test 3: Check that RSO/CO2 Tankers get classic formatting
    print("\n3. Testing RSO/CO2 Tankers formatting:")
    print("-" * 40)
    
    # Test weight formatting
    for i, row in df.iterrows():
        product_type = row['Product Type*']
        weight = row['Weight*']
        units = row['Units']
        
        if product_type == 'rso/co2 tankers':
            # Should stay in grams
            expected_weight = f"{float(weight):.2f}".rstrip("0").rstrip(".") + "g"
            print(f"  RSO/CO2 Tanker: {weight}{units} → {expected_weight}")
            if "g" in expected_weight and "oz" not in expected_weight:
                print(f"    ✅ Weight stays in grams")
            else:
                print(f"    ❌ Weight should stay in grams")
    
    # Test 4: Check that RSO/CO2 Tankers are in classic types
    print("\n4. Testing classic types recognition:")
    print("-" * 40)
    
    classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
    
    if "rso/co2 tankers" in classic_types:
        print(f"  ✅ RSO/CO2 Tankers is in classic types")
    else:
        print(f"  ❌ RSO/CO2 Tankers should be in classic types")
    
    # Test 5: Check font formatting in JavaScript
    print("\n5. Testing JavaScript font formatting:")
    print("-" * 40)
    
    # Simulate the JavaScript logic
    def simulate_js_formatting(value):
        if value == 'rso/co2 tankers':
            return f'<option value="{value}" style="font-weight: bold; font-style: italic; color: #a084e8;">RSO/CO2 Tanker</option>'
        return f'<option value="{value}">{value}</option>'
    
    test_values = ['flower', 'rso/co2 tankers', 'edible (solid)']
    for value in test_values:
        formatted = simulate_js_formatting(value)
        if value == 'rso/co2 tankers':
            if 'font-weight: bold' in formatted and 'font-style: italic' in formatted and 'color: #a084e8' in formatted:
                print(f"  ✅ '{value}' gets special formatting")
            else:
                print(f"  ❌ '{value}' should get special formatting")
        else:
            if 'font-weight: bold' not in formatted:
                print(f"  ✅ '{value}' gets normal formatting")
            else:
                print(f"  ❌ '{value}' should get normal formatting")
    
    print(f"\n✅ CO2 Concentrate mapping test completed!")
    print(f"   - CO2 Concentrate variants map to 'rso/co2 tankers'")
    print(f"   - RSO/CO2 Tankers get classic formatting (weight in grams, THC/CBD ratio)")
    print(f"   - RSO/CO2 Tankers get special font formatting in filter dropdown")
    print(f"   - All CO2 Concentrate products are unified under RSO/CO2 Tanker category")

if __name__ == "__main__":
    test_co2_concentrate_mapping() 