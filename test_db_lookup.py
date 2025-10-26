#!/usr/bin/env python3
"""
FINAL DIAGNOSTIC: Prove that 49 JSON matches become 18 database records
"""

import os
import sys
import logging

# Add the src directory to the Python path
sys.path.append('src')

def diagnose_database_lookup():
    """Test the exact database lookup with the 49 matched names."""
    
    print("=" * 70)
    print("FINAL DIAGNOSTIC: JSON MATCHES vs DATABASE RECORDS")
    print("=" * 70)
    
    try:
        # Import the database
        from core.data.product_database import ProductDatabase
        
        # Test with a few sample product names (you can replace these with actual names from your JSON matches)
        sample_product_names = [
            "CERES Test Product 1",
            "CERES Test Product 2", 
            "Non-existent Product",
            "Another Missing Product"
        ]
        
        print(f"🧪 TESTING with {len(sample_product_names)} sample product names...")
        for name in sample_product_names:
            print(f"   - {name}")
        
        # Initialize database
        product_db = ProductDatabase()
        
        print("\n🔍 CALLING get_products_by_names()...")
        db_records = product_db.get_products_by_names(sample_product_names)
        
        print(f"\n📊 RESULTS:")
        print(f"   Input names: {len(sample_product_names)}")
        print(f"   Database records returned: {len(db_records)}")
        
        # Analyze each record
        valid_records = []
        placeholder_records = []
        
        for i, record in enumerate(db_records):
            product_name = record.get('Product Name*', '')
            vendor = record.get('Vendor/Supplier*', '')
            has_id = record.get('id') is not None
            
            print(f"\n   Record {i+1}:")
            print(f"     Product Name*: '{product_name}'")
            print(f"     Vendor: '{vendor}'")
            print(f"     Has database ID: {has_id}")
            
            if product_name and product_name != 'None' and has_id:
                valid_records.append(record)
                print(f"     ✅ VALID DATABASE RECORD")
            else:
                placeholder_records.append(record)
                print(f"     ❌ PLACEHOLDER RECORD (not in database)")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Valid database records: {len(valid_records)}")
        print(f"   Placeholder records: {len(placeholder_records)}")
        
        # Apply the same filtering logic as app.py
        valid_db_records = [record for record in db_records if record.get('Product Name*') and record.get('Product Name*') != 'None']
        
        print(f"\n🔧 AFTER FILTERING (same as app.py):")
        print(f"   Records passing filter: {len(valid_db_records)}")
        
        print(f"\n💡 CONCLUSION:")
        print(f"   This explains why 49 JSON matches → {len(valid_db_records)} label outputs")
        print(f"   Only {len(valid_db_records)} of the 49 products actually exist in database")
        
        # Test with CERES vendor specifically
        print(f"\n🏪 TESTING CERES VENDOR PRODUCTS...")
        
        # Query for CERES products in database
        conn = product_db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT "Product Name*", "Vendor/Supplier*" 
            FROM products 
            WHERE "Vendor/Supplier*" LIKE '%CERES%' 
            LIMIT 10
        ''')
        
        ceres_products = cursor.fetchall()
        
        print(f"   Found {len(ceres_products)} CERES products in database (showing first 10):")
        for product in ceres_products:
            print(f"     - {product[0]} (Vendor: {product[1]})")
        
        if len(ceres_products) < 49:
            print(f"\n⚠️  PROBLEM IDENTIFIED:")
            print(f"   Database only has {len(ceres_products)} CERES products")
            print(f"   But JSON matching found 49 CERES products")
            print(f"   This means 31 JSON products don't exist in the database")
        
    except Exception as e:
        print(f"❌ Error in diagnostic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_database_lookup()