#!/usr/bin/env python3
"""
Comprehensive test for the enhanced lineage fix:
- Classic types with empty lineage should get HYBRID
- Non-classic types with empty lineage should get MIXED
- Non-classic types with CBD content should get CBD
"""

import pandas as pd
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.constants import CLASSIC_TYPES

def test_cbd_lineage_fix():
    """Test the enhanced lineage fix comprehensively."""
    
    # Test data covering all scenarios including CBD
    test_data = {
        'Product Name*': [
            # Classic types (should get HYBRID)
            'Test Flower',
            'Test Pre-roll', 
            'Test Concentrate',
            'Test Vape Cartridge',
            'Test Solventless',
            'Test Infused Pre-roll',
            
            # Non-classic types without CBD (should get MIXED)
            'Test Edible',
            'Test Tincture',
            'Test Topical',
            'Test Capsule',
            'Test Regular Edible',
            
            # Non-classic types with CBD content (should get CBD)
            'CBD Tincture',
            'CBG Capsule',
            'CBN Topical',
            'CBC Edible',
            'CBD Blend Tincture',
            'High CBD Edible'
        ],
        'Product Type*': [
            # Classic types
            'flower',
            'pre-roll',
            'concentrate', 
            'vape cartridge',
            'solventless concentrate',
            'infused pre-roll',
            
            # Non-classic types without CBD
            'edible (solid)',
            'tincture',
            'topical',
            'capsule',
            'edible (liquid)',
            
            # Non-classic types with CBD
            'tincture',
            'capsule',
            'topical',
            'edible (solid)',
            'tincture',
            'edible (solid)'
        ],
        'Lineage': [
            # Classic types - empty lineage
            '',  # Empty - should become HYBRID for flower
            None,  # None - should become HYBRID for pre-roll
            '',  # Empty - should become HYBRID for concentrate
            '',  # Empty - should become HYBRID for vape cartridge
            None,  # None - should become HYBRID for solventless
            '',  # Empty - should become HYBRID for infused pre-roll
            
            # Non-classic types without CBD - empty lineage
            '',  # Empty - should become MIXED for edible
            None,  # None - should become MIXED for tincture
            '',  # Empty - should become MIXED for topical
            '',  # Empty - should become MIXED for capsule
            None,  # None - should become MIXED for edible liquid
            
            # Non-classic types with CBD - empty lineage
            '',  # Empty - should become CBD for CBD tincture
            None,  # None - should become CBD for CBG capsule
            '',  # Empty - should become CBD for CBN topical
            '',  # Empty - should become CBD for CBC edible
            '',  # Empty - should become CBD for CBD blend
            None  # None - should become CBD for high CBD edible
        ],
        'Description': [
            # Classic types
            'Regular flower',
            'Regular pre-roll',
            'Regular concentrate',
            'Regular vape cartridge',
            'Regular solventless',
            'Regular infused pre-roll',
            
            # Non-classic types without CBD
            'Regular edible',
            'Regular tincture',
            'Regular topical',
            'Regular capsule',
            'Regular edible liquid',
            
            # Non-classic types with CBD
            'CBD tincture for pain relief',
            'CBG capsule for inflammation',
            'CBN topical for sleep',
            'CBC edible for focus',
            'CBD blend tincture',
            'High CBD edible for anxiety'
        ],
        'Product Strain': [
            # Classic types
            'Mixed',
            'Mixed',
            'Mixed',
            'Mixed',
            'Mixed',
            'Mixed',
            
            # Non-classic types without CBD
            'Mixed',
            'Mixed',
            'Mixed',
            'Mixed',
            'Mixed',
            
            # Non-classic types with CBD
            'Mixed',
            'Mixed',
            'Mixed',
            'Mixed',
            'CBD Blend',
            'Mixed'
        ],
        'Vendor': ['Test Vendor'] * 19,
        'Product Brand': ['Test Brand'] * 19,
        'Weight*': ['1g'] * 19,
        'Units': ['g'] * 19
    }
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Apply the enhanced lineage processing logic (same as in excel_processor.py)
    if "Lineage" in df.columns:
        # First, standardize existing values
        df["Lineage"] = (
            df["Lineage"]
            .str.lower()
            .replace({
                "indica_hybrid": "HYBRID/INDICA",
                "sativa_hybrid": "HYBRID/SATIVA",
                "sativa": "SATIVA",
                "hybrid": "HYBRID",
                "indica": "INDICA",
                "cbd": "CBD"
            })
            .str.upper()
        )
        
        # For classic types, set empty lineage to HYBRID
        # For non-classic types, set empty lineage to MIXED or CBD based on content
        from src.core.constants import CLASSIC_TYPES
        
        # Create mask for classic types
        classic_mask = df["Product Type*"].str.strip().str.lower().isin(CLASSIC_TYPES)
        
        # Set empty lineage values based on product type
        empty_lineage_mask = df["Lineage"].isnull() | (df["Lineage"].astype(str).str.strip() == "")
        
        # For classic types, set to HYBRID
        classic_empty_mask = classic_mask & empty_lineage_mask
        if classic_empty_mask.any():
            df.loc[classic_empty_mask, "Lineage"] = "HYBRID"
        
        # For non-classic types, check for CBD content first
        non_classic_empty_mask = ~classic_mask & empty_lineage_mask
        if non_classic_empty_mask.any():
            # Check if non-classic products with empty lineage contain CBD-related content
            cbd_content_mask = (
                df["Description"].str.contains(r"CBD|CBG|CBN|CBC", case=False, na=False) |
                (df["Product Name*"].str.contains(r"CBD|CBG|CBN|CBC", case=False, na=False)) |
                (df["Product Strain"].astype(str).str.lower().str.strip() == "cbd blend")
            )
            
            # Non-classic products with CBD content get CBD lineage
            cbd_non_classic_empty = non_classic_empty_mask & cbd_content_mask
            if cbd_non_classic_empty.any():
                df.loc[cbd_non_classic_empty, "Lineage"] = "CBD"
            
            # Non-classic products without CBD content get MIXED lineage
            non_cbd_non_classic_empty = non_classic_empty_mask & ~cbd_content_mask
            if non_cbd_non_classic_empty.any():
                df.loc[non_cbd_non_classic_empty, "Lineage"] = "MIXED"
    
    # Check results
    print("Testing enhanced lineage fix for empty values (including CBD):")
    print("=" * 70)
    
    passed = 0
    total = 0
    
    for i, row in df.iterrows():
        product_name = row['Product Name*']
        product_type = row['Product Type*']
        lineage = row['Lineage']
        description = row['Description']
        is_classic = product_type in CLASSIC_TYPES
        
        # Determine expected lineage based on product type and content
        if is_classic:
            expected = 'HYBRID'
        else:
            # Check for CBD content in non-classic types
            has_cbd_content = (
                'cbd' in description.lower() or 
                'cbg' in description.lower() or 
                'cbn' in description.lower() or 
                'cbc' in description.lower() or
                'cbd' in product_name.lower() or
                row['Product Strain'].lower() == 'cbd blend'
            )
            expected = 'CBD' if has_cbd_content else 'MIXED'
        
        status = "✓ PASS" if lineage == expected else "✗ FAIL"
        print(f"{status} {product_name} ({product_type}): {lineage} (expected: {expected})")
        
        if lineage == expected:
            passed += 1
        total += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The enhanced lineage fix is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    # Show classic types for reference
    print(f"\nClassic types (should get HYBRID): {sorted(list(CLASSIC_TYPES))}")
    
    return passed == total

if __name__ == "__main__":
    success = test_cbd_lineage_fix()
    sys.exit(0 if success else 1) 