#!/usr/bin/env python3
"""
Migration script to add sovereign_lineage column to products table.

This enables lineage edits to persist for products without strain associations.
Products with manual lineage changes will store them in sovereign_lineage,
which won't be overwritten by Excel uploads.
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def migrate_database(db_path):
    """Add sovereign_lineage column to products table in a single database."""
    print(f"\n{'='*80}")
    print(f"Migrating: {db_path}")
    print(f"{'='*80}")

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if products table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        if not cursor.fetchone():
            print("⚠️  No products table found - skipping")
            conn.close()
            return True

        # Check if sovereign_lineage column already exists
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'sovereign_lineage' in column_names:
            print("✅ sovereign_lineage column already exists - no migration needed")
            conn.close()
            return True

        # Get current product count
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"📊 Current products: {product_count}")

        # Add the column
        print("🔄 Adding sovereign_lineage column to products table...")
        cursor.execute("ALTER TABLE products ADD COLUMN sovereign_lineage TEXT")

        # Verify the column was added
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'sovereign_lineage' in column_names:
            print("✅ sovereign_lineage column added successfully")
            conn.commit()
            conn.close()
            return True
        else:
            print("❌ Failed to add sovereign_lineage column")
            conn.close()
            return False

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False

def main():
    """Migrate all store databases."""
    uploads_dir = Path(__file__).parent.parent.parent / 'uploads'

    if not uploads_dir.exists():
        print(f"❌ Uploads directory not found: {uploads_dir}")
        return

    # Find all database files
    db_files = list(uploads_dir.glob('product_database*.db'))

    if not db_files:
        print("❌ No database files found in uploads directory")
        return

    print(f"\n{'='*80}")
    print(f"ADD SOVEREIGN_LINEAGE COLUMN MIGRATION")
    print(f"{'='*80}")
    print(f"Found {len(db_files)} database(s) to migrate:")
    for db_file in db_files:
        print(f"  - {db_file.name}")
    print()

    # Migrate each database
    success_count = 0
    for db_file in db_files:
        if migrate_database(str(db_file)):
            success_count += 1

    print(f"\n{'='*80}")
    print(f"MIGRATION SUMMARY")
    print(f"{'='*80}")
    print(f"Total databases: {len(db_files)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(db_files) - success_count}")
    print()

    if success_count == len(db_files):
        print("✅ All databases migrated successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart your Flask application")
        print("   2. Edit lineage for any product")
        print("   3. Changes will now persist in sovereign_lineage column")
        print("   4. Excel uploads will not overwrite sovereign_lineage")
    else:
        print("⚠️  Some databases failed to migrate - check errors above")

if __name__ == '__main__':
    main()
