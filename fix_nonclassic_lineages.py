#!/usr/bin/env python3
"""
Fix nonclassic types with classic lineages in the database.

PROBLEM: Nonclassic types (edibles, tinctures, topicals, capsules, etc.) are appearing
with classic lineages (SATIVA, INDICA, HYBRID, etc.) when they should ONLY have:
- MIXED (displayed as "THC" in UI)
- CBD
- PARAPHERNALIA

This script:
1. Finds all nonclassic products with classic lineages
2. Converts classic lineages (SATIVA, INDICA, HYBRID, etc.) to MIXED
3. Preserves CBD and PARAPHERNALIA lineages for nonclassic types
4. Updates both products and strains tables
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.constants import CLASSIC_TYPES, VALID_CLASSIC_LINEAGES, VALID_NONCLASSIC_LINEAGES

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DB_PATH = os.path.join(os.path.dirname(__file__), 'uploads', 'product_database.db')

def get_connection():
    """Get database connection."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at: {DB_PATH}")
    return sqlite3.connect(DB_PATH)

def fix_nonclassic_lineages():
    """Fix nonclassic products with classic lineages."""
    print("\n" + "=" * 80)
    print("FIX NONCLASSIC LINEAGES")
    print("=" * 80)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Step 1: Find all nonclassic products with classic lineages
        print("\n📊 Analyzing nonclassic products...")
        
        classic_types_list = [ct.lower() for ct in CLASSIC_TYPES]
        classic_lineages = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA']
        
        # Build query to find nonclassic products with classic lineages
        classic_types_placeholders = ','.join(['?' for _ in classic_types_list])
        lineages_placeholders = ','.join(['?' for _ in classic_lineages])
        
        query = f"""
            SELECT 
                p.id,
                p."Product Name*",
                p."Product Type",
                p.Lineage,
                p.sovereign_lineage,
                p.strain_id,
                s.strain_name,
                s.canonical_lineage as strain_canonical_lineage,
                s.sovereign_lineage as strain_sovereign_lineage
            FROM products p
            LEFT JOIN strains s ON p.strain_id = s.id
            WHERE 
                LOWER(p."Product Type") NOT IN ({classic_types_placeholders})
                AND (
                    UPPER(p.Lineage) IN ({lineages_placeholders})
                    OR UPPER(s.canonical_lineage) IN ({lineages_placeholders})
                )
        """
        
        params = classic_types_list + classic_lineages + classic_lineages
        cursor.execute(query, params)
        problem_products = cursor.fetchall()
        
        if not problem_products:
            print("✅ No nonclassic products found with classic lineages!")
            return
        
        print(f"\n🚨 Found {len(problem_products)} nonclassic products with classic lineages:")
        print("\n" + "-" * 80)
        
        # Group by product type for summary
        by_type = {}
        for row in problem_products:
            p_type = row[2] or 'Unknown'
            if p_type not in by_type:
                by_type[p_type] = []
            by_type[p_type].append(row)
        
        for p_type, products in by_type.items():
            print(f"\n{p_type}: {len(products)} products")
            for row in products[:5]:  # Show first 5
                product_id, name, _, lineage, canonical, strain_id, strain_name, strain_canonical, strain_sovereign = row
                print(f"  - {name}")
                print(f"    Product lineage: {lineage}, canonical: {canonical}")
                if strain_name:
                    print(f"    Strain: {strain_name} (canonical: {strain_canonical}, sovereign: {strain_sovereign})")
            if len(products) > 5:
                print(f"  ... and {len(products) - 5} more")
        
        print("\n" + "-" * 80)
        
        # Step 2: Ask for confirmation
        response = input("\n⚠️  Convert all classic lineages to MIXED for these nonclassic products? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Aborted by user")
            return
        
        # Step 3: Update products table
        print("\n🔧 Updating products table...")
        products_updated = 0
        
        for row in problem_products:
            product_id, name, product_type, lineage, sovereign, strain_id, _, _, _ = row
            
            # Determine new lineage - preserve CBD, convert everything else to MIXED
            new_lineage = None
            new_sovereign = None
            
            if lineage:
                lineage_upper = lineage.upper()
                if lineage_upper == 'CBD':
                    new_lineage = 'CBD'
                elif lineage_upper in classic_lineages:
                    new_lineage = 'MIXED'  # Convert classic lineages to MIXED
                else:
                    new_lineage = lineage  # Keep as is
            
            if sovereign:
                sovereign_upper = sovereign.upper()
                if sovereign_upper == 'CBD':
                    new_sovereign = 'CBD'
                elif sovereign_upper in classic_lineages:
                    new_sovereign = 'MIXED'  # Convert classic lineages to MIXED
                else:
                    new_sovereign = sovereign  # Keep as is
            
            # Update product
            update_fields = []
            update_params = []
            
            if new_lineage and new_lineage != lineage:
                update_fields.append("Lineage = ?")
                update_params.append(new_lineage)
            
            if new_sovereign and new_sovereign != sovereign:
                update_fields.append("sovereign_lineage = ?")
                update_params.append(new_sovereign)
            
            if update_fields:
                update_params.append(product_id)
                update_query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(update_query, update_params)
                products_updated += 1
                print(f"  ✅ Updated: {name} ({product_type})")
                if new_lineage and new_lineage != lineage:
                    print(f"     Lineage: {lineage} → {new_lineage}")
                if new_sovereign and new_sovereign != sovereign:
                    print(f"     sovereign_lineage: {sovereign} → {new_sovereign}")
        
        # Step 4: Update strains table for nonclassic strain linkages
        print("\n🔧 Updating strains table...")
        
        # Get unique strain IDs from problem products
        strain_ids = [row[5] for row in problem_products if row[5]]
        unique_strain_ids = list(set(strain_ids))
        
        strains_updated = 0
        for strain_id in unique_strain_ids:
            cursor.execute("""
                SELECT id, strain_name, canonical_lineage, sovereign_lineage
                FROM strains
                WHERE id = ?
            """, (strain_id,))
            strain_row = cursor.fetchone()
            
            if strain_row:
                s_id, s_name, s_canonical, s_sovereign = strain_row
                
                # Only update if canonical_lineage is a classic lineage
                if s_canonical:
                    s_canonical_upper = s_canonical.upper()
                    if s_canonical_upper in classic_lineages:
                        new_canonical = 'MIXED'
                        cursor.execute("""
                            UPDATE strains
                            SET canonical_lineage = ?
                            WHERE id = ?
                        """, (new_canonical, s_id))
                        strains_updated += 1
                        print(f"  ✅ Updated strain: {s_name}")
                        print(f"     canonical_lineage: {s_canonical} → {new_canonical}")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 80)
        print("✅ FIX COMPLETE!")
        print("=" * 80)
        print(f"Products updated: {products_updated}")
        print(f"Strains updated: {strains_updated}")
        print("\nNonclassic types now have correct lineages:")
        print("  - MIXED (displayed as 'THC' in UI)")
        print("  - CBD (preserved)")
        print("  - PARAPHERNALIA (preserved)")
        print("\nClassic lineages (SATIVA, INDICA, HYBRID) have been converted to MIXED")
        print("=" * 80)
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Error fixing nonclassic lineages: {e}", exc_info=True)
        print(f"\n❌ ERROR: {e}")
    finally:
        conn.close()

def verify_fix():
    """Verify that the fix was successful."""
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        classic_types_list = [ct.lower() for ct in CLASSIC_TYPES]
        classic_lineages = ['SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA']
        
        classic_types_placeholders = ','.join(['?' for _ in classic_types_list])
        lineages_placeholders = ','.join(['?' for _ in classic_lineages])
        
        query = f"""
            SELECT COUNT(*) as count
            FROM products p
            WHERE 
                LOWER(p."Product Type") NOT IN ({classic_types_placeholders})
                AND UPPER(p.Lineage) IN ({lineages_placeholders})
        """
        
        params = classic_types_list + classic_lineages
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("✅ VERIFICATION PASSED: No nonclassic products with classic lineages found!")
        else:
            print(f"⚠️  VERIFICATION FAILED: Still found {count} nonclassic products with classic lineages")
        
        # Show lineage distribution for nonclassic types
        print("\n📊 Lineage distribution for nonclassic types:")
        cursor.execute(f"""
            SELECT 
                COALESCE(UPPER(Lineage), 'NULL') as lineage,
                COUNT(*) as count
            FROM products
            WHERE LOWER("Product Type") NOT IN ({classic_types_placeholders})
            GROUP BY UPPER(Lineage)
            ORDER BY count DESC
        """, classic_types_list)
        
        for row in cursor.fetchall():
            lineage, count = row
            print(f"  {lineage}: {count}")
        
    except Exception as e:
        logging.error(f"Error verifying fix: {e}", exc_info=True)
    finally:
        conn.close()

if __name__ == '__main__':
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  FIX NONCLASSIC LINEAGES - Convert Classic to MIXED/THC".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    fix_nonclassic_lineages()
    verify_fix()
    
    print("\n✅ Done! Nonclassic types now have proper lineages (MIXED/THC or CBD).")
