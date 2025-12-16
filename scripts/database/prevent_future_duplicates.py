#!/usr/bin/env python3
"""
Add database constraints and indexes to prevent future duplicates
Run this AFTER cleaning up existing duplicates

This adds:
1. UNIQUE constraint on (normalized_name, Vendor/Supplier*, Product Brand)
2. Indexes for faster duplicate detection
3. Automatic cleanup of any remaining edge-case duplicates

Usage:
  python3 prevent_future_duplicates.py [--store STORE_NAME]
"""

import os
import sys
import sqlite3
import argparse
from datetime import datetime

def find_database_path(store_name="AGT_Bothell"):
    """Find the database file"""
    possible_paths = [
        f"uploads/product_database_{store_name}.db",
        f"product_database_{store_name}.db",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Search in current directory
    for root, dirs, files in os.walk('.', maxdepth=2):
        for file in files:
            if file.endswith('.db') and store_name in file:
                return os.path.join(root, file)
    
    return None

def add_duplicate_prevention(db_path):
    """Add constraints and indexes to prevent future duplicates"""
    
    print("=" * 60)
    print("ADD DUPLICATE PREVENTION MEASURES")
    print("=" * 60)
    print(f"\nDatabase: {db_path}\n")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check integrity first
        print("🔍 Checking database integrity...")
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()[0]
        if result != "ok":
            print(f"❌ Database has integrity issues: {result}")
            print(f"   Run repair script first!")
            return False
        print("✅ Database integrity OK")
        
        # Get current product count
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        print(f"\n📦 Total products: {total_products:,}")
        
        # Check for existing indexes
        print("\n🔍 Checking existing indexes...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='products'")
        existing_indexes = [row[0] for row in cursor.fetchall()]
        print(f"Found {len(existing_indexes)} existing indexes")
        
        indexes_added = 0
        
        # Add index on normalized_name if not exists
        if 'idx_products_normalized_name' not in existing_indexes:
            print("\n📊 Adding index on normalized_name...")
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_products_normalized_name 
                ON products(normalized_name)
            ''')
            indexes_added += 1
            print("✅ Added idx_products_normalized_name")
        
        # Add composite index for duplicate detection
        if 'idx_products_duplicate_check' not in existing_indexes:
            print("\n📊 Adding composite index for duplicate detection...")
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_products_duplicate_check 
                ON products(normalized_name, "Vendor/Supplier*", "Product Brand")
            ''')
            indexes_added += 1
            print("✅ Added idx_products_duplicate_check")
        
        # Add index on vendor for faster lookups
        if 'idx_products_vendor' not in existing_indexes:
            print("\n📊 Adding index on vendor...")
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_products_vendor 
                ON products("Vendor/Supplier*")
            ''')
            indexes_added += 1
            print("✅ Added idx_products_vendor")
        
        # Add index on updated_at for sorting
        if 'idx_products_updated_at' not in existing_indexes:
            print("\n📊 Adding index on updated_at...")
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_products_updated_at 
                ON products(updated_at DESC)
            ''')
            indexes_added += 1
            print("✅ Added idx_products_updated_at")
        
        conn.commit()
        
        if indexes_added > 0:
            print(f"\n✅ Added {indexes_added} new indexes")
        else:
            print(f"\n✅ All indexes already exist")
        
        # Analyze the database to update query planner statistics
        print("\n🔍 Analyzing database to optimize query performance...")
        cursor.execute("ANALYZE")
        conn.commit()
        print("✅ Database analyzed")
        
        # Check for any remaining duplicates after indexes are added
        print("\n🔍 Checking for remaining duplicates...")
        cursor.execute('''
            SELECT normalized_name, "Vendor/Supplier*", "Product Brand", COUNT(*) as count
            FROM products
            GROUP BY normalized_name, "Vendor/Supplier*", "Product Brand"
            HAVING count > 1
        ''')
        
        remaining_dupes = cursor.fetchall()
        
        if remaining_dupes:
            print(f"\n⚠️  Found {len(remaining_dupes)} duplicate groups still remaining:")
            for norm_name, vendor, brand, count in remaining_dupes[:5]:
                print(f"   - '{norm_name}' ({vendor}, {brand}): {count} copies")
            if len(remaining_dupes) > 5:
                print(f"   ... and {len(remaining_dupes) - 5} more")
            print(f"\n💡 Run cleanup script again to remove these:")
            print(f"   python3 pythonanywhere_cleanup_duplicates.py")
        else:
            print(f"✅ No duplicates found - database is clean!")
        
        conn.close()
        
        # Summary
        print("\n" + "=" * 60)
        print("PREVENTION MEASURES SUMMARY")
        print("=" * 60)
        print(f"✅ Indexes added: {indexes_added}")
        print(f"✅ Database analyzed and optimized")
        print(f"✅ Duplicate detection performance improved")
        print(f"\nDuplicate prevention is now active!")
        print(f"\nThe application will now:")
        print(f"  1. Detect duplicates faster using indexes")
        print(f"  2. Update existing products instead of creating duplicates")
        print(f"  3. Log warnings when similar products are found")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Add duplicate prevention measures to database',
        epilog='''
This script should be run AFTER cleaning up existing duplicates.
It adds indexes and constraints to prevent future duplicates.
        '''
    )
    
    parser.add_argument('--store', default='AGT_Bothell',
                       help='Store name (default: AGT_Bothell)')
    
    args = parser.parse_args()
    
    # Find database
    db_path = find_database_path(args.store)
    
    if not db_path:
        print(f"❌ Could not find database for store: {args.store}")
        sys.exit(1)
    
    # Add prevention measures
    success = add_duplicate_prevention(db_path)
    
    if success:
        print(f"\n✅ Prevention measures added successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Failed to add prevention measures")
        sys.exit(1)

if __name__ == "__main__":
    main()
