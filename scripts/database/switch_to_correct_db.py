#!/usr/bin/env python3
"""
Switch ProductDatabase to use the correct database file
Run this on PythonAnywhere to see all databases and switch to the right one
"""

import os
import sqlite3
from datetime import datetime

def find_all_databases():
    """Find all database files and show their details."""
    
    print("=" * 70)
    print("FINDING ALL DATABASE FILES")
    print("=" * 70)
    
    db_files = []
    
    # Search in uploads directory
    if os.path.exists('uploads'):
        for file in os.listdir('uploads'):
            if file.endswith('.db') and not file.endswith('-shm') and not file.endswith('-wal'):
                full_path = os.path.join('uploads', file)
                try:
                    size = os.path.getsize(full_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                    
                    # Get product count
                    conn = sqlite3.connect(full_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM products;")
                    product_count = cursor.fetchone()[0]
                    
                    # Check for Lineage column
                    cursor.execute("PRAGMA table_info(products);")
                    columns = [row[1] for row in cursor.fetchall()]
                    has_lineage = "Lineage" in columns
                    
                    # Get a sample product name
                    cursor.execute('SELECT "Product Name*" FROM products LIMIT 1;')
                    sample = cursor.fetchone()
                    sample_name = sample[0] if sample else "N/A"
                    
                    conn.close()
                    
                    db_files.append({
                        'path': full_path,
                        'filename': file,
                        'size_mb': size / (1024 * 1024),
                        'modified': modified,
                        'product_count': product_count,
                        'has_lineage': has_lineage,
                        'sample_product': sample_name
                    })
                except Exception as e:
                    print(f"⚠️  Error reading {file}: {e}")
    
    if not db_files:
        print("❌ No database files found in uploads/")
        return None
    
    # Sort by modification time (most recent first)
    db_files.sort(key=lambda x: x['modified'], reverse=True)
    
    # Display all databases
    print(f"\n📊 Found {len(db_files)} database file(s):\n")
    
    for i, db in enumerate(db_files, 1):
        print(f"{i}. {db['filename']}")
        print(f"   Path: {db['path']}")
        print(f"   Size: {db['size_mb']:.2f} MB")
        print(f"   Modified: {db['modified']}")
        print(f"   Products: {db['product_count']:,}")
        print(f"   Has Lineage Column: {db['has_lineage']}")
        print(f"   Sample Product: {db['sample_product'][:50]}...")
        print()
    
    return db_files

def show_current_config():
    """Show which database ProductDatabase is currently using."""
    
    print("=" * 70)
    print("CURRENT PRODUCTDATABASE CONFIGURATION")
    print("=" * 70)
    
    try:
        from src.core.data.product_database import ProductDatabase
        db = ProductDatabase()
        print(f"\n📁 Currently using: {db.db_path}")
        print(f"📊 Database exists: {os.path.exists(db.db_path) if db.db_path else 'No path set'}")
        
        if db.db_path and os.path.exists(db.db_path):
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products;")
            count = cursor.fetchone()[0]
            print(f"📦 Products in current DB: {count:,}")
            conn.close()
        
        print()
    except Exception as e:
        print(f"❌ Error: {e}\n")

def suggest_correct_database(db_files):
    """Suggest which database is probably the correct one."""
    
    print("=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    
    # Criteria for "correct" database:
    # 1. Most products
    # 2. Most recently modified
    # 3. Has Lineage column
    
    # Find database with most products
    most_products = max(db_files, key=lambda x: x['product_count'])
    
    # Find most recently modified
    most_recent = db_files[0]  # Already sorted by modification time
    
    print(f"\n🎯 Recommended database: {most_products['filename']}")
    print(f"   Reason: Has the most products ({most_products['product_count']:,})")
    print(f"   Last modified: {most_products['modified']}")
    print(f"   Has Lineage column: {most_products['has_lineage']}")
    
    if most_products['filename'] != most_recent['filename']:
        print(f"\n💡 Note: Most recently modified is '{most_recent['filename']}'")
        print(f"   (modified {most_recent['modified']})")
    
    return most_products

def main():
    """Main function."""
    
    # Show current configuration
    show_current_config()
    
    # Find all databases
    db_files = find_all_databases()
    
    if not db_files:
        return
    
    # Suggest correct database
    recommended = suggest_correct_database(db_files)
    
    # Show how to fix
    print("\n" + "=" * 70)
    print("HOW TO FIX")
    print("=" * 70)
    
    current_db = "uploads/product_database.db"
    recommended_db = recommended['path']
    
    if current_db == recommended_db:
        print("\n✅ ProductDatabase is already using the correct file!")
        print("   The lineage changes should work.")
        print("\n🔍 If lineage changes still don't work:")
        print("   1. Reload web app: https://www.pythonanywhere.com/user/adamcordova/webapps/")
        print("   2. Clear browser cache: Ctrl+Shift+R or Cmd+Shift+R")
        print("   3. Check server logs for errors")
    else:
        print(f"\n⚠️  ProductDatabase is using the WRONG file!")
        print(f"   Current:     {current_db}")
        print(f"   Should use:  {recommended_db}")
        print(f"\n🔧 To fix, you have two options:")
        print(f"\nOption 1: Copy the correct database to product_database.db")
        print(f"   cp {recommended_db} {current_db}")
        print(f"   (This will replace the current database)")
        print(f"\nOption 2: Rename files to make the correct one be used")
        print(f"   mv {current_db} {current_db}.old")
        print(f"   cp {recommended_db} {current_db}")
        print(f"   (This keeps a backup of the old database)")
        print(f"\n⚠️  After copying:")
        print(f"   1. Reload web app")
        print(f"   2. Test lineage changes")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

