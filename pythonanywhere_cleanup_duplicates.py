#!/usr/bin/env python3
"""
Remove duplicate products from PythonAnywhere web database
Run this script ON PYTHONANYWHERE to clean up duplicates

Usage:
  python pythonanywhere_cleanup_duplicates.py [--dry-run] [--store STORE_NAME]

Options:
  --dry-run    Show what would be deleted without actually deleting
  --store      Specify store name (default: AGT_Bothell)
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
import argparse

def find_database_path(store_name="AGT_Bothell"):
    """Find the database file for the specified store"""
    possible_paths = [
        f"uploads/product_database_{store_name}.db",
        f"product_database_{store_name}.db",
        f"/home/yourusername/AGTDesigner/uploads/product_database_{store_name}.db",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Search in current directory and subdirectories
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.db') and store_name in file:
                return os.path.join(root, file)
    
    return None

def cleanup_duplicates(db_path, dry_run=False):
    """
    Remove duplicate products from database.
    Duplicates are identified by: normalized_name + Vendor + Brand
    Keeps the most recently updated entry.
    """
    
    print("=" * 60)
    print("PYTHONANYWHERE DATABASE DUPLICATE CLEANUP")
    print("=" * 60)
    print(f"\nDatabase: {db_path}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will delete duplicates)'}")
    print()
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    # Get initial database info
    db_size_mb = os.path.getsize(db_path) / 1024 / 1024
    print(f"📊 Database size: {db_size_mb:.2f} MB")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check integrity
        print("\n🔍 Checking database integrity...")
        cursor.execute("PRAGMA integrity_check;")
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result != "ok":
            print(f"❌ Database integrity check failed: {integrity_result}")
            return False
        print("✅ Database integrity OK")
        
        # Get initial product count
        cursor.execute("SELECT COUNT(*) FROM products")
        initial_count = cursor.fetchone()[0]
        print(f"\n📦 Initial product count: {initial_count:,}")
        
        # Check for required columns
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_cols = ['normalized_name', 'Vendor/Supplier*', 'Product Brand', 'updated_at']
        missing_cols = [col for col in required_cols if col not in columns]
        
        if missing_cols:
            print(f"⚠️  Missing columns: {missing_cols}")
            print("Using fallback duplicate detection by Product Name* only...")
            use_fallback = True
        else:
            use_fallback = False
        
        # Create backup before cleanup (unless dry run)
        if not dry_run:
            backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"\n📁 Creating backup: {backup_path}")
            shutil.copy2(db_path, backup_path)
            print(f"✅ Backup created")
        
        print(f"\n🔍 Finding duplicates...")
        
        if use_fallback:
            # Fallback: Use only Product Name*
            cursor.execute('''
                SELECT "Product Name*", COUNT(*) as count
                FROM products
                WHERE "Product Name*" IS NOT NULL AND "Product Name*" != ''
                GROUP BY "Product Name*"
                HAVING count > 1
            ''')
            duplicate_groups = cursor.fetchall()
        else:
            # Primary method: Use normalized_name + vendor + brand
            # Use COALESCE to treat NULL as empty string for grouping
            cursor.execute('''
                SELECT normalized_name, 
                       COALESCE("Vendor/Supplier*", '') as vendor,
                       COALESCE("Product Brand", '') as brand,
                       COUNT(*) as count
                FROM products
                WHERE normalized_name IS NOT NULL AND normalized_name != ''
                GROUP BY normalized_name, vendor, brand
                HAVING count > 1
            ''')
            duplicate_groups = cursor.fetchall()
        
        total_duplicate_groups = len(duplicate_groups)
        print(f"📋 Found {total_duplicate_groups:,} duplicate product groups")
        
        if total_duplicate_groups == 0:
            print("\n✅ No duplicates found! Database is clean.")
            conn.close()
            return True
        
        deleted_count = 0
        kept_count = 0
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Processing duplicates...\n")
        
        for idx, group in enumerate(duplicate_groups, 1):
            if use_fallback:
                product_name, count = group
                
                # Get all entries for this product name
                cursor.execute('''
                    SELECT id, "Product Name*", 
                           COALESCE(updated_at, created_at, '1970-01-01') as last_updated
                    FROM products
                    WHERE "Product Name*" = ?
                    ORDER BY last_updated DESC, id DESC
                ''', (product_name,))
            else:
                norm_name, vendor, brand, count = group
                
                # Get all entries for this duplicate group, ordered by most recent first
                # Use COALESCE to match NULL values correctly
                cursor.execute('''
                    SELECT id, "Product Name*", 
                           COALESCE(updated_at, created_at, '1970-01-01') as last_updated
                    FROM products
                    WHERE normalized_name = ? 
                      AND COALESCE("Vendor/Supplier*", '') = ? 
                      AND COALESCE("Product Brand", '') = ?
                    ORDER BY last_updated DESC, id DESC
                ''', (norm_name, vendor, brand))
            
            entries = cursor.fetchall()
            
            if len(entries) > 1:
                # Keep the first (most recent), delete the rest
                keep_id = entries[0][0]
                keep_name = entries[0][1]
                keep_date = entries[0][2]
                
                ids_to_delete = [entry[0] for entry in entries[1:]]
                
                # Show progress every 10 groups
                if idx % 10 == 0 or idx == 1:
                    print(f"  [{idx}/{total_duplicate_groups}] Processing '{keep_name}'...")
                
                if dry_run:
                    print(f"    [DRY RUN] Would keep: ID {keep_id} (updated: {keep_date})")
                    print(f"    [DRY RUN] Would delete {len(ids_to_delete)} older duplicate(s)")
                else:
                    # Delete older duplicates
                    cursor.executemany('DELETE FROM products WHERE id = ?', 
                                     [(id,) for id in ids_to_delete])
                
                deleted_count += len(ids_to_delete)
                kept_count += 1
        
        if not dry_run:
            conn.commit()
            print(f"\n✅ Changes committed to database")
        
        # Get final product count
        cursor.execute("SELECT COUNT(*) FROM products")
        final_count = cursor.fetchone()[0]
        
        # Summary
        print("\n" + "=" * 60)
        print("CLEANUP SUMMARY")
        print("=" * 60)
        print(f"Initial products:        {initial_count:,}")
        print(f"Duplicate groups found:  {total_duplicate_groups:,}")
        print(f"Products kept:           {kept_count:,}")
        print(f"Duplicates removed:      {deleted_count:,}")
        print(f"Final product count:     {final_count:,}")
        
        if dry_run:
            print(f"\n💡 This was a DRY RUN - no changes were made")
            print(f"   Run without --dry-run to actually remove duplicates")
        else:
            # Vacuum to reclaim space
            print(f"\n🧹 Vacuuming database to reclaim space...")
            cursor.execute("VACUUM")
            conn.commit()
            
            new_size_mb = os.path.getsize(db_path) / 1024 / 1024
            space_saved = db_size_mb - new_size_mb
            print(f"✅ Database vacuumed")
            print(f"📊 New size: {new_size_mb:.2f} MB (saved {space_saved:.2f} MB)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Remove duplicate products from PythonAnywhere database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Dry run to see what would be deleted
  python pythonanywhere_cleanup_duplicates.py --dry-run
  
  # Actually remove duplicates
  python pythonanywhere_cleanup_duplicates.py
  
  # Clean up specific store
  python pythonanywhere_cleanup_duplicates.py --store AGT_Issaquah
        '''
    )
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--store', default='AGT_Bothell',
                       help='Store name (default: AGT_Bothell)')
    
    args = parser.parse_args()
    
    # Find database
    db_path = find_database_path(args.store)
    
    if not db_path:
        print(f"❌ Could not find database for store: {args.store}")
        print(f"\nSearched in:")
        print(f"  - uploads/product_database_{args.store}.db")
        print(f"  - product_database_{args.store}.db")
        print(f"  - Current directory and subdirectories")
        sys.exit(1)
    
    # Run cleanup
    success = cleanup_duplicates(db_path, dry_run=args.dry_run)
    
    if success:
        print(f"\n✅ Cleanup completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Cleanup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
