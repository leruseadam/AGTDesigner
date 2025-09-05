#!/usr/bin/env python3
"""
Test script to check database products after JSON matching
"""

import requests
import json
import sqlite3
import os
from datetime import datetime, timedelta

def test_database_products():
    base_url = "http://127.0.0.1:5003"
    
    print("🔍 Testing Database Products After JSON Matching")
    print("=" * 60)
    
    # Step 1: Perform JSON matching to populate database
    print("📦 Step 1: Performing JSON matching...")
    try:
        response = requests.post(
            f"{base_url}/api/json-match",
            json={"url": "https://files.cultivera.com/435553542D5753353635/Interop/25/34/GFJZZ9ZJQKVBWQDR/Cultivera_ORD-11766_422044.json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ JSON matching successful!")
            print(f"   Matched count: {result.get('matched_count', 0)}")
        else:
            print(f"❌ JSON matching failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error during JSON matching: {e}")
        return
    
    # Step 2: Check database for new products
    print("\n📦 Step 2: Checking database for new products...")
    try:
        # Connect to the database
        db_path = os.path.join(os.getcwd(), 'uploads', 'product_database.db')
        if not os.path.exists(db_path):
            print(f"❌ Database not found at: {db_path}")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total products in database
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        print(f"📊 Total products in database: {total_products}")
        
        # Get recent products (created in the last hour)
        one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            SELECT "Product Name*", "Product Type*", "Vendor/Supplier*", "Product Brand", "Product Strain", 
                   "Weight*", "Price* (Tier Name for Bulk)", created_at, total_occurrences
            FROM products 
            WHERE created_at > ?
            ORDER BY created_at DESC
        """, (one_hour_ago,))
        
        recent_products = cursor.fetchall()
        
        print(f"✅ Found {len(recent_products)} recent products in database:")
        for i, product in enumerate(recent_products, 1):
            name, ptype, vendor, brand, strain, weight, price, created, occurrences = product
            print(f"   {i}. {name}")
            print(f"      Type: {ptype}, Vendor: {vendor}, Brand: {brand}")
            print(f"      Strain: {strain}, Weight: {weight}, Price: {price}")
            print(f"      Created: {created}, Occurrences: {occurrences}")
            print()
        
        # Get all products with "Oleum" vendor (from the JSON data)
        cursor.execute("""
            SELECT "Product Name*", "Product Type*", "Vendor/Supplier*", "Product Brand", "Product Strain", 
                   "Weight*", "Price* (Tier Name for Bulk)", created_at, total_occurrences
            FROM products 
            WHERE "Vendor/Supplier*" LIKE '%Oleum%'
            ORDER BY "Product Name*"
        """)
        
        oleum_products = cursor.fetchall()
        
        print(f"✅ Found {len(oleum_products)} Oleum products in database:")
        for i, product in enumerate(oleum_products, 1):
            name, ptype, vendor, brand, strain, weight, price, created, occurrences = product
            print(f"   {i}. {name}")
            print(f"      Type: {ptype}, Vendor: {vendor}, Brand: {brand}")
            print(f"      Strain: {strain}, Weight: {weight}, Price: {price}")
            print(f"      Created: {created}, Occurrences: {occurrences}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return
    
    # Step 3: Check available tags to see if new products are included
    print("\n📦 Step 3: Checking available tags for new products...")
    try:
        response = requests.get(f"{base_url}/api/available-tags")
        if response.status_code == 200:
            result = response.json()
            available_tags = result.get('available_tags', [])
            
            # Look for Oleum products in available tags
            oleum_products_in_tags = []
            for tag in available_tags:
                if isinstance(tag, dict):
                    vendor = tag.get('Vendor/Supplier*', '')
                    if 'Oleum' in vendor:
                        oleum_products_in_tags.append(tag.get('Product Name*', 'Unknown'))
            
            print(f"✅ Found {len(oleum_products_in_tags)} Oleum products in available tags:")
            for i, name in enumerate(oleum_products_in_tags, 1):
                print(f"   {i}. {name}")
        else:
            print(f"❌ Failed to get available tags: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking available tags: {e}")

if __name__ == "__main__":
    test_database_products()
