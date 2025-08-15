#!/usr/bin/env python3
"""
Test script to check for duplication in ProductStrain and ProductVendor fields.
This script will examine the actual data to see if there are any duplications.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_duplication():
    """Check for duplication in ProductStrain and ProductVendor fields."""
    
    print("=== DUPLICATION CHECK FOR PRODUCTSTRAIN AND PRODUCTVENDOR ===\n")
    
    try:
        # Import the necessary modules
        from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file
        
        print("✅ Successfully imported required modules")
        
        # Get the default file
        default_file = get_default_upload_file()
        if not default_file:
            print("❌ No default file found")
            return
        
        print(f"📁 Using file: {default_file}")
        
        # Load the data
        processor = ExcelProcessor()
        success = processor.load_file(default_file)
        
        if not success or processor.df is None or processor.df.empty:
            print("❌ No data loaded")
            return
        
        print(f"✅ Loaded {len(processor.df)} records\n")
        
        # Print column names to see what they actually are
        print("📋 ACTUAL COLUMN NAMES:")
        print("-" * 50)
        for i, col in enumerate(processor.df.columns):
            print(f"   {i}: '{col}'")
        print()
        
        # Check for duplication in ProductStrain
        print("🔍 CHECKING PRODUCTSTRAIN DUPLICATION:")
        print("-" * 50)
        
        # Check if ProductStrain equals ProductBrand
        strain_brand_duplicates = processor.df[
            (processor.df['Product Strain'].notna()) & 
            (processor.df['Product Brand'].notna()) &
            (processor.df['Product Strain'].astype(str) == processor.df['Product Brand'].astype(str))
        ]
        
        if len(strain_brand_duplicates) > 0:
            print(f"❌ Found {len(strain_brand_duplicates)} records where ProductStrain equals ProductBrand:")
            for idx, row in strain_brand_duplicates.head(5).iterrows():
                print(f"   Row {idx}: '{row.get('Product Strain', '')}' = '{row.get('Product Brand', '')}'")
            if len(strain_brand_duplicates) > 5:
                print(f"   ... and {len(strain_brand_duplicates) - 5} more")
        else:
            print("✅ No ProductStrain equals ProductBrand duplication found")
        
        # Check if ProductStrain equals Product Type
        strain_type_duplicates = processor.df[
            (processor.df['Product Strain'].notna()) & 
            (processor.df['Product Type*'].notna()) &
            (processor.df['Product Strain'].astype(str) == processor.df['Product Type*'].astype(str))
        ]
        
        if len(strain_type_duplicates) > 0:
            print(f"❌ Found {len(strain_type_duplicates)} records where ProductStrain equals Product Type:")
            for idx, row in strain_type_duplicates.head(5).iterrows():
                print(f"   Row {idx}: '{row.get('Product Strain', '')}' = '{row.get('Product Type*', '')}'")
            if len(strain_type_duplicates) > 5:
                print(f"   ... and {len(strain_type_duplicates) - 5} more")
        else:
            print("✅ No ProductStrain equals Product Type duplication found")
        
        # Check for ProductStrain containing Product Type
        strain_contains_type = []
        for idx, row in processor.df.iterrows():
            strain = str(row.get('Product Strain', '')).lower()
            product_type = str(row.get('Product Type*', '')).lower()
            if (strain and product_type and 
                product_type in strain and 
                strain != product_type):
                strain_contains_type.append((idx, row))
        
        if strain_contains_type:
            print(f"⚠️  Found {len(strain_contains_type)} records where ProductStrain contains Product Type:")
            for idx, row in strain_contains_type[:5]:
                print(f"   Row {idx}: '{row.get('Product Strain', '')}' contains '{row.get('Product Type*', '')}'")
            if len(strain_contains_type) > 5:
                print(f"   ... and {len(strain_contains_type) - 5} more")
        else:
            print("✅ No ProductStrain contains Product Type found")
        
        print("\n" + "=" * 50)
        
        # Check for duplication in Vendor fields
        print("🔍 CHECKING VENDOR DUPLICATION:")
        print("-" * 50)
        
        # Check if Vendor equals Product Brand
        vendor_brand_duplicates = processor.df[
            (processor.df['Vendor'].notna()) & 
            (processor.df['Product Brand'].notna()) &
            (processor.df['Vendor'].astype(str) == processor.df['Product Brand'].astype(str))
        ]
        
        if len(vendor_brand_duplicates) > 0:
            print(f"❌ Found {len(vendor_brand_duplicates)} records where Vendor equals Product Brand:")
            for idx, row in vendor_brand_duplicates.head(5).iterrows():
                print(f"   Row {idx}: '{row.get('Vendor', '')}' = '{row.get('Product Brand', '')}'")
            if len(vendor_brand_duplicates) > 5:
                print(f"   ... and {len(vendor_brand_duplicates) - 5} more")
        else:
            print("✅ No Vendor equals Product Brand duplication found")
        
        # Check if Vendor equals Product Type
        vendor_type_duplicates = processor.df[
            (processor.df['Vendor'].notna()) & 
            (processor.df['Product Type*'].notna()) &
            (processor.df['Vendor'].astype(str) == processor.df['Product Type*'].astype(str))
        ]
        
        if len(vendor_type_duplicates) > 0:
            print(f"❌ Found {len(vendor_type_duplicates)} records where Vendor equals Product Type:")
            for idx, row in vendor_type_duplicates.head(5).iterrows():
                print(f"   Row {idx}: '{row.get('Vendor', '')}' = '{row.get('Product Type*', '')}'")
            if len(vendor_type_duplicates) > 5:
                print(f"   ... and {len(vendor_type_duplicates) - 5} more")
        else:
            print("✅ No Vendor equals Product Type duplication found")
        
        # Check for Vendor containing Product Type
        vendor_contains_type = []
        for idx, row in processor.df.iterrows():
            vendor = str(row.get('Vendor', '')).lower()
            product_type = str(row.get('Product Type*', '')).lower()
            if (vendor and product_type and 
                product_type in vendor and 
                vendor != product_type):
                vendor_contains_type.append((idx, row))
        
        if vendor_contains_type:
            print(f"⚠️  Found {len(vendor_contains_type)} records where Vendor contains Product Type:")
            for idx, row in vendor_contains_type[:5]:
                print(f"   Row {idx}: '{row.get('Vendor', '')}' contains '{row.get('Product Type*', '')}'")
            if len(vendor_contains_type) > 5:
                print(f"   ... and {len(vendor_contains_type) - 5} more")
        else:
            print("✅ No Vendor contains Product Type found")
        
        print("\n" + "=" * 50)
        
        # Check specific problematic records
        print("🔍 CHECKING SPECIFIC PROBLEMATIC RECORDS:")
        print("-" * 50)
        
        # Check Moonshot products specifically
        moonshot_products = processor.df[
            processor.df['ProductName'].str.contains('Moonshot', case=False, na=False)
        ]
        
        if len(moonshot_products) > 0:
            print(f"📋 Found {len(moonshot_products)} Moonshot products:")
            for idx, row in moonshot_products.iterrows():
                print(f"   Row {idx}:")
                print(f"     Product Name: '{row.get('Product Name', '')}'")
                print(f"     Product Type: '{row.get('Product Type*', '')}'")
                print(f"     Product Strain: '{row.get('Product Strain', '')}'")
                print(f"     Product Brand: '{row.get('Product Brand', '')}'")
                print(f"     Vendor: '{row.get('Vendor', '')}'")
                print()
        else:
            print("ℹ️  No Moonshot products found")
        
        # Check Paraphernalia products
        paraphernalia_products = processor.df[
            processor.df['Product Type*'].str.contains('Paraphernalia', case=False, na=False)
        ]
        
        if len(paraphernalia_products) > 0:
            print(f"📋 Found {len(paraphernalia_products)} Paraphernalia products:")
            for idx, row in paraphernalia_products.head(3).iterrows():
                print(f"   Row {idx}:")
                print(f"     Product Name: '{row.get('Product Name', '')}'")
                print(f"     Product Type: '{row.get('Product Type*', '')}'")
                print(f"     Product Strain: '{row.get('Product Strain', '')}'")
                print(f"     Product Brand: '{row.get('Product Brand', '')}'")
                print(f"     Vendor: '{row.get('Vendor', '')}'")
                print()
            if len(paraphernalia_products) > 3:
                print(f"   ... and {len(paraphernalia_products) - 3} more")
        
        print("✅ Duplication check completed")
        
    except Exception as e:
        print(f"❌ Error during duplication check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_duplication()
