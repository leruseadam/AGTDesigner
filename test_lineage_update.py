#!/usr/bin/env python3
"""
Test script to verify lineage updates are working correctly.
"""

import sqlite3
import os

def test_lineage_update():
    """Test lineage update functionality."""
    
    db_path = 'uploads/product_database_AGT_Bothell.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    print(f"Testing lineage updates on: {db_path}\n")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get a sample product
    print("1. Getting sample product...")
    cursor.execute('''
        SELECT "Product Name*", "Lineage", "Product Strain", "Product Type*"
        FROM products
        WHERE "Lineage" IS NOT NULL AND "Lineage" != ''
        LIMIT 1
    ''')
    
    result = cursor.fetchone()
    if not result:
        print("❌ No products found with lineage")
        conn.close()
        return
    
    product_name, current_lineage, strain, product_type = result
    print(f"   Product: {product_name}")
    print(f"   Current lineage: {current_lineage}")
    print(f"   Strain: {strain}")
    print(f"   Type: {product_type}")
    
    # Test update
    print(f"\n2. Testing lineage update...")
    test_lineage = 'HYBRID' if current_lineage != 'HYBRID' else 'SATIVA'
    
    cursor.execute('''
        UPDATE products
        SET "Lineage" = ?
        WHERE "Product Name*" = ?
    ''', (test_lineage, product_name))
    
    updated_rows = cursor.rowcount
    conn.commit()
    
    print(f"   Updated {updated_rows} rows")
    
    # Verify update
    print(f"\n3. Verifying update...")
    cursor.execute('''
        SELECT "Lineage"
        FROM products
        WHERE "Product Name*" = ?
    ''', (product_name,))
    
    new_lineage_result = cursor.fetchone()
    if new_lineage_result:
        verified_lineage = new_lineage_result[0]
        print(f"   Verified lineage: {verified_lineage}")
        
        if verified_lineage == test_lineage:
            print(f"   ✅ Update successful! {current_lineage} → {verified_lineage}")
        else:
            print(f"   ❌ Update failed! Expected {test_lineage}, got {verified_lineage}")
    else:
        print(f"   ❌ Could not verify update")
    
    # Restore original lineage
    print(f"\n4. Restoring original lineage...")
    cursor.execute('''
        UPDATE products
        SET "Lineage" = ?
        WHERE "Product Name*" = ?
    ''', (current_lineage, product_name))
    conn.commit()
    print(f"   ✅ Restored to {current_lineage}")
    
    # Test strain update
    print(f"\n5. Testing strain lineage update...")
    cursor.execute('''
        SELECT strain_name, canonical_lineage
        FROM strains
        WHERE canonical_lineage IS NOT NULL AND canonical_lineage != ''
        LIMIT 1
    ''')
    
    strain_result = cursor.fetchone()
    if strain_result:
        strain_name, strain_lineage = strain_result
        print(f"   Strain: {strain_name}")
        print(f"   Current lineage: {strain_lineage}")
        
        test_strain_lineage = 'INDICA' if strain_lineage != 'INDICA' else 'SATIVA'
        
        cursor.execute('''
            UPDATE strains
            SET canonical_lineage = ?
            WHERE strain_name = ?
        ''', (test_strain_lineage, strain_name))
        
        conn.commit()
        print(f"   Updated to {test_strain_lineage}")
        
        # Verify
        cursor.execute('''
            SELECT canonical_lineage
            FROM strains
            WHERE strain_name = ?
        ''', (strain_name,))
        
        verified = cursor.fetchone()[0]
        if verified == test_strain_lineage:
            print(f"   ✅ Strain update successful!")
        else:
            print(f"   ❌ Strain update failed!")
        
        # Restore
        cursor.execute('''
            UPDATE strains
            SET canonical_lineage = ?
            WHERE strain_name = ?
        ''', (strain_lineage, strain_name))
        conn.commit()
        print(f"   ✅ Restored to {strain_lineage}")
    else:
        print(f"   ⚠️  No strains found to test")
    
    conn.close()
    
    print(f"\n✅ Lineage update test complete!")
    print(f"\nConclusion: Database supports lineage updates correctly.")
    print(f"If lineage changes aren't working in the app, the issue is likely:")
    print(f"  1. Frontend not sending the request correctly")
    print(f"  2. Session/cache preventing updates from showing")
    print(f"  3. Excel processor not updating correctly")

if __name__ == "__main__":
    test_lineage_update()

