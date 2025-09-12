#!/usr/bin/env python3
"""
Fix the full database by properly removing the Cost* column
"""

import sqlite3
import os
import shutil

def fix_full_database():
    """Remove Cost* column from the full database safely"""
    
    print("🔧 Fixing full database with proper cost column removal...")
    
    # Backup the full database first
    shutil.copy2('product_database_full.db', 'product_database_full_backup.db')
    print("✅ Created backup of full database")
    
    conn = sqlite3.connect('product_database_full.db')
    cursor = conn.cursor()
    
    try:
        # Check current state
        cursor.execute('SELECT COUNT(*) FROM products')
        total_products = cursor.fetchone()[0]
        print(f"📊 Total products: {total_products}")
        
        # Check if Cost* column exists
        cursor.execute('PRAGMA table_info(products)')
        columns = [col[1] for col in cursor.fetchall()]
        has_cost = 'Cost*' in columns
        print(f"💰 Has Cost* column: {has_cost}")
        
        if not has_cost:
            print("✅ Cost* column already removed")
            return True
        
        # Get all column names except Cost*
        columns_to_keep = [col for col in columns if col != 'Cost*']
        
        # Create new table without Cost* column
        print("🔄 Creating new table without Cost* column...")
        
        # Build column definitions
        column_definitions = []
        for col in columns_to_keep:
            if col == 'id':
                column_definitions.append('"id" INTEGER PRIMARY KEY AUTOINCREMENT')
            else:
                column_definitions.append(f'"{col}" TEXT')
        
        create_sql = f"""
        CREATE TABLE products_new (
            {', '.join(column_definitions)}
        )
        """
        
        cursor.execute(create_sql)
        
        # Copy data from old table to new table (excluding Cost* column)
        print("📋 Copying data to new table...")
        columns_str = ', '.join([f'"{col}"' for col in columns_to_keep])
        cursor.execute(f'INSERT INTO products_new ({columns_str}) SELECT {columns_str} FROM products')
        
        # Drop old table and rename new one
        print("🔄 Replacing old table...")
        cursor.execute('DROP TABLE products')
        cursor.execute('ALTER TABLE products_new RENAME TO products')
        
        # Recreate indexes
        print("🔗 Recreating indexes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_strains_normalized ON strains(normalized_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_normalized ON products(normalized_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_strain ON products(strain_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_vendor_brand ON products("Vendor/Supplier*", "Product Brand")')
        
        conn.commit()
        
        # Verify the fix
        cursor.execute('SELECT COUNT(*) FROM products')
        new_count = cursor.fetchone()[0]
        
        cursor.execute('PRAGMA table_info(products)')
        new_columns = [col[1] for col in cursor.fetchall()]
        cost_removed = 'Cost*' not in new_columns
        
        print(f"✅ Products after fix: {new_count}")
        print(f"✅ Cost* column removed: {cost_removed}")
        
        if new_count == total_products and cost_removed:
            print("🎉 Database fix successful!")
            return True
        else:
            print("❌ Database fix failed")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_full_database()
    if success:
        print("\n✅ Full database fixed and ready!")
    else:
        print("\n❌ Database fix failed")
