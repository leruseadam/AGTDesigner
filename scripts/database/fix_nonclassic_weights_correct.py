#!/usr/bin/env python3
"""
Fix ONLY non-classic product weights to use oz instead of grams.
Non-classic types: Topicals, Edible Solids (but NOT concentrates - those stay in grams!)
"""

import sqlite3
from src.core.data.product_database import ProductDatabase
import sys
import os
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'uploads' / 'product_database_AGT_Bothell.db'

def fix_nonclassic_weights():
    """Fix non-classic product weights to oz (except concentrates which stay in grams)."""
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    try:
        product_db = ProductDatabase(store_name='AGT_Bothell')
        conn = product_db._get_connection()
    except Exception:
        conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("="*80)
    print("FIXING NON-CLASSIC WEIGHTS (TOPICALS & EDIBLE SOLIDS ONLY)")
    print("="*80)
    print("Note: Concentrates stay in grams (not converted to oz)")
    print()
    
    total_fixed = 0
    
    # FIX 1: Topicals (bath salts, creams, etc.)
    print("1. Fixing Topicals...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT rowid, "Product Name*", "Product Brand", "Weight*", "Units", "Product Type*"
        FROM products
        WHERE "Product Type*" LIKE '%Topical%'
        AND LOWER("Units") = 'g'
        AND CAST("Weight*" AS REAL) > 0
    ''')
    
    topicals = cursor.fetchall()
    topical_count = 0
    
    for rowid, name, brand, weight, units, ptype in topicals:
        try:
            weight_g = float(weight)
            weight_oz = round(weight_g / 28.3495, 2)  # Convert grams to oz
            
            display_name = name if name and name.strip() else f"{brand} - {ptype}"
            print(f"  {display_name}")
            print(f"    {weight}g → {weight_oz} oz")
            
            cursor.execute('''
                UPDATE products
                SET "Weight*" = ?,
                    "Units" = 'oz',
                    "updated_at" = ?
                WHERE rowid = ?
            ''', (str(weight_oz), datetime.now().isoformat(), rowid))
            
            topical_count += 1
        except ValueError:
            pass
    
    print(f"  ✓ Fixed {topical_count} topicals")
    total_fixed += topical_count
    print()
    
    # FIX 2: Edible Solids (chips, gummies, etc.)
    print("2. Fixing Edible Solids...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT rowid, "Product Name*", "Product Brand", "Weight*", "Units", "Product Type*"
        FROM products
        WHERE "Product Type*" LIKE '%Edible (Solid)%'
        AND LOWER("Units") = 'g'
        AND CAST("Weight*" AS REAL) > 10  -- Only fix larger items
    ''')
    
    edible_solids = cursor.fetchall()
    edible_count = 0
    
    for rowid, name, brand, weight, units, ptype in edible_solids:
        try:
            weight_g = float(weight)
            weight_oz = round(weight_g / 28.3495, 2)
            
            display_name = name if name and name.strip() else f"{brand} - {ptype}"
            print(f"  {display_name}")
            print(f"    {weight}g → {weight_oz} oz")
            
            cursor.execute('''
                UPDATE products
                SET "Weight*" = ?,
                    "Units" = 'oz',
                    "updated_at" = ?
                WHERE rowid = ?
            ''', (str(weight_oz), datetime.now().isoformat(), rowid))
            
            edible_count += 1
        except ValueError:
            pass
    
    print(f"  ✓ Fixed {edible_count} edible solids")
    total_fixed += edible_count
    print()
    
    # FIX 3: Other non-classic types (tinctures, capsules, etc.)
    print("3. Fixing Other Non-Classic Types (Tinctures, Capsules, etc.)...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT rowid, "Product Name*", "Product Brand", "Weight*", "Units", "Product Type*"
        FROM products
        WHERE (
            "Product Type*" LIKE '%Tincture%' OR
            "Product Type*" LIKE '%Capsule%' OR
            "Product Type*" LIKE '%Powder%' OR
            "Product Type*" LIKE '%Syrup%'
        )
        AND LOWER("Units") = 'g'
        AND CAST("Weight*" AS REAL) > 5  -- Only fix larger items
    ''')
    
    other_types = cursor.fetchall()
    other_count = 0
    
    for rowid, name, brand, weight, units, ptype in other_types:
        try:
            weight_g = float(weight)
            weight_oz = round(weight_g / 28.3495, 2)
            
            display_name = name if name and name.strip() else f"{brand} - {ptype}"
            print(f"  {display_name}")
            print(f"    {weight}g → {weight_oz} oz")
            
            cursor.execute('''
                UPDATE products
                SET "Weight*" = ?,
                    "Units" = 'oz',
                    "updated_at" = ?
                WHERE rowid = ?
            ''', (str(weight_oz), datetime.now().isoformat(), rowid))
            
            other_count += 1
        except ValueError:
            pass
    
    print(f"  ✓ Fixed {other_count} other types")
    total_fixed += other_count
    print()
    
    conn.commit()
    conn.close()
    
    print("="*80)
    print(f"✅ COMPLETE: Fixed {total_fixed} non-classic products")
    print("="*80)
    print()
    print("⚠️  Note: Concentrates were NOT converted (they stay in grams)")
    print()
    
    return True

def verify_nonclassic_weights():
    """Verify all non-classic weights are correct."""
    
    try:
        product_db = ProductDatabase(store_name='AGT_Bothell')
        conn = product_db._get_connection()
    except Exception:
        conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("="*80)
    print("VERIFICATION - NON-CLASSIC WEIGHTS")
    print("="*80)
    
    # Check topicals
    cursor.execute('''
        SELECT COUNT(*) FROM products
        WHERE "Product Type*" LIKE '%Topical%'
        AND LOWER("Units") = 'g'
    ''')
    topical_g_count = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM products
        WHERE "Product Type*" LIKE '%Topical%'
        AND LOWER("Units") = 'oz'
    ''')
    topical_oz_count = cursor.fetchone()[0]
    
    print(f"Topicals: {topical_oz_count} in oz, {topical_g_count} still in g")
    
    # Check edible solids
    cursor.execute('''
        SELECT COUNT(*) FROM products
        WHERE "Product Type*" LIKE '%Edible (Solid)%'
        AND LOWER("Units") = 'g'
        AND CAST("Weight*" AS REAL) > 10
    ''')
    edible_g_count = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM products
        WHERE "Product Type*" LIKE '%Edible (Solid)%'
        AND LOWER("Units") = 'oz'
    ''')
    edible_oz_count = cursor.fetchone()[0]
    
    print(f"Edible Solids: {edible_oz_count} in oz, {edible_g_count} still in g")
    
    # Check concentrates (should still be in grams!)
    cursor.execute('''
        SELECT COUNT(*) FROM products
        WHERE ("Product Type*" LIKE '%Concentrate%' OR "Product Type*" LIKE '%Wax%')
        AND LOWER("Units") = 'g'
    ''')
    concentrate_g_count = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM products
        WHERE ("Product Type*" LIKE '%Concentrate%' OR "Product Type*" LIKE '%Wax%')
        AND LOWER("Units") = 'oz'
    ''')
    concentrate_oz_count = cursor.fetchone()[0]
    
    print(f"Concentrates: {concentrate_g_count} in g (correct!), {concentrate_oz_count} in oz (wrong!)")
    
    # Show any remaining high gram weights (excluding concentrates)
    cursor.execute('''
        SELECT "Product Name*", "Product Brand", "Weight*", "Units", "Product Type*"
        FROM products
        WHERE CAST("Weight*" AS REAL) > 100
        AND LOWER("Units") = 'g'
        AND "Product Type*" NOT LIKE '%Concentrate%'
        ORDER BY CAST("Weight*" AS REAL) DESC
        LIMIT 10
    ''')
    
    high_gram = cursor.fetchall()
    
    if high_gram:
        print()
        print("Remaining high gram weights (>100g, excluding concentrates):")
        for name, brand, weight, units, ptype in high_gram:
            display = name if name and name.strip() else f"{brand} - {ptype}"
            print(f"  • {display}: {weight}g ({ptype})")
    else:
        print()
        print("✅ No high gram weights remaining (excluding concentrates)!")
    
    conn.close()

if __name__ == "__main__":
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        verify_nonclassic_weights()
    else:
        success = fix_nonclassic_weights()
        if success:
            verify_nonclassic_weights()

