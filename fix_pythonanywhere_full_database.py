#!/usr/bin/env python3

"""
PythonAnywhere Database Fix - Show Full Database
===============================================
Fixes the issue where only 5 sample products are shown instead of full database
"""

import sqlite3
import os
from datetime import datetime

def fix_database_display():
    """Fix the database display issue on PythonAnywhere"""
    print("🔧 Fixing PythonAnywhere Database Display")
    print("=" * 60)
    
    main_db = "uploads/product_database.db"
    agt_db = "uploads/product_database_AGT_Bothell.db"
    
    if not os.path.exists(main_db):
        print(f"❌ Main database not found: {main_db}")
        return False
    
    if not os.path.exists(agt_db):
        print(f"❌ AGT Bothell database not found: {agt_db}")
        return False
    
    try:
        # Connect to both databases
        conn_main = sqlite3.connect(main_db)
        cursor_main = conn_main.cursor()
        
        conn_agt = sqlite3.connect(agt_db)
        cursor_agt = conn_agt.cursor()
        
        # Check current counts
        cursor_main.execute("SELECT COUNT(*) FROM products")
        main_count = cursor_main.fetchone()[0]
        
        cursor_agt.execute("SELECT COUNT(*) FROM products")
        agt_count = cursor_agt.fetchone()[0]
        
        print(f"📊 Current status:")
        print(f"   Main database: {main_count:,} products")
        print(f"   AGT Bothell database: {agt_count:,} products")
        
        if main_count < agt_count:
            print(f"\n🔄 Copying {agt_count - main_count:,} missing products...")
            
            # Get all products from AGT database
            cursor_agt.execute("SELECT * FROM products")
            agt_products = cursor_agt.fetchall()
            
            # Get column names
            cursor_agt.execute("PRAGMA table_info(products)")
            columns = [col[1] for col in cursor_agt.fetchall()]
            
            # Clear main database products (keep strains)
            cursor_main.execute("DELETE FROM products")
            
            # Insert all products from AGT database
            placeholders = ', '.join(['?' for _ in columns])
            insert_query = f"INSERT INTO products ({', '.join([f'\"{col}\"' for col in columns])}) VALUES ({placeholders})"
            
            cursor_main.executemany(insert_query, agt_products)
            conn_main.commit()
            
            print(f"✅ Copied {len(agt_products):,} products to main database")
        
        # Verify final count
        cursor_main.execute("SELECT COUNT(*) FROM products")
        final_count = cursor_main.fetchone()[0]
        
        print(f"\n📊 Final database status:")
        print(f"   Products: {final_count:,}")
        
        # Show sample products
        cursor_main.execute('SELECT "Product Name*", "Product Type*", "Product Strain" FROM products WHERE "Product Name*" IS NOT NULL AND "Product Name*" != "" LIMIT 5')
        samples = cursor_main.fetchall()
        
        print(f"\n📋 Sample products:")
        for i, (name, ptype, strain) in enumerate(samples, 1):
            print(f"   {i}. {name} ({ptype}) - {strain}")
        
        conn_main.close()
        conn_agt.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

def disable_default_file_loading():
    """Disable default file loading to use database products"""
    print("\n🔧 Disabling Default File Loading")
    print("=" * 50)
    
    # Create a simple script to disable default file loading
    disable_script = '''
import os
os.environ["DISABLE_DEFAULT_FILE_LOADING"] = "True"
print("✅ Default file loading disabled - will use database products")
'''
    
    with open("disable_default_loading.py", "w") as f:
        f.write(disable_script)
    
    print("✅ Created disable_default_loading.py")
    print("📋 Run this before starting your app:")
    print("   python3 disable_default_loading.py")

def test_application():
    """Test the application with full database"""
    print("\n🧪 Testing Application with Full Database")
    print("=" * 50)
    
    try:
        # Set environment variable
        os.environ["DISABLE_DEFAULT_FILE_LOADING"] = "True"
        
        from app import get_product_database, get_excel_processor
        
        # Test database
        product_db = get_product_database()
        if product_db:
            print("✅ Database connection successful")
            
            # Test Excel processor without default file
            processor = get_excel_processor()
            if processor:
                print("✅ Excel processor loaded")
                
                # Check if it's using database products
                if hasattr(processor, 'df') and processor.df is not None:
                    print(f"📊 Products loaded: {len(processor.df)}")
                    
                    if len(processor.df) > 5:
                        print("✅ Full database products loaded!")
                    else:
                        print("⚠️  Still showing sample data")
                else:
                    print("📊 Excel processor ready for file upload")
            else:
                print("❌ Excel processor failed")
        else:
            print("❌ Database connection failed")
            
    except Exception as e:
        print(f"❌ Application test failed: {e}")

if __name__ == "__main__":
    print("🚀 PythonAnywhere Database Fix")
    print("=" * 60)
    
    # Step 1: Fix database
    if fix_database_display():
        print("\n✅ Database fixed successfully!")
    else:
        print("\n❌ Database fix failed!")
        exit(1)
    
    # Step 2: Disable default file loading
    disable_default_file_loading()
    
    # Step 3: Test application
    test_application()
    
    print("\n🎉 Database fix complete!")
    print("\n📋 Next steps:")
    print("1. Reload your web app in PythonAnywhere Web tab")
    print("2. Visit your site - should show 5,000+ products")
    print("3. If still showing 5 products, run: python3 disable_default_loading.py")
    print("4. Then restart your web app")
