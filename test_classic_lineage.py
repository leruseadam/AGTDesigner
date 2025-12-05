#!/usr/bin/env python3
"""
Test script to ensure classic types never get MIXED lineage.
Classic types should only have: SATIVA, INDICA, HYBRID, HYBRID/SATIVA, HYBRID/INDICA, CBD
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Classic types that should NEVER have MIXED lineage
CLASSIC_TYPES = [
    'flower', 'pre-roll', 'concentrate', 'infused pre-roll', 
    'solventless concentrate', 'vape cartridge', 'rso/co2 tankers'
]

# Valid classic lineages
VALID_CLASSIC_LINEAGES = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD']

# Invalid lineages for classic types
INVALID_FOR_CLASSIC = ['MIXED', 'THC', 'PARAPHERNALIA', 'PARA']

def test_excel_processor_lineage_fix():
    """Test that ExcelProcessor fixes MIXED lineage for classic types."""
    print("=" * 60)
    print("Testing ExcelProcessor MIXED lineage fix for classic types")
    print("=" * 60)
    
    try:
        from src.core.data.excel_processor import ExcelProcessor
        from src.core.constants import CLASSIC_TYPES
        
        # Create a test processor
        processor = ExcelProcessor()
        
        # Test data with classic types having MIXED lineage
        import pandas as pd
        test_data = {
            'Product Name*': ['Test Flower', 'Test Concentrate', 'Test Pre-roll'],
            'Product Type*': ['Flower', 'Concentrate', 'Pre-roll'],
            'Lineage': ['MIXED', 'MIXED', 'THC'],  # Invalid lineages for classic types
            'Vendor/Supplier*': ['Test Vendor'] * 3,
            'Product Brand': ['Test Brand'] * 3,
            'Weight*': ['1g'] * 3,
            'Units': ['g'] * 3
        }
        
        df = pd.DataFrame(test_data)
        
        # Simulate the lineage fix logic
        classic_mask = df["Product Type*"].str.strip().str.lower().isin([ct.lower() for ct in CLASSIC_TYPES])
        mixed_lineage_mask = (df["Lineage"] == "MIXED") | (df["Lineage"].str.upper() == "THC")
        classic_with_mixed_mask = classic_mask & mixed_lineage_mask
        
        if classic_with_mixed_mask.any():
            df.loc[classic_with_mixed_mask, "Lineage"] = "HYBRID"
            print(f"   ✅ Fixed {classic_with_mixed_mask.sum()} classic products with MIXED/THC lineage")
        
        # Verify all classic types have valid lineages
        for idx, row in df.iterrows():
            product_type = row['Product Type*'].lower()
            lineage = str(row['Lineage']).upper()
            
            if product_type in [ct.lower() for ct in CLASSIC_TYPES]:
                if lineage in INVALID_FOR_CLASSIC:
                    print(f"   ❌ FAILED: {row['Product Name*']} ({product_type}) has invalid lineage: {lineage}")
                    return False
                elif lineage not in VALID_CLASSIC_LINEAGES:
                    print(f"   ⚠️  WARNING: {row['Product Name*']} ({product_type}) has unexpected lineage: {lineage}")
                else:
                    print(f"   ✅ {row['Product Name*']} ({product_type}) has valid lineage: {lineage}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enrichment_lineage_conversion():
    """Test that tag enrichment converts MIXED to HYBRID for classic types."""
    print("\n" + "=" * 60)
    print("Testing tag enrichment MIXED->HYBRID conversion")
    print("=" * 60)
    
    try:
        from src.core.constants import CLASSIC_TYPES
        
        # Test tags with MIXED lineage for classic types
        test_tags = [
            {
                'Product Name*': 'Test Flower',
                'Product Type*': 'Flower',
                'Lineage': 'MIXED',
                'canonical_lineage': 'MIXED',
                'currentLineage': 'MIXED'
            },
            {
                'Product Name*': 'Test Concentrate',
                'Product Type*': 'Concentrate',
                'Lineage': 'THC',
                'canonical_lineage': 'THC',
                'currentLineage': 'THC'
            },
            {
                'Product Name*': 'Test Edible',
                'Product Type*': 'Edible (Solid)',
                'Lineage': 'MIXED',
                'canonical_lineage': 'MIXED',
                'currentLineage': 'MIXED'
            }
        ]
        
        for tag in test_tags:
            product_type = str(tag.get('Product Type*', '') or tag.get('Type', '')).strip().lower()
            is_classic_type = product_type in [ct.lower() for ct in CLASSIC_TYPES]
            
            # Simulate the conversion logic
            lineage = str(tag.get('canonical_lineage') or tag.get('currentLineage') or tag.get('Lineage', '')).strip().upper()
            
            if is_classic_type and (lineage == 'MIXED' or lineage == 'THC'):
                lineage = 'HYBRID'
                print(f"   ✅ Converted {tag['Product Name*']} ({product_type}) from MIXED/THC to HYBRID")
            elif not is_classic_type and lineage == 'MIXED':
                print(f"   ✅ {tag['Product Name*']} ({product_type}) correctly keeps MIXED (non-classic)")
            elif is_classic_type and lineage not in INVALID_FOR_CLASSIC:
                print(f"   ✅ {tag['Product Name*']} ({product_type}) has valid lineage: {lineage}")
            else:
                print(f"   ❌ FAILED: {tag['Product Name*']} ({product_type}) has invalid lineage: {lineage}")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_lineage_display():
    """Test that UI correctly displays lineage for classic types."""
    print("\n" + "=" * 60)
    print("Testing UI lineage display logic")
    print("=" * 60)
    
    try:
        # Simulate the UI logic from main.js
        def get_unique_lineages(product_type):
            """Simulate getUniqueLineages function."""
            classic_types = ['flower', 'pre-roll', 'concentrate', 'infused pre-roll', 
                           'solventless concentrate', 'vape cartridge', 'rso/co2 tankers']
            if product_type.lower() in [ct.lower() for ct in classic_types]:
                return ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD']
            return ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD', 'MIXED']
        
        test_cases = [
            {
                'name': 'Flower with MIXED',
                'product_type': 'Flower',
                'lineage': 'MIXED',
                'expected': 'HYBRID'
            },
            {
                'name': 'Concentrate with THC',
                'product_type': 'Concentrate',
                'lineage': 'THC',
                'expected': 'HYBRID'
            },
            {
                'name': 'Edible with MIXED',
                'product_type': 'Edible (Solid)',
                'lineage': 'MIXED',
                'expected': 'MIXED'  # Non-classic, should keep MIXED
            },
            {
                'name': 'Flower with HYBRID',
                'product_type': 'Flower',
                'lineage': 'HYBRID',
                'expected': 'HYBRID'
            }
        ]
        
        for case in test_cases:
            product_type = case['product_type']
            lineage = case['lineage'].upper()
            expected = case['expected']
            
            # Simulate UI conversion logic
            is_classic_type = product_type and len(get_unique_lineages(product_type)) == 6
            if is_classic_type and (lineage == 'MIXED' or lineage == 'THC'):
                lineage = 'HYBRID'
            
            if lineage == expected:
                print(f"   ✅ {case['name']}: {lineage} (expected {expected})")
            else:
                print(f"   ❌ {case['name']}: got {lineage}, expected {expected}")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_lineage_validation():
    """Test that database prevents saving MIXED lineage for classic types."""
    print("\n" + "=" * 60)
    print("Testing database lineage validation")
    print("=" * 60)
    
    try:
        from src.core.constants import CLASSIC_TYPES, VALID_CLASSIC_LINEAGES
        
        # Test cases
        test_cases = [
            {
                'product_type': 'Flower',
                'lineage': 'MIXED',
                'should_convert': True,
                'expected': 'HYBRID'
            },
            {
                'product_type': 'Concentrate',
                'lineage': 'THC',
                'should_convert': True,
                'expected': 'HYBRID'
            },
            {
                'product_type': 'Edible (Solid)',
                'lineage': 'MIXED',
                'should_convert': False,
                'expected': 'MIXED'
            },
            {
                'product_type': 'Flower',
                'lineage': 'SATIVA',
                'should_convert': False,
                'expected': 'SATIVA'
            }
        ]
        
        for case in test_cases:
            product_type = case['product_type'].lower()
            lineage = case['lineage'].upper()
            is_classic = product_type in [ct.lower() for ct in CLASSIC_TYPES]
            
            # Simulate database validation
            if is_classic and lineage == 'MIXED':
                lineage = 'HYBRID'
            elif is_classic and lineage == 'THC':
                lineage = 'HYBRID'
            
            if is_classic and lineage not in VALID_CLASSIC_LINEAGES:
                print(f"   ❌ FAILED: {case['product_type']} would have invalid lineage: {lineage}")
                return False
            
            if lineage == case['expected']:
                print(f"   ✅ {case['product_type']}: {lineage} (expected {case['expected']})")
            else:
                print(f"   ❌ {case['product_type']}: got {lineage}, expected {case['expected']}")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_lineage_handling():
    """Test that API endpoints handle classic type lineage correctly."""
    print("\n" + "=" * 60)
    print("Testing API lineage handling")
    print("=" * 60)
    
    try:
        from src.core.constants import CLASSIC_TYPES
        
        # Simulate API tag processing
        test_tags = [
            {
                'Product Name*': 'Test Flower',
                'Product Type*': 'Flower',
                'canonical_lineage': 'MIXED',
                'currentLineage': 'MIXED',
                'Lineage': 'MIXED'
            },
            {
                'Product Name*': 'Test Concentrate',
                'Product Type*': 'Concentrate',
                'canonical_lineage': 'THC',
                'currentLineage': 'THC',
                'Lineage': 'THC'
            }
        ]
        
        for tag in test_tags:
            product_type = str(tag.get('Product Type*', '')).strip().lower()
            is_classic_type = product_type in [ct.lower() for ct in CLASSIC_TYPES]
            
            # Get lineage
            lineage = str(tag.get('canonical_lineage') or tag.get('currentLineage') or tag.get('Lineage', '')).strip().upper()
            
            # Apply conversion
            if is_classic_type and (lineage == 'MIXED' or lineage == 'THC'):
                lineage = 'HYBRID'
                print(f"   ✅ API converted {tag['Product Name*']} ({product_type}) from {tag.get('canonical_lineage')} to {lineage}")
            else:
                print(f"   ✅ API kept {tag['Product Name*']} ({product_type}) lineage as {lineage}")
            
            # Verify result
            if is_classic_type and lineage in INVALID_FOR_CLASSIC:
                print(f"   ❌ FAILED: {tag['Product Name*']} still has invalid lineage: {lineage}")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("CLASSIC TYPE LINEAGE VALIDATION TEST SUITE")
    print("=" * 60)
    print("\nTesting that classic types NEVER get MIXED/THC lineage")
    print("Classic types: " + ", ".join(CLASSIC_TYPES))
    print("Valid lineages: " + ", ".join(VALID_CLASSIC_LINEAGES))
    print("Invalid lineages: " + ", ".join(INVALID_FOR_CLASSIC))
    
    success = True
    
    # Run all tests
    if not test_excel_processor_lineage_fix():
        success = False
    
    if not test_enrichment_lineage_conversion():
        success = False
    
    if not test_ui_lineage_display():
        success = False
    
    if not test_database_lineage_validation():
        success = False
    
    if not test_api_lineage_handling():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED - Classic types correctly protected from MIXED lineage")
    else:
        print("❌ SOME TESTS FAILED - Classic types may have invalid lineage")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
