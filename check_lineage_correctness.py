#!/usr/bin/env python3
"""
Diagnostic script to check lineage correctness in the database.
Checks for:
1. Classic products with MIXED lineage
2. Strains with MIXED canonical_lineage used by classic products
3. Products with invalid lineage values
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.data.product_database import get_database_path
from src.core.constants import CLASSIC_TYPES

def check_lineage_correctness(store_name='AGT_Bothell'):
    """Check lineage correctness in the database."""
    
    db_path = get_database_path(store_name)
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"📊 Checking lineage correctness in database: {db_path}\n")
    
    # Get classic types as lowercase for comparison
    classic_types_lower = [ct.lower() for ct in CLASSIC_TYPES]
    
    # Check 1: Classic products with MIXED lineage
    print("1. Checking classic products with MIXED lineage...")
    cursor.execute("""
        SELECT p.id, p."Product Name*", p."Product Type*", p."Lineage", p.sovereign_lineage, p.strain_id
        FROM products p
        WHERE UPPER(TRIM(p."Lineage")) = 'MIXED'
           OR UPPER(TRIM(p.sovereign_lineage)) = 'MIXED'
    """)
    products_mixed = cursor.fetchall()
    
    classic_with_mixed = []
    for prod in products_mixed:
        prod_id, name, prod_type, lineage, sovereign, strain_id = prod
        prod_type_lower = (prod_type or '').lower().strip()
        is_classic = any(ct in prod_type_lower for ct in classic_types_lower)
        if is_classic:
            classic_with_mixed.append({
                'id': prod_id,
                'name': name,
                'type': prod_type,
                'lineage': lineage,
                'sovereign': sovereign,
                'strain_id': strain_id
            })
    
    if classic_with_mixed:
        print(f"   ⚠️  Found {len(classic_with_mixed)} classic products with MIXED lineage:")
        for prod in classic_with_mixed[:10]:  # Show first 10
            print(f"      - {prod['name']} ({prod['type']}): Lineage={prod['lineage']}, Sovereign={prod['sovereign']}")
        if len(classic_with_mixed) > 10:
            print(f"      ... and {len(classic_with_mixed) - 10} more")
    else:
        print("   ✅ No classic products with MIXED lineage")
    
    # Check 2: Strains with MIXED canonical_lineage used by classic products
    print("\n2. Checking strains with MIXED canonical_lineage used by classic products...")
    cursor.execute("""
        SELECT DISTINCT s.id, s.strain_name, s.canonical_lineage, s.sovereign_lineage, COUNT(p.id) as product_count
        FROM strains s
        JOIN products p ON p.strain_id = s.id
        WHERE UPPER(TRIM(s.canonical_lineage)) = 'MIXED'
        GROUP BY s.id, s.strain_name, s.canonical_lineage, s.sovereign_lineage
    """)
    strains_mixed = cursor.fetchall()
    
    classic_strains_mixed = []
    for strain in strains_mixed:
        strain_id, strain_name, canonical, sovereign, count = strain
        # Check if any products using this strain are classic
        cursor.execute("""
            SELECT COUNT(*) 
            FROM products p
            WHERE p.strain_id = ? 
              AND (
                LOWER(p."Product Type*") LIKE '%flower%'
                OR LOWER(p."Product Type*") LIKE '%concentrate%'
                OR LOWER(p."Product Type*") LIKE '%pre-roll%'
                OR LOWER(p."Product Type*") LIKE '%preroll%'
                OR LOWER(p."Product Type*") LIKE '%wax%'
                OR LOWER(p."Product Type*") LIKE '%shatter%'
                OR LOWER(p."Product Type*") LIKE '%rosin%'
                OR LOWER(p."Product Type*") LIKE '%live resin%'
                OR LOWER(p."Product Type*") LIKE '%distillate%'
                OR LOWER(p."Product Type*") LIKE '%cured resin%'
                OR LOWER(p."Product Type*") LIKE '%badder%'
                OR LOWER(p."Product Type*") LIKE '%budder%'
                OR LOWER(p."Product Type*") LIKE '%sugar%'
                OR LOWER(p."Product Type*") LIKE '%sauce%'
                OR LOWER(p."Product Type*") LIKE '%diamonds%'
                OR LOWER(p."Product Type*") LIKE '%isolate%'
                OR LOWER(p."Product Type*") LIKE '%kief%'
                OR LOWER(p."Product Type*") LIKE '%hash%'
              )
        """, (strain_id,))
        classic_count = cursor.fetchone()[0]
        
        if classic_count > 0:
            classic_strains_mixed.append({
                'id': strain_id,
                'name': strain_name,
                'canonical': canonical,
                'sovereign': sovereign,
                'total_products': count,
                'classic_products': classic_count
            })
    
    if classic_strains_mixed:
        print(f"   ⚠️  Found {len(classic_strains_mixed)} strains with MIXED canonical_lineage used by classic products:")
        for strain in classic_strains_mixed[:10]:  # Show first 10
            print(f"      - {strain['name']}: canonical={strain['canonical']}, used by {strain['classic_products']}/{strain['total_products']} classic products")
        if len(classic_strains_mixed) > 10:
            print(f"      ... and {len(classic_strains_mixed) - 10} more")
    else:
        print("   ✅ No strains with MIXED canonical_lineage used by classic products")
    
    # Check 3: Invalid lineage values (SOVEREIGN, NONE, etc.)
    print("\n3. Checking for invalid lineage values...")
    invalid_values = ['SOVEREIGN', 'NONE', 'NULL', 'NAN']
    for invalid_val in invalid_values:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM products 
            WHERE UPPER(TRIM("Lineage")) = ? 
               OR UPPER(TRIM(sovereign_lineage)) = ?
        """, (invalid_val, invalid_val))
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"   ⚠️  Found {count} products with '{invalid_val}' as lineage value")
        else:
            print(f"   ✅ No products with '{invalid_val}' as lineage value")
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM strains 
            WHERE UPPER(TRIM(canonical_lineage)) = ? 
               OR UPPER(TRIM(sovereign_lineage)) = ?
        """, (invalid_val, invalid_val))
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"   ⚠️  Found {count} strains with '{invalid_val}' as lineage value")
    
    # Check 4: Summary statistics
    print("\n4. Lineage distribution summary...")
    cursor.execute("""
        SELECT UPPER(TRIM("Lineage")) as lineage, COUNT(*) as count
        FROM products
        WHERE "Lineage" IS NOT NULL AND TRIM("Lineage") != ''
        GROUP BY UPPER(TRIM("Lineage"))
        ORDER BY count DESC
    """)
    lineage_dist = cursor.fetchall()
    print("   Product Lineage distribution:")
    for lineage, count in lineage_dist[:10]:
        print(f"      - {lineage}: {count} products")
    
    cursor.execute("""
        SELECT UPPER(TRIM(canonical_lineage)) as lineage, COUNT(*) as count
        FROM strains
        WHERE canonical_lineage IS NOT NULL AND TRIM(canonical_lineage) != ''
        GROUP BY UPPER(TRIM(canonical_lineage))
        ORDER BY count DESC
    """)
    canonical_dist = cursor.fetchall()
    print("\n   Strain canonical_lineage distribution:")
    for lineage, count in canonical_dist[:10]:
        print(f"      - {lineage}: {count} strains")
    
    conn.close()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY:")
    print(f"   - Classic products with MIXED: {len(classic_with_mixed)}")
    print(f"   - Strains with MIXED canonical used by classic: {len(classic_strains_mixed)}")
    print("="*60)
    
    if classic_with_mixed or classic_strains_mixed:
        print("\n⚠️  ISSUES FOUND - Lineages need correction")
        return False
    else:
        print("\n✅ All lineages appear correct!")
        return True

if __name__ == '__main__':
    store_name = sys.argv[1] if len(sys.argv) > 1 else 'AGT_Bothell'
    check_lineage_correctness(store_name)
