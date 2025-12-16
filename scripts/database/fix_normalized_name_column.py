#!/usr/bin/env python3
"""
Fix the normalized_name column issue in the database
This adds the missing column that ProductDatabase expects
"""

import sqlite3
import os
import sys

def fix_normalized_name_column(db_path):
    """Add normalized_name column and populate it."""
    
    print(f"🔧 Fixing normalized_name column in: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(products);")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'normalized_name' in columns:
            print(f"✅ normalized_name column already exists")
        else:
            print(f"📝 Adding normalized_name column...")
            cursor.execute('ALTER TABLE products ADD COLUMN normalized_name TEXT;')
            print(f"✅ Column added")
        
        # Check how many rows need updating
        cursor.execute("SELECT COUNT(*) FROM products WHERE normalized_name IS NULL;")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            print(f"📊 Populating normalized_name for {null_count:,} products...")
            
            # Populate normalized_name from Product Name*
            cursor.execute('''
                UPDATE products 
                SET normalized_name = LOWER(TRIM("Product Name*")) 
                WHERE normalized_name IS NULL AND "Product Name*" IS NOT NULL;
            ''')
            
            updated = cursor.rowcount
            print(f"✅ Updated {updated:,} products")
        else:
            print(f"✅ All products already have normalized_name")
        
        # Create index for performance
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_normalized_name';")
        if cursor.fetchone():
            print(f"✅ Index already exists")
        else:
            print(f"📝 Creating index on normalized_name...")
            cursor.execute('CREATE INDEX idx_normalized_name ON products(normalized_name);')
            print(f"✅ Index created")
        
        conn.commit()
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM products WHERE normalized_name IS NOT NULL;")
        populated_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products;")
        total_count = cursor.fetchone()[0]
        
        print(f"\n📊 Verification:")
        print(f"   Total products: {total_count:,}")
        print(f"   With normalized_name: {populated_count:,}")
        
        if populated_count == total_count:
            print(f"   ✅ All products have normalized_name!")
        else:
            print(f"   ⚠️  {total_count - populated_count} products still missing normalized_name")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fix all database files."""
    
    print("=" * 80)
    print("FIXING NORMALIZED_NAME COLUMN IN ALL DATABASES")
    print("=" * 80)
    
    databases_to_fix = [
        "uploads/product_database.db",
        "uploads/product_database_AGT_Bothell.db"
    ]
    
    results = []
    
    for db_path in databases_to_fix:
        print(f"\n{'='*80}")
        if os.path.exists(db_path):
            success = fix_normalized_name_column(db_path)
            results.append((db_path, success))
        else:
            print(f"⚠️  Skipping {db_path} (not found)")
            results.append((db_path, None))
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    for db_path, result in results:
        if result is None:
            status = "⚠️  NOT FOUND"
        elif result:
            status = "✅ FIXED"
        else:
            status = "❌ FAILED"
        print(f"{status}: {db_path}")
    
    all_fixed = all(result for _, result in results if result is not None)
    
    if all_fixed:
        print(f"\n✅ ALL DATABASES FIXED!")
        print(f"\n📋 Next steps:")
        print(f"1. Reload web app: https://www.pythonanywhere.com/user/adamcordova/webapps/")
        print(f"2. Test Excel upload - should work now")
        print(f"3. Test lineage changes - should persist now")
        print(f"4. Check logs - should have fewer errors")
    else:
        print(f"\n⚠️  Some databases had issues - check errors above")
    
    print(f"{'='*80}")
    
    return all_fixed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

