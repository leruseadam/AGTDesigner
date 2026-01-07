#!/usr/bin/env python3
"""
Fix normalized_product_strain column for lineage lookup in all databases.

This script:
1. Adds the normalized_product_strain column if missing
2. Populates it with normalized Product Strain values
3. Creates an index for fast lookups
4. Verifies the fix by testing lineage queries

Usage:
    python3 scripts/database/fix_normalized_product_strain.py
"""

import sqlite3
import os
import sys
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def normalize_strain_name(strain_name):
    """Normalize strain name for matching (same logic as ProductDatabase)."""
    if not strain_name:
        return None

    # Convert to lowercase and strip whitespace
    normalized = str(strain_name).strip().lower()

    # Remove special characters but keep spaces and hyphens
    normalized = re.sub(r'[^\w\s\-]', '', normalized)

    # Replace multiple spaces with single space
    normalized = re.sub(r'\s+', ' ', normalized)

    return normalized.strip()


def fix_database(db_path):
    """Fix a single database by adding and populating normalized_product_strain column."""
    print(f"\n{'='*80}")
    print(f"Processing: {os.path.basename(db_path)}")
    print(f"{'='*80}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = {row[1] for row in cursor.fetchall()}

        column_exists = 'normalized_product_strain' in columns

        # Step 1: Add column if missing
        if not column_exists:
            print("✅ Adding normalized_product_strain column...")
            cursor.execute('ALTER TABLE products ADD COLUMN normalized_product_strain TEXT')
            conn.commit()
            print("   Column added successfully")
        else:
            print("ℹ️  Column normalized_product_strain already exists")

        # Step 2: Check how many products need population
        cursor.execute('''
            SELECT COUNT(*)
            FROM products
            WHERE normalized_product_strain IS NULL
              AND "Product Strain" IS NOT NULL
              AND "Product Strain" != ""
        ''')
        count_to_update = cursor.fetchone()[0]

        if count_to_update > 0:
            print(f"✅ Populating normalized_product_strain for {count_to_update} products...")

            # Get products that need updating
            cursor.execute('''
                SELECT id, "Product Strain"
                FROM products
                WHERE normalized_product_strain IS NULL
                  AND "Product Strain" IS NOT NULL
                  AND "Product Strain" != ""
            ''')
            products_to_update = cursor.fetchall()

            # Update in batches
            updated_count = 0
            batch_size = 500
            for i in range(0, len(products_to_update), batch_size):
                batch = products_to_update[i:i+batch_size]
                for product_id, product_strain in batch:
                    if product_strain:
                        normalized = normalize_strain_name(product_strain)
                        if normalized:
                            cursor.execute(
                                'UPDATE products SET normalized_product_strain = ? WHERE id = ?',
                                (normalized, product_id)
                            )
                            updated_count += 1

                # Commit after each batch
                conn.commit()
                print(f"   Progress: {min(i+batch_size, len(products_to_update))}/{len(products_to_update)} products processed")

            print(f"   ✅ Populated {updated_count} products")
        else:
            print("ℹ️  All products already have normalized_product_strain")

        # Step 3: Create index for performance
        print("✅ Creating index on normalized_product_strain...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_products_normalized_strain
            ON products(normalized_product_strain)
        ''')
        conn.commit()
        print("   Index created successfully")

        # Step 4: Verify the fix by testing the query
        print("\n📊 Verification:")

        # Count products with sovereign_lineage
        cursor.execute('''
            SELECT COUNT(*) FROM products
            WHERE sovereign_lineage IS NOT NULL AND sovereign_lineage != ''
        ''')
        product_sov_count = cursor.fetchone()[0]
        print(f"   Products with sovereign_lineage: {product_sov_count}")

        # Count strains with sovereign_lineage
        cursor.execute('''
            SELECT COUNT(*) FROM strains
            WHERE sovereign_lineage IS NOT NULL AND sovereign_lineage != ''
        ''')
        strain_sov_count = cursor.fetchone()[0]
        print(f"   Strains with sovereign_lineage: {strain_sov_count}")

        # Test the COALESCE query (same as get_product_lineage)
        if product_sov_count > 0:
            cursor.execute('''
                SELECT p."Product Name*",
                       COALESCE(p.sovereign_lineage, s1.sovereign_lineage, s2.sovereign_lineage,
                                s1.canonical_lineage, s2.canonical_lineage, p."Lineage") as lineage
                FROM products p
                LEFT JOIN strains s1 ON p.strain_id = s1.id
                LEFT JOIN strains s2 ON LOWER(TRIM(p."Product Strain")) = s2.normalized_name
                WHERE p.sovereign_lineage IS NOT NULL AND p.sovereign_lineage != ''
                LIMIT 3
            ''')
            results = cursor.fetchall()
            if results:
                print("\n   Sample products with sovereign_lineage:")
                for name, lineage in results:
                    print(f"      • {name[:60]:<60} → {lineage}")

        # Count total products with normalized_product_strain
        cursor.execute('''
            SELECT COUNT(*) FROM products
            WHERE normalized_product_strain IS NOT NULL AND normalized_product_strain != ''
        ''')
        normalized_count = cursor.fetchone()[0]
        print(f"\n   Total products with normalized_product_strain: {normalized_count}")

        conn.close()
        print(f"\n✅ Successfully fixed {os.path.basename(db_path)}")
        return True

    except Exception as e:
        print(f"\n❌ Error processing {os.path.basename(db_path)}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fix all product databases in the uploads directory."""
    print("=" * 80)
    print("FIX NORMALIZED_PRODUCT_STRAIN COLUMN FOR LINEAGE LOOKUP")
    print("=" * 80)

    # Find all product databases
    uploads_dir = project_root / "uploads"
    db_files = list(uploads_dir.glob("product_database*.db"))

    if not db_files:
        print(f"\n❌ No database files found in {uploads_dir}")
        return 1

    print(f"\nFound {len(db_files)} database file(s) to process:")
    for db_file in db_files:
        print(f"  • {db_file.name}")

    # Process each database
    success_count = 0
    failure_count = 0

    for db_file in db_files:
        if fix_database(str(db_file)):
            success_count += 1
        else:
            failure_count += 1

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully processed: {success_count} database(s)")
    if failure_count > 0:
        print(f"❌ Failed to process: {failure_count} database(s)")
    print("=" * 80)

    return 0 if failure_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
