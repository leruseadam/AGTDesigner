#!/usr/bin/env python3
"""
Migration script to add Weight* to the products UNIQUE constraint.

This fixes the bug where products with the same name/vendor/brand but different
weights were being rejected as duplicates during Excel import.

BEFORE: UNIQUE(Product Name*, Vendor/Supplier*, Product Brand)
AFTER:  UNIQUE(Product Name*, Vendor/Supplier*, Product Brand, Weight*)
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def migrate_database(db_path):
    """Migrate a single database to add Weight* to UNIQUE constraint."""
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

        # Get current count
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"📊 Current products: {product_count}")

        # Check current constraints
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='products'")
        current_schema = cursor.fetchone()[0]

        if 'UNIQUE("Product Name*", "Vendor/Supplier*", "Product Brand", "Weight*")' in current_schema:
            print("✅ Database already has correct UNIQUE constraint - no migration needed")
            conn.close()
            return True

        print("🔄 Backing up products table...")

        # Create backup table
        cursor.execute("DROP TABLE IF EXISTS products_backup")
        cursor.execute("CREATE TABLE products_backup AS SELECT * FROM products")

        backup_count = cursor.execute("SELECT COUNT(*) FROM products_backup").fetchone()[0]
        print(f"✅ Backed up {backup_count} products")

        # Drop the old products table
        print("🔄 Dropping old products table...")
        cursor.execute("DROP TABLE products")

        # Recreate products table with new UNIQUE constraint
        print("🔄 Creating new products table with correct UNIQUE constraint...")
        cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                "Product Name*" TEXT,
                "Product Type" TEXT,
                "Product Brand" TEXT,
                "Vendor/Supplier*" TEXT,
                "Weight*" TEXT,
                "Weight Unit*" TEXT,
                "Price*" TEXT,
                "Quantity*" TEXT,
                "Ratio" TEXT,
                "Lineage" TEXT,
                "Product Strain" TEXT,
                normalized_name TEXT,
                "last_seen_date" TEXT,
                strain_id INTEGER,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (strain_id) REFERENCES strains (id),
                UNIQUE("Product Name*", "Vendor/Supplier*", "Product Brand", "Weight*")
            )
        ''')

        # Restore data from backup
        print("🔄 Restoring products from backup...")
        cursor.execute('''
            INSERT INTO products
            SELECT * FROM products_backup
        ''')

        restored_count = cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        print(f"✅ Restored {restored_count} products")

        if restored_count != backup_count:
            print(f"⚠️  WARNING: Count mismatch! Backup: {backup_count}, Restored: {restored_count}")
            print(f"           This means some products were duplicates with different weights")
            print(f"           and couldn't be restored due to the old UNIQUE constraint.")

        # Drop backup table
        cursor.execute("DROP TABLE products_backup")

        conn.commit()
        conn.close()

        print("✅ Migration complete!")
        return True

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
    print(f"UNIQUE CONSTRAINT MIGRATION")
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
        print("\n⚠️  IMPORTANT: Re-upload your Excel file to restore missing products")
        print("   (Products with same name/vendor/brand but different weights were")
        print("    rejected by the old UNIQUE constraint and need to be re-imported)")
    else:
        print("⚠️  Some databases failed to migrate - check errors above")

if __name__ == '__main__':
    main()
