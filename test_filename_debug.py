#!/usr/bin/env python3
"""
Test script to debug filename generation issue.
This script will help identify why vendor and product type are showing as 'Unknown'.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor

def test_filename_debug():
    """Test the filename generation logic with sample data."""
    print("🔍 Testing filename generation debug...")
    
    # Initialize Excel processor
    excel_processor = ExcelProcessor()
    
    # Try to load the default file
    from src.core.data.excel_processor import get_default_upload_file
    default_file = get_default_upload_file()
    
    if not default_file or not os.path.exists(default_file):
        print("❌ No default file found")
        return
    
    print(f"📁 Loading default file: {default_file}")
    success = excel_processor.load_file(default_file)
    
    if not success:
        print("❌ Failed to load file")
        return
    
    print(f"✅ File loaded successfully: {excel_processor.df.shape[0]} rows, {excel_processor.df.shape[1]} columns")
    
    # Check column names
    print(f"📋 Available columns: {list(excel_processor.df.columns)}")
    
    # Look for vendor-related columns
    vendor_cols = [col for col in excel_processor.df.columns if 'vendor' in col.lower()]
    print(f"🏪 Vendor-related columns: {vendor_cols}")
    
    # Look for product type columns
    type_cols = [col for col in excel_processor.df.columns if 'type' in col.lower()]
    print(f"📦 Product type columns: {type_cols}")
    
    # Test with a sample product
    sample_product = "Banana OG Distillate Cartridge by Hustler's Ambition - 1g"
    print(f"\n🔍 Testing with sample product: '{sample_product}'")
    
    # Find the product in the DataFrame
    product_name_col = 'Product Name*'
    if product_name_col not in excel_processor.df.columns:
        possible_cols = ['ProductName', 'Product Name', 'Description']
        product_name_col = next((col for col in possible_cols if col in excel_processor.df.columns), None)
    
    if not product_name_col:
        print("❌ No product name column found")
        return
    
    print(f"📝 Using product name column: '{product_name_col}'")
    
    # Search for the product
    mask = excel_processor.df[product_name_col].str.strip().str.lower() == sample_product.strip().lower()
    matches = excel_processor.df[mask]
    
    if matches.empty:
        print("❌ No exact match found, trying fuzzy match...")
        # Try fuzzy matching
        for idx, row in excel_processor.df.iterrows():
            df_name = str(row[product_name_col]).strip()
            if sample_product.strip().lower() in df_name.lower() or df_name.lower() in sample_product.strip().lower():
                print(f"✅ Fuzzy match found: '{df_name}'")
                matches = excel_processor.df.iloc[[idx]]
                break
    
    if matches.empty:
        print("❌ No matches found")
        return
    
    print(f"✅ Found {len(matches)} matches")
    
    # Get the first match
    record = matches.iloc[0].to_dict()
    print(f"📄 Record keys: {list(record.keys())}")
    
    # Test vendor extraction
    print("\n🏪 Testing vendor extraction:")
    vendor = None
    for vendor_field in ['Vendor', 'vendor', 'Vendor/Supplier*']:
        vendor = str(record.get(vendor_field, '')).strip()
        print(f"  Field '{vendor_field}': '{vendor}'")
        if vendor and vendor != 'Unknown' and vendor != '':
            break
    
    if not vendor or vendor == 'Unknown' or vendor == '':
        print("  ⚠️  No vendor found, trying ProductBrand...")
        product_brand = str(record.get('ProductBrand', '')).strip()
        print(f"  ProductBrand: '{product_brand}'")
        if product_brand and product_brand != 'Unknown' and product_brand != '':
            vendor = product_brand
            print(f"  ✅ Using ProductBrand as vendor: '{vendor}'")
    
    # Test product type extraction
    print("\n📦 Testing product type extraction:")
    product_type = None
    for type_field in ['Product Type*', 'productType', 'Product Type', 'ProductType']:
        product_type = str(record.get(type_field, '')).strip()
        print(f"  Field '{type_field}': '{product_type}'")
        if product_type and product_type != 'Unknown' and product_type != '':
            break
    
    print(f"\n📊 Results:")
    print(f"  Vendor: '{vendor}'")
    print(f"  Product Type: '{product_type}'")
    
    # Test filename generation
    if vendor and product_type:
        vendor_clean = vendor.replace(' ', '_').replace('&', 'AND').replace(',', '').replace('.', '')[:15]
        product_type_clean = product_type.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')[:10]
        
        filename = f"AGT_{vendor_clean}_{product_type_clean}_VERT_Labels_1TAGS_H_20250718_120000.docx"
        print(f"  Generated filename: {filename}")
    else:
        print("  ❌ Cannot generate filename - missing vendor or product type")

if __name__ == "__main__":
    test_filename_debug() 