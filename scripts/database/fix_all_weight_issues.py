#!/usr/bin/env python3
"""
Fix all identified weight issues in the database.
"""

import sqlite3
from src.core.data.product_database import ProductDatabase
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'uploads' / 'product_database_AGT_Bothell.db'

def fix_all_weight_issues():
    """Fix all weight issues found in the database."""
    
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
    print("FIXING ALL WEIGHT ISSUES")
    print("="*80)
    print()
    
    total_fixed = 0
    
    # FIX 1: Flower product in oz (should be g)
    print("1. Fixing flower products in oz → g...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT rowid, "Product Name*", "Weight*", "Units"
        FROM products
        WHERE "Product Type*" LIKE '%Flower%'
        AND LOWER("Units") = 'oz'
    ''')
    
    flower_oz = cursor.fetchall()
    for rowid, name, weight, units in flower_oz:
        try:
            weight_oz = float(weight)
            weight_g = round(weight_oz * 28.3495, 2)
            
            print(f"  {name}: {weight}oz → {weight_g}g")
            
            cursor.execute('''
                UPDATE products
                SET "Weight*" = ?, "Units" = 'g', "updated_at" = ?
                WHERE rowid = ?
            ''', (str(weight_g), datetime.now().isoformat(), rowid))
            
            total_fixed += 1
        except ValueError:
            pass
    
    print(f"  ✓ Fixed {len(flower_oz)} flower products")
    print()
    
    # FIX 2: Concentrates in oz (should be g)
    print("2. Fixing concentrates in oz → g...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT rowid, "Product Name*", "Weight*", "Units"
        FROM products
        WHERE ("Product Type*" LIKE '%Concentrate%' OR "Product Type*" LIKE '%Wax%')
        AND LOWER("Units") = 'oz'
    ''')
    
    concentrate_oz = cursor.fetchall()
    for rowid, name, weight, units in concentrate_oz:
        try:
            weight_oz = float(weight)
            # Most concentrates are 1g, so if it's close to 0.04oz or 1oz, make it 1g
            if 0.03 <= weight_oz <= 0.05 or 0.98 <= weight_oz <= 1.02:
                weight_g = 1.0
            else:
                weight_g = round(weight_oz * 28.3495, 2)
            
            print(f"  {name}: {weight}oz → {weight_g}g")
            
            cursor.execute('''
                UPDATE products
                SET "Weight*" = ?, "Units" = 'g', "updated_at" = ?
                WHERE rowid = ?
            ''', (str(weight_g), datetime.now().isoformat(), rowid))
            
            total_fixed += 1
        except ValueError:
            pass
    
    print(f"  ✓ Fixed {len(concentrate_oz)} concentrates")
    print()
    
    # FIX 3: Major beverages 190g → 6.7oz
    print("3. Fixing Major beverages 190g → 6.7oz...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT rowid, "Product Brand"
        FROM products
        WHERE "Product Brand" = 'Major'
        AND CAST("Weight*" AS REAL) = 190
        AND LOWER("Units") = 'g'
    ''')
    
    major_beverages = cursor.fetchall()
    for rowid, brand in major_beverages:
        print(f"  Major beverage: 190g → 6.7oz")
        
        cursor.execute('''
            UPDATE products
            SET "Weight*" = '6.7', "Units" = 'oz', "updated_at" = ?
            WHERE rowid = ?
        ''', (datetime.now().isoformat(), rowid))
        
        total_fixed += 1
    
    print(f"  ✓ Fixed {len(major_beverages)} Major beverages")
    print()
    
    # FIX 4: Pre-roll packs (name says 0.5g but DB has total weight)
    # These are actually CORRECT in the DB - the DB shows total pack weight
    # which is what we want for labels. No fix needed.
    print("4. Checking pre-roll packs...")
    print("-" * 80)
    print("  ℹ️  Pre-roll packs are correct (DB shows total pack weight)")
    print()
    
    # FIX 5: Infused pre-rolls with decimal point issues
    print("5. Fixing infused pre-rolls with decimal issues...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT rowid, "Product Name*", "Weight*"
        FROM products
        WHERE "Product Type*" LIKE '%Infused Pre-Roll%'
        AND "Product Name*" LIKE '%.75g%'
        AND CAST("Weight*" AS REAL) > 10
    ''')
    
    decimal_issues = cursor.fetchall()
    for rowid, name, weight in decimal_issues:
        # These likely have ".75g" in the name but were read as "75g"
        try:
            weight_val = float(weight)
            if weight_val > 10:
                corrected = weight_val / 100  # Convert 75 to 0.75
                print(f"  {name}: {weight}g → {corrected}g")
                
                cursor.execute('''
                    UPDATE products
                    SET "Weight*" = ?, "updated_at" = ?
                    WHERE rowid = ?
                ''', (str(corrected), datetime.now().isoformat(), rowid))
                
                total_fixed += 1
        except ValueError:
            pass
    
    print(f"  ✓ Fixed {len(decimal_issues)} decimal issues")
    print()
    
    # FIX 6: Dragon Balm topical (2oz in name, but DB has 3.4oz)
    print("6. Fixing specific product mismatches...")
    print("-" * 80)
    
    cursor.execute('''
        SELECT rowid, "Product Name*", "Weight*", "Units"
        FROM products
        WHERE "Product Name*" LIKE '%Dragon Balm%'
        AND "Product Name*" LIKE '%2oz%'
    ''')
    
    dragon_balm = cursor.fetchall()
    for rowid, name, weight, units in dragon_balm:
        print(f"  {name}: {weight}{units} → 2.0oz")
        
        cursor.execute('''
            UPDATE products
            SET "Weight*" = '2.0', "Units" = 'oz', "updated_at" = ?
            WHERE rowid = ?
        ''', (datetime.now().isoformat(), rowid))
        
        total_fixed += 1
    
    print(f"  ✓ Fixed {len(dragon_balm)} specific products")
    print()
    
    conn.commit()
    conn.close()
    
    print("="*80)
    print(f"✅ COMPLETE: Fixed {total_fixed} weight issues")
    print("="*80)
    print()
    
    return True

def verify_fixes():
    """Verify the fixes were applied."""
    
    try:
        product_db = ProductDatabase(store_name='AGT_Bothell')
        conn = product_db._get_connection()
    except Exception:
        conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("="*80)
    print("VERIFICATION")
    print("="*80)
    print()
    
    # Check flower in oz
    cursor.execute('''
        SELECT COUNT(*) FROM products
        WHERE "Product Type*" LIKE '%Flower%'
        AND LOWER("Units") = 'oz'
    ''')
    flower_oz = cursor.fetchone()[0]
    print(f"Flower in oz: {flower_oz} (should be 0)")
    
    # Check concentrates in oz
    cursor.execute('''
        SELECT COUNT(*) FROM products
        WHERE ("Product Type*" LIKE '%Concentrate%' OR "Product Type*" LIKE '%Wax%')
        AND LOWER("Units") = 'oz'
    ''')
    concentrate_oz = cursor.fetchone()[0]
    print(f"Concentrates in oz: {concentrate_oz} (should be 0)")
    
    # Check Major beverages in g
    cursor.execute('''
        SELECT COUNT(*) FROM products
        WHERE "Product Brand" = 'Major'
        AND CAST("Weight*" AS REAL) = 190
        AND LOWER("Units") = 'g'
    ''')
    major_g = cursor.fetchone()[0]
    print(f"Major beverages still in 190g: {major_g} (should be 0)")
    
    # Check high weights (excluding concentrates)
    cursor.execute('''
        SELECT COUNT(*) FROM products
        WHERE CAST("Weight*" AS REAL) > 100
        AND LOWER("Units") = 'g'
        AND "Product Type*" NOT LIKE '%Concentrate%'
    ''')
    high_weights = cursor.fetchone()[0]
    print(f"High gram weights (>100g, excluding concentrates): {high_weights}")
    
    print()
    if flower_oz == 0 and concentrate_oz == 0 and major_g == 0:
        print("✅ All critical issues fixed!")
    else:
        print("⚠️  Some issues remain")
    
    conn.close()

if __name__ == "__main__":
    print()
    success = fix_all_weight_issues()
    if success:
        verify_fixes()

