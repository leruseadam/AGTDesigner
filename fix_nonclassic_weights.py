#!/usr/bin/env python3
"""
Fix all non-classic product weights to use oz instead of grams.
Non-classic types: Topicals, Edible Solids, Concentrates, etc.
"""

import sqlite3
import sys
import os
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'uploads' / 'product_database_AGT_Bothell.db'

def fix_nonclassic_weights():
    """Fix all non-classic product weights to oz."""
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("="*80)
    print("FIXING ALL NON-CLASSIC WEIGHTS")
    print("="*80)
    print("Converting topicals, edible solids, concentrates, etc. to oz")
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
    
    # FIX 3: Concentrates (wax, shatter, etc.)
    print("3. Fixing Concentrates...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT rowid, "Product Name*", "Product Brand", "Weight*", "Units", "Product Type*"
        FROM products
        WHERE ("Product Type*" LIKE '%Concentrate%' OR "Product Type*" LIKE '%Wax%' OR "Product Type*" LIKE '%Shatter%')
        AND LOWER("Units") = 'g'
        AND CAST("Weight*" AS REAL) > 0
    ''')
    
    concentrates = cursor.fetchall()
    concentrate_count = 0
    
    for rowid, name, brand, weight, units, ptype in concentrates:
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
            
            concentrate_count += 1
        except ValueError:
            pass
    
    print(f"  ✓ Fixed {concentrate_count} concentrates")
    total_fixed += concentrate_count
    print()
    
    # FIX 4: Other non-classic types
    print("4. Fixing Other Non-Classic Types...")
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
    
    return True

def verify_nonclassic_weights():
    """Verify all non-classic weights are in oz."""
    
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
    
    # Check concentrates
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
    
    print(f"Concentrates: {concentrate_oz_count} in oz, {concentrate_g_count} still in g")
    
    # Show any remaining high gram weights
    cursor.execute('''
        SELECT "Product Name*", "Product Brand", "Weight*", "Units", "Product Type*"
        FROM products
        WHERE CAST("Weight*" AS REAL) > 100
        AND LOWER("Units") = 'g'
        ORDER BY CAST("Weight*" AS REAL) DESC
        LIMIT 10
    ''')
    
    high_gram = cursor.fetchall()
    
    if high_gram:
        print()
        print("Remaining high gram weights (>100g):")
        for name, brand, weight, units, ptype in high_gram:
            display = name if name and name.strip() else f"{brand} - {ptype}"
            print(f"  • {display}: {weight}g ({ptype})")
    else:
        print()
        print("✅ No high gram weights remaining!")
    
    conn.close()

if __name__ == "__main__":
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        verify_nonclassic_weights()
    else:
        success = fix_nonclassic_weights()
        if success:
            verify_nonclassic_weights()
