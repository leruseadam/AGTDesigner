#!/usr/bin/env python3
"""
Diagnostic script to check lineage mismatches between UI tags and database
"""
import sqlite3
import json
import sys
from pathlib import Path

def check_lineage_alignment(db_path="uploads/product_database.db"):
    """Check if product lineages match their strain lineages in the database"""

    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return

    print(f"🔍 Checking lineage alignment in: {db_path}\n")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to find products with mismatched lineages
    query = '''
        SELECT
            p."Product Name*",
            p."Product Strain",
            p."Lineage" AS product_lineage,
            COALESCE(s.sovereign_lineage, s.canonical_lineage) AS strain_lineage
        FROM products p
        LEFT JOIN strains s ON s.normalized_name = LOWER(TRIM(p."Product Strain"))
        WHERE p."Product Strain" IS NOT NULL
        AND p."Product Strain" != ''
        AND s.canonical_lineage IS NOT NULL
        ORDER BY p."Product Name*"
    '''

    cursor.execute(query)
    results = cursor.fetchall()

    mismatches = []
    matches = []

    for row in results:
        product_name, strain, product_lin, strain_lin = row

        # Normalize for comparison
        prod_lin_norm = (product_lin or '').strip().upper()
        strain_lin_norm = (strain_lin or '').strip().upper()

        if prod_lin_norm != strain_lin_norm:
            mismatches.append({
                'product': product_name,
                'strain': strain,
                'product_lineage': prod_lin_norm or 'NULL',
                'strain_lineage': strain_lin_norm or 'NULL'
            })
        else:
            matches.append(product_name)

    print(f"✅ Matches: {len(matches)}")
    print(f"❌ Mismatches: {len(mismatches)}\n")

    if mismatches:
        print("Mismatched lineages (showing first 20):")
        print("-" * 100)
        for mismatch in mismatches[:20]:
            print(f"Product: {mismatch['product'][:50]}")
            print(f"  Strain: {mismatch['strain']}")
            print(f"  Product Lineage: {mismatch['product_lineage']}")
            print(f"  Strain Lineage: {mismatch['strain_lineage']}")
            print()

    # Check strains table
    cursor.execute('SELECT strain_name, canonical_lineage, sovereign_lineage FROM strains LIMIT 10')
    strains = cursor.fetchall()

    print("\n📊 Sample strains in database:")
    print("-" * 100)
    for strain_name, canon, sov in strains:
        print(f"{strain_name}: canonical={canon}, sovereign={sov}")

    conn.close()

    return mismatches

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else "uploads/product_database.db"
    check_lineage_alignment(db_path)
