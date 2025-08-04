#!/usr/bin/env python3
"""
Test script to debug why dose tanker products might not be appearing in Excel generation.
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file

def test_dose_tanker_products():
    """Test to see if dose tanker products are being filtered out."""
    
    print("=== Dose Tanker Debug Test ===\n")
    
    # Initialize the Excel processor
    processor = ExcelProcessor()
    
    # Try to load the default file
    default_file = get_default_upload_file()
    if not default_file:
        print("❌ No default file found")
        return
    
    print(f"📁 Loading file: {default_file}")
    
    # Load the file
    success = processor.load_file(default_file)
    if not success:
        print("❌ Failed to load file")
        return
    
    print(f"✅ File loaded successfully: {len(processor.df)} rows")
    
    # Check for dose tanker products in the raw data
    print("\n🔍 Searching for dose tanker products in raw data...")
    
    # Search in Product Name* column
    if 'Product Name*' in processor.df.columns:
        dose_tanker_mask = processor.df['Product Name*'].astype(str).str.lower().str.contains('dose tanker', na=False)
        dose_tanker_products = processor.df[dose_tanker_mask]
        print(f"Found {len(dose_tanker_products)} products with 'dose tanker' in Product Name*")
        
        if len(dose_tanker_products) > 0:
            print("\nDose tanker products found:")
            for idx, row in dose_tanker_products.iterrows():
                print(f"  - {row.get('Product Name*', 'NO NAME')} (Type: {row.get('Product Type*', 'NO TYPE')})")
    
    # Search in Description column
    if 'Description' in processor.df.columns:
        dose_tanker_desc_mask = processor.df['Description'].astype(str).str.lower().str.contains('dose tanker', na=False)
        dose_tanker_desc_products = processor.df[dose_tanker_desc_mask]
        print(f"Found {len(dose_tanker_desc_products)} products with 'dose tanker' in Description")
        
        if len(dose_tanker_desc_products) > 0:
            print("\nDose tanker products in Description:")
            for idx, row in dose_tanker_desc_products.iterrows():
                print(f"  - {row.get('Product Name*', 'NO NAME')} (Desc: {row.get('Description', 'NO DESC')})")
    
    # Check available tags
    print("\n🔍 Checking available tags...")
    available_tags = processor.get_available_tags()
    print(f"Total available tags: {len(available_tags)}")
    
    # Look for dose tanker in available tags
    dose_tanker_tags = []
    for tag in available_tags:
        product_name = tag.get('Product Name*', '').lower()
        description = tag.get('Description', '').lower() if 'Description' in tag else ''
        if 'dose tanker' in product_name or 'dose tanker' in description:
            dose_tanker_tags.append(tag)
    
    print(f"Found {len(dose_tanker_tags)} dose tanker products in available tags")
    
    if len(dose_tanker_tags) > 0:
        print("\nDose tanker products in available tags:")
        for tag in dose_tanker_tags:
            print(f"  - {tag.get('Product Name*', 'NO NAME')} (Type: {tag.get('Product Type*', 'NO TYPE')})")
    else:
        print("❌ No dose tanker products found in available tags")
        
        # Check if they were filtered out
        print("\n🔍 Checking filtering logic...")
        
        # Look for products that might be dose tankers but got filtered
        all_products = processor.df['Product Name*'].astype(str).str.lower()
        potential_dose_products = []
        
        for idx, product_name in enumerate(all_products):
            if 'dose' in product_name and ('tanker' in product_name or 'rso' in product_name or 'co2' in product_name):
                potential_dose_products.append((idx, product_name))
        
        print(f"Found {len(potential_dose_products)} potential dose-related products:")
        for idx, product_name in potential_dose_products:
            row = processor.df.iloc[idx]
            print(f"  - {row.get('Product Name*', 'NO NAME')} (Type: {row.get('Product Type*', 'NO TYPE')})")
    
    # Check product types
    print("\n🔍 Checking product types...")
    if 'Product Type*' in processor.df.columns:
        product_types = processor.df['Product Type*'].value_counts()
        print("Product types in data:")
        for product_type, count in product_types.head(20).items():
            print(f"  - {product_type}: {count}")
    
    # Check if dose tanker products have valid lineage
    print("\n🔍 Checking lineage validation...")
    if len(dose_tanker_products) > 0:
        for idx, row in dose_tanker_products.iterrows():
            lineage = row.get('Lineage', '')
            print(f"  - {row.get('Product Name*', 'NO NAME')}: Lineage = '{lineage}'")
    
    print("\n=== End Debug Test ===")

if __name__ == "__main__":
    test_dose_tanker_products() 