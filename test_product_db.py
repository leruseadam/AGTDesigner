#!/usr/bin/env python3
"""
Test script to verify product database functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import ProductDatabase

def test_product_database():
    print("🔍 Testing Product Database Functionality")
    print("=" * 50)
    
    try:
        # Initialize product database
        db_path = os.path.join(os.getcwd(), 'uploads', 'product_database.db')
        print(f"📁 Database path: {db_path}")
        
        if not os.path.exists(db_path):
            print(f"❌ Database file not found at: {db_path}")
            return
        
        product_db = ProductDatabase(db_path)
        print("✅ Product database initialized successfully")
        
        # Test adding a product
        test_product = {
            "Product Name*": "Test Product from JSON Import",
            "Product Type*": "Vape Cartridge",
            "Vendor/Supplier*": "Test Vendor",
            "Product Brand": "Test Brand",
            "Product Strain": "Test Strain",
            "Lineage": "HYBRID",
            "Weight*": "1",
            "Weight Unit* (grams/gm or ounces/oz)": "g",
            "Price* (Tier Name for Bulk)": "25",
            "Description": "Test product for database verification",
            "Source": "JSON Import Test",
            "Total Occurrences": 1
        }
        
        print("📝 Testing product addition...")
        success = product_db.add_or_update_product(test_product)
        
        if success:
            print("✅ Product added successfully")
            
            # Verify the product was added
            product_info = product_db.get_product_info("Test Product from JSON Import")
            if product_info:
                print("✅ Product found in database after addition")
                print(f"   Name: {product_info.get('Product Name*', 'Unknown')}")
                print(f"   Type: {product_info.get('Product Type*', 'Unknown')}")
                print(f"   Vendor: {product_info.get('Vendor/Supplier*', 'Unknown')}")
            else:
                print("❌ Product not found in database after addition")
        else:
            print("❌ Failed to add product to database")
        
        # Get total products
        all_products = product_db.get_all_products()
        print(f"📊 Total products in database: {len(all_products)}")
        
        # Look for recent products
        recent_products = []
        for product in all_products:
            if "Test" in product.get("Product Name*", ""):
                recent_products.append(product)
        
        print(f"✅ Found {len(recent_products)} test products in database")
        for i, product in enumerate(recent_products, 1):
            print(f"   {i}. {product.get('Product Name*', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error testing product database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_product_database()
