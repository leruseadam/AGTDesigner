#!/usr/bin/env python3
"""
Script to normalize and fix incorrect product weights in the database.

Use this to fix known weight issues, like Constellation Moonshots that should be 1.7oz.
"""

import sqlite3
import sys
import os
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'uploads', 'product_database_AGT_Bothell.db')

def normalize_moonshot_weights():
    """Normalize all Constellation Moonshots to 1.7 oz."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("="*80)
    print("NORMALIZING CONSTELLATION MOONSHOT WEIGHTS")
    print("="*80)
    print()
    
    # Find all Constellation Moonshots
    cursor.execute('''
        SELECT id, "Product Name*", "Weight*", "Units"
        FROM products
        WHERE "Product Name*" LIKE '%Moonshot%' 
        AND "Product Brand" = 'Constellation Cannabis'
    ''')
    
    moonshots = cursor.fetchall()
    
    if not moonshots:
        print("No Constellation Moonshots found in database")
        conn.close()
        return
    
    print(f"Found {len(moonshots)} Constellation Moonshots")
    print()
    
    updated_count = 0
    for product_id, name, current_weight, current_units in moonshots:
        # Normalize to 1.7 oz
        target_weight = "1.7"
        target_units = "oz"
        
        # Check if update needed
        needs_update = (str(current_weight) != target_weight or 
                       str(current_units or "").lower() != target_units)
        
        if needs_update:
            print(f"Updating: {name}")
            print(f"  Old: {current_weight} {current_units or '(no unit)'}")
            print(f"  New: {target_weight} {target_units}")
            
            cursor.execute('''
                UPDATE products
                SET "Weight*" = ?, 
                    "Units" = ?,
                    "updated_at" = ?
                WHERE id = ?
            ''', (target_weight, target_units, datetime.now().isoformat(), product_id))
            
            updated_count += 1
            from src.core.data.product_database import ProductDatabase
            print("  ✓ Updated")
        else:
            print(f"Already correct: {name} ({current_weight} {current_units})")
        
        print()
    
    conn.commit()
                try:
                    product_db = ProductDatabase(store_name='AGT_Bothell')
                    conn = product_db._get_connection()
                except Exception:
                    conn = sqlite3.connect(DB_PATH)
    print("="*80)
    print(f"COMPLETE: Updated {updated_count} of {len(moonshots)} Moonshots")
    print("="*80)

def fix_specific_product(product_name_pattern, correct_weight, correct_units):
    """Fix weight for products matching a specific name pattern."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"\nFixing products matching: {product_name_pattern}")
    print(f"Setting to: {correct_weight} {correct_units}")
    print()
    
    cursor.execute('''
        SELECT id, "Product Name*", "Product Brand", "Weight*", "Units"
        FROM products
        WHERE "Product Name*" LIKE ?
    ''', (f'%{product_name_pattern}%',))
                    try:
                        if 'product_db' not in locals():
                            conn.close()
                    except Exception:
                        pass
    products = cursor.fetchall()
    
    if not products:
        print(f"No products found matching: {product_name_pattern}")
        conn.close()
        return
    
    print(f"Found {len(products)} products:")
    print()
    
    for product_id, name, brand, current_weight, current_units in products:
        print(f"  {name} ({brand})")
        print(f"    Old: {current_weight} {current_units or '(no unit)'}")
        print(f"    New: {correct_weight} {correct_units}")
        
        cursor.execute('''
            UPDATE products
            SET "Weight*" = ?,
                "Units" = ?,
                "updated_at" = ?
            WHERE id = ?
        ''', (correct_weight, correct_units, datetime.now().isoformat(), product_id))
        
        print("    ✓ Updated")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Updated {len(products)} products")

def list_products_by_brand(brand_name, name_pattern=None):
    """List all products for a specific brand to audit weights."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
                try:
                    if 'product_db' not in locals():
                        conn.close()
                except Exception:
                    pass
    params = [brand_name]
    
    if name_pattern:
        query += ' AND "Product Name*" LIKE ?'
        params.append(f'%{name_pattern}%')
    
    query += ' ORDER BY "Product Name*"'
    
                try:
                    product_db = ProductDatabase(store_name='AGT_Bothell')
                    conn = product_db._get_connection()
                except Exception:
                    conn = sqlite3.connect(DB_PATH)
    
    print(f"\n{brand_name} Products:")
    print("="*80)
    
    for name, brand, weight, units in products:
        print(f"{name}")
        print(f"  Weight: {weight} {units or '(no unit)'}")
        print()
    
    print(f"Total: {len(products)} products")
    conn.close()

def audit_weights():
    """Audit all product weights to find inconsistencies."""
    
    conn = sqlite3.connect(DB_PATH)
                    try:
                        if 'product_db' not in locals():
                            conn.close()
                    except Exception:
                        pass
    
    print("\n" + "="*80)
    print("WEIGHT AUDIT - Finding Potential Issues")
    print("="*80)
    print()
    
    # Find products with missing units
    print("1. Products with missing units:")
    cursor.execute('''
        SELECT "Product Name*", "Product Brand", "Weight*", "Units"
        FROM products
        WHERE ("Units" IS NULL OR "Units" = '' OR "Units" = 'N/A')
        AND "Weight*" IS NOT NULL
        ORDER BY "Product Brand", "Product Name*"
    ''')
    
    missing_units = cursor.fetchall()
    print(f"   Found {len(missing_units)} products")
    for name, brand, weight, units in missing_units[:10]:  # Show first 10
        print(f"   - {name} ({brand}): {weight} {units or '(no unit)'}")
    if len(missing_units) > 10:
                try:
                    if 'product_db' not in locals():
                        conn.close()
                except Exception:
                    pass
    print()
    
    # Find products with unusual weights
    print("2. Products with potentially incorrect weights (> 100):")
    cursor.execute('''
        SELECT "Product Name*", "Product Brand", "Weight*", "Units"
                try:
                    product_db = ProductDatabase(store_name='AGT_Bothell')
                    conn = product_db._get_connection()
                except Exception:
                    conn = sqlite3.connect(DB_PATH)
        ORDER BY CAST("Weight*" AS REAL) DESC
    ''')
    
    high_weights = cursor.fetchall()
    print(f"   Found {len(high_weights)} products")
    for name, brand, weight, units in high_weights[:10]:
        print(f"   - {name} ({brand}): {weight} {units or '(no unit)'}")
    if len(high_weights) > 10:
        print(f"   ... and {len(high_weights) - 10} more")
    print()
    
    # Find products with weight/unit mismatches
    print("3. Products with g units but small values (likely should be oz):")
    cursor.execute('''
        SELECT "Product Name*", "Product Brand", "Weight*", "Units"
        FROM products
        WHERE LOWER("Units") = 'g'
        AND CAST("Weight*" AS REAL) < 10
        AND "Product Type*" IN ('Edibles', 'Beverage')
        ORDER BY "Product Brand", "Product Name*"
    ''')
    
    unit_issues = cursor.fetchall()
                try:
                    if 'product_db' not in locals():
                        conn.close()
                except Exception:
                    pass
    for name, brand, weight, units in unit_issues[:10]:
        print(f"   - {name} ({brand}): {weight} {units}")
    if len(unit_issues) > 10:
        print(f"   ... and {len(unit_issues) - 10} more")
                try:
                    product_db = ProductDatabase(store_name='AGT_Bothell')
                    conn = product_db._get_connection()
                except Exception:
                    conn = sqlite3.connect(DB_PATH)

def interactive_mode():
    """Interactive mode to fix weights."""
    
    print("\n" + "="*80)
    print("INTERACTIVE WEIGHT FIXER")
    print("="*80)
    print()
    print("Commands:")
    print("  1. Fix Constellation Moonshots (normalize to 1.7 oz)")
    print("  2. Fix specific product by name pattern")
    print("  3. List products by brand")
    print("  4. Run weight audit")
    print("  5. Exit")
    print()
    
    while True:
        choice = input("Enter command (1-5): ").strip()
        
        if choice == '1':
            normalize_moonshot_weights()
        
        elif choice == '2':
            pattern = input("Enter product name pattern (e.g., 'Moonshot'): ").strip()
            weight = input("Enter correct weight (e.g., '1.7'): ").strip()
            units = input("Enter correct units (e.g., 'oz' or 'g'): ").strip()
            
            confirm = input(f"Fix all products matching '{pattern}' to {weight} {units}? (yes/no): ")
            if confirm.lower() == 'yes':
                fix_specific_product(pattern, weight, units)
            else:
                print("Cancelled")
        
        elif choice == '3':
            brand = input("Enter brand name: ").strip()
            pattern = input("Enter name pattern (or press Enter for all): ").strip()
            list_products_by_brand(brand, pattern if pattern else None)
        
        elif choice == '4':
            audit_weights()
        
        elif choice == '5':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    print("="*80)
    print("DATABASE WEIGHT NORMALIZATION TOOL")
    print("="*80)
    print(f"Database: {DB_PATH}")
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)
    
    if len(sys.argv) > 1:
                try:
                    if 'product_db' not in locals():
                        conn.close()
                except Exception:
                    pass
        
        if command == 'moonshots':
            # Quick fix for Constellation Moonshots
            normalize_moonshot_weights()
        
        elif command == 'audit':
            # Run weight audit
            audit_weights()
        
        elif command == 'list' and len(sys.argv) > 2:
            # List products by brand
            brand = sys.argv[2]
            pattern = sys.argv[3] if len(sys.argv) > 3 else None
            list_products_by_brand(brand, pattern)
        
        else:
            print("Usage:")
            print("  python fix_database_weights.py              # Interactive mode")
            print("  python fix_database_weights.py moonshots    # Fix Constellation Moonshots")
            print("  python fix_database_weights.py audit        # Run weight audit")
            print("  python fix_database_weights.py list 'Brand Name' [pattern]")
    else:
        # Interactive mode
        interactive_mode()

