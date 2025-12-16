#!/usr/bin/env python3
"""
Comprehensive weight normalization for all known product issues.
Fixes:
1. Constellation Moonshots → 1.7 oz
2. Major beverages → 6.7 oz (100mg THC drinks)
3. Any 190g → 6.7 oz (190g = 6.7 oz conversion)
"""

import sqlite3
import sys
import os
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'uploads' / 'product_database_AGT_Bothell.db'

def fix_all_weights(dry_run=False):
    """Fix all known weight issues."""
    
    if not DB_PATH.exists():
        print(f"❌ Error: Database not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("="*80)
    print("COMPREHENSIVE WEIGHT NORMALIZATION")
    print("="*80)
    if dry_run:
        print("DRY RUN MODE - No changes will be saved")
    print()
    
    total_updated = 0
    
    # FIX 1: Constellation Moonshots → 1.7 oz
    print("1. Normalizing Constellation Moonshots to 1.7 oz...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT id, "Product Name*", "Weight*", "Units"
        FROM products
        WHERE "Product Name*" LIKE '%Moonshot%' 
        AND "Product Brand" = 'Constellation Cannabis'
    ''')
    
    moonshots = cursor.fetchall()
    moonshot_count = 0
    
    for product_id, name, weight, units in moonshots:
        if str(weight) != "1.7" or str(units or "").lower() != "oz":
            print(f"  {name}")
            print(f"    {weight} {units or '(no unit)'} → 1.7 oz")
            
            if not dry_run:
                cursor.execute('''
                    UPDATE products
                    SET "Weight*" = '1.7', 
                        "Units" = 'oz',
                        "updated_at" = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), product_id))
            
            moonshot_count += 1
    
    if moonshot_count == 0:
        print("  ✓ All Moonshots already correct")
    else:
        print(f"  ✓ Fixed {moonshot_count} Moonshots")
    
    total_updated += moonshot_count
    print()
    
    # FIX 2: Major beverages → 6.7 oz
    print("2. Normalizing Major beverages to 6.7 oz...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT id, "Product Name*", "Weight*", "Units", "Product Type*"
        FROM products
        WHERE "Product Brand" = 'Major'
        AND ("Product Type*" LIKE '%Liquid%' OR "Product Type*" LIKE '%Beverage%')
    ''')
    
    major_products = cursor.fetchall()
    major_count = 0
    
    for product_id, name, weight, units, ptype in major_products:
        # Check if needs fixing
        current_weight = str(weight).strip()
        current_units = str(units or "").strip().lower()
        
        needs_fix = False
        
        # If 190 (any unit) → should be 6.7 oz
        if current_weight == "190" or current_weight == "190.0":
            needs_fix = True
        # If not 6.7 oz
        elif current_weight != "6.7" or current_units != "oz":
            needs_fix = True
        
        if needs_fix:
            display_name = name if name else "(empty name)"
            print(f"  {display_name}")
            print(f"    {weight} {units or '(no unit)'} → 6.7 oz")
            
            if not dry_run:
                cursor.execute('''
                    UPDATE products
                    SET "Weight*" = '6.7', 
                        "Units" = 'oz',
                        "updated_at" = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), product_id))
            
            major_count += 1
    
    if major_count == 0:
        print("  ✓ All Major beverages already correct")
    else:
        print(f"  ✓ Fixed {major_count} Major beverages")
    
    total_updated += major_count
    print()
    
    # FIX 3: Any remaining 190g → 6.7 oz (190g = 6.7 oz)
    print("3. Converting any 190g → 6.7 oz...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT id, "Product Name*", "Product Brand", "Weight*", "Units", "Product Type*"
        FROM products
        WHERE ("Weight*" = '190' OR "Weight*" = '190.0')
        AND LOWER("Units") = 'g'
    ''')
    
    g_products = cursor.fetchall()
    g_count = 0
    
    for product_id, name, brand, weight, units, ptype in g_products:
        display_name = name if name else f"(empty - {brand})"
        print(f"  {display_name}")
        print(f"    {weight} {units} → 6.7 oz")
        
        if not dry_run:
            cursor.execute('''
                UPDATE products
                SET "Weight*" = '6.7', 
                    "Units" = 'oz',
                    "updated_at" = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), product_id))
        
        g_count += 1
    
    if g_count == 0:
        print("  ✓ No 190g products found")
    else:
        print(f"  ✓ Converted {g_count} products")
    
    total_updated += g_count
    print()
    
    # FIX 4: Non-classic types (topicals, edible solids) → oz
    print("4. Converting non-classic products (topicals, edible solids) to oz...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT rowid, "Product Name*", "Product Brand", "Weight*", "Units", "Product Type*"
        FROM products
        WHERE (
            ("Product Type*" LIKE '%Topical%' AND CAST("Weight*" AS REAL) > 100)
            OR
            ("Product Type*" LIKE '%Edible (Solid)%' AND CAST("Weight*" AS REAL) > 100)
        )
        AND LOWER("Units") = 'g'
    ''')
    
    nonclassic_products = cursor.fetchall()
    nonclassic_count = 0
    
    for rowid, name, brand, weight, units, ptype in nonclassic_products:
        try:
            weight_g = float(weight)
            weight_oz = round(weight_g / 28.3495, 2)  # Convert grams to oz
            
            display_name = name if name and name.strip() else f"{brand} - {ptype}"
            print(f"  {display_name}")
            print(f"    {weight}g → {weight_oz} oz")
            
            if not dry_run:
                cursor.execute('''
                    UPDATE products
                    SET "Weight*" = ?,
                        "Units" = 'oz',
                        "updated_at" = ?
                    WHERE rowid = ?
                ''', (str(weight_oz), datetime.now().isoformat(), rowid))
            
            nonclassic_count += 1
        except ValueError:
            pass
    
    if nonclassic_count == 0:
        print("  ✓ No non-classic products need conversion")
    else:
        print(f"  ✓ Converted {nonclassic_count} products")
    
    total_updated += nonclassic_count
    print()
    
    # FIX 5: Flower weight mismatches (e.g., "14g" in name but wrong weight in DB)
    print("5. Fixing flower weight mismatches...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT rowid, "Product Name*", "Weight*"
        FROM products
        WHERE "Product Name*" LIKE '%14g%'
        AND "Weight*" != '14'
        AND "Weight*" != '14.0'
    ''')
    
    flower_mismatches = cursor.fetchall()
    flower_count = 0
    
    for rowid, name, weight in flower_mismatches:
        print(f"  {name}")
        print(f"    {weight} → 14g (based on product name)")
        
        if not dry_run:
            cursor.execute('''
                UPDATE products
                SET "Weight*" = '14',
                    "Units" = 'g',
                    "updated_at" = ?
                WHERE rowid = ?
            ''', (datetime.now().isoformat(), rowid))
        
        flower_count += 1
    
    if flower_count == 0:
        print("  ✓ No flower weight mismatches found")
    else:
        print(f"  ✓ Fixed {flower_count} products")
    
    total_updated += flower_count
    print()
    
    # Commit changes
    if not dry_run:
        conn.commit()
        print("="*80)
        print(f"✅ COMPLETE: Updated {total_updated} products")
        print("="*80)
    else:
        print("="*80)
        print(f"DRY RUN COMPLETE: Would update {total_updated} products")
        print("Run without --dry-run to apply changes")
        print("="*80)
    
    conn.close()
    return True

def verify_fixes():
    """Verify all fixes were applied correctly."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    print()
    
    # Check Moonshots
    print("1. Constellation Moonshots:")
    cursor.execute('''
        SELECT "Product Name*", "Weight*", "Units"
        FROM products
        WHERE "Product Name*" LIKE '%Moonshot%' 
        AND "Product Brand" = 'Constellation Cannabis'
        ORDER BY "Product Name*"
    ''')
    
    moonshots = cursor.fetchall()
    all_correct = True
    for name, weight, units in moonshots:
        status = "✓" if str(weight) == "1.7" and str(units) == "oz" else "✗"
        print(f"  {status} {name}: {weight} {units}")
        if status == "✗":
            all_correct = False
    
    if all_correct and moonshots:
        print("  ✅ All Moonshots correct!")
    print()
    
    # Check Major beverages
    print("2. Major Beverages:")
    cursor.execute('''
        SELECT "Product Name*", "Weight*", "Units"
        FROM products
        WHERE "Product Brand" = 'Major'
        AND "Product Type*" LIKE '%Liquid%'
        ORDER BY "Product Name*"
        LIMIT 10
    ''')
    
    majors = cursor.fetchall()
    all_correct = True
    for name, weight, units in majors:
        display_name = name if name else "(empty)"
        status = "✓" if str(weight) == "6.7" and str(units) == "oz" else "✗"
        print(f"  {status} {display_name}: {weight} {units}")
        if status == "✗":
            all_correct = False
    
    if all_correct and majors:
        print("  ✅ All Major beverages correct!")
    
    # Check for any remaining issues
    print()
    print("3. Checking for remaining issues...")
    cursor.execute('''
        SELECT COUNT(*) FROM products
        WHERE (CAST("Weight*" AS REAL) > 100 AND LOWER("Units") != 'oz')
        OR ("Units" IS NULL AND "Weight*" IS NOT NULL)
    ''')
    
    issue_count = cursor.fetchone()[0]
    if issue_count > 0:
        print(f"  ⚠ {issue_count} products may still have issues")
        print("  Run: python fix_database_weights.py audit")
    else:
        print("  ✅ No obvious issues found!")
    
    conn.close()
    print()

if __name__ == "__main__":
    print()
    
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Usage:")
        print("  python fix_all_weights.py           # Fix all weights")
        print("  python fix_all_weights.py --dry-run # Preview changes without applying")
        print("  python fix_all_weights.py verify    # Verify fixes")
        print()
        print("Fixes:")
        print("  1. Constellation Moonshots → 1.7 oz")
        print("  2. Major beverages → 6.7 oz")
        print("  3. Any 190g → 6.7 oz")
        print("  4. Non-classic types (topicals, edible solids >100g) → oz")
        print("  5. Flower weight mismatches (name vs database)")
        sys.exit(0)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        verify_fixes()
    else:
        success = fix_all_weights(dry_run=dry_run)
        if success and not dry_run:
            verify_fixes()

