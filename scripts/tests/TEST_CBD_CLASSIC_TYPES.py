#!/usr/bin/env python3
"""
Test script to understand how CBD classic types are being processed.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cbd_classic_type_classification():
    """Test how CBD classic types are being classified."""
    print("=== TESTING CBD CLASSIC TYPE CLASSIFICATION ===")
    
    # Import the constants
    from src.core.constants import CLASSIC_TYPES, VALID_CLASSIC_LINEAGES
    
    print("Current CLASSIC_TYPES:")
    for classic_type in sorted(CLASSIC_TYPES):
        print(f"  - {classic_type}")
    
    print("\nCurrent VALID_CLASSIC_LINEAGES:")
    for lineage in sorted(VALID_CLASSIC_LINEAGES):
        print(f"  - {lineage}")
    
    # Test CBD flower scenarios
    test_products = [
        {
            'product_name': 'CBD Flower - Charlotte\'s Web',
            'product_type': 'Flower',
            'lineage': 'CBD',
            'expected_classification': 'classic'
        },
        {
            'product_name': 'THC Flower - Blue Dream',
            'product_type': 'Flower',
            'lineage': 'HYBRID',
            'expected_classification': 'classic'
        },
        {
            'product_name': 'CBD Pre-Roll',
            'product_type': 'Pre-roll',
            'lineage': 'CBD',
            'expected_classification': 'classic'
        },
        {
            'product_name': 'CBD Gummies',
            'product_type': 'Edible (Solid)',
            'lineage': 'CBD',
            'expected_classification': 'non-classic'
        }
    ]
    
    print("\nTesting product classifications:")
    for product in test_products:
        product_type = product['product_type'].lower()
        lineage = product['lineage']
        
        # Check if product type is classic
        is_classic_type = product_type in [ct.lower() for ct in CLASSIC_TYPES]
        
        # Check if lineage is valid for classic types
        is_valid_classic_lineage = lineage in VALID_CLASSIC_LINEAGES
        
        print(f"\n  Product: {product['product_name']}")
        print(f"    Product Type: {product['product_type']} -> {'Classic' if is_classic_type else 'Non-Classic'}")
        print(f"    Lineage: {lineage} -> {'Valid Classic' if is_valid_classic_lineage else 'Invalid Classic'}")
        print(f"    Expected: {product['expected_classification']}")
        
        # Determine actual classification
        if is_classic_type and is_valid_classic_lineage:
            actual_classification = 'classic'
        else:
            actual_classification = 'non-classic'
        
        if actual_classification == product['expected_classification']:
            print(f"    ✅ CORRECT: {actual_classification}")
        else:
            print(f"    ❌ INCORRECT: Expected {product['expected_classification']}, got {actual_classification}")

def test_template_processing_logic():
    """Test the template processing logic for CBD products."""
    print("\n=== TESTING TEMPLATE PROCESSING LOGIC ===")
    
    # Simulate template processing logic
    from src.core.constants import CLASSIC_TYPES
    
    def simulate_template_processing(product_type, lineage):
        """Simulate how template processing would handle a product."""
        is_classic_type = product_type.lower() in [ct.lower() for ct in CLASSIC_TYPES]
        
        if is_classic_type:
            # Classic types should show lineage, not brand
            return {
                'styling': 'classic',
                'shows': 'lineage',
                'lineage_display': lineage,
                'brand_display': None
            }
        else:
            # Non-classic types should show brand, not lineage
            return {
                'styling': 'non-classic',
                'shows': 'brand',
                'lineage_display': None,
                'brand_display': 'BRAND_NAME'
            }
    
    test_cases = [
        ('Flower', 'CBD'),
        ('Flower', 'HYBRID'),
        ('Pre-roll', 'CBD'),
        ('Edible (Solid)', 'CBD'),
        ('Vape Cartridge', 'HYBRID')
    ]
    
    print("Template processing simulation:")
    for product_type, lineage in test_cases:
        result = simulate_template_processing(product_type, lineage)
        print(f"\n  {product_type} with {lineage} lineage:")
        print(f"    Styling: {result['styling']}")
        print(f"    Shows: {result['shows']}")
        if result['lineage_display']:
            print(f"    Lineage Display: {result['lineage_display']}")
        if result['brand_display']:
            print(f"    Brand Display: {result['brand_display']}")

if __name__ == "__main__":
    test_cbd_classic_type_classification()
    test_template_processing_logic()
    print("\n=== CBD CLASSIC TYPE TEST COMPLETE ===")
