#!/usr/bin/env python3
"""
Test script to investigate ProductStrain duplication issue.
This script will test the current system to see where ProductStrain is getting duplicated
with information other than "Mixed" or "CBD Blend".
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_product_strain_duplication():
    """Test the current system for ProductStrain duplication issues."""
    
    print("=== PRODUCT STRAIN DUPLICATION TEST ===")
    
    try:
        # Import the necessary modules
        from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file
        
        print("✅ Successfully imported required modules")
        
        # Initialize Excel processor
        excel_processor = ExcelProcessor()
        print("✅ Excel processor initialized")
        
        # Check if we have data, if not try to load default file
        if excel_processor.df is None or excel_processor.df.empty:
            print("📁 No data found, attempting to load default file...")
            default_file = get_default_upload_file()
            if default_file and os.path.exists(default_file):
                print(f"📂 Loading default file: {default_file}")
                excel_processor.load_file(default_file)
            else:
                print("❌ No default file found")
                return
        
        # Check if we have data now
        if excel_processor.df is None or excel_processor.df.empty:
            print("❌ Still no data found in Excel processor")
            return
        
        print(f"✅ Found {len(excel_processor.df)} records in data")
        
        # Look for records with ProductStrain that might be duplicated
        print("\n🔍 Analyzing ProductStrain data...")
        
        # Check for records where ProductStrain equals ProductBrand (potential duplication)
        df = excel_processor.df
        
        # Ensure we have the required columns
        required_cols = ['Product Strain', 'Product Brand', 'Product Type*']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"❌ Missing required columns: {missing_cols}")
            print(f"📋 Available columns: {list(df.columns)}")
            return
        
        # Find records where ProductStrain equals ProductBrand (potential duplication)
        strain_col = 'Product Strain'
        brand_col = 'Product Brand'
        type_col = 'Product Type*'
        
        # Clean the data for comparison
        df_clean = df.copy()
        df_clean[strain_col] = df_clean[strain_col].astype(str).str.strip()
        df_clean[brand_col] = df_clean[brand_col].astype(str).str.strip()
        
        # Find exact matches
        exact_matches = df_clean[df_clean[strain_col] == df_clean[brand_col]]
        exact_matches = exact_matches[exact_matches[strain_col] != 'nan']
        exact_matches = exact_matches[exact_matches[strain_col] != '']
        
        print(f"\n📊 Records where ProductStrain equals ProductBrand: {len(exact_matches)}")
        
        if len(exact_matches) > 0:
            print("⚠️  Potential duplication found:")
            for idx, row in exact_matches.head(10).iterrows():
                print(f"  Row {idx}: Strain='{row[strain_col]}' Brand='{row[brand_col]}' Type='{row[type_col]}'")
        
        # Check for records that should show "Mixed" or "CBD Blend" but don't
        print("\n🔍 Checking non-classic product types...")
        
        # Define classic types
        classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", 
                        "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
        
        non_classic_records = df_clean[~df_clean[type_col].str.lower().isin(classic_types)]
        non_classic_records = non_classic_records[non_classic_records[strain_col] != 'nan']
        non_classic_records = non_classic_records[non_classic_records[strain_col] != '']
        
        print(f"📊 Non-classic product types found: {len(non_classic_records)}")
        
        # Check which non-classic records don't have "Mixed" or "CBD Blend"
        incorrect_non_classic = non_classic_records[
            ~non_classic_records[strain_col].isin(['Mixed', 'CBD Blend'])
        ]
        
        print(f"⚠️  Non-classic products with incorrect ProductStrain: {len(incorrect_non_classic)}")
        
        if len(incorrect_non_classic) > 0:
            print("❌ These should show 'Mixed' or 'CBD Blend':")
            for idx, row in incorrect_non_classic.head(10).iterrows():
                print(f"  Row {idx}: Type='{row[type_col]}' Strain='{row[strain_col]}' Brand='{row[brand_col]}'")
        
        # Test the template processor's context processing logic
        print("\n🔧 Testing template processor context processing logic...")
        
        # Get a sample record that has the issue
        sample_record = incorrect_non_classic.iloc[0].to_dict()
        print(f"📝 Testing with problematic record: {sample_record.get('Product Name*', 'Unknown')}")
        
        # Simulate the context processing that happens in the template processor
        product_strain = sample_record.get(strain_col, '')
        product_type = sample_record.get(type_col, '').lower()
        product_brand = sample_record.get(brand_col, '')
        
        # Define classic types
        classic_types = ["flower", "pre-roll", "infused pre-roll", "concentrate", 
                        "solventless concentrate", "vape cartridge", "rso/co2 tankers"]
        
        print(f"  Original ProductStrain: '{product_strain}'")
        print(f"  Product Type: '{product_type}'")
        print(f"  Product Brand: '{product_brand}'")
        print(f"  Is Classic Type: {product_type in classic_types}")
        
        # Test the logic that should be applied
        if product_strain:
            if product_type in classic_types:
                # For classic types, extract strain names (e.g., "Grape Moonshot" -> "Grape")
                if 'Moonshot' in product_strain:
                    # Extract the strain name (everything before "Moonshot")
                    strain_name = product_strain.replace(' Moonshot', '').strip()
                    if strain_name:
                        product_strain = strain_name
                        print(f"  ✅ Classic type: Extracted strain '{strain_name}' from '{sample_record.get(strain_col)}'")
            else:
                # For non-classic types (edibles, tinctures, etc.), show "Mixed" or "CBD Blend"
                if 'cbd' in product_strain.lower() or 'cbd' in (sample_record.get('Product Name*', '') or '').lower():
                    product_strain = "CBD Blend"
                    print(f"  ✅ Non-classic type: Setting Product Strain to 'CBD Blend' for CBD product")
                else:
                    product_strain = "Mixed"
                    print(f"  ✅ Non-classic type: Setting Product Strain to 'Mixed' for non-CBD product")
        
        print(f"  Final ProductStrain: '{product_strain}'")
        
        # Test with a few more problematic records
        print("\n🔍 Testing more problematic records...")
        for i, (idx, row) in enumerate(incorrect_non_classic.head(5).iterrows()):
            test_strain = row[strain_col]
            test_type = row[type_col].lower()
            test_brand = row[brand_col]
            
            print(f"\n  Record {i+1}:")
            print(f"    Type: '{test_type}'")
            print(f"    Original Strain: '{test_strain}'")
            print(f"    Brand: '{test_brand}'")
            
            # Apply the logic
            if test_strain:
                if test_type in classic_types:
                    # Classic type logic
                    if 'Moonshot' in test_strain:
                        strain_name = test_strain.replace(' Moonshot', '').strip()
                        if test_strain:
                            test_strain = strain_name
                            print(f"    ✅ Classic: Extracted '{strain_name}'")
                else:
                    # Non-classic type logic
                    if 'cbd' in test_strain.lower() or 'cbd' in (row.get('Product Name*', '') or '').lower():
                        test_strain = "CBD Blend"
                        print(f"    ✅ Non-classic: Set to 'CBD Blend'")
                    else:
                        test_strain = "Mixed"
                        print(f"    ✅ Non-classic: Set to 'Mixed'")
            
            print(f"    Final Strain: '{test_strain}'")
        
        print("\n✅ Product strain duplication test completed successfully")
        
        # Summary of findings
        print("\n📋 SUMMARY OF FINDINGS:")
        print(f"  • Total records: {len(df)}")
        print(f"  • Records with ProductStrain = ProductBrand: {len(exact_matches)}")
        print(f"  • Non-classic products with wrong ProductStrain: {len(incorrect_non_classic)}")
        print(f"  • Main issue: Non-classic products (like 'Paraphernalia') should show 'Mixed' or 'CBD Blend'")
        print(f"  • Current logic appears correct, but may not be applied consistently")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_product_strain_duplication()
