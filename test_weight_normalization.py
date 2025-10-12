#!/usr/bin/env python3
"""
Test script for weight normalization during Excel uploads.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.data.weight_normalizer import WeightNormalizer

def test_weight_normalization():
    """Test various weight normalization scenarios."""
    
    normalizer = WeightNormalizer()
    
    print("="*80)
    print("TESTING WEIGHT NORMALIZATION")
    print("="*80)
    print()
    
    # Test cases
    test_cases = [
        # Constellation Moonshots
        {
            'name': 'Green Apple Moonshot by Constellation Cannabis - 100mg THC',
            'brand': 'Constellation Cannabis',
            'type': 'Edible (Solid)',
            'weight': '2.5',
            'unit': 'oz',
            'expected': ('1.7', 'oz')
        },
        {
            'name': 'Orange Moonshot by Constellation Cannabis - 100mg THC',
            'brand': 'Constellation Cannabis', 
            'type': 'Edible (Solid)',
            'weight': '2.5',
            'unit': 'oz',
            'expected': ('1.7', 'oz')
        },
        
        # Major beverages
        {
            'name': 'Major Beverage',
            'brand': 'Major',
            'type': 'Edible (Liquid)',
            'weight': '190',
            'unit': 'g',
            'expected': ('6.7', 'oz')
        },
        
        # Generic 190g conversion
        {
            'name': 'Some Product',
            'brand': 'Unknown Brand',
            'type': 'Edible (Solid)',
            'weight': '190',
            'unit': 'g',
            'expected': ('6.7', 'oz')
        },
        
        # Topicals (should convert to oz)
        {
            'name': 'Bath Salts',
            'brand': 'Brand',
            'type': 'Topical',
            'weight': '50',
            'unit': 'g',
            'expected': ('1.76', 'oz')
        },
        
        # Flower (should stay in grams)
        {
            'name': 'Blue Dream',
            'brand': 'Brand',
            'type': 'Flower',
            'weight': '3.5',
            'unit': 'oz',
            'expected': ('99.22', 'g')
        },
        
        # Concentrates (should stay in grams)
        {
            'name': 'Wax Product',
            'brand': 'Brand',
            'type': 'Concentrate',
            'weight': '1',
            'unit': 'oz',
            'expected': ('28.35', 'g')
        },
        
        # No change needed
        {
            'name': 'Regular Product',
            'brand': 'Brand',
            'type': 'Edible (Solid)',
            'weight': '2.0',
            'unit': 'oz',
            'expected': ('2.0', 'oz')
        },
        
        # New rules based on database analysis
        # Vape Cartridge (non-classic) - should be in oz
        {
            'name': 'Blue Dream Vape Cartridge',
            'brand': 'Brand',
            'type': 'Vape Cartridge',
            'weight': '28',
            'unit': 'g',
            'expected': ('0.99', 'oz')
        },
        
        # Topical (non-classic) - should be in oz
        {
            'name': 'CBD Cream',
            'brand': 'Brand',
            'type': 'Topical',
            'weight': '50',
            'unit': 'g',
            'expected': ('1.76', 'oz')
        },
        
        # Capsule (non-classic) - should be in oz
        {
            'name': 'CBD Capsules',
            'brand': 'Brand',
            'type': 'Capsule',
            'weight': '10',
            'unit': 'g',
            'expected': ('0.35', 'oz')
        },
        
        # Large Edible Solid - should be in oz
        {
            'name': 'Large Gummy Package',
            'brand': 'Brand',
            'type': 'Edible (Solid)',
            'weight': '50',
            'unit': 'g',
            'expected': ('1.76', 'oz')
        },
        
        # Paraphernalia - standardize "each" units
        {
            'name': 'Pipe',
            'brand': 'Brand',
            'type': 'Paraphernalia',
            'weight': '0',
            'unit': 'each',
            'expected': ('1', 'each')
        },
        
        # Pre-roll (classic) - should be in grams
        {
            'name': 'Blue Dream Pre-Roll',
            'brand': 'Brand',
            'type': 'Pre-Roll',
            'weight': '0.5',
            'unit': 'oz',
            'expected': ('14.17', 'g')
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"  Input: {test_case['weight']}{test_case['unit']} ({test_case['type']})")
        
        product_data = {
            'Product Name*': test_case['name'],
            'Product Brand': test_case['brand'],
            'Product Type*': test_case['type'],
            'Weight*': test_case['weight'],
            'Units': test_case['unit']
        }
        
        normalized_weight, normalized_unit = normalizer.normalize_weight(product_data)
        expected_weight, expected_unit = test_case['expected']
        
        print(f"  Expected: {expected_weight}{expected_unit}")
        print(f"  Got: {normalized_weight}{normalized_unit}")
        
        # Check if results match (with small tolerance for floating point)
        try:
            weight_match = abs(float(normalized_weight) - float(expected_weight)) < 0.01
            unit_match = normalized_unit == expected_unit
            
            if weight_match and unit_match:
                print(f"  ✅ PASS")
                passed += 1
            else:
                print(f"  ❌ FAIL")
                failed += 1
        except ValueError:
            print(f"  ❌ FAIL (invalid weight format)")
            failed += 1
        
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
    test_weight_normalization()
