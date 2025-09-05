#!/usr/bin/env python3
"""
Test script to verify JSON save method with a simple test case
"""

import requests
import json
import sqlite3
import os
from datetime import datetime, timedelta

def test_json_save():
    base_url = "http://127.0.0.1:5003"
    
    print("🔍 Testing JSON Save Method")
    print("=" * 50)
    
    # Step 1: Check current database count
    print("📦 Step 1: Checking current database state...")
    try:
        db_path = os.path.join(os.getcwd(), 'uploads', 'product_database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM products")
        initial_count = cursor.fetchone()[0]
        print(f"📊 Initial database count: {initial_count}")
        
        # Check for recent Oleum products
        one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            SELECT "Product Name*", "Vendor/Supplier*", created_at 
            FROM products 
            WHERE "Vendor/Supplier*" LIKE '%Oleum%' AND created_at > ?
            ORDER BY created_at DESC
        """, (one_hour_ago,))
        
        oleum_products = cursor.fetchall()
        print(f"📋 Found {len(oleum_products)} recent Oleum products")
        for product in oleum_products:
            print(f"   - {product[0]} (Vendor: {product[1]}, Created: {product[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return
    
    # Step 2: Create a test JSON with a unique product
    print("\n📦 Step 2: Creating test JSON with unique product...")
    test_json = {
        "inventory_transfer_items": [
            {
                "name": "Test Unique Product by Oleum",
                "vendor": "Oleum",
                "brand": "Oleum",
                "strain_name": "Test Strain",
                "inventory_type": "vape_cartridge",
                "unit_weight": "1",
                "price": "25"
            }
        ],
        "from_license_name": "Oleum"
    }
    
    # Step 3: Test JSON matching with this unique product
    print("\n📦 Step 3: Testing JSON matching...")
    try:
        # First, let's test with a simple POST to see if the server is working
        response = requests.post(
            f"{base_url}/api/json-match",
            json={"url": "data:application/json;base64," + json.dumps(test_json).encode().hex()},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON matching successful!")
            print(f"   Matched count: {result.get('matched_count', 0)}")
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error during JSON matching: {e}")
        return
    
    # Step 4: Check if new products were saved
    print("\n📦 Step 4: Checking for new products...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM products")
        final_count = cursor.fetchone()[0]
        print(f"📊 Final database count: {final_count}")
        print(f"📊 Database change: {final_count - initial_count}")
        
        # Check for the test product
        cursor.execute("""
            SELECT "Product Name*", "Vendor/Supplier*", created_at 
            FROM products 
            WHERE "Product Name*" LIKE '%Test Unique Product%'
            ORDER BY created_at DESC
        """)
        
        test_products = cursor.fetchall()
        print(f"📋 Found {len(test_products)} test products")
        for product in test_products:
            print(f"   - {product[0]} (Vendor: {product[1]}, Created: {product[2]})")
        
        # Check for recent Oleum products again
        cursor.execute("""
            SELECT "Product Name*", "Vendor/Supplier*", created_at 
            FROM products 
            WHERE "Vendor/Supplier*" LIKE '%Oleum%' AND created_at > ?
            ORDER BY created_at DESC
        """, (one_hour_ago,))
        
        oleum_products = cursor.fetchall()
        print(f"📋 Found {len(oleum_products)} recent Oleum products after test")
        for product in oleum_products:
            print(f"   - {product[0]} (Vendor: {product[1]}, Created: {product[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking final database state: {e}")
        return

if __name__ == "__main__":
    test_json_save()
