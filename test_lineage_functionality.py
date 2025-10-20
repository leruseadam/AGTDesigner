#!/usr/bin/env python3
"""
Test lineage functionality on PythonAnywhere
Run this script ON PYTHONANYWHERE to test lineage changes
"""

import os
import sys
import sqlite3
from datetime import datetime

def test_lineage_functionality():
    """Test if lineage functionality is working properly."""
    
    print("=======================================")
    print("TESTING LINEAGE FUNCTIONALITY")
    print("=======================================")
    
    db_path = "uploads/product_database_AGT_Bothell.db"
    
    if not os.path.exists(db_path):
        print("❌ No database file found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Check if database has products
        cursor.execute("SELECT COUNT(*) FROM products;")
        product_count = cursor.fetchone()[0]
        print(f"📦 Products in database: {product_count}")
        
        if product_count == 0:
            print("⚠️  Database is empty - lineage changes won't work without products")
            return False
        
        # Test 2: Check if lineage column exists
        cursor.execute("PRAGMA table_info(products);")
        columns = cursor.fetchall()
        lineage_columns = [col for col in columns if 'lineage' in col[1].lower()]
        
        if lineage_columns:
            print(f"✅ Lineage columns found: {[col[1] for col in lineage_columns]}")
        else:
            print("❌ No lineage columns found in products table")
            return False
        
        # Test 3: Check for products with lineage data
        cursor.execute('SELECT COUNT(*) FROM products WHERE "Lineage" IS NOT NULL AND "Lineage" != "";')
        lineage_count = cursor.fetchone()[0]
        print(f"📊 Products with lineage data: {lineage_count}")
        
        # Test 4: Test lineage update functionality
        print("\n🧪 Testing lineage update functionality...")
        
        # Get a sample product
        cursor.execute('SELECT "Product Name*", "Lineage" FROM products LIMIT 1;')
        sample = cursor.fetchone()
        
        if sample:
            product_name, current_lineage = sample
            print(f"   Sample product: '{product_name}'")
            print(f"   Current lineage: '{current_lineage}'")
            
            # Test updating lineage
            test_lineage = "TEST_LINEAGE"
            cursor.execute('UPDATE products SET "Lineage" = ? WHERE "Product Name*" = ?;', (test_lineage, product_name))
            conn.commit()
            
            # Verify update
            cursor.execute('SELECT "Lineage" FROM products WHERE "Product Name*" = ?;', (product_name,))
            updated_lineage = cursor.fetchone()[0]
            
            if updated_lineage == test_lineage:
                print(f"   ✅ Lineage update test passed: '{updated_lineage}'")
                
                # Restore original lineage
                cursor.execute('UPDATE products SET "Lineage" = ? WHERE "Product Name*" = ?;', (current_lineage, product_name))
                conn.commit()
                print(f"   ✅ Original lineage restored: '{current_lineage}'")
            else:
                print(f"   ❌ Lineage update test failed: expected '{test_lineage}', got '{updated_lineage}'")
                return False
        else:
            print("   ❌ No products found to test lineage update")
            return False
        
        # Test 5: Check if ProductDatabase methods exist
        print("\n🔍 Testing ProductDatabase methods...")
        try:
            from src.core.data.product_database import ProductDatabase
            db = ProductDatabase()
            
            print(f"   ✅ ProductDatabase imported successfully")
            print(f"   ✅ get_product_lineage method: {hasattr(db, 'get_product_lineage')}")
            print(f"   ✅ update_product_lineage method: {hasattr(db, 'update_product_lineage')}")
            
            # Test get_product_lineage method
            if hasattr(db, 'get_product_lineage') and sample:
                lineage = db.get_product_lineage(product_name)
                print(f"   ✅ get_product_lineage test: '{lineage}' for '{product_name}'")
            
        except Exception as e:
            print(f"   ❌ ProductDatabase import failed: {e}")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing lineage functionality: {e}")
        return False

def check_web_app_status():
    """Check if the web app is running and accessible."""
    
    print("\n🌐 Checking web app status...")
    
    # Check if the app.py file exists and has the lineage fix
    app_py_path = "app.py"
    if os.path.exists(app_py_path):
        with open(app_py_path, 'r') as f:
            content = f.read()
            
        if 'get_product_lineage' in content and 'LINEAGE OVERRIDE' in content:
            print("   ✅ app.py contains lineage fix")
        else:
            print("   ❌ app.py missing lineage fix")
            return False
    else:
        print("   ❌ app.py not found")
        return False
    
    # Check if the product_database.py has the new method
    db_py_path = "src/core/data/product_database.py"
    if os.path.exists(db_py_path):
        with open(db_py_path, 'r') as f:
            content = f.read()
            
        if 'def get_product_lineage' in content:
            print("   ✅ product_database.py contains get_product_lineage method")
        else:
            print("   ❌ product_database.py missing get_product_lineage method")
            return False
    else:
        print("   ❌ product_database.py not found")
        return False
    
    return True

def main():
    """Main test function."""
    
    print("🚀 Starting lineage functionality test...")
    
    if not os.path.exists("uploads"):
        print("❌ Not in the correct directory. Please run from the AGTDesigner directory.")
        return False
    
    # Test database functionality
    db_success = test_lineage_functionality()
    
    # Test web app status
    app_success = check_web_app_status()
    
    print(f"\n📊 Test Results:")
    print(f"   Database functionality: {'✅ PASSED' if db_success else '❌ FAILED'}")
    print(f"   Web app status: {'✅ PASSED' if app_success else '❌ FAILED'}")
    
    if db_success and app_success:
        print(f"\n🎉 ALL TESTS PASSED! Lineage functionality should work.")
        print(f"\nNext steps:")
        print(f"1. Go to PythonAnywhere Web tab")
        print(f"2. Click 'Reload www.agtpricetags.com'")
        print(f"3. Test lineage changes in the web interface")
    else:
        print(f"\n⚠️  Some tests failed. Lineage functionality may not work properly.")
        print(f"\nTroubleshooting:")
        if not db_success:
            print(f"- Check database file and permissions")
            print(f"- Ensure database has products")
        if not app_success:
            print(f"- Check if latest code is deployed")
            print(f"- Verify lineage fix is in the code")
    
    return db_success and app_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
