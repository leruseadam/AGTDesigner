#!/usr/bin/env python3
"""
CRITICAL FIX: Remove MIXED values from strains table canonical_lineage

This script:
1. Finds all strains with canonical_lineage = 'MIXED'
2. Looks at products for that strain and finds the most common VALID lineage (excluding MIXED)
3. Updates the strain's canonical_lineage to the valid lineage
4. Preserves sovereign_lineage (manual edits) - never overwrites those
"""

import sqlite3
import sys
import os
from collections import Counter

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import ProductDatabase
from app import get_current_store_name, get_product_database

VALID_LINEAGES = ('SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD', 'CBD_BLEND')

def fix_mixed_canonical_lineages():
    """Fix all strains that have MIXED as their canonical_lineage."""

    print("=" * 80)
    print("FIXING MIXED VALUES IN STRAINS TABLE")
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

    # Find all strains with MIXED canonical_lineage (and no sovereign_lineage)
    cursor.execute('''
        SELECT id, strain_name, canonical_lineage, sovereign_lineage
        FROM strains
        WHERE UPPER(TRIM(canonical_lineage)) = 'MIXED'
          AND (sovereign_lineage IS NULL OR sovereign_lineage = '')
    ''')

    mixed_strains = cursor.fetchall()

    if not mixed_strains:
        print("\n✅ No strains found with MIXED canonical_lineage (all clean!)")
        return

    print(f"\n🔍 Found {len(mixed_strains)} strains with MIXED canonical_lineage")
    print("-" * 80)

    fixed = 0
    skipped = 0
    failed = 0

    for strain_id, strain_name, canonical_lineage, sovereign_lineage in mixed_strains:
        print(f"\n📋 Strain: '{strain_name}' (ID: {strain_id})")
        print(f"   Current canonical_lineage: {canonical_lineage}")
        print(f"   Current sovereign_lineage: {sovereign_lineage}")

        # Skip if sovereign lineage exists (manual edit)
        if sovereign_lineage:
            print(f"   ⏭️  SKIPPED - has sovereign_lineage: {sovereign_lineage}")
            skipped += 1
            continue

        # Find the most common VALID lineage for this strain in products
        cursor.execute('''
            SELECT "Lineage", COUNT(*) as count
            FROM products
            WHERE "Product Strain" = ?
              AND "Lineage" IS NOT NULL
              AND "Lineage" != ''
              AND UPPER(TRIM("Lineage")) IN (?, ?, ?, ?, ?, ?, ?)
            GROUP BY "Lineage"
            ORDER BY count DESC
            LIMIT 1
        ''', (strain_name,) + VALID_LINEAGES)

        result = cursor.fetchone()

        if result:
            valid_lineage = result[0]
            product_count = result[1]

            print(f"   ✅ Found valid lineage: '{valid_lineage}' ({product_count} products)")

            # Update the canonical_lineage
            cursor.execute('''
                UPDATE strains
                SET canonical_lineage = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (valid_lineage, strain_id))

            print(f"   ✅ FIXED: Updated canonical_lineage to '{valid_lineage}'")
            fixed += 1
        else:
            # No valid lineage found in products, try to use HYBRID as default
            print(f"   ⚠️  WARNING: No valid lineage found in products")

            # Check if there are ANY products with this strain
            cursor.execute('''
                SELECT COUNT(*)
                FROM products
                WHERE "Product Strain" = ?
            ''', (strain_name,))

            total_products = cursor.fetchone()[0]

            if total_products > 0:
                print(f"   ℹ️  {total_products} products exist, but all have MIXED lineage")
                print(f"   ✅ Setting canonical_lineage to 'HYBRID' (default for classic types)")

                cursor.execute('''
                    UPDATE strains
                    SET canonical_lineage = 'HYBRID',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (strain_id,))

                fixed += 1
            else:
                print(f"   ⚠️  No products found with this strain")
                print(f"   ⏭️  SKIPPED - no data to determine lineage")
                skipped += 1

    # Commit changes
    conn.commit()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Fixed: {fixed} strains")
    print(f"⏭️  Skipped: {skipped} strains")
    print(f"❌ Failed: {failed} strains")
    print(f"📊 Total: {len(mixed_strains)} strains")
    print("=" * 80)

    if fixed > 0:
        print("\n🎉 SUCCESS! Strains table has been cleaned.")
        print("   Refresh your browser to see the updated lineage values.")
    else:
        print("\n✅ No changes needed.")

if __name__ == '__main__':
    try:
        fix_mixed_canonical_lineages()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
