#!/usr/bin/env python3
"""
Debug script to test the Description field processing fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

def test_description_processing():
    """Test the Description field processing to see if the weight removal is working."""
    print("🔍 Debugging Description Field Processing")
    print("=" * 50)
    
    # Create test data
    test_data = {
        'Product Name*': [
            'Afghani Kush Wax -1g',
            'Blue Dream Wax -1g', 
            'Bruce Banner Wax -1g',
            'Lemon Jealousy Wax -1g',
            'Memory Loss Wax -1g',
            'Birthday Cake -14g'
        ],
        'Product Type*': [
            'concentrate',
            'concentrate',
            'concentrate', 
            'concentrate',
            'concentrate',
            'flower'
        ],
        'Product Brand': [
            'Test Brand 1',
            'Test Brand 2',
            'Test Brand 3',
            'Test Brand 4', 
            'Test Brand 5',
            'Test Brand 6'
        ],
        'Price': ['$12', '$12', '$12', '$12', '$12', '$100'],
        'Weight*': [1, 1, 1, 1, 1, 14],
        'Units': ['g', 'g', 'g', 'g', 'g', 'g'],
        'DOH': ['YES', 'YES', 'YES', 'YES', 'YES', 'YES'],
        'Lineage': ['INDICA', 'SATIVA', 'HYBRID/SATIVA', 'SATIVA', 'SATIVA', 'HYBRID'],
        'Product Strain': ['Afghani Kush', 'Blue Dream', 'Bruce Banner', 'Lemon Jealousy', 'Memory Loss', 'Birthday Cake'],
        'Ratio': ['THC: 66.73% CBD: -0.17%', 'THC: 65.12% CBD: 0.08%', 'THC: 68.45% CBD: 0.12%', 'THC: 67.89% CBD: 0.05%', 'THC: 66.21% CBD: 0.09%', 'THC: 24.95% CBD: 0.05%']
    }
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    print("Original data:")
    print(df[['Product Name*', 'Product Type*']].head())
    print()
    
    # Simulate the Description processing logic
    product_names = df['Product Name*'].str.strip()
    print("Product names after strip:")
    print(product_names.head())
    print()
    
    # Set Description to ProductName values
    df["Description"] = product_names
    print("Description after setting to ProductName:")
    print(df[['Product Name*', 'Description']].head())
    print()
    
    # Check for different dash patterns
    print("Checking for different dash patterns:")
    for i, desc in enumerate(df["Description"].head()):
        print(f"  Record {i}: '{desc}' (repr: {repr(desc)})")
        print(f"    Contains ' - ': {' - ' in desc}")
        print(f"    Contains '-': {'-' in desc}")
        print(f"    Contains '–': {'–' in desc}")
        print(f"    Contains '—': {'—' in desc}")
        print(f"    Contains '−': {'−' in desc}")
        print()
    
    # Handle ' by ' pattern for all Description values
    mask_by = df["Description"].str.contains(' by ', na=False)
    df.loc[mask_by, "Description"] = df.loc[mask_by, "Description"].str.split(' by ').str[0].str.strip()
    print("Description after 'by' processing:")
    print(df[['Product Name*', 'Description']].head())
    print()
    
    # Handle ' - ' pattern - remove weight part from Description to prevent duplication
    mask_dash = df["Description"].str.contains(' - ', na=False)
    print(f"Mask for dash processing: {mask_dash.sum()} records have dashes")
    print("Records with dashes:")
    print(df[mask_dash][['Product Name*', 'Description']])
    print()
    
    # Try different dash patterns
    print("Trying different dash patterns:")
    for pattern in [' - ', '-', '–', '—', '−']:
        mask_pattern = df["Description"].str.contains(pattern, na=False)
        print(f"  Pattern '{pattern}' (repr: {repr(pattern)}): {mask_pattern.sum()} matches")
        if mask_pattern.any():
            print(f"    Matches: {df[mask_pattern]['Description'].tolist()}")
    
    print()
    
    # Remove weight part from Description for all types to prevent duplication
    # Try with different patterns
    for pattern in [' - ', '-', '–', '—', '−']:
        mask_pattern = df["Description"].str.contains(pattern, na=False)
        if mask_pattern.any():
            print(f"Processing pattern '{pattern}':")
            df.loc[mask_pattern, "Description"] = df.loc[mask_pattern, "Description"].str.rsplit(pattern, n=1).str[0].str.strip()
            print(f"  After processing: {df[mask_pattern]['Description'].tolist()}")
    
    print("\nFinal Description after all processing:")
    print(df[['Product Name*', 'Description']].head())
    print()
    
    # Check for any remaining dashes
    remaining_dashes = df["Description"].str.contains(' - ', na=False)
    print(f"Remaining dashes after processing: {remaining_dashes.sum()}")
    if remaining_dashes.any():
        print("Records with remaining dashes:")
        print(df[remaining_dashes][['Product Name*', 'Description']])
    
    return df

if __name__ == "__main__":
    result_df = test_description_processing()
    print("\n✅ Description processing test completed!") 