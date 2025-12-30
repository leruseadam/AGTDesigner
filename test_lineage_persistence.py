#!/usr/bin/env python3
"""
Test script to verify manual lineage changes persist.

Steps:
1. Find a product in the database
2. Update its lineage via update_product_lineage (simulating manual update)
3. Verify sovereign_lineage was set
4. Simulate Excel upload trying to overwrite
5. Verify sovereign lineage was protected
"""

import sqlite3
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.data.product_database import ProductDatabase

def test_lineage_persistence():
    """Test that manual lineage changes persist."""

    print("\n" + "="*70)
    print("TESTING MANUAL LINEAGE PERSISTENCE")
    print("="*70)

    # Use the actual database
    db = ProductDatabase(store_name='AGT_Bothell')
    conn = db._get_connection()
    cursor = conn.cursor()

    # Find a product with lineage
    cursor.execute('''
        SELECT "Product Name*", "Lineage", sovereign_lineage
        FROM products
        WHERE "Lineage" IS NOT NULL AND "Lineage" != ''
        LIMIT 1
    ''')

    result = cursor.fetchone()
    if not result:
        print("❌ No products with lineage found in database")
        return False

    product_name, original_lineage, original_sovereign = result
    print(f"\n[Step 1] Found test product: {product_name}")
    print(f"   Original Lineage: {original_lineage}")
    print(f"   Original sovereign_lineage: {original_sovereign}")

    # Step 2: Manually update lineage (simulating UI update)
    new_lineage = "HYBRID"  # Change to HYBRID
    print(f"\n[Step 2] Updating lineage to '{new_lineage}' (manual update)...")

    success = db.update_product_lineage(product_name, new_lineage)
    print(f"   update_product_lineage returned: {success}")

    # Verify it was updated
    cursor.execute('''
        SELECT "Lineage", sovereign_lineage
        FROM products
        WHERE "Product Name*" = ?
        ORDER BY id DESC
        LIMIT 1
    ''', (product_name,))

    result = cursor.fetchone()
    if result:
        db_lineage, db_sovereign = result
        print(f"   Database Lineage: {db_lineage}")
        print(f"   Database sovereign_lineage: {db_sovereign}")

        if db_sovereign and db_sovereign.upper() == new_lineage.upper():
            print(f"✅ sovereign_lineage was set correctly!")
        else:
            print(f"❌ sovereign_lineage NOT set! Expected '{new_lineage}', got '{db_sovereign}'")
            return False
    else:
        print(f"❌ Could not find product after update")
        return False

    # Step 3: Simulate Excel upload with different lineage
    print(f"\n[Step 3] Simulating Excel upload with lineage 'INDICA' (should be blocked)...")

    excel_data = {
        'Product Name*': product_name,
        'Lineage': 'INDICA',
        'Product Type*': 'Usable Marijuana',
        'Vendor/Supplier*': 'Test Vendor',
        'Weight*': '3.5g',
        'Price': '25.00'
    }

    # Call add_or_update_product which should protect sovereign lineage
    db.add_or_update_product(excel_data)

    # Step 4: Verify sovereign lineage was protected
    print(f"\n[Step 4] Verifying sovereign lineage was protected...")
    cursor.execute('''
        SELECT "Lineage", sovereign_lineage
        FROM products
        WHERE "Product Name*" = ?
        ORDER BY id DESC
        LIMIT 1
    ''', (product_name,))

    result = cursor.fetchone()
    if result:
        final_lineage, final_sovereign = result
        print(f"   Final Lineage: {final_lineage}")
        print(f"   Final sovereign_lineage: {final_sovereign}")

        if final_sovereign and final_sovereign.upper() == new_lineage.upper():
            print(f"✅ SUCCESS: Sovereign lineage was PROTECTED!")
            print(f"   Excel tried to set 'INDICA' but sovereign lineage stayed '{final_sovereign}'")
            success = True
        else:
            print(f"❌ FAILURE: Sovereign lineage was NOT protected!")
            print(f"   Expected '{new_lineage}', got '{final_sovereign}'")
            success = False
    else:
        print(f"❌ Could not find product after Excel simulation")
        success = False

    # Cleanup - restore original values
    print(f"\n[Cleanup] Restoring original values...")
    cursor.execute('''
        UPDATE products
        SET "Lineage" = ?, sovereign_lineage = ?
        WHERE "Product Name*" = ?
    ''', (original_lineage, original_sovereign, product_name))
    conn.commit()
    print(f"✅ Original values restored")

    print("="*70 + "\n")
    return success

if __name__ == '__main__':
    try:
        success = test_lineage_persistence()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
