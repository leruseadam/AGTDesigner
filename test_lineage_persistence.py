#!/usr/bin/env python3
"""
Test script to verify that manually updated lineage values persist after Excel file reload.
"""

import sys
import os
import pandas as pd
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.data.product_database import get_product_database

def test_lineage_persistence():
    """Test that manually updated lineage persists after Excel upload."""
    
    print("=" * 80)
    print("TESTING LINEAGE PERSISTENCE")
    print("=" * 80)
    print()
    
    # Get product database
    try:
        product_db = get_product_database('AGT_Bothell')
        if not product_db:
            print("❌ ERROR: Could not get product database")
            return False
    except Exception as e:
        print(f"❌ ERROR: Failed to get product database: {e}")
        return False
    
    conn = product_db._get_connection()
    cursor = conn.cursor()
    
    # Step 1: Find a test product
    print("Step 1: Finding a test product...")
    cursor.execute('''
        SELECT "Product Name*", "Lineage", "Vendor/Supplier*"
        FROM products
        WHERE "Product Name*" IS NOT NULL 
          AND "Product Name*" != ''
        LIMIT 1
    ''')
    
    result = cursor.fetchone()
    if not result:
        print("❌ ERROR: No products found in database")
        return False
    
    test_product_name = result[0]
    original_lineage = result[1] or ''
    test_vendor = result[2] or ''
    
    print(f"✅ Found test product: '{test_product_name}'")
    print(f"   Original lineage: '{original_lineage}'")
    print(f"   Vendor: '{test_vendor}'")
    print()
    
    # Step 2: Manually update the lineage (simulating user action)
    print("Step 2: Manually updating lineage (simulating user action)...")
    test_lineage = "HYBRID"  # Use a different lineage for testing
    if original_lineage and original_lineage.upper() == "HYBRID":
        test_lineage = "SATIVA"  # Use different one if already HYBRID
    
    success = product_db.update_product_lineage(test_product_name, test_lineage)
    if not success:
        print(f"❌ ERROR: Failed to update lineage to '{test_lineage}'")
        return False
    
    # Verify the update
    cursor.execute('''
        SELECT p."Lineage", s.sovereign_lineage, s.canonical_lineage
        FROM products p
        LEFT JOIN strains s ON p.strain_id = s.id
        WHERE p."Product Name*" = ?
        LIMIT 1
    ''', (test_product_name,))
    
    verify_result = cursor.fetchone()
    db_lineage = verify_result[0] or verify_result[1] or verify_result[2] if verify_result else None
    
    if not db_lineage or db_lineage.upper() != test_lineage.upper():
        print(f"❌ ERROR: Lineage update failed. Expected '{test_lineage}', got '{db_lineage}'")
        return False
    
    print(f"✅ Successfully updated lineage to '{test_lineage}'")
    print()
    
    # Step 3: Create a test Excel DataFrame with different lineage
    print("Step 3: Creating test Excel DataFrame with different lineage...")
    excel_lineage = "INDICA"  # Different from what we just set
    
    test_df = pd.DataFrame([{
        'Product Name*': test_product_name,
        'Product Type*': 'Flower',
        'Vendor/Supplier*': test_vendor,
        'Lineage': excel_lineage,  # Excel has different lineage
        'Weight*': '3.5',
        'Units': 'g',
        'Price': '25.00',
        'Description': 'Test product for lineage persistence',
        'Product Brand': 'Test Brand'
    }])
    
    print(f"✅ Created test DataFrame with Excel lineage: '{excel_lineage}'")
    print()
    
    # Step 4: Store Excel data (this should preserve the manually updated lineage)
    print("Step 4: Storing Excel data (should preserve manually updated lineage)...")
    try:
        result = product_db.store_excel_data(test_df, 'test_lineage_persistence.xlsx')
        print(f"✅ Excel data stored: {result.get('message', 'Success')}")
        print()
    except Exception as e:
        print(f"❌ ERROR: Failed to store Excel data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Verify that the manually updated lineage persisted
    print("Step 5: Verifying that manually updated lineage persisted...")
    cursor.execute('''
        SELECT p."Lineage", s.sovereign_lineage, s.canonical_lineage
        FROM products p
        LEFT JOIN strains s ON p.strain_id = s.id
        WHERE p."Product Name*" = ?
        LIMIT 1
    ''', (test_product_name,))
    
    final_result = cursor.fetchone()
    if not final_result:
        print("❌ ERROR: Product not found after Excel upload")
        return False
    
    final_lineage = (
        final_result[1] or  # sovereign_lineage (manually updated)
        final_result[2] or  # canonical_lineage (manually updated)
        final_result[0]     # product Lineage
    )
    final_lineage = str(final_lineage).strip().upper() if final_lineage else ''
    
    print(f"   Final lineage in database: '{final_lineage}'")
    print(f"   Expected (manually updated): '{test_lineage.upper()}'")
    print(f"   Excel had: '{excel_lineage.upper()}'")
    print()
    
    # Check if lineage persisted correctly
    if final_lineage == test_lineage.upper():
        print("✅ SUCCESS: Manually updated lineage persisted correctly!")
        print(f"   The lineage '{test_lineage}' was preserved even though Excel had '{excel_lineage}'")
        print()
        
        # Restore original lineage if it was different
        if original_lineage and original_lineage.upper() != test_lineage.upper():
            print(f"Step 6: Restoring original lineage '{original_lineage}'...")
            product_db.update_product_lineage(test_product_name, original_lineage)
            print(f"✅ Restored original lineage")
        
        return True
    else:
        print("❌ FAILURE: Lineage did not persist correctly!")
        print(f"   Expected '{test_lineage.upper()}', but got '{final_lineage}'")
        print(f"   This means the Excel lineage '{excel_lineage}' overwrote the manually updated lineage")
        return False

if __name__ == '__main__':
    success = test_lineage_persistence()
    sys.exit(0 if success else 1)

