#!/usr/bin/env python3
"""
Debug script to investigate ProductStrain repeating ProductBrand issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
from src.core.generation.template_processor import TemplateProcessor
import pandas as pd

def debug_productstrain_issue():
    """Debug the ProductStrain repeating ProductBrand issue"""
    
    print("=== ProductStrain Issue Debug ===")
    
    # Initialize Excel processor
    excel_processor = ExcelProcessor()
    
    # Try to load the default file - use the function from the module
    from src.core.data.excel_processor import get_default_upload_file
    default_file = get_default_upload_file()
    if not default_file or not os.path.exists(default_file):
        print("❌ No default file found")
        return
    
    print(f"📁 Loading file: {os.path.basename(default_file)}")
    
    # Load the file using the correct method name
    if not excel_processor.load_file(default_file):
        print("❌ Failed to load file")
        return
    
    print(f"✅ File loaded successfully with {len(excel_processor.df)} records")
    
    # Get the dataframe
    df = excel_processor.df
    
    # Check for ProductStrain repeating ProductBrand
    print("\n🔍 Checking for ProductStrain repeating ProductBrand...")
    
    # Convert to string for comparison to avoid categorical issues
    product_strain_str = df['Product Strain'].astype(str)
    product_brand_str = df['Product Brand'].astype(str)
    
    # Find records where ProductStrain equals ProductBrand
    matching_records = df[product_strain_str == product_brand_str]
    
    if len(matching_records) > 0:
        print(f"⚠️  Found {len(matching_records)} records where ProductStrain equals ProductBrand:")
        
        # Show first 10 examples
        for idx, row in matching_records.head(10).iterrows():
            print(f"  Row {idx}: Strain='{row['Product Strain']}' Brand='{row['Product Brand']}' Type='{row['Product Type*']}'")
        
        # Check if this is happening for specific product types
        print("\n📊 Breakdown by Product Type:")
        type_counts = matching_records['Product Type*'].value_counts()
        for product_type, count in type_counts.items():
            print(f"  {product_type}: {count} records")
            
    else:
        print("✅ No records found where ProductStrain equals ProductBrand")
    
    # Check for any other patterns
    print("\n🔍 Additional analysis...")
    
    # Check for empty ProductStrain values
    empty_strain = df[df['Product Strain'].isna() | (df['Product Strain'] == '')]
    print(f"📝 Records with empty ProductStrain: {len(empty_strain)}")
    
    # Check for ProductStrain values that might be copied from other fields
    print("\n🔍 Checking for potential field copying issues...")
    
    # Look for ProductStrain values that contain common brand names
    brand_names = df['Product Brand'].dropna().unique()
    brand_names = [str(brand).strip() for brand in brand_names if str(brand).strip()]
    
    # Check if any ProductStrain values are exactly matching brand names
    strain_values = df['Product Strain'].dropna().unique()
    strain_values = [str(strain).strip() for strain in strain_values if str(strain).strip()]
    
    brand_strain_matches = set(brand_names) & set(strain_values)
    if brand_strain_matches:
        print(f"⚠️  Found {len(brand_strain_matches)} ProductStrain values that exactly match ProductBrand values:")
        for match in list(brand_strain_matches)[:10]:  # Show first 10
            print(f"  '{match}'")
    
    print("\n✅ Debug analysis complete")

if __name__ == "__main__":
    debug_productstrain_issue() 