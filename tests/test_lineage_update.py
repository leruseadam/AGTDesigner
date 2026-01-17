#!/usr/bin/env python3
"""
Test lineage update mechanism
Run this to test if updates are working
"""
import sqlite3
import sys

db_path = "uploads/product_database_AGT_Bothell.db"

def run_update(product_name, new_lineage):
    """Run updating a product's lineage (not a pytest test)."""
    print(f"\n{'='*60}")
    print(f"Testing update for: {product_name}")
    print(f"New lineage: {new_lineage}")
    print(f"{'='*60}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check BEFORE
    print("\n📋 BEFORE UPDATE:")
    cursor.execute("""
        SELECT
            p."Product Name*",
            p.Lineage,
            p.sovereign_lineage,
            p.strain_id,
            s.strain_name,
            s.canonical_lineage,
            s.sovereign_lineage as strain_sovereign
        FROM products p
        LEFT JOIN strains s ON p.strain_id = s.id
        WHERE p."Product Name*" = ?
        LIMIT 1
    """, (product_name,))

    row = cursor.fetchone()
    if not row:
        print(f"❌ Product '{product_name}' not found!")
        conn.close()
        return

    print(f"  Product Lineage: {row[1]}")
    print(f"  Product Sovereign: {row[2]}")
    print(f"  Strain ID: {row[3]}")
    print(f"  Strain Name: {row[4]}")
    print(f"  Strain Canonical: {row[5]}")
    print(f"  Strain Sovereign: {row[6]}")

    # UPDATE product sovereign_lineage
    print(f"\n🔄 UPDATING product.sovereign_lineage to '{new_lineage}'...")
    cursor.execute("""
        UPDATE products
        SET sovereign_lineage = ?
        WHERE "Product Name*" = ?
    """, (new_lineage, product_name))

    updated_count = cursor.rowcount
    print(f"  Updated {updated_count} row(s)")

    # If product has a strain, update strain too
    strain_id = row[3]
    if strain_id:
        print(f"\n🔄 UPDATING strain.sovereign_lineage (strain_id={strain_id}) to '{new_lineage}'...")
        cursor.execute("""
            UPDATE strains
            SET sovereign_lineage = ?
            WHERE id = ?
        """, (new_lineage, strain_id))
        strain_updated = cursor.rowcount
        print(f"  Updated {strain_updated} strain row(s)")

    # COMMIT
    conn.commit()
    print("\n✅ COMMITTED")

    # Check AFTER
    print("\n📋 AFTER UPDATE:")
    cursor.execute("""
        SELECT
            p."Product Name*",
            p.Lineage,
            p.sovereign_lineage,
            p.strain_id,
            s.strain_name,
            s.canonical_lineage,
            s.sovereign_lineage as strain_sovereign,
            COALESCE(p.sovereign_lineage, s.sovereign_lineage, s.canonical_lineage, p.Lineage) as effective
        FROM products p
        LEFT JOIN strains s ON p.strain_id = s.id
        WHERE p."Product Name*" = ?
        LIMIT 1
    """, (product_name,))

    row = cursor.fetchone()
    print(f"  Product Lineage: {row[1]}")
    print(f"  Product Sovereign: {row[2]} {'✅' if row[2] == new_lineage else '❌'}")
    print(f"  Strain ID: {row[3]}")
    print(f"  Strain Name: {row[4]}")
    print(f"  Strain Canonical: {row[5]}")
    print(f"  Strain Sovereign: {row[6]} {'✅' if strain_id and row[6] == new_lineage else ''}")
    print(f"  → EFFECTIVE LINEAGE: {row[7]} {'✅' if row[7] == new_lineage else '❌ WRONG!'}")

    conn.close()

    if row[7] == new_lineage:
        print(f"\n✅ SUCCESS! Update worked correctly.")
    else:
        print(f"\n❌ FAILURE! Expected '{new_lineage}' but effective lineage is '{row[7]}'")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 test_lineage_update.py 'Product Name' 'NEW_LINEAGE'")
        print("\nExample:")
        print("  python3 test_lineage_update.py 'Core Reactor Quartz Banger' 'INDICA'")
        sys.exit(1)

    product_name = sys.argv[1]
    new_lineage = sys.argv[2]

    run_update(product_name, new_lineage)
