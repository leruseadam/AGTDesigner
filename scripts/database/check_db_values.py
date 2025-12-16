#!/usr/bin/env python3
"""Quick script to check actual database values for products."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import get_product_database, get_current_store_name
import sqlite3

# Product names from the image
product_names = [
    "100 Rackz $ 100 RackzS Flower",
    "Gelato 33 S Gelato 33 S Flower", 
    "Terpgasm S Terpgasm S Flower",
    "Baby Joker: Baby Joker: Flower"
]

def check_database_values():
    """Check actual database values for products."""
    store_name = get_current_store_name()
    product_db = get_product_database(store_name)
    
    if not product_db:
        print("❌ Database not available")
        return
    
    print(f"📊 Database: {product_db.db_path}")
    print(f"🏪 Store: {store_name}")
    print("=" * 80)
    
    conn = product_db._get_connection()
    cursor = conn.cursor()
    
    for product_name in product_names:
        print(f"\n🔍 Product: {product_name}")
        print("-" * 80)
        
        # Get from products table with JOIN to strains
        cursor.execute('''
            SELECT p.id, p."Product Name*", p."Lineage" as products_lineage,
                   p."Product Strain", p.strain_id,
                   s.sovereign_lineage, s.canonical_lineage, s.strain_name
            FROM products p
            LEFT JOIN strains s ON p.strain_id = s.id
            WHERE p."Product Name*" LIKE ? OR p."ProductName" LIKE ?
            ORDER BY p.id DESC
            LIMIT 1
        ''', (f'%{product_name.split()[0]}%', f'%{product_name.split()[0]}%'))
        
        row = cursor.fetchone()
        
        if row:
            product_id, db_product_name, products_lineage, product_strain, strain_id, sovereign_lineage, canonical_lineage, strain_name = row
            
            print(f"  Products Table:")
            print(f"    - ID: {product_id}")
            print(f"    - Product Name*: {db_product_name}")
            print(f"    - Lineage (products.Lineage): {products_lineage}")
            print(f"    - Product Strain: {product_strain}")
            print(f"    - strain_id: {strain_id}")
            
            print(f"  Strains Table:")
            print(f"    - strain_name: {strain_name}")
            print(f"    - sovereign_lineage: {sovereign_lineage}")
            print(f"    - canonical_lineage: {canonical_lineage}")
            
            # Get what get_product_lineage returns
            lineage_from_method = product_db.get_product_lineage(db_product_name)
            print(f"  Method Results:")
            print(f"    - get_product_lineage(): {lineage_from_method}")
            
            # Get what get_products_by_names returns
            products_from_method = product_db.get_products_by_names([db_product_name])
            if products_from_method:
                p = products_from_method[0]
                print(f"    - get_products_by_names():")
                print(f"      - Lineage: {p.get('Lineage')}")
                print(f"      - currentLineage: {p.get('currentLineage')}")
                print(f"      - canonical_lineage: {p.get('canonical_lineage')}")
            
            # Calculate effective lineage
            effective = sovereign_lineage or canonical_lineage or products_lineage
            print(f"  ✅ Effective Lineage (sovereign > canonical > products): {effective}")
        else:
            print(f"  ❌ Product not found in database")
            
            # Try partial match
            cursor.execute('''
                SELECT p."Product Name*", p."Lineage"
                FROM products p
                WHERE p."Product Name*" LIKE ? OR p."ProductName" LIKE ?
                LIMIT 5
            ''', (f'%{product_name.split()[0]}%', f'%{product_name.split()[0]}%'))
            
            similar = cursor.fetchall()
            if similar:
                print(f"  💡 Similar products found:")
                for sim_name, sim_lineage in similar:
                    print(f"      - {sim_name}: {sim_lineage}")

if __name__ == '__main__':
    check_database_values()

