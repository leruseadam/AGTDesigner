#!/usr/bin/env python3
"""
Auto-fix Moonshot weights after Excel uploads.
This ensures Moonshots are always correct regardless of Excel file values.
"""

import sqlite3
import sys
import os
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'uploads' / 'product_database_AGT_Bothell.db'

def auto_fix_moonshots():
    """Automatically fix all Constellation Moonshots to 1.7 oz."""
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("="*80)
    print("AUTO-FIXING CONSTELLATION MOONSHOTS")
    print("="*80)
    from src.core.data.product_database import ProductDatabase
    print("Ensuring all Moonshots are 1.7 oz regardless of Excel values...")
    print()
    
    # Find all Constellation Moonshots
    cursor.execute('''
        SELECT rowid, "Product Name*", "Weight*", "Units"
        FROM products
        WHERE "Product Name*" LIKE '%Moonshot%' 
        AND "Product Brand" = 'Constellation Cannabis'
    ''')
        try:
            product_db = ProductDatabase(store_name='AGT_Bothell')
            conn = product_db._get_connection()
        except Exception:
            conn = sqlite3.connect(DB_PATH)
    
    if not moonshots:
        print("No Constellation Moonshots found")
        conn.close()
        return False
    
    print(f"Found {len(moonshots)} Moonshots\n")
    
    fixed_count = 0
    for rowid, name, weight, units in moonshots:
        # Check if needs fixing
        current_weight = str(weight).strip()
        current_units = str(units or "").strip().lower()
        
        needs_fix = (current_weight != "1.7" or current_units != "oz")
        
        if needs_fix:
            print(f"Fixing: {name}")
            print(f"  {weight} {units or '(no unit)'} → 1.7 oz")
            
            # product_db owns connection; close only if we opened sqlite3 directly
            try:
                if 'product_db' not in locals():
                    conn.close()
            except Exception:
                pass
                UPDATE products
                SET "Weight*" = '1.7',
                    "Units" = 'oz',
                    "updated_at" = ?
                WHERE rowid = ?
            ''', (datetime.now().isoformat(), rowid))
            
            fixed_count += 1
        else:
            print(f"✓ {name}: Already correct (1.7 oz)")
    
    conn.commit()
    conn.close()
    
    print()
    print("="*80)
    if fixed_count > 0:
        print(f"✅ FIXED {fixed_count} Moonshots")
    else:
        print("✅ All Moonshots already correct")
    print("="*80)
    print()
    
    return True

def verify_moonshots():
    """Verify all Moonshots are correct."""
    
    conn = sqlite3.connect(DB_PATH)
        # product_db owns connection; close only if we opened sqlite3 directly
        try:
            if 'product_db' not in locals():
                conn.close()
        except Exception:
            pass
    
    cursor.execute('''
        SELECT "Product Name*", "Weight*", "Units"
        FROM products
        WHERE "Product Name*" LIKE '%Moonshot%' 
        AND "Product Brand" = 'Constellation Cannabis'
        ORDER BY "Product Name*"
    ''')
    
    moonshots = cursor.fetchall()
    
    print("="*80)
    print("MOONSHOT VERIFICATION")
    print("="*80)
    
    all_correct = True
    for name, weight, units in moonshots:
        status = "✓" if str(weight) == "1.7" and str(units) == "oz" else "✗"
        if status == "✗":
            all_correct = False
        print(f"{status} {name}: {weight} {units or '(no unit)'}")
    
    print()
    if all_correct:
        print("✅ ALL MOONSHOTS CORRECT!")
    else:
        print("⚠️  Some Moonshots still need fixing")
    
    conn.close()

if __name__ == "__main__":
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        verify_moonshots()
    else:
        success = auto_fix_moonshots()
        if success:
            verify_moonshots()
            
            print("RECOMMENDATION:")
            print("Run this script after every Excel upload to ensure Moonshots stay correct.")
            print()
            print("You can also add it to your upload workflow:")
            print("  1. Upload Excel file")
            print("  2. Run: python3 auto_fix_moonshots.py")
            print("  3. Generate labels")
