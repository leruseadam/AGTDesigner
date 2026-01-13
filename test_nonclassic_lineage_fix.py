#!/usr/bin/env python3
"""
Test the nonclassic lineage normalization logic.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.constants import normalize_lineage_for_product_type, CLASSIC_TYPES

def test_classic_types():
    """Test classic types get HYBRID when given MIXED."""
    print("\n" + "=" * 80)
    print("TEST: Classic Types - MIXED/THC should convert to HYBRID")
    print("=" * 80)
    
    test_cases = [
        ("Flower", "MIXED", "HYBRID"),
        ("Flower", "THC", "HYBRID"),
        ("Pre-Roll", "MIXED", "HYBRID"),
        ("Concentrate", "MIXED", "HYBRID"),
        ("Vape Cartridge", "THC", "HYBRID"),
        ("Flower", "SATIVA", "SATIVA"),  # Should preserve
        ("Flower", "INDICA", "INDICA"),  # Should preserve
        ("Flower", "CBD", "CBD"),  # Should preserve
    ]
    
    all_passed = True
    for product_type, input_lineage, expected in test_cases:
        result = normalize_lineage_for_product_type(input_lineage, product_type)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_passed = False
        print(f"{status} {product_type:20} | {input_lineage:15} → {result:15} (expected: {expected})")
    
    return all_passed

def test_nonclassic_types():
    """Test nonclassic types get MIXED when given classic lineages."""
    print("\n" + "=" * 80)
    print("TEST: Nonclassic Types - Classic lineages should convert to MIXED")
    print("=" * 80)
    
    test_cases = [
        ("Edible (Solid)", "SATIVA", "MIXED"),
        ("Edible (Solid)", "INDICA", "MIXED"),
        ("Edible (Solid)", "HYBRID", "MIXED"),
        ("Edible (Solid)", "HYBRID/SATIVA", "MIXED"),
        ("Tincture", "SATIVA", "MIXED"),
        ("Topical", "INDICA", "MIXED"),
        ("Capsule", "HYBRID", "MIXED"),
        ("Edible (Solid)", "CBD", "CBD"),  # Should preserve
        ("Edible (Solid)", "MIXED", "MIXED"),  # Should preserve
        ("Edible (Solid)", "THC", "MIXED"),  # THC is same as MIXED
        ("Paraphernalia", "PARAPHERNALIA", "PARAPHERNALIA"),  # Should preserve
    ]
    
    all_passed = True
    for product_type, input_lineage, expected in test_cases:
        result = normalize_lineage_for_product_type(input_lineage, product_type)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_passed = False
        print(f"{status} {product_type:20} | {input_lineage:15} → {result:15} (expected: {expected})")
    
    return all_passed

def test_mixed_products():
    """Test products that could be confusing."""
    print("\n" + "=" * 80)
    print("TEST: Edge Cases")
    print("=" * 80)
    
    test_cases = [
        ("Flower", "MIXED", "HYBRID", "Classic type with MIXED should become HYBRID"),
        ("Edible (Solid)", "INDICA", "MIXED", "Nonclassic with INDICA should become MIXED"),
        ("Tincture", "HYBRID/SATIVA", "MIXED", "Nonclassic with HYBRID/SATIVA should become MIXED"),
        ("CBD Gummies", "CBD", "CBD", "CBD should be preserved for any type"),
        ("", "SATIVA", "HYBRID", "Empty product type defaults to HYBRID"),
    ]
    
    all_passed = True
    for product_type, input_lineage, expected, description in test_cases:
        result = normalize_lineage_for_product_type(input_lineage, product_type)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_passed = False
        print(f"{status} {description}")
        print(f"   {product_type or 'Empty':20} | {input_lineage:15} → {result:15} (expected: {expected})")
    
    return all_passed

if __name__ == '__main__':
    print("\n╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  NONCLASSIC LINEAGE NORMALIZATION TEST".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    classic_passed = test_classic_types()
    nonclassic_passed = test_nonclassic_types()
    edge_passed = test_mixed_products()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Classic Types Test:    {'✅ PASSED' if classic_passed else '❌ FAILED'}")
    print(f"Nonclassic Types Test: {'✅ PASSED' if nonclassic_passed else '❌ FAILED'}")
    print(f"Edge Cases Test:       {'✅ PASSED' if edge_passed else '❌ FAILED'}")
    
    if classic_passed and nonclassic_passed and edge_passed:
        print("\n🎉 ALL TESTS PASSED! Lineage normalization is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED! Review the output above.")
        sys.exit(1)
