#!/usr/bin/env python3
"""
Test script to specifically look for products with "HIGH THC" in the name.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd

def test_high_thc_detection():
    """Test to find products with HIGH THC in the name."""
    
    print("=== Testing HIGH THC Detection ===")
    
    # Initialize processor
    processor = ExcelProcessor()
    
    # Load the default file
    downloads_dir = os.path.expanduser("~/Downloads")
    matching_files = [f for f in os.listdir(downloads_dir) if f.startswith("A Greener Today") and f.endswith(".xlsx")]
    
    if not matching_files:
        print("❌ No AGT files found in Downloads directory")
        return False
    
    # Use the most recent file
    latest_file = max(matching_files, key=lambda x: os.path.getctime(os.path.join(downloads_dir, x)))
    file_path = os.path.join(downloads_dir, latest_file)
    
    print(f"📁 Using file: {latest_file}")
    
    # Load the file
    if not processor.load_file(file_path):
        print("❌ Failed to load file")
        return False
    
    # Get the raw DataFrame to search
    df = processor.df
    print(f"📊 DataFrame shape: {df.shape}")
    
    # Check what columns are available
    print("\n📋 Available columns:")
    for i, col in enumerate(df.columns):
        print(f"   {i+1:2d}. {col}")
    
    # Find the product name column
    product_name_col = None
    for col in df.columns:
        if 'product' in col.lower() and 'name' in col.lower():
            product_name_col = col
            break
    
    if not product_name_col:
        print("❌ Could not find product name column")
        return False
    
    print(f"\n🎯 Using product name column: '{product_name_col}'")
    
    # Search for products with "HIGH THC" in various columns
    print(f"\n🔍 Searching for 'HIGH THC' in {product_name_col} column:")
    high_thc_products = df[df[product_name_col].str.contains('HIGH THC', case=False, na=False)]
    print(f"Found {len(high_thc_products)} products with 'HIGH THC' in {product_name_col}")
    
    if len(high_thc_products) > 0:
        print("\n🏷️  HIGH THC Products found:")
        for idx, row in high_thc_products.iterrows():
            product_name = row[product_name_col]
            vendor = row.get('Vendor', 'Unknown')
            product_type = row.get('Product Type*', 'Unknown')
            doh_value = row.get('DOH', 'Unknown')
            print(f"   Product: {product_name}")
            print(f"   Vendor: {vendor}")
            print(f"   Type: {product_type}")
            print(f"   DOH: {doh_value}")
            print()
    
    # Also search in Description column
    print("🔍 Searching for 'HIGH THC' in Description column:")
    high_thc_desc = df[df['Description'].str.contains('HIGH THC', case=False, na=False)]
    print(f"Found {len(high_thc_desc)} products with 'HIGH THC' in Description")
    
    if len(high_thc_desc) > 0:
        print("\n🏷️  HIGH THC Products in Description:")
        for idx, row in high_thc_desc.iterrows():
            product_name = row[product_name_col]
            description = row['Description']
            vendor = row.get('Vendor', 'Unknown')
            product_type = row.get('Product Type*', 'Unknown')
            doh_value = row.get('DOH', 'Unknown')
            print(f"   Product: {product_name}")
            print(f"   Description: {description}")
            print(f"   Vendor: {vendor}")
            print(f"   Type: {product_type}")
            print(f"   DOH: {doh_value}")
            print()
    
    # Search for "Gorilla Glue" specifically
    print(f"🔍 Searching for 'Gorilla Glue' in {product_name_col}:")
    gorilla_glue_products = df[df[product_name_col].str.contains('Gorilla Glue', case=False, na=False)]
    print(f"Found {len(gorilla_glue_products)} products with 'Gorilla Glue' in name")
    
    if len(gorilla_glue_products) > 0:
        print("\n🏷️  Gorilla Glue Products:")
        for idx, row in gorilla_glue_products.iterrows():
            product_name = row[product_name_col]
            description = row['Description']
            vendor = row.get('Vendor', 'Unknown')
            product_type = row.get('Product Type*', 'Unknown')
            doh_value = row.get('DOH', 'Unknown')
            print(f"   Product: {product_name}")
            print(f"   Description: {description}")
            print(f"   Vendor: {vendor}")
            print(f"   Type: {product_type}")
            print(f"   DOH: {doh_value}")
            print()
    
    # Search for "Swifts" vendor
    print("🔍 Searching for 'Swifts' vendor:")
    swifts_products = df[df['Vendor'].str.contains('Swifts', case=False, na=False)]
    print(f"Found {len(swifts_products)} products from Swifts vendor")
    
    if len(swifts_products) > 0:
        print("\n🏷️  Swifts Products:")
        for idx, row in swifts_products.iterrows():
            product_name = row[product_name_col]
            description = row['Description']
            vendor = row.get('Vendor', 'Unknown')
            product_type = row.get('Product Type*', 'Unknown')
            doh_value = row.get('DOH', 'Unknown')
            print(f"   Product: {product_name}")
            print(f"   Description: {description}")
            print(f"   Vendor: {vendor}")
            print(f"   Type: {product_type}")
            print(f"   DOH: {doh_value}")
            print()
    
    # Search for "Tablets" product type
    print("🔍 Searching for 'Tablets' product type:")
    tablets_products = df[df['Product Type*'].str.contains('Tablets', case=False, na=False)]
    print(f"Found {len(tablets_products)} products with 'Tablets' type")
    
    if len(tablets_products) > 0:
        print("\n🏷️  Tablets Products:")
        for idx, row in tablets_products.iterrows():
            product_name = row[product_name_col]
            description = row['Description']
            vendor = row.get('Vendor', 'Unknown')
            product_type = row.get('Product Type*', 'Unknown')
            doh_value = row.get('DOH', 'Unknown')
            print(f"   Product: {product_name}")
            print(f"   Description: {description}")
            print(f"   Vendor: {vendor}")
            print(f"   Type: {product_type}")
            print(f"   DOH: {doh_value}")
            print()
    
    return True

if __name__ == "__main__":
    test_high_thc_detection() 