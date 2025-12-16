#!/usr/bin/env python3
"""
Check if a specific product exists in the database
"""
import sys
import os
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_product_in_database(product_name, vendor=None, brand=None):
    """Check if a product exists in the database."""
    
    print("=" * 80)
    print("CHECKING DATABASE FOR PRODUCT")
    print("=" * 80)
    print(f"Product Name: {product_name}")
    if vendor:
        print(f"Vendor: {vendor}")
    if brand:
        print(f"Brand: {brand}")
    print()
    
    # Try to get database path
    try:
        from app import get_product_database, get_current_store_name
        store_name = get_current_store_name()
        print(f"Store Name: {store_name}")
        
        product_db = get_product_database(store_name)
        if not product_db:
            print("❌ Could not get product database")
            return
        
        db_path = getattr(product_db, 'db_path', None)
        if not db_path:
            print("❌ Database path not found")
            return
        
        print(f"Database Path: {db_path}")
        print()
        
        # Check if database file exists
        if not os.path.exists(db_path):
            print(f"❌ Database file does not exist: {db_path}")
            return
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total product count
        cursor.execute("SELECT COUNT(*) FROM products")
        total_count = cursor.fetchone()[0]
        print(f"Total products in database: {total_count}")
        print()
        
        # Search for the product
        print("Searching for product...")
        print()
        
        # Try exact match first
        cursor.execute('''
            SELECT "Product Name*", "Vendor/Supplier*", "Product Brand", "Weight*", "Units", "Price", "Lineage"
            FROM products
            WHERE "Product Name*" LIKE ?
        ''', (f'%{product_name}%',))
        
        results = cursor.fetchall()
        
        if results:
            print(f"✅ Found {len(results)} matching product(s):")
            print()
            for i, row in enumerate(results, 1):
                name, vendor_db, brand_db, weight, units, price, lineage = row
                print(f"  {i}. {name}")
                print(f"     Vendor: {vendor_db or 'N/A'}")
                print(f"     Brand: {brand_db or 'N/A'}")
                print(f"     Weight: {weight or 'N/A'} {units or ''}")
                print(f"     Price: {price or 'N/A'}")
                print(f"     Lineage: {lineage or 'N/A'}")
                print()
        else:
            print("❌ No products found matching that name")
            print()
            
            # Try searching for "Donny Burger" or "Bacon" separately
            print("Trying partial matches...")
            cursor.execute('''
                SELECT "Product Name*", "Vendor/Supplier*", "Product Brand"
                FROM products
                WHERE "Product Name*" LIKE '%Donny%' OR "Product Name*" LIKE '%Burger%'
                LIMIT 10
            ''')
            partial_results = cursor.fetchall()
            
            if partial_results:
                print(f"Found {len(partial_results)} products with 'Donny' or 'Burger':")
                for row in partial_results:
                    print(f"  - {row[0]} (Vendor: {row[1]}, Brand: {row[2]})")
            else:
                print("No products found with 'Donny' or 'Burger'")
            
            print()
            
            # Check for Bacon's Buds vendor
            print("Checking for Bacon's Buds vendor...")
            cursor.execute('''
                SELECT "Product Name*", "Vendor/Supplier*", "Product Brand"
                FROM products
                WHERE "Vendor/Supplier*" LIKE '%Bacon%' OR "Product Brand" LIKE '%Bacon%'
                LIMIT 10
            ''')
            vendor_results = cursor.fetchall()
            
            if vendor_results:
                print(f"Found {len(vendor_results)} products from Bacon's Buds:")
                for row in vendor_results:
                    print(f"  - {row[0]} (Vendor: {row[1]}, Brand: {row[2]})")
            else:
                print("No products found from Bacon's Buds")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    product_name = "Donny Burger by Bacon's Buds - 3.5g"
    check_product_in_database(product_name, vendor="Bacon's Buds", brand="Bacon's Buds")

