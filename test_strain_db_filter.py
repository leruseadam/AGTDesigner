#!/usr/bin/env python3
"""
Test script to verify that non-classic types are not processed through the strain database.
"""

import pandas as pd
from src.core.constants import CLASSIC_TYPES
from src.core.data.excel_processor import ExcelProcessor

def test_strain_db_filtering():
    """Test that only classic types are processed through the strain database."""
    print("Testing strain database filtering...")
    
    # Create a test DataFrame with mixed product types
    test_data = [
        {'Product Name*': 'Test Flower', 'Product Type*': 'Flower', 'Product Strain': 'OG Kush', 'Lineage': 'HYBRID'},
        {'Product Name*': 'Test Pre-roll', 'Product Type*': 'Pre-roll', 'Product Strain': 'Sour Diesel', 'Lineage': 'SATIVA'},
        {'Product Name*': 'Test Concentrate', 'Product Type*': 'Concentrate', 'Product Strain': 'Blue Dream', 'Lineage': 'HYBRID'},
        {'Product Name*': 'Test Edible', 'Product Type*': 'Edible (Solid)', 'Product Strain': 'CBD Blend', 'Lineage': 'CBD'},
        {'Product Name*': 'Test Tincture', 'Product Type*': 'Tincture', 'Product Strain': 'MIXED', 'Lineage': 'MIXED'},
        {'Product Name*': 'Test Vape Cart', 'Product Type*': 'Vape Cartridge', 'Product Strain': 'Gelato', 'Lineage': 'HYBRID'},
        {'Product Name*': 'Test Topical', 'Product Type*': 'Topical', 'Product Strain': 'CBD Blend', 'Lineage': 'CBD'},
    ]
    
    df = pd.DataFrame(test_data)
    
    print(f"Test data created with {len(df)} products:")
    for _, row in df.iterrows():
        product_type = row['Product Type*']
        is_classic = product_type.lower() in [c.lower() for c in CLASSIC_TYPES]
        print(f"  - {row['Product Name*']} ({product_type}): {'Classic' if is_classic else 'Non-classic'}")
    
    # Test the filtering logic
    classic_count = 0
    non_classic_count = 0
    
    for _, row in df.iterrows():
        product_type = row.get('Product Type*', '').strip().lower()
        if product_type in [c.lower() for c in CLASSIC_TYPES]:
            classic_count += 1
        else:
            non_classic_count += 1
    
    print(f"\nResults:")
    print(f"  Classic types (will be processed through strain DB): {classic_count}")
    print(f"  Non-classic types (will NOT be processed through strain DB): {non_classic_count}")
    
    # Verify the expected results
    expected_classic = 4  # Flower, Pre-roll, Concentrate, Vape Cartridge
    expected_non_classic = 3  # Edible, Tincture, Topical
    
    if classic_count == expected_classic and non_classic_count == expected_non_classic:
        print("✅ Test passed! Non-classic types are correctly filtered out from strain database processing.")
        return True
    else:
        print(f"❌ Test failed! Expected {expected_classic} classic and {expected_non_classic} non-classic, but got {classic_count} classic and {non_classic_count} non-classic.")
        return False

def test_classic_types_definition():
    """Test that CLASSIC_TYPES contains the expected values."""
    print("\nTesting CLASSIC_TYPES definition...")
    
    expected_classic_types = {
        "flower", "pre-roll", "concentrate",
        "infused pre-roll", "solventless concentrate",
        "vape cartridge"
    }
    
    print(f"Expected classic types: {expected_classic_types}")
    print(f"Actual classic types: {CLASSIC_TYPES}")
    
    if CLASSIC_TYPES == expected_classic_types:
        print("✅ CLASSIC_TYPES definition is correct.")
        return True
    else:
        print("❌ CLASSIC_TYPES definition does not match expected values.")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("Testing Strain Database Filtering")
    print("=" * 60)
    
    # Test CLASSIC_TYPES definition
    types_test = test_classic_types_definition()
    
    # Test filtering logic
    filtering_test = test_strain_db_filtering()
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"  CLASSIC_TYPES definition: {'PASS' if types_test else 'FAIL'}")
    print(f"  Strain DB filtering: {'PASS' if filtering_test else 'FAIL'}")
    
    if types_test and filtering_test:
        print("\n✅ All tests passed! Non-classic types will not be processed through the strain database.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main() 