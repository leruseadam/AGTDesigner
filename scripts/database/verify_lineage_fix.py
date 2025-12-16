#!/usr/bin/env python3
"""
Quick verification script to confirm lineage fix is working
"""

import sys
import os

def verify_lineage_fix():
    """Verify all components of the lineage fix are working."""
    
    print("🔍 VERIFYING LINEAGE FIX")
    print("=" * 50)
    
    all_passed = True
    
    # Test 1: Import ProductDatabase
    print("\n1️⃣  Testing ProductDatabase import...")
    try:
        from src.core.data.product_database import ProductDatabase
        print("   ✅ ProductDatabase imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import ProductDatabase: {e}")
        all_passed = False
        return False
    
    # Test 2: Check methods exist
    print("\n2️⃣  Checking ProductDatabase methods...")
    try:
        db = ProductDatabase()
        has_get = hasattr(db, 'get_product_lineage')
        has_update = hasattr(db, 'update_product_lineage')
        
        if has_get and has_update:
            print("   ✅ get_product_lineage method exists")
            print("   ✅ update_product_lineage method exists")
        else:
            print(f"   ❌ Missing methods: get={has_get}, update={has_update}")
            all_passed = False
    except Exception as e:
        print(f"   ❌ Error checking methods: {e}")
        all_passed = False
    
    # Test 3: Check database exists and has products
    print("\n3️⃣  Checking database...")
    try:
        import sqlite3
        db_path = "uploads/product_database.db"
        
        if not os.path.exists(db_path):
            print(f"   ⚠️  Database not found at: {db_path}")
            print("   ℹ️  This is normal if you haven't uploaded products yet")
        else:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check products count
            cursor.execute("SELECT COUNT(*) FROM products;")
            count = cursor.fetchone()[0]
            print(f"   ✅ Database found with {count} products")
            
            # Check for lineage column
            cursor.execute("PRAGMA table_info(products);")
            columns = [row[1] for row in cursor.fetchall()]
            
            if "Lineage" in columns:
                print("   ✅ Lineage column exists")
            else:
                print("   ❌ Lineage column missing")
                all_passed = False
            
            conn.close()
    except Exception as e:
        print(f"   ❌ Error checking database: {e}")
        all_passed = False
    
    # Test 4: Check DOCX formatting
    print("\n4️⃣  Checking DOCX formatting...")
    try:
        import src.core.generation.docx_formatting as docx_fmt
        
        if hasattr(docx_fmt, 'apply_lineage_colors'):
            print("   ✅ apply_lineage_colors function exists")
        else:
            print("   ❌ apply_lineage_colors function missing")
            all_passed = False
        
        if hasattr(docx_fmt, 'COLORS'):
            colors = docx_fmt.COLORS
            required_colors = ['SATIVA', 'INDICA', 'HYBRID', 'CBD', 'MIXED']
            missing = [c for c in required_colors if c not in colors]
            
            if not missing:
                print(f"   ✅ All required colors defined ({len(colors)} total)")
            else:
                print(f"   ❌ Missing colors: {missing}")
                all_passed = False
        else:
            print("   ❌ COLORS dict missing")
            all_passed = False
    except Exception as e:
        print(f"   ❌ Error checking DOCX formatting: {e}")
        all_passed = False
    
    # Test 5: Check if debugging is enabled
    print("\n5️⃣  Checking debugging features...")
    try:
        with open('src/core/generation/docx_formatting.py', 'r') as f:
            content = f.read()
        
        if 'LINEAGE COLOR:' in content:
            print("   ✅ Lineage color debugging enabled")
        else:
            print("   ⚠️  Lineage color debugging not found")
        
        if 'debug_lineage_data' in content:
            print("   ✅ Debug lineage data function exists")
        else:
            print("   ⚠️  Debug lineage data function not found")
    except Exception as e:
        print(f"   ❌ Error checking debugging: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("\nNext steps:")
        print("1. Test lineage changes in the web interface")
        print("2. Generate a DOCX file")
        print("3. Check that lineage colors appear correctly")
        print("4. Monitor logs for debugging output")
        return True
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("\nPlease review the errors above and:")
        print("1. Make sure all files are up to date (git pull)")
        print("2. Check that database exists and has products")
        print("3. Verify all imports are working correctly")
        return False

if __name__ == "__main__":
    success = verify_lineage_fix()
    sys.exit(0 if success else 1)

