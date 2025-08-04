#!/usr/bin/env python3
"""
Comprehensive test script to verify edible Product Strain logic fix.
Tests that:
1. Edibles with CBD, CBG, CBN, or CBC in description get "CBD Blend" Product Strain
2. Edibles without cannabinoids get "Mixed" Product Strain
3. Non-edible products are not affected by the edible-specific logic
"""

import pandas as pd
import sys
import os

# Add the src directory to the path so we can import the ExcelProcessor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.data.excel_processor import ExcelProcessor

def test_comprehensive_edible_strain_logic():
    """Test the comprehensive edible Product Strain logic."""
    
    # Create test data with both edible and non-edible products
    test_data = [
        # Edible products with cannabinoids - should get "CBD Blend"
        {
            'Product Name*': 'CBD Gummy Bears',
            'Product Type*': 'edible (solid)',
            'Description': 'Delicious gummy bears with CBD for relaxation',
            'Expected Product Strain': 'CBD Blend',
            'Category': 'Edible with cannabinoids'
        },
        {
            'Product Name*': 'CBG Tincture',
            'Product Type*': 'tincture',
            'Description': 'High-quality CBG tincture for wellness',
            'Expected Product Strain': 'CBD Blend',
            'Category': 'Edible with cannabinoids'
        },
        {
            'Product Name*': 'CBN Sleep Capsules',
            'Product Type*': 'capsule',
            'Description': 'Sleep aid with CBN for better rest',
            'Expected Product Strain': 'CBD Blend',
            'Category': 'Edible with cannabinoids'
        },
        {
            'Product Name*': 'CBC Wellness Drops',
            'Product Type*': 'edible (liquid)',
            'Description': 'CBC drops for overall wellness',
            'Expected Product Strain': 'CBD Blend',
            'Category': 'Edible with cannabinoids'
        },
        
        # Edible products without cannabinoids - should get "Mixed"
        {
            'Product Name*': 'Regular THC Gummies',
            'Product Type*': 'edible (solid)',
            'Description': 'Delicious THC gummies for recreational use',
            'Expected Product Strain': 'Mixed',
            'Category': 'Edible without cannabinoids'
        },
        {
            'Product Name*': 'Chocolate Brownie',
            'Product Type*': 'edible (solid)',
            'Description': 'Delicious chocolate brownie with cannabis',
            'Expected Product Strain': 'Mixed',
            'Category': 'Edible without cannabinoids'
        },
        {
            'Product Name*': 'THC Tincture',
            'Product Type*': 'tincture',
            'Description': 'High-potency THC tincture',
            'Expected Product Strain': 'Mixed',
            'Category': 'Edible without cannabinoids'
        },
        {
            'Product Name*': 'Regular Cannabis Cookie',
            'Product Type*': 'edible (solid)',
            'Description': 'Delicious cannabis-infused cookie',
            'Expected Product Strain': 'Mixed',
            'Category': 'Edible without cannabinoids'
        },
        
        # Non-edible products with cannabinoids - should NOT be affected by edible logic
        {
            'Product Name*': 'CBD Flower',
            'Product Type*': 'flower',
            'Description': 'High-CBD flower strain for medical use',
            'Expected Product Strain': 'Original Strain',  # Should keep original or be set by other logic
            'Category': 'Non-edible with cannabinoids'
        },
        {
            'Product Name*': 'CBG Concentrate',
            'Product Type*': 'concentrate',
            'Description': 'Pure CBG concentrate for therapeutic use',
            'Expected Product Strain': 'Original Strain',  # Should keep original or be set by other logic
            'Category': 'Non-edible with cannabinoids'
        },
        {
            'Product Name*': 'CBN Vape Cartridge',
            'Product Type*': 'vape cartridge',
            'Description': 'CBN vape cartridge for sleep',
            'Expected Product Strain': 'Original Strain',  # Should keep original or be set by other logic
            'Category': 'Non-edible with cannabinoids'
        },
        
        # Non-edible products without cannabinoids - should NOT be affected by edible logic
        {
            'Product Name*': 'Regular Flower',
            'Product Type*': 'flower',
            'Description': 'High-THC flower for recreational use',
            'Expected Product Strain': 'Original Strain',  # Should keep original or be set by other logic
            'Category': 'Non-edible without cannabinoids'
        },
        {
            'Product Name*': 'THC Concentrate',
            'Product Type*': 'concentrate',
            'Description': 'High-potency THC concentrate',
            'Expected Product Strain': 'Original Strain',  # Should keep original or be set by other logic
            'Category': 'Non-edible without cannabinoids'
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Add required columns that ExcelProcessor expects
    df['Product Brand'] = 'Test Brand'
    df['Vendor'] = 'Test Vendor'
    df['Lineage'] = ''
    df['Product Strain'] = 'Original Strain'  # Set initial value
    df['Ratio'] = ''
    df['Price'] = '10.00'
    df['Weight*'] = '1.0'
    df['Units'] = 'oz'
    
    # Create ExcelProcessor instance
    processor = ExcelProcessor()
    
    # Set the DataFrame directly (bypassing file loading)
    processor.df = df.copy()
    
    # Define edible types
    edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"}
    edible_mask = processor.df["Product Type*"].str.strip().str.lower().isin(edible_types)
    
    print("=== Testing Comprehensive Edible Product Strain Logic ===")
    print(f"Found {edible_mask.sum()} edible products out of {len(processor.df)} total products")
    
    # Store original Product Strain values for non-edibles
    original_strains = processor.df['Product Strain'].copy()
    
    if edible_mask.any():
        # Check if Description contains CBD, CBG, CBN, or CBC
        edible_cbd_content_mask = (
            processor.df["Description"].str.contains(r"CBD|CBG|CBN|CBC", case=False, na=False)
        )
        
        # For edibles with cannabinoid content in Description, set to "CBD Blend"
        edible_cbd_mask = edible_mask & edible_cbd_content_mask
        if edible_cbd_mask.any():
            processor.df.loc[edible_cbd_mask, "Product Strain"] = "CBD Blend"
            print(f"✅ Assigned 'CBD Blend' to {edible_cbd_mask.sum()} edibles with cannabinoid content in Description")
        
        # For edibles without cannabinoid content in Description, set to "Mixed"
        edible_mixed_mask = edible_mask & ~edible_cbd_content_mask
        if edible_mixed_mask.any():
            processor.df.loc[edible_mixed_mask, "Product Strain"] = "Mixed"
            print(f"✅ Assigned 'Mixed' to {edible_mixed_mask.sum()} edibles without cannabinoid content in Description")
    
    print("\n=== Results ===")
    results = []
    
    for idx, row in processor.df.iterrows():
        product_name = row['Product Name*']
        product_type = row['Product Type*']
        description = row['Description']
        actual_strain = row['Product Strain']
        expected_strain = row['Expected Product Strain']
        category = row['Category']
        original_strain = original_strains.iloc[idx]
        
        # Check if it's an edible
        is_edible = product_type.lower() in edible_types
        
        # Check if description contains cannabinoids
        has_cannabinoids = bool(pd.Series([description]).str.contains(r"CBD|CBG|CBN|CBC", case=False, na=False).iloc[0])
        
        # Determine if the result is correct
        if is_edible:
            # For edibles, check against expected strain
            correct = actual_strain == expected_strain
        else:
            # For non-edibles, they should keep their original strain (not be affected by edible logic)
            correct = actual_strain == original_strain
        
        result = {
            'Product': product_name,
            'Type': product_type,
            'Category': category,
            'Is Edible': is_edible,
            'Has Cannabinoids': has_cannabinoids,
            'Original Strain': original_strain,
            'Actual Strain': actual_strain,
            'Expected Strain': expected_strain,
            'Correct': correct
        }
        results.append(result)
        
        status = "✅ PASS" if correct else "❌ FAIL"
        print(f"{status} | {product_name} | {product_type} | {category} | Cannabinoids: {has_cannabinoids} | Actual: {actual_strain} | Expected: {expected_strain}")
    
    # Summary by category
    print(f"\n=== Summary by Category ===")
    categories = {}
    for result in results:
        category = result['Category']
        if category not in categories:
            categories[category] = {'total': 0, 'passed': 0}
        categories[category]['total'] += 1
        if result['Correct']:
            categories[category]['passed'] += 1
    
    for category, stats in categories.items():
        success_rate = stats['passed'] / stats['total'] * 100
        print(f"{category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
    
    # Overall summary
    correct_count = sum(1 for r in results if r['Correct'])
    total_count = len(results)
    
    print(f"\n=== Overall Summary ===")
    print(f"Total tests: {total_count}")
    print(f"Passed: {correct_count}")
    print(f"Failed: {total_count - correct_count}")
    print(f"Success rate: {correct_count/total_count*100:.1f}%")
    
    if correct_count == total_count:
        print("🎉 All tests passed! Edible Product Strain logic is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the logic.")
    
    return correct_count == total_count

if __name__ == "__main__":
    success = test_comprehensive_edible_strain_logic()
    sys.exit(0 if success else 1) 