#!/usr/bin/env python3
"""
Complete test of lineage change flow on web version
This will test every step to find where it's failing
"""

import sys
import os
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_complete_lineage_flow():
    """Test the complete lineage flow step by step."""
    
    print("=" * 80)
    print("COMPLETE WEB LINEAGE FLOW TEST")
    print("=" * 80)
    
    all_tests_passed = True
    
    # TEST 1: Check database has products
    print("\n1️⃣  Test 1: Database has products...")
    try:
        db_path = "uploads/product_database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM products;")
        count = cursor.fetchone()[0]
        print(f"   Products in database: {count:,}")
        
        if count == 0:
            print(f"   ❌ FAIL: Database is empty!")
            all_tests_passed = False
            conn.close()
            return False
        else:
            print(f"   ✅ PASS: Database has products")
        
        # Get a sample product
        cursor.execute('SELECT "Product Name*", "Lineage", "Product Type*" FROM products WHERE "Lineage" IS NOT NULL AND "Lineage" != "" LIMIT 1;')
        sample = cursor.fetchone()
        
        if not sample:
            print(f"   ❌ FAIL: No products with lineage found!")
            all_tests_passed = False
            conn.close()
            return False
        
        product_name, original_lineage, product_type = sample
        print(f"   Sample product: '{product_name}'")
        print(f"   Original lineage: '{original_lineage}'")
        print(f"   Product type: '{product_type}'")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        all_tests_passed = False
        return False
    
    # TEST 2: ProductDatabase can update lineage
    print("\n2️⃣  Test 2: ProductDatabase.update_product_lineage works...")
    try:
        from src.core.data.product_database import ProductDatabase
        db = ProductDatabase()
        
        new_lineage = "SATIVA" if original_lineage != "SATIVA" else "INDICA"
        print(f"   Updating to: '{new_lineage}'")
        
        success = db.update_product_lineage(product_name, new_lineage)
        if not success:
            print(f"   ❌ FAIL: update_product_lineage returned False")
            all_tests_passed = False
        else:
            print(f"   ✅ PASS: update_product_lineage returned True")
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        all_tests_passed = False
        return False
    
    # TEST 3: ProductDatabase can retrieve updated lineage
    print("\n3️⃣  Test 3: ProductDatabase.get_product_lineage retrieves update...")
    try:
        retrieved = db.get_product_lineage(product_name)
        print(f"   Retrieved lineage: '{retrieved}'")
        
        if retrieved != new_lineage:
            print(f"   ❌ FAIL: Expected '{new_lineage}', got '{retrieved}'")
            all_tests_passed = False
        else:
            print(f"   ✅ PASS: Lineage retrieved correctly")
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        all_tests_passed = False
        return False
    
    # TEST 4: Check app.py has lineage override logic
    print("\n4️⃣  Test 4: app.py has lineage override in /api/generate...")
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        if 'LINEAGE OVERRIDE: Checking for updated lineage in database' in app_content:
            print(f"   ✅ PASS: Lineage override code found")
        else:
            print(f"   ❌ FAIL: Lineage override code NOT found!")
            all_tests_passed = False
        
        if 'product_db.get_product_lineage' in app_content:
            print(f"   ✅ PASS: get_product_lineage call found")
        else:
            print(f"   ❌ FAIL: get_product_lineage call NOT found!")
            all_tests_passed = False
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        all_tests_passed = False
    
    # TEST 5: Simulate DOCX generation retrieval
    print("\n5️⃣  Test 5: DOCX generation would retrieve correct lineage...")
    try:
        # This simulates what /api/generate does
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Direct database query (like what DOCX generation does)
        cursor.execute('SELECT "Lineage" FROM products WHERE "Product Name*" = ?;', (product_name,))
        result = cursor.fetchone()
        
        if result:
            db_lineage = result[0]
            print(f"   Direct DB query result: '{db_lineage}'")
            
            if db_lineage != new_lineage:
                print(f"   ❌ FAIL: Database has '{db_lineage}' but expected '{new_lineage}'")
                all_tests_passed = False
            else:
                print(f"   ✅ PASS: Database has correct lineage")
        else:
            print(f"   ❌ FAIL: Product not found in direct query!")
            all_tests_passed = False
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        all_tests_passed = False
    
    # TEST 6: Check lineage color mapping
    print("\n6️⃣  Test 6: Lineage color mapping exists...")
    try:
        from src.core.generation.docx_formatting import COLORS, apply_lineage_colors
        
        if new_lineage in COLORS:
            color = COLORS[new_lineage]
            print(f"   ✅ PASS: '{new_lineage}' has color #{color}")
        else:
            print(f"   ❌ FAIL: '{new_lineage}' has no color mapping!")
            all_tests_passed = False
        
        # Test that apply_lineage_colors exists
        if callable(apply_lineage_colors):
            print(f"   ✅ PASS: apply_lineage_colors function exists")
        else:
            print(f"   ❌ FAIL: apply_lineage_colors is not callable!")
            all_tests_passed = False
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        all_tests_passed = False
    
    # TEST 7: Test actual color application
    print("\n7️⃣  Test 7: Color application works on test document...")
    try:
        from docx import Document
        from src.core.generation.docx_formatting import apply_lineage_colors, COLORS
        
        # Create test document
        doc = Document()
        table = doc.add_table(rows=1, cols=1)
        table.rows[0].cells[0].text = new_lineage
        
        # Apply colors
        doc = apply_lineage_colors(doc)
        
        # Check if color was applied
        cell = table.rows[0].cells[0]
        tc = cell._tc
        tcPr = tc.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcPr')
        
        if tcPr is not None:
            shd = tcPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
            if shd is not None:
                fill_color = shd.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill')
                expected_color = COLORS.get(new_lineage)
                
                if fill_color == expected_color:
                    print(f"   ✅ PASS: Color applied correctly (#{fill_color})")
                else:
                    print(f"   ❌ FAIL: Wrong color! Expected #{expected_color}, got #{fill_color}")
                    all_tests_passed = False
            else:
                print(f"   ❌ FAIL: No shading element found!")
                all_tests_passed = False
        else:
            print(f"   ❌ FAIL: No tcPr element found!")
            all_tests_passed = False
        
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Restore original lineage
    print("\n8️⃣  Cleanup: Restoring original lineage...")
    try:
        db.update_product_lineage(product_name, original_lineage)
        print(f"   ✅ Restored to '{original_lineage}'")
    except Exception as e:
        print(f"   ⚠️  Warning: Could not restore: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    if all_tests_passed:
        print("✅ ALL TESTS PASSED!")
        print("\n🎯 The lineage system is working correctly!")
        print("\nIf web version still doesn't work, the issue is:")
        print("   1. Web app needs to be reloaded")
        print("   2. Browser cache needs to be cleared")
        print("   3. Check server logs for errors during DOCX generation")
    else:
        print("❌ SOME TESTS FAILED!")
        print("\n🔍 Check the failed tests above to identify the issue.")
    print("=" * 80)
    
    return all_tests_passed

if __name__ == "__main__":
    try:
        success = test_complete_lineage_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

