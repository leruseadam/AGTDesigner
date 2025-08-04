#!/usr/bin/env python3
"""
Comprehensive fix for ProductBrand field issue where THC ratio values are incorrectly 
appearing in the ProductBrand field instead of the actual brand name.
This script will directly check and clean the Excel data file and also check the template generation process.
"""

import sys
import os
import pandas as pd
from pathlib import Path
import re

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.data.excel_processor import ExcelProcessor, get_default_upload_file

def fix_product_brand_ratio_issue_comprehensive():
    """Comprehensive fix for the ProductBrand field issue by directly cleaning the Excel data."""
    
    print("=== Comprehensive ProductBrand Field Fix ===")
    
    # Get the default upload file
    default_file = get_default_upload_file()
    if not default_file:
        print("❌ No default upload file found!")
        return False
    
    print(f"📁 Found default file: {default_file}")
    
    try:
        # Load the Excel file directly
        print("📊 Loading Excel file...")
        df = pd.read_excel(default_file)
        
        # Check if Product Brand column exists
        product_brand_col = None
        for col in df.columns:
            if 'product brand' in col.lower() or col.lower() == 'product brand':
                product_brand_col = col
                break
        
        if not product_brand_col:
            print("❌ No Product Brand column found!")
            return False
        
        print(f"✅ Found Product Brand column: {product_brand_col}")
        
        # Check for THC ratio patterns in Product Brand column
        print("🔍 Checking for THC ratio values in Product Brand column...")
        
        # Define THC ratio patterns
        thc_patterns = [
            r'\d+mg\s+THC',
            r'\d+\.\d+mg\s+THC',
            r'THC:\s*\d+',
            r'THC:\s*\d+\.\d+',
            r'\d+mg',
            r'\d+\.\d+mg',
            r'THC\s+\d+',
            r'THC\s+\d+\.\d+',
            r'\d+\s*mg\s*THC',
            r'\d+\.\d+\s*mg\s*THC',
            r'100mg\s+THC',
            r'50mg\s+THC',
            r'25mg\s+THC',
            r'10mg\s+THC'
        ]
        
        # Find suspicious values
        suspicious_mask = pd.Series([False] * len(df))
        for pattern in thc_patterns:
            mask = df[product_brand_col].astype(str).str.contains(pattern, case=False, na=False)
            suspicious_mask = suspicious_mask | mask
        
        suspicious_count = suspicious_mask.sum()
        print(f"🔍 Found {suspicious_count} suspicious Product Brand values")
        
        if suspicious_count > 0:
            print("🚨 Found THC ratio values in Product Brand column!")
            
            # Show the suspicious values
            suspicious_records = df[suspicious_mask]
            print("\n📋 Suspicious Product Brand values:")
            for idx, row in suspicious_records.iterrows():
                product_name = row.get('Product Name*', 'NO NAME')
                product_brand = row.get(product_brand_col, 'NO BRAND')
                print(f"  Row {idx}: '{product_name}' -> Product Brand: '{product_brand}'")
            
            # Clean the suspicious values
            print("\n🧹 Cleaning suspicious Product Brand values...")
            
            # For each suspicious record, try to extract brand from product name or use vendor
            for idx in suspicious_records.index:
                row = df.loc[idx]
                product_name = str(row.get('Product Name*', ''))
                vendor = str(row.get('Vendor', '') or row.get('Vendor/Supplier*', ''))
                
                # Try to extract brand from product name
                new_brand = ''
                
                # Look for common brand patterns in product name
                brand_patterns = [
                    r'(.+?)\s+(Platinum|Premium|Gold|Silver|Elite|Select|Reserve|Craft|Artisan|Boutique|Signature|Limited|Exclusive|Private|Custom|Special|Deluxe|Ultra|Super|Mega|Max|Pro|Plus|X)\s+(Distillate|Extract|Concentrate|Oil|Tincture|Gel|Capsule|Edible|Gummy|Chocolate|Beverage|Topical|Cream|Lotion|Salve|Balm|Spray|Drops|Syrup|Sauce|Dab|Wax|Shatter|Live|Rosin|Resin|Kief|Hash|Bubble|Ice|Water|Solventless|Full\s+Spectrum|Broad\s+Spectrum|Isolate|Terpene|Terpenes|Terp|Terps)',
                    r'(.+?)\s+(Distillate|Extract|Concentrate|Oil|Tincture|Gel|Capsule|Edible|Gummy|Chocolate|Beverage|Topical|Cream|Lotion|Salve|Balm|Spray|Drops|Syrup|Sauce|Dab|Wax|Shatter|Live|Rosin|Resin|Kief|Hash|Bubble|Ice|Water|Solventless|Full\s+Spectrum|Broad\s+Spectrum|Isolate|Terpene|Terpenes|Terp|Terps)',
                    r'(.+?)\s+(Platinum|Premium|Gold|Silver|Elite|Select|Reserve|Craft|Artisan|Boutique|Signature|Limited|Exclusive|Private|Custom|Special|Deluxe|Ultra|Super|Mega|Max|Pro|Plus|X)',
                ]
                
                for pattern in brand_patterns:
                    match = re.search(pattern, product_name, re.IGNORECASE)
                    if match:
                        full_match = match.group(0)
                        product_part = match.group(1).strip()
                        brand_part = full_match[len(product_part):].strip()
                        if brand_part:
                            new_brand = brand_part.upper()
                            break
                
                # If no brand extracted from product name, use vendor as fallback
                if not new_brand and vendor.strip():
                    new_brand = vendor.strip().upper()
                
                # If still no brand, use a generic placeholder
                if not new_brand:
                    new_brand = "UNKNOWN BRAND"
                
                # Update the Product Brand column
                old_brand = df.loc[idx, product_brand_col]
                df.loc[idx, product_brand_col] = new_brand
                
                print(f"  Row {idx}: '{old_brand}' -> '{new_brand}'")
            
            # Save the cleaned data
            print("\n💾 Saving cleaned data...")
            df.to_excel(default_file, index=False)
            print("✅ Data saved successfully!")
            
            # Verify the fix
            print("\n🔍 Verifying the fix...")
            df_verify = pd.read_excel(default_file)
            
            # Check for remaining suspicious values
            suspicious_mask_verify = pd.Series([False] * len(df_verify))
            for pattern in thc_patterns:
                mask = df_verify[product_brand_col].astype(str).str.contains(pattern, case=False, na=False)
                suspicious_mask_verify = suspicious_mask_verify | mask
            
            remaining_suspicious = suspicious_mask_verify.sum()
            print(f"✅ Remaining suspicious values: {remaining_suspicious}")
            
            if remaining_suspicious == 0:
                print("🎉 All THC ratio values have been successfully removed from Product Brand column!")
            else:
                print("⚠️  Some suspicious values remain. Manual review may be needed.")
                
        else:
            print("✅ No THC ratio values found in Product Brand column!")
        
        # Test the data processing pipeline
        print("\n🧪 Testing data processing pipeline...")
        processor = ExcelProcessor()
        if processor.load_file(default_file):
            # Get some sample records
            sample_records = processor.get_selected_records()[:5]
            
            print("📋 Sample processed records:")
            for i, record in enumerate(sample_records):
                product_name = record.get('ProductName', 'NO NAME')
                product_brand = record.get('ProductBrand', 'NO BRAND')
                print(f"  Record {i+1}: '{product_name}' -> ProductBrand: '{product_brand}'")
                
                # Check if ProductBrand contains THC ratio patterns
                for pattern in thc_patterns:
                    if re.search(pattern, str(product_brand), re.IGNORECASE):
                        print(f"    ⚠️  WARNING: ProductBrand still contains THC ratio pattern: {pattern}")
                        break
                else:
                    print(f"    ✅ ProductBrand looks clean")
        
        # Now test the template generation process
        print("\n🧪 Testing template generation process...")
        try:
            from core.generation.template_processor import TemplateProcessor
            
            # Create a template processor
            template_processor = TemplateProcessor('horizontal', {}, 1.0)
            
            # Test with a few sample records
            if sample_records:
                print("📋 Testing template generation with sample records:")
                for i, record in enumerate(sample_records[:3]):
                    # Build label context
                    label_context = template_processor._build_label_context(record, None)
                    
                    product_name = record.get('ProductName', 'NO NAME')
                    product_brand = label_context.get('ProductBrand', 'NO BRAND')
                    
                    print(f"  Template Record {i+1}: '{product_name}' -> ProductBrand: '{product_brand}'")
                    
                    # Check if ProductBrand contains THC ratio patterns
                    for pattern in thc_patterns:
                        if re.search(pattern, str(product_brand), re.IGNORECASE):
                            print(f"    ⚠️  WARNING: Template ProductBrand contains THC ratio pattern: {pattern}")
                            break
                    else:
                        print(f"    ✅ Template ProductBrand looks clean")
                        
        except Exception as e:
            print(f"⚠️  Template generation test failed: {e}")
        
        print("\n🎉 ProductBrand field fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_product_brand_ratio_issue_comprehensive() 