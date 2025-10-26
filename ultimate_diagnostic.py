#!/usr/bin/env python3
"""
ULTIMATE DIAGNOSTIC: See actual JSON matched names vs database names
"""

import json
import sys
import os

def check_json_matches():
    """Extract and analyze the actual JSON matched names."""
    
    print("=" * 70)
    print("ULTIMATE DIAGNOSTIC: JSON MATCHED NAMES vs DATABASE")
    print("=" * 70)
    
    try:
        # Look for JSON files with CERES vendor data
        json_files = [
            'data/product_data_CERES.json',
            'data/product_data.json',
            'uploads/product_data_CERES.json',
            'uploads/product_data.json',
            'src/data/product_data_CERES.json',
            'src/data/product_data.json'
        ]
        
        found_json = None
        for json_file in json_files:
            if os.path.exists(json_file):
                found_json = json_file
                break
        
        if not found_json:
            print("❌ No JSON data files found")
            print(f"   Searched: {json_files}")
            return
        
        print(f"🔍 FOUND JSON FILE: {found_json}")
        
        with open(found_json, 'r') as f:
            json_data = json.load(f)
        
        print(f"📊 JSON DATA STATS:")
        print(f"   Total products in JSON: {len(json_data)}")
        
        # Filter to CERES products (matching the logic from your matching)
        ceres_products = []
        for product in json_data:
            vendor = product.get('vendor', '').upper()
            if 'CERES' in vendor:
                ceres_products.append(product)
        
        print(f"   CERES products in JSON: {len(ceres_products)}")
        
        # Show first 20 JSON product names
        print(f"\n🔍 FIRST 20 JSON CERES PRODUCT NAMES:")
        for i, product in enumerate(ceres_products[:20], 1):
            product_name = product.get('product_name', product.get('name', 'UNKNOWN'))
            vendor = product.get('vendor', 'UNKNOWN')
            print(f"   {i:2d}. {product_name} (Vendor: {vendor})")
        
        if len(ceres_products) > 20:
            print(f"   ... and {len(ceres_products) - 20} more")
        
        # Now check normalization and database matching
        sys.path.append('src')
        from core.data.product_database import ProductDatabase
        
        db = ProductDatabase()
        
        # Test normalization
        print(f"\n🧪 TESTING NORMALIZATION & DATABASE LOOKUP:")
        
        test_json_names = [product.get('product_name', product.get('name', '')) for product in ceres_products[:10]]
        
        print(f"   Testing first 10 JSON product names...")
        
        for i, json_name in enumerate(test_json_names, 1):
            if not json_name:
                continue
                
            # Normalize the JSON name the same way the database does
            normalized_name = db._normalize_product_name(json_name)
            
            # Check if it exists in database
            db_records = db.get_products_by_names([json_name])
            
            found_in_db = len(db_records) > 0 and db_records[0].get('id') is not None
            
            print(f"\n   {i:2d}. JSON: '{json_name}'")
            print(f"       Normalized: '{normalized_name}'")
            print(f"       Found in DB: {'✅ YES' if found_in_db else '❌ NO'}")
            
            if found_in_db:
                db_name = db_records[0].get('Product Name*', '')
                print(f"       DB Name: '{db_name}'")
        
        # Count how many would actually match
        print(f"\n🎯 TESTING ALL {len(ceres_products)} JSON PRODUCTS...")
        
        all_json_names = [product.get('product_name', product.get('name', '')) for product in ceres_products if product.get('product_name', product.get('name', ''))]
        
        if len(all_json_names) != len(ceres_products):
            print(f"   ⚠️  Warning: {len(ceres_products) - len(all_json_names)} products have no name")
        
        # Batch lookup
        db_records = db.get_products_by_names(all_json_names)
        
        # Count valid matches
        valid_matches = [record for record in db_records if record.get('id') is not None]
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"   JSON CERES products: {len(ceres_products)}")
        print(f"   JSON products with names: {len(all_json_names)}")
        print(f"   Database records returned: {len(db_records)}")
        print(f"   Valid database matches: {len(valid_matches)}")
        
        print(f"\n🎯 CONCLUSION:")
        if len(valid_matches) == 18:
            print(f"   ✅ This explains the 18 labels!")
            print(f"   Only {len(valid_matches)} of {len(all_json_names)} JSON names exist in database")
        else:
            print(f"   ❓ Expected 18 but got {len(valid_matches)} valid matches")
        
        # Show which ones matched
        if valid_matches:
            print(f"\n✅ VALID MATCHES (first 10):")
            for i, record in enumerate(valid_matches[:10], 1):
                print(f"   {i:2d}. {record.get('Product Name*', 'UNKNOWN')}")
            
            if len(valid_matches) > 10:
                print(f"   ... and {len(valid_matches) - 10} more")
        
    except Exception as e:
        print(f"❌ Error in diagnostic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_json_matches()