#!/usr/bin/env python3
"""
Test script to verify the save method in JSON matcher
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor
from src.core.data.product_database import ProductDatabase

def test_save_method():
    print("🔍 Testing JSON Matcher Save Method")
    print("=" * 50)
    
    try:
        # Initialize components
        excel_processor = ExcelProcessor()
        product_db = ProductDatabase(os.path.join(os.getcwd(), 'uploads', 'product_database.db'))
        json_matcher = JSONMatcher(excel_processor, product_db)
        
        print("✅ Components initialized")
        
        # Test product data
        test_product = {
            'Product Name*': 'Test JSON Product',
            'Product Type*': 'Vape Cartridge',
            'Vendor/Supplier*': 'Test Vendor',
            'Product Brand': 'Test Brand',
            'Product Strain': 'Test Strain',
            'Lineage': 'HYBRID',
            'Weight*': '1',
            'Weight Unit* (grams/gm or ounces/oz)': 'g',
            'Price* (Tier Name for Bulk)': '25',
            'Description': 'Test product from JSON matcher'
        }
        
        print("📝 Testing save method...")
        success = json_matcher._save_product_to_database(test_product, 'Test Vendor', 'Test JSON Product')
        
        if success:
            print("✅ Save method successful")
            
            # Verify the product was saved
            import sqlite3
            conn = sqlite3.connect(os.path.join(os.getcwd(), 'uploads', 'product_database.db'))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT "Product Name*", "Vendor/Supplier*", "Product Brand", created_at 
                FROM products 
                WHERE "Product Name*" = ?
            ''', ('Test JSON Product',))
            
            result = cursor.fetchone()
            if result:
                print("✅ Product found in database after save")
                print(f"   Name: {result[0]}")
                print(f"   Vendor: {result[1]}")
                print(f"   Brand: {result[2]}")
                print(f"   Created: {result[3]}")
            else:
                print("❌ Product not found in database after save")
            
            conn.close()
        else:
            print("❌ Save method failed")
        
    except Exception as e:
        print(f"❌ Error testing save method: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_save_method()
