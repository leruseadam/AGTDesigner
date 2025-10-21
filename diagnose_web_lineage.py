#!/usr/bin/env python3
"""
Diagnostic script for troubleshooting lineage issues on web version
Run this ON PYTHONANYWHERE to identify the problem
"""

import os
import sys
import sqlite3
from datetime import datetime

def diagnose_web_lineage():
    """Diagnose lineage issues on the web version."""
    
    print("=" * 70)
    print("WEB VERSION LINEAGE DIAGNOSTIC")
    print("=" * 70)
    
    # Check 1: Find all database files
    print("\n1️⃣  Finding all database files...")
    try:
        db_files = []
        for root, dirs, files in os.walk('uploads'):
            for file in files:
                if file.endswith('.db') and not file.endswith('-shm') and not file.endswith('-wal'):
                    full_path = os.path.join(root, file)
                    size = os.path.getsize(full_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                    db_files.append((full_path, size, modified))
        
        if db_files:
            print(f"   📊 Found {len(db_files)} database file(s):")
            for path, size, modified in sorted(db_files, key=lambda x: x[2], reverse=True):
                size_mb = size / (1024 * 1024)
                print(f"      {path}")
                print(f"         Size: {size_mb:.2f} MB")
                print(f"         Modified: {modified}")
                
                # Check permissions
                readable = os.access(path, os.R_OK)
                writable = os.access(path, os.W_OK)
                print(f"         Permissions: R={readable}, W={writable}")
                
                # Check product count
                try:
                    conn = sqlite3.connect(path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM products;")
                    count = cursor.fetchone()[0]
                    print(f"         Products: {count}")
                    
                    # Check for Lineage column
                    cursor.execute("PRAGMA table_info(products);")
                    columns = [row[1] for row in cursor.fetchall()]
                    has_lineage = "Lineage" in columns
                    print(f"         Has 'Lineage' column: {has_lineage}")
                    
                    conn.close()
                except Exception as e:
                    print(f"         ❌ Error reading: {e}")
        else:
            print("   ❌ No database files found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 2: Which database does ProductDatabase use?
    print("\n2️⃣  Checking ProductDatabase configuration...")
    try:
        from src.core.data.product_database import ProductDatabase
        db = ProductDatabase()
        print(f"   📁 Database path: {db.db_path}")
        print(f"   📊 Database exists: {os.path.exists(db.db_path) if db.db_path else 'No path set'}")
        
        if db.db_path and os.path.exists(db.db_path):
            # Check permissions
            readable = os.access(db.db_path, os.R_OK)
            writable = os.access(db.db_path, os.W_OK)
            print(f"   🔒 Permissions: Readable={readable}, Writable={writable}")
            
            if not writable:
                print(f"   ⚠️  WARNING: Database is not writable!")
                print(f"   Fix with: chmod 664 {db.db_path}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 3: Test lineage update and retrieval
    print("\n3️⃣  Testing lineage update/retrieval...")
    try:
        from src.core.data.product_database import ProductDatabase
        db = ProductDatabase()
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Get a test product
        cursor.execute('SELECT "Product Name*", "Lineage" FROM products WHERE "Lineage" IS NOT NULL AND "Lineage" != "" LIMIT 1;')
        sample = cursor.fetchone()
        
        if sample:
            product_name, original_lineage = sample
            print(f"   📦 Test product: '{product_name}'")
            print(f"   📊 Current lineage: '{original_lineage}'")
            
            # Try to update
            test_lineage = "TEST_" + datetime.now().strftime('%H%M%S')
            print(f"   🔄 Testing update to: '{test_lineage}'")
            
            success = db.update_product_lineage(product_name, test_lineage)
            if success:
                print(f"   ✅ Update returned success")
                
                # Verify the update
                retrieved = db.get_product_lineage(product_name)
                if retrieved == test_lineage:
                    print(f"   ✅ Update verified: '{retrieved}'")
                else:
                    print(f"   ❌ Update failed to persist")
                    print(f"      Expected: '{test_lineage}'")
                    print(f"      Got: '{retrieved}'")
                
                # Restore original
                db.update_product_lineage(product_name, original_lineage)
                print(f"   ✅ Restored original lineage")
            else:
                print(f"   ❌ Update failed")
        else:
            print(f"   ❌ No products with lineage found")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Check 4: Check app.py configuration
    print("\n4️⃣  Checking app.py lineage override...")
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        checks = [
            ('LINEAGE OVERRIDE: Checking for updated lineage in database', 'Lineage override in /api/generate'),
            ('product_db.get_product_lineage', 'get_product_lineage call'),
            ('product_db.update_product_lineage', 'update_product_lineage call in /api/update-lineage'),
        ]
        
        for check_str, description in checks:
            if check_str in app_content:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description} MISSING!")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 5: Check for database locks
    print("\n5️⃣  Checking for database locks...")
    try:
        db_path = "uploads/product_database.db"
        lock_files = [
            f"{db_path}-shm",
            f"{db_path}-wal",
            f"{db_path}-journal"
        ]
        
        locks_found = []
        for lock_file in lock_files:
            if os.path.exists(lock_file):
                locks_found.append(lock_file)
        
        if locks_found:
            print(f"   ⚠️  Lock files found:")
            for lock in locks_found:
                print(f"      {lock}")
            print(f"   💡 These are normal during database operations")
        else:
            print(f"   ✅ No lock files (database not in use)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 DIAGNOSTIC COMPLETE")
    print("\n🔍 Common issues and fixes:")
    print("\n1. Database not writable:")
    print("   chmod 664 uploads/product_database.db")
    print("\n2. Multiple database files:")
    print("   Make sure ProductDatabase points to the correct file")
    print("\n3. Old code running:")
    print("   Reload web app at pythonanywhere.com/webapps")
    print("\n4. Browser cache:")
    print("   Clear cache with Ctrl+Shift+R or Cmd+Shift+R")
    print("\n5. Session data cached:")
    print("   Clear sessions folder: rm -rf sessions/*")
    print("=" * 70)

if __name__ == "__main__":
    try:
        diagnose_web_lineage()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

