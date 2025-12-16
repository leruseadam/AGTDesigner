#!/usr/bin/env python3
"""
Test script for smart Excel normalizer.
Tests comprehensive data cleaning and normalization.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.data.smart_excel_normalizer import SmartExcelNormalizer

def test_smart_excel_normalizer():
    """Test comprehensive smart Excel normalization."""
    
    normalizer = SmartExcelNormalizer()
    
    print("="*80)
    print("TESTING SMART EXCEL NORMALIZER")
    print("="*80)
    print()
    
    # Test cases covering all normalization aspects
    test_cases = [
        # Weight normalization (existing functionality)
        {
            'name': 'Green Apple Moonshot by Constellation Cannabis - 100mg THC',
            'brand': 'constellation cannabis',
            'type': 'Edible (Solid)',
            'weight': '2.5',
            'unit': 'oz',
            'expected_weight': '1.7',
            'expected_unit': 'oz'
        },
        
        # Product name cleaning
        {
            'name': 'Blue  Blue   Dream  Dream  Flower',
            'brand': 'Brand',
            'type': 'Flower',
            'weight': '3.5',
            'unit': 'g',
            'expected_name': 'Blue Dream Flower'
        },
        
        # Brand standardization
        {
            'name': 'Product by major',
            'brand': 'major',
            'type': 'Edible (Liquid)',
            'weight': '190',
            'unit': 'g',
            'expected_brand': 'Major'
        },
        
        # Product type correction
        {
            'name': 'CBD Gummy Bears',
            'brand': 'Brand',
            'type': 'edible solid',
            'weight': '50',
            'unit': 'g',
            'expected_type': 'Edible (Solid)'
        },
        
        # Price normalization
        {
            'name': 'Product',
            'brand': 'Brand',
            'type': 'Flower',
            'weight': '3.5',
            'unit': 'g',
            'price': '$25.99',
            'expected_price': '25.99'
        },
        
        # THC/CBD cleaning
        {
            'name': 'Product',
            'brand': 'Brand',
            'type': 'Flower',
            'weight': '3.5',
            'unit': 'g',
            'thc_content': '22.5%',
            'cbd_content': '1.2%',
            'expected_thc': '22.5',
            'expected_cbd': '1.2'
        },
        
        # Ratio standardization
        {
            'name': '1:1 Product',
            'brand': 'Brand',
            'type': 'Edible (Solid)',
            'weight': '10',
            'unit': 'g',
            'ratio': '1 to 1',
            'expected_ratio': '1:1'
        },
        
        # Missing brand extraction
        {
            'name': 'Blue Dream by Dank Czar - 25% THC',
            'brand': '',
            'type': 'Flower',
            'weight': '3.5',
            'unit': 'g',
            'expected_brand': 'Dank Czar'
        },
        
        # Missing type inference
        {
            'name': 'Chocolate Chip Cookies',
            'brand': 'Brand',
            'type': '',
            'weight': '50',
            'unit': 'g',
            'expected_type': 'Edible (Solid)'
        },
        
        # Barcode cleaning
        {
            'name': 'Product',
            'brand': 'Brand',
            'type': 'Flower',
            'weight': '3.5',
            'unit': 'g',
            'barcode': 'ABC-123-DEF',
            'expected_barcode': '123'
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        
        # Create product data
        product_data = {
            'Product Name*': test_case.get('name', ''),
            'Product Brand': test_case.get('brand', ''),
            'Product Type*': test_case.get('type', ''),
            'Weight*': test_case.get('weight', ''),
            'Units': test_case.get('unit', ''),
            'Price*': test_case.get('price', ''),
            'THC Content': test_case.get('thc_content', ''),
            'CBD Content': test_case.get('cbd_content', ''),
            'Ratio': test_case.get('ratio', ''),
            'Barcode*': test_case.get('barcode', '')
        }
        
        # Normalize
        normalized_data = normalizer.normalize_product_data(product_data)
        
        # Check results
        test_passed = True
        
        # Check weight normalization
        if 'expected_weight' in test_case:
            actual_weight = normalized_data.get('Weight*', '')
            expected_weight = test_case['expected_weight']
            if str(actual_weight) != expected_weight:
                print(f"  ❌ Weight: expected {expected_weight}, got {actual_weight}")
                test_passed = False
        
        if 'expected_unit' in test_case:
            actual_unit = normalized_data.get('Units', '')
            expected_unit = test_case['expected_unit']
            if actual_unit != expected_unit:
                print(f"  ❌ Unit: expected {expected_unit}, got {actual_unit}")
                test_passed = False
        
        # Check name cleaning
        if 'expected_name' in test_case:
            actual_name = normalized_data.get('Product Name*', '')
            expected_name = test_case['expected_name']
            if actual_name != expected_name:
                print(f"  ❌ Name: expected '{expected_name}', got '{actual_name}'")
                test_passed = False
        
        # Check brand standardization
        if 'expected_brand' in test_case:
            actual_brand = normalized_data.get('Product Brand', '')
            expected_brand = test_case['expected_brand']
            if actual_brand != expected_brand:
                print(f"  ❌ Brand: expected '{expected_brand}', got '{actual_brand}'")
                test_passed = False
        
        # Check type correction
        if 'expected_type' in test_case:
            actual_type = normalized_data.get('Product Type*', '')
            expected_type = test_case['expected_type']
            if actual_type != expected_type:
                print(f"  ❌ Type: expected '{expected_type}', got '{actual_type}'")
                test_passed = False
        
        # Check price normalization
        if 'expected_price' in test_case:
            actual_price = normalized_data.get('Price*', '')
            expected_price = test_case['expected_price']
            if actual_price != expected_price:
                print(f"  ❌ Price: expected '{expected_price}', got '{actual_price}'")
                test_passed = False
        
        # Check THC/CBD cleaning
        if 'expected_thc' in test_case:
            actual_thc = normalized_data.get('THC Content', '')
            expected_thc = test_case['expected_thc']
            if actual_thc != expected_thc:
                print(f"  ❌ THC: expected '{expected_thc}', got '{actual_thc}'")
                test_passed = False
        
        if 'expected_cbd' in test_case:
            actual_cbd = normalized_data.get('CBD Content', '')
            expected_cbd = test_case['expected_cbd']
            if actual_cbd != expected_cbd:
                print(f"  ❌ CBD: expected '{expected_cbd}', got '{actual_cbd}'")
                test_passed = False
        
        # Check ratio standardization
        if 'expected_ratio' in test_case:
            actual_ratio = normalized_data.get('Ratio', '')
            expected_ratio = test_case['expected_ratio']
            if actual_ratio != expected_ratio:
                print(f"  ❌ Ratio: expected '{expected_ratio}', got '{actual_ratio}'")
                test_passed = False
        
        # Check barcode cleaning
        if 'expected_barcode' in test_case:
            actual_barcode = normalized_data.get('Barcode*', '')
            expected_barcode = test_case['expected_barcode']
            if actual_barcode != expected_barcode:
                print(f"  ❌ Barcode: expected '{expected_barcode}', got '{actual_barcode}'")
                test_passed = False
        
        if test_passed:
            print(f"  ✅ PASS")
            passed += 1
        else:
            print(f"  ❌ FAIL")
            failed += 1
        
        print()
    
    # Test normalization statistics
    print("="*80)
    print("NORMALIZATION STATISTICS")
    print("="*80)
    stats = normalizer.get_normalization_stats()
    for stat_name, count in stats.items():
        print(f"{stat_name}: {count}")
    print()
    
    print("="*80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*80)
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed!")
        return False

if __name__ == "__main__":
    test_smart_excel_normalizer()
