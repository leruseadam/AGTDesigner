#!/usr/bin/env python3
"""
Check all store databases to find which one has products
Run this on PythonAnywhere to see which database to use
"""

import os
import sqlite3
from datetime import datetime

def check_all_databases():
    """Check all database files and show their details."""
    
    print("=" * 80)
    print("CHECKING ALL STORE DATABASES")
    print("=" * 80)
    
    db_files = []
    
    # Search in uploads directory
    if os.path.exists('uploads'):
        for file in sorted(os.listdir('uploads')):
            if file.endswith('.db') and not file.endswith('-shm') and not file.endswith('-wal'):
                full_path = os.path.join('uploads', file)
                try:
                    size = os.path.getsize(full_path)
                    size_mb = size / (1024 * 1024)
                    modified = datetime.fromtimestamp(os.path.getmtime(full_path))
                    
                    # Get product count
                    conn = sqlite3.connect(full_path)
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute("SELECT COUNT(*) FROM products;")
                        product_count = cursor.fetchone()[0]
                    except:
                        product_count = 0
                    
                    # Check for Lineage column
                    try:
                        cursor.execute("PRAGMA table_info(products);")
                        columns = [row[1] for row in cursor.fetchall()]
                        has_lineage = "Lineage" in columns
                    except:
                        has_lineage = False
                    
                    # Get a sample product name if products exist
                    sample_name = "N/A"
                    if product_count > 0:
                        try:
                            cursor.execute('SELECT "Product Name*" FROM products LIMIT 1;')
                            sample = cursor.fetchone()
                            sample_name = sample[0] if sample else "N/A"
                        except:
                            pass
                    
                    conn.close()
                    
                    db_files.append({
                        'filename': file,
                        'path': full_path,
                        'size_mb': size_mb,
                        'modified': modified,
                        'product_count': product_count,
                        'has_lineage': has_lineage,
                        'sample_product': sample_name
                    })
                except Exception as e:
                    print(f"⚠️  Error reading {file}: {e}")
    
    if not db_files:
        print("\n❌ No database files found in uploads/")
        return None
    
    # Display all databases
    print(f"\n📊 Found {len(db_files)} database file(s):\n")
    
    databases_with_products = []
    
    for db in db_files:
        status = "✅" if db['product_count'] > 0 else "❌"
        print(f"{status} {db['filename']}")
        print(f"   Size: {db['size_mb']:.2f} MB")
        print(f"   Products: {db['product_count']:,}")
        print(f"   Has Lineage: {db['has_lineage']}")
        print(f"   Modified: {db['modified']}")
        if db['product_count'] > 0:
            print(f"   Sample: {db['sample_product'][:60]}")
            databases_with_products.append(db)
        print()
    
    return databases_with_products

def recommend_database(databases_with_products):
    """Recommend which database to use."""
    
    print("=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    
    if not databases_with_products:
        print("\n❌ No databases with products found!")
        print("\n💡 You may need to:")
        print("   1. Upload an Excel file to populate the database")
        print("   2. Check if you're in the right directory")
        print("   3. Restore from a backup")
        return None
    
    # Find database with most products
    best_db = max(databases_with_products, key=lambda x: x['product_count'])
    
    print(f"\n🎯 RECOMMENDED DATABASE: {best_db['filename']}")
    print(f"   Products: {best_db['product_count']:,}")
    print(f"   Size: {best_db['size_mb']:.2f} MB")
    print(f"   Modified: {best_db['modified']}")
    print(f"   Has Lineage Column: {best_db['has_lineage']}")
    
    return best_db

def show_fix_command(recommended_db):
    """Show the command to fix the database."""
    
    if not recommended_db:
        return
    
    print("\n" + "=" * 80)
    print("HOW TO FIX")
    print("=" * 80)
    
    source = recommended_db['path']
    target = "uploads/product_database.db"
    
    print(f"\nRun this command to use {recommended_db['filename']}:")
    print(f"\n   cp {source} {target}")
    print(f"\nOr use the automated script:")
    print(f"\n   bash fix_database.sh {recommended_db['filename']}")
    
    print("\nAfter copying:")
    print("1. Reload web app: https://www.pythonanywhere.com/user/adamcordova/webapps/")
    print("2. Clear browser cache: Ctrl+Shift+R or Cmd+Shift+R")
    print("3. Test lineage changes")
    
    print("\n" + "=" * 80)

def main():
    """Main function."""
    
    # Check current ProductDatabase configuration
    print("\n📁 Current ProductDatabase configuration:")
    try:
        from src.core.data.product_database import ProductDatabase
        db = ProductDatabase()
        print(f"   Using: {db.db_path}")
        
        if db.db_path and os.path.exists(db.db_path):
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products;")
            count = cursor.fetchone()[0]
            print(f"   Products: {count:,}")
            conn.close()
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    print()
    
    # Check all databases
    databases_with_products = check_all_databases()
    
    # Recommend the best one
    recommended = recommend_database(databases_with_products)
    
    # Show how to fix
    show_fix_command(recommended)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

