#!/usr/bin/env python3
"""
Complete diagnostic for lineage changes not persisting
This will test every single step and tell us exactly what's wrong
"""

import sys
import os
import sqlite3

def diagnose_complete():
    """Complete diagnostic of the lineage issue."""
    
    print("=" * 80)
    print("COMPLETE LINEAGE DIAGNOSTIC - FINAL CHECK")
    print("=" * 80)
    
    issues_found = []
    
    # CHECK 1: Database has normalized_name column
    print("\n1️⃣  Checking if normalized_name column exists...")
    try:
        db_path = "uploads/product_database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(products);")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'normalized_name' in columns:
            print(f"   ✅ normalized_name column exists")
            
            # Check if populated
            cursor.execute("SELECT COUNT(*) FROM products WHERE normalized_name IS NULL;")
            null_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products;")
            total_count = cursor.fetchone()[0]
            
            print(f"   📊 Products: {total_count:,} total, {null_count} without normalized_name")
            
            if null_count > 0:
                print(f"   ⚠️  WARNING: {null_count} products missing normalized_name!")
                issues_found.append(f"{null_count} products missing normalized_name")
        else:
            print(f"   ❌ CRITICAL: normalized_name column MISSING!")
            print(f"   ⚠️  This is causing all the errors!")
            issues_found.append("normalized_name column missing")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        issues_found.append(f"Database check failed: {e}")
    
    # CHECK 2: Test lineage update and retrieval
    print("\n2️⃣  Testing lineage update/retrieval flow...")
    try:
        from src.core.data.product_database import ProductDatabase
        
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
            print(f"   📊 Current lineage: '{original_lineage}'")
            
            # Test update
            new_lineage = "SATIVA" if original_lineage != "SATIVA" else "INDICA"
            print(f"   🔄 Updating to: '{new_lineage}'")
            
            try:
                success = db.update_product_lineage(product_name, new_lineage)
                if success:
                    print(f"   ✅ Update succeeded")
                    
                    # Verify in database directly
                    cursor.execute('SELECT "Lineage" FROM products WHERE "Product Name*" = ?;', (product_name,))
                    db_lineage = cursor.fetchone()[0]
                    
                    if db_lineage == new_lineage:
                        print(f"   ✅ Database has correct lineage: '{db_lineage}'")
                    else:
                        print(f"   ❌ Database mismatch! Expected '{new_lineage}', got '{db_lineage}'")
                        issues_found.append("Lineage update not persisting to database")
                    
                    # Test retrieval via ProductDatabase
                    retrieved = db.get_product_lineage(product_name)
                    if retrieved == new_lineage:
                        print(f"   ✅ Retrieval works: '{retrieved}'")
                    else:
                        print(f"   ❌ Retrieval mismatch! Expected '{new_lineage}', got '{retrieved}'")
                        issues_found.append("Lineage retrieval not working")
                    
                    # Restore
                    db.update_product_lineage(product_name, original_lineage)
                    print(f"   ✅ Restored original lineage")
                else:
                    print(f"   ❌ Update failed!")
                    issues_found.append("update_product_lineage returned False")
            except Exception as update_error:
                print(f"   ❌ Update error: {update_error}")
                issues_found.append(f"Update error: {update_error}")
        else:
            print(f"   ⚠️  No products with lineage found")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        issues_found.append(f"Test failed: {e}")
    
    # CHECK 3: Verify app.py has lineage override for ALL paths
    print("\n3️⃣  Checking app.py lineage override code...")
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        checks = [
            ('LINEAGE OVERRIDE: Checking for updated lineage in database for Excel records', 'Excel record override'),
            ('LINEAGE OVERRIDE: Checking for updated lineage in database...', 'Database record override'),
            ('product_db.get_product_lineage', 'get_product_lineage call'),
        ]
        
        for check_str, description in checks:
            if check_str in app_content:
                print(f"   ✅ {description} found")
            else:
                print(f"   ❌ {description} MISSING!")
                issues_found.append(f"{description} missing from app.py")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # CHECK 4: Check which source is being used for generation
    print("\n4️⃣  Checking what source is used for record generation...")
    try:
        # Look for recent generation in logs
        log_path = "/var/log/www.agtpricetags.com.error.log"
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                lines = f.readlines()
            
            # Look for recent generation
            recent_lines = lines[-500:]  # Last 500 lines
            
            found_generation = False
            for line in recent_lines:
                if 'Using database for record generation' in line:
                    print(f"   📊 Using: Database records")
                    found_generation = True
                    break
                elif 'Using Excel data for record generation' in line:
                    print(f"   📊 Using: Excel records")
                    found_generation = True
                    break
            
            if not found_generation:
                print(f"   ⚠️  No recent generation found in logs")
            
            # Check for lineage override messages
            override_found = False
            for line in recent_lines:
                if 'LINEAGE OVERRIDE' in line and 'Checking for updated lineage' in line:
                    print(f"   ✅ Lineage override is being called")
                    override_found = True
                    break
            
            if not override_found:
                print(f"   ❌ WARNING: Lineage override not being called!")
                issues_found.append("Lineage override not being called during generation")
        else:
            print(f"   ⚠️  Log file not found: {log_path}")
    except Exception as e:
        print(f"   ⚠️  Could not check logs: {e}")
    
    # CHECK 5: Test if records actually use database lineage
    print("\n5️⃣  Simulating DOCX generation to see if lineage is used...")
    try:
        from src.core.data.product_database import ProductDatabase
        
        db = ProductDatabase()
        conn = sqlite3.connect("uploads/product_database.db")
        cursor = conn.cursor()
        
        # Get a product
        cursor.execute('SELECT "Product Name*", "Lineage" FROM products LIMIT 1;')
        sample = cursor.fetchone()
        
        if sample:
            product_name, current_lineage = sample
            
            # Simulate what happens during DOCX generation
            # Step 1: Get lineage from database
            db_lineage = db.get_product_lineage(product_name)
            
            # Step 2: Create a mock record (like what Excel processor creates)
            record = {
                'Product Name*': product_name,
                'Lineage': 'OLD_LINEAGE_FROM_EXCEL'  # Simulate old lineage from Excel
            }
            
            # Step 3: Simulate the override logic
            original_lineage = record.get('Lineage', '')
            if db_lineage and str(db_lineage).strip() != str(original_lineage).strip():
                record['Lineage'] = str(db_lineage).strip()
                print(f"   ✅ Override would happen: '{original_lineage}' → '{db_lineage}'")
            else:
                print(f"   ℹ️  No override needed (lineages match)")
            
            print(f"   📊 Final record lineage: '{record['Lineage']}'")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # SUMMARY
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    if issues_found:
        print(f"\n❌ FOUND {len(issues_found)} ISSUE(S):")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n🔧 RECOMMENDED FIXES:")
        
        if any('normalized_name' in issue.lower() for issue in issues_found):
            print(f"\n   1. Run: python3 fix_normalized_name_column.py")
            print(f"      This will add the missing normalized_name column")
        
        if any('override' in issue.lower() for issue in issues_found):
            print(f"\n   2. Reload web app:")
            print(f"      https://www.pythonanywhere.com/user/adamcordova/webapps/")
            print(f"      Click 'Reload www.agtpricetags.com'")
        
        print(f"\n   3. Clear browser cache: Ctrl+Shift+R or Cmd+Shift+R")
        
    else:
        print(f"\n✅ NO CRITICAL ISSUES FOUND!")
        print(f"\n📋 If lineage changes still don't work:")
        print(f"   1. Make sure you've reloaded the web app")
        print(f"   2. Clear browser cache completely")
        print(f"   3. Check that you're testing with the RIGHT database")
        print(f"   4. Monitor logs during generation:")
        print(f"      tail -f /var/log/www.agtpricetags.com.error.log | grep LINEAGE")
    
    print("=" * 80)
    
    return len(issues_found) == 0

if __name__ == "__main__":
    try:
        success = diagnose_complete()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

