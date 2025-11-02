#!/usr/bin/env python3
"""
Test script to verify lineage alignment is working correctly
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import ProductDatabase

def test_lineage_alignment():
    """Test that lineages are properly aligned between products and strains"""

    print("🔍 Testing lineage alignment...\n")

    # Create database instance
    db = ProductDatabase()

    # Get connection
    conn = db._get_connection()
    cursor = conn.cursor()

    # Test a few products that we know have mismatches
    test_products = [
        "$10 Chillum Pack by VID INC",
        "100 Rackz by Mt Baker Homegrown - 14g",
        "*VOID* 1:1:1:1 Dark Chocolate Sea Salt 420 Minis b"
    ]

    print("Testing sample products:")
    print("-" * 80)

    for product_name in test_products:
        # Get product info
        normalized = db._normalize_product_name(product_name)
        cursor.execute('''
            SELECT p."Product Strain", p."Lineage"
            FROM products p
            WHERE p."Product Name*" = ? OR p.normalized_name = ?
            ORDER BY p.id DESC
            LIMIT 1
        ''', (product_name, normalized))

        row = cursor.fetchone()
        if not row:
            print(f"❌ Product not found: {product_name}")
            continue

        product_strain, product_lineage = row[0], row[1]

        # Get strain lineage
        strain_lineage = None
        if product_strain:
            norm_strain = db._normalize_strain_name(str(product_strain))
            cursor.execute('''
                SELECT COALESCE(sovereign_lineage, canonical_lineage) AS current_lineage
                FROM strains s
                WHERE s.normalized_name = ?
                LIMIT 1
            ''', (norm_strain,))
            srow = cursor.fetchone()
            if srow:
                strain_lineage = srow[0]

        # Display results
        resolved_lineage = strain_lineage or product_lineage
        match_status = "✅" if product_lineage == strain_lineage else "❌"

        print(f"\n{match_status} {product_name[:50]}")
        print(f"   Strain: {product_strain}")
        print(f"   Product Lineage: {product_lineage}")
        print(f"   Strain Lineage: {strain_lineage}")
        print(f"   Resolved (should be used): {resolved_lineage}")

    print("\n" + "-" * 80)
    print("\n✨ The backend should now return the 'Resolved' lineage for each product")
    print("   This ensures UI displays match database values.\n")

    conn.close()

if __name__ == '__main__':
    test_lineage_alignment()
