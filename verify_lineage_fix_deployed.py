#!/usr/bin/env python3
"""
Verify that the lineage fix is deployed and working
"""

import sys
import os

def verify_deployment():
    """Verify the lineage fix is properly deployed."""
    
    print("=" * 80)
    print("VERIFYING LINEAGE FIX DEPLOYMENT")
    print("=" * 80)
    
    all_checks_passed = True
    
    # Check 1: Verify app.py has the Excel record lineage override
    print("\n1️⃣  Checking app.py for Excel record lineage override...")
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        critical_strings = [
            'LINEAGE OVERRIDE: Checking for updated lineage in database for Excel records',
            'LINEAGE OVERRIDE (Excel)',
            'product_db.get_product_lineage(product_name)',
        ]
        
        for check_str in critical_strings:
            if check_str in app_content:
                print(f"   ✅ Found: '{check_str[:60]}...'")
            else:
                print(f"   ❌ MISSING: '{check_str[:60]}...'")
                all_checks_passed = False
        
        # Count how many lineage override sections exist
        override_count = app_content.count('LINEAGE OVERRIDE: Checking for updated lineage')
        print(f"\n   📊 Found {override_count} lineage override section(s)")
        
        if override_count < 2:
            print(f"   ⚠️  WARNING: Should have at least 2 lineage override sections:")
            print(f"      1. For database records")
            print(f"      2. For Excel records")
            all_checks_passed = False
        else:
            print(f"   ✅ Has multiple lineage override sections")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_checks_passed = False
    
    # Check 2: Verify ProductDatabase methods exist
    print("\n2️⃣  Checking ProductDatabase methods...")
    try:
        from src.core.data.product_database import ProductDatabase
        db = ProductDatabase()
        
        methods = ['get_product_lineage', 'update_product_lineage']
        for method in methods:
            if hasattr(db, method):
                print(f"   ✅ {method} exists")
            else:
                print(f"   ❌ {method} MISSING!")
                all_checks_passed = False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_checks_passed = False
    
    # Check 3: Verify database has products
    print("\n3️⃣  Checking database...")
    try:
        import sqlite3
        db_path = "uploads/product_database.db"
        
        if not os.path.exists(db_path):
            print(f"   ❌ Database not found: {db_path}")
            all_checks_passed = False
        else:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM products;")
            count = cursor.fetchone()[0]
            print(f"   📊 Products in database: {count:,}")
            
            if count == 0:
                print(f"   ⚠️  WARNING: Database is empty!")
                all_checks_passed = False
            else:
                print(f"   ✅ Database has products")
            
            conn.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_checks_passed = False
    
    # Check 4: Test actual lineage change flow
    print("\n4️⃣  Testing lineage change flow...")
    try:
        from src.core.data.product_database import ProductDatabase
        import sqlite3
        
        db = ProductDatabase()
        db_path = "uploads/product_database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get a product
        cursor.execute('SELECT "Product Name*", "Lineage" FROM products WHERE "Lineage" IS NOT NULL LIMIT 1;')
        sample = cursor.fetchone()
        
        if sample:
            product_name, original_lineage = sample
            print(f"   📦 Test product: '{product_name}'")
            print(f"   📊 Original lineage: '{original_lineage}'")
            
            # Test update
            new_lineage = "INDICA" if original_lineage != "INDICA" else "SATIVA"
            success = db.update_product_lineage(product_name, new_lineage)
            
            if success:
                print(f"   ✅ Update successful")
                
                # Verify retrieval
                retrieved = db.get_product_lineage(product_name)
                if retrieved == new_lineage:
                    print(f"   ✅ Retrieval successful: '{retrieved}'")
                    
                    # Restore
                    db.update_product_lineage(product_name, original_lineage)
                    print(f"   ✅ Restored to original")
                else:
                    print(f"   ❌ Retrieval failed: expected '{new_lineage}', got '{retrieved}'")
                    all_checks_passed = False
            else:
                print(f"   ❌ Update failed")
                all_checks_passed = False
        else:
            print(f"   ⚠️  No products with lineage found")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        all_checks_passed = False
    
    # Check 5: Look for the specific fix commit
    print("\n5️⃣  Checking git commit history...")
    try:
        import subprocess
        result = subprocess.run(['git', 'log', '--oneline', '-10'], 
                              capture_output=True, text=True, check=True)
        commits = result.stdout.strip().split('\n')
        
        fix_found = False
        for commit in commits:
            if 'lineage override for Excel record' in commit.lower():
                print(f"   ✅ Found fix commit: {commit[:70]}")
                fix_found = True
                break
        
        if not fix_found:
            print(f"   ⚠️  Fix commit not found in recent history")
            print(f"   Recent commits:")
            for commit in commits[:5]:
                print(f"      {commit[:70]}")
            all_checks_passed = False
        
    except Exception as e:
        print(f"   ⚠️  Could not check git history: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED!")
        print("\n🎯 The fix is deployed correctly.")
        print("\n📋 If lineage changes still don't work:")
        print("   1. Make sure web app is reloaded")
        print("   2. Clear browser cache completely")
        print("   3. Check server logs during DOCX generation:")
        print("      tail -f /var/log/www.agtpricetags.com.error.log | grep LINEAGE")
        print("   4. Verify you're generating from the right source:")
        print("      - If using Excel upload, should see 'LINEAGE OVERRIDE (Excel)'")
        print("      - If using database, should see 'LINEAGE OVERRIDE:' (not Excel)")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\n🔧 The fix may not be fully deployed or working.")
        print("   Review the failures above.")
    print("=" * 80)
    
    return all_checks_passed

if __name__ == "__main__":
    try:
        success = verify_deployment()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

