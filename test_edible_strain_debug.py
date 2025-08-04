#!/usr/bin/env python3
"""
Debug test to see what's happening with the edible Product Strain logic.
"""

import pandas as pd
import sys
import os

# Add the src directory to the path so we can import the ExcelProcessor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.data.excel_processor import ExcelProcessor

def test_edible_strain_debug():
    """Debug the edible Product Strain logic."""
    
    # Create test data that matches what we see in the image
    test_data = [
        {
            'Product Name*': '20:20:1 Sour Watermelon Gummies',
            'Product Type*': 'edible (solid)',
            'Description': 'Delicious gummy bears with CBD for relaxation',
            'Expected Product Strain': 'CBD Blend'
        },
        {
            'Product Name*': '1:1:1 Indica Boysenberry Gummies',
            'Product Type*': 'edible (solid)',
            'Description': 'Boysenberry gummies with CBN for sleep',
            'Expected Product Strain': 'CBD Blend'
        },
        {
            'Product Name*': 'MAX Pink Lemonade Gummie Single',
            'Product Type*': 'edible (solid)',
            'Description': 'Pink lemonade gummies with CBG for wellness',
            'Expected Product Strain': 'CBD Blend'
        },
        {
            'Product Name*': 'CBD Watermelon Fruit Chews',
            'Product Type*': 'edible (solid)',
            'Description': 'Watermelon fruit chews with CBD',
            'Expected Product Strain': 'CBD Blend'
        },
        {
            'Product Name*': '2:1 CBD Hybrid Peach Gummies',
            'Product Type*': 'edible (solid)',
            'Description': 'Peach gummies with CBD and THC',
            'Expected Product Strain': 'CBD Blend'
        },
        {
            'Product Name*': 'Regular THC Gummies',
            'Product Type*': 'edible (solid)',
            'Description': 'Delicious THC gummies for recreational use',
            'Expected Product Strain': 'Mixed'
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Add required columns that ExcelProcessor expects
    df['Product Brand'] = 'Test Brand'
    df['Vendor'] = 'Test Vendor'
    df['Lineage'] = ''
    df['Product Strain'] = ''
    df['Ratio'] = ''
    df['Price'] = '10.00'
    df['Weight*'] = '1.0'
    df['Units'] = 'oz'
    
    # Create ExcelProcessor instance
    processor = ExcelProcessor()
    
    # Set the DataFrame directly (bypassing file loading)
    processor.df = df.copy()
    
    print("=== Initial State ===")
    for idx, row in processor.df.iterrows():
        print(f"{row['Product Name*']}: Product Strain = '{row['Product Strain']}'")
    
    # Define edible types
    edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"}
    edible_mask = processor.df["Product Type*"].str.strip().str.lower().isin(edible_types)
    
    print(f"\n=== Found {edible_mask.sum()} edible products ===")
    
    if edible_mask.any():
        # Check if Description contains CBD, CBG, CBN, or CBC
        edible_cbd_content_mask = (
            processor.df["Description"].str.contains(r"CBD|CBG|CBN|CBC", case=False, na=False)
        )
        
        print(f"\n=== Cannabinoid Detection ===")
        for idx, row in processor.df.iterrows():
            if edible_mask.iloc[idx]:
                has_cannabinoids = edible_cbd_content_mask.iloc[idx]
                print(f"{row['Product Name*']}: Has cannabinoids = {has_cannabinoids}")
        
        # For edibles with cannabinoid content in Description, set to "CBD Blend"
        edible_cbd_mask = edible_mask & edible_cbd_content_mask
        if edible_cbd_mask.any():
            processor.df.loc[edible_cbd_mask, "Product Strain"] = "CBD Blend"
            print(f"\n✅ Assigned 'CBD Blend' to {edible_cbd_mask.sum()} edibles with cannabinoid content in Description")
        
        # For edibles without cannabinoid content in Description, set to "Mixed"
        edible_mixed_mask = edible_mask & ~edible_cbd_content_mask
        if edible_mixed_mask.any():
            processor.df.loc[edible_mixed_mask, "Product Strain"] = "Mixed"
            print(f"✅ Assigned 'Mixed' to {edible_mixed_mask.sum()} edibles without cannabinoid content in Description")
    
    print(f"\n=== Final State ===")
    results = []
    
    for idx, row in processor.df.iterrows():
        product_name = row['Product Name*']
        product_type = row['Product Type*']
        description = row['Description']
        actual_strain = row['Product Strain']
        expected_strain = row['Expected Product Strain']
        
        # Check if it's an edible
        is_edible = product_type.lower() in edible_types
        
        # Check if description contains cannabinoids
        has_cannabinoids = bool(pd.Series([description]).str.contains(r"CBD|CBG|CBN|CBC", case=False, na=False).iloc[0])
        
        result = {
            'Product': product_name,
            'Type': product_type,
            'Is Edible': is_edible,
            'Has Cannabinoids': has_cannabinoids,
            'Actual Strain': actual_strain,
            'Expected Strain': expected_strain,
            'Correct': actual_strain == expected_strain
        }
        results.append(result)
        
        status = "✅ PASS" if actual_strain == expected_strain else "❌ FAIL"
        print(f"{status} | {product_name} | {product_type} | Cannabinoids: {has_cannabinoids} | Actual: {actual_strain} | Expected: {expected_strain}")
    
    # Summary
    correct_count = sum(1 for r in results if r['Correct'])
    total_count = len(results)
    
    print(f"\n=== Summary ===")
    print(f"Total tests: {total_count}")
    print(f"Passed: {correct_count}")
    print(f"Failed: {total_count - correct_count}")
    print(f"Success rate: {correct_count/total_count*100:.1f}%")
    
    if correct_count == total_count:
        print("🎉 All tests passed! The logic is working correctly in isolation.")
        print("The issue might be in the full file processing pipeline.")
    else:
        print("⚠️  Some tests failed. The logic itself has issues.")
    
    return correct_count == total_count

if __name__ == "__main__":
    success = test_edible_strain_debug()
    sys.exit(0 if success else 1) 