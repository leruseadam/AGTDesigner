#!/usr/bin/env python3
"""
CRITICAL FIX: Link all products to strains table via strain_id

This script:
1. Finds all products with NULL strain_id
2. Matches them to strains by Product Strain name
3. Updates the strain_id to link products to the strains table
4. This enables products to use canonical_lineage and sovereign_lineage from strains table
"""

import sqlite3
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import ProductDatabase
from app import get_current_store_name, get_product_database

def fix_strain_id_linkage():
    """Link all products to strains table via strain_id."""

    print("=" * 80)
    print("FIXING STRAIN_ID LINKAGE")
    print("=" * 80)

    # Get the product database
    store_name = get_current_store_name()
    if not store_name:
        print("❌ Error: No store selected")
        return

    print(f"✅ Store: {store_name}")

    product_db = get_product_database(store_name)
    if not product_db:
        print("❌ Error: Could not get product database")
        return

    conn = product_db._get_connection()
    cursor = conn.cursor()

    # Check current status
    cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN strain_id IS NOT NULL THEN 1 ELSE 0 END) as linked,
            SUM(CASE WHEN strain_id IS NULL THEN 1 ELSE 0 END) as unlinked
        FROM products
    ''')

    total, linked, unlinked = cursor.fetchone()

    print(f"\n📊 Current Status:")
    print(f"   Total products: {total}")
    print(f"   With strain_id: {linked} ({linked*100/total:.1f}%)")
    print(f"   Without strain_id: {unlinked} ({unlinked*100/total:.1f}%)")

    if unlinked == 0:
        print("\n✅ All products already linked!")
        return

    print(f"\n🔧 Fixing {unlinked} unlinked products...")
    print("-" * 80)

    # Strategy 1: Match by Product Strain name (exact match)
    print("\n📋 Strategy 1: Matching by Product Strain (exact)")
    cursor.execute('''
        UPDATE products
        SET strain_id = (
            SELECT s.id
            FROM strains s
            WHERE s.strain_name = products."Product Strain"
            LIMIT 1
        )
        WHERE strain_id IS NULL
          AND "Product Strain" IS NOT NULL
          AND "Product Strain" != ''
          AND EXISTS (
              SELECT 1 FROM strains s
              WHERE s.strain_name = products."Product Strain"
          )
    ''')

    matched_exact = cursor.rowcount
    conn.commit()
    print(f"   ✅ Matched {matched_exact} products by exact Product Strain name")

    # Strategy 2: Match by normalized strain name
    print("\n📋 Strategy 2: Matching by normalized strain name")
    cursor.execute('''
        UPDATE products
        SET strain_id = (
            SELECT s.id
            FROM strains s
            WHERE s.normalized_name = LOWER(TRIM(products."Product Strain"))
            LIMIT 1
        )
        WHERE strain_id IS NULL
          AND "Product Strain" IS NOT NULL
          AND "Product Strain" != ''
          AND EXISTS (
              SELECT 1 FROM strains s
              WHERE s.normalized_name = LOWER(TRIM(products."Product Strain"))
          )
    ''')

    matched_normalized = cursor.rowcount
    conn.commit()
    print(f"   ✅ Matched {matched_normalized} products by normalized name")

    # Strategy 3: Extract strain from product name for products without Product Strain
    print("\n📋 Strategy 3: Extracting strain from product name (classic types only)")

    # Get products without strain_id and without Product Strain field
    cursor.execute('''
        SELECT id, "Product Name*", "Product Type*"
        FROM products
        WHERE strain_id IS NULL
          AND ("Product Strain" IS NULL OR "Product Strain" = '')
          AND "Product Type*" IN ('Flower', 'Pre-Roll', 'Concentrate', 'Infused Pre-Roll',
                                   'Solventless Concentrate', 'Vape Cartridge', 'RSO/CO2 Tankers')
    ''')

    products_to_extract = cursor.fetchall()
    extracted_count = 0

    for product_id, product_name, product_type in products_to_extract:
        # Extract strain name from product name
        extracted_strain = product_db._extract_strain_from_product_name(product_name, product_type)

        if extracted_strain:
            # Find matching strain
            cursor.execute('''
                SELECT id FROM strains
                WHERE strain_name = ? OR normalized_name = LOWER(TRIM(?))
                LIMIT 1
            ''', (extracted_strain, extracted_strain))

            strain_match = cursor.fetchone()

            if strain_match:
                strain_id = strain_match[0]
                cursor.execute('''
                    UPDATE products
                    SET strain_id = ?
                    WHERE id = ?
                ''', (strain_id, product_id))
                extracted_count += 1

    conn.commit()
    print(f"   ✅ Matched {extracted_count} products by extracting strain from name")

    # Final status
    cursor.execute('''
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN strain_id IS NOT NULL THEN 1 ELSE 0 END) as linked,
            SUM(CASE WHEN strain_id IS NULL THEN 1 ELSE 0 END) as unlinked
        FROM products
    ''')

    total, linked, unlinked = cursor.fetchone()

    print("\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    print(f"   Total products: {total}")
    print(f"   With strain_id: {linked} ({linked*100/total:.1f}%)")
    print(f"   Without strain_id: {unlinked} ({unlinked*100/total:.1f}%)")

    total_fixed = matched_exact + matched_normalized + extracted_count
    print(f"\n✅ Fixed {total_fixed} products!")

    # Show Blackberry Kush status
    print("\n" + "=" * 80)
    print("BLACKBERRY KUSH STATUS")
    print("=" * 80)

    cursor.execute('''
        SELECT
            p."Product Name*",
            p.strain_id,
            s.strain_name,
            s.canonical_lineage,
            COALESCE(p.sovereign_lineage, s.sovereign_lineage, s.canonical_lineage, p."Lineage") as display_lineage
        FROM products p
        LEFT JOIN strains s ON p.strain_id = s.id
        WHERE p."Product Name*" LIKE '%Blackberry%Kush%'
        LIMIT 5
    ''')

    print("\nSample Blackberry Kush products:")
    for row in cursor.fetchall():
        name = row[0][:60]
        strain_id = row[1] or "NULL"
        strain_name = row[2] or "NULL"
        canonical = row[3] or "NULL"
        display = row[4] or "NULL"
        print(f"  {name}")
        print(f"    strain_id={strain_id}, strain='{strain_name}', canonical='{canonical}', UI shows='{display}'")

    print("\n🎉 SUCCESS! Products are now linked to strains table.")
    print("   Refresh your browser to see lineage from strains table.")

if __name__ == '__main__':
    try:
        fix_strain_id_linkage()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
