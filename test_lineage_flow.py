#!/usr/bin/env python3
"""
Test script to verify lineage read/write flow
"""
import sqlite3
import sys

db_path = "uploads/product_database_AGT_Bothell.db"

def test_lineage_columns():
    """Test that lineage columns exist"""
    print("=" * 60)
    print("TEST 1: Checking database schema")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check products table
    cursor.execute("PRAGMA table_info(products)")
    products_cols = [row[1] for row in cursor.fetchall()]
    print(f"\n✓ Products table has {len(products_cols)} columns")
    print(f"  - Has 'Lineage': {'Lineage' in products_cols}")
    print(f"  - Has 'sovereign_lineage': {'sovereign_lineage' in products_cols}")

    # Check strains table
    cursor.execute("PRAGMA table_info(strains)")
    strains_cols = [row[1] for row in cursor.fetchall()]
    print(f"\n✓ Strains table has {len(strains_cols)} columns")
    print(f"  - Has 'canonical_lineage': {'canonical_lineage' in strains_cols}")
    print(f"  - Has 'sovereign_lineage': {'sovereign_lineage' in strains_cols}")

    conn.close()

def test_lineage_read():
    """Test reading lineage from database"""
    print("\n" + "=" * 60)
    print("TEST 2: Reading lineage from database")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find a product with sovereign_lineage set
    cursor.execute("""
        SELECT "Product Name*", Lineage, sovereign_lineage
        FROM products
        WHERE sovereign_lineage IS NOT NULL AND sovereign_lineage <> ''
        LIMIT 3
    """)

    rows = cursor.fetchall()
    if rows:
        print(f"\n✓ Found {len(rows)} products with sovereign_lineage:")
        for row in rows:
            print(f"  - {row[0][:50]}")
            print(f"    Lineage: {row[1]}")
            print(f"    Sovereign: {row[2]}")
    else:
        print("\n✗ No products found with sovereign_lineage set")

    conn.close()
    return rows

def test_lineage_write():
    """Test writing lineage to database"""
    print("\n" + "=" * 60)
    print("TEST 3: Writing lineage to database")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Pick a test product
    test_product = "Core Reactor Quartz Banger"
    test_lineage = "TEST_HYBRID"

    print(f"\n→ Testing with product: {test_product}")

    # Read current value
    cursor.execute("""
        SELECT Lineage, sovereign_lineage
        FROM products
        WHERE "Product Name*" = ?
        LIMIT 1
    """, (test_product,))

    before = cursor.fetchone()
    if before:
        print(f"  Before: Lineage={before[0]}, Sovereign={before[1]}")
    else:
        print(f"  ✗ Product not found!")
        conn.close()
        return

    # Update sovereign_lineage
    cursor.execute("""
        UPDATE products
        SET sovereign_lineage = ?
        WHERE "Product Name*" = ?
    """, (test_lineage, test_product))

    updated_count = cursor.rowcount
    print(f"  Updated {updated_count} row(s)")

    # Commit
    conn.commit()
    print(f"  ✓ Committed")

    # Read back
    cursor.execute("""
        SELECT Lineage, sovereign_lineage
        FROM products
        WHERE "Product Name*" = ?
        LIMIT 1
    """, (test_product,))

    after = cursor.fetchone()
    if after:
        print(f"  After: Lineage={after[0]}, Sovereign={after[1]}")

        if after[1] == test_lineage:
            print(f"  ✓ Write successful!")
        else:
            print(f"  ✗ Write failed - expected {test_lineage}, got {after[1]}")

    # Restore original value
    cursor.execute("""
        UPDATE products
        SET sovereign_lineage = ?
        WHERE "Product Name*" = ?
    """, (before[1], test_product))
    conn.commit()
    print(f"  ✓ Restored original value")

    conn.close()

def test_lineage_priority():
    """Test lineage priority logic"""
    print("\n" + "=" * 60)
    print("TEST 4: Testing lineage priority logic")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find a product with strain
    cursor.execute("""
        SELECT
            p."Product Name*",
            p.Lineage,
            p.sovereign_lineage,
            s.canonical_lineage,
            s.sovereign_lineage as strain_sovereign,
            COALESCE(p.sovereign_lineage, s.sovereign_lineage, s.canonical_lineage, p.Lineage) as effective_lineage
        FROM products p
        LEFT JOIN strains s ON p.strain_id = s.id
        WHERE p.sovereign_lineage IS NOT NULL OR s.sovereign_lineage IS NOT NULL
        LIMIT 5
    """)

    print(f"\n→ Testing lineage priority (product.sovereign > strain.sovereign > canonical > lineage):")
    for row in cursor.fetchall():
        print(f"\n  Product: {row[0][:50]}")
        print(f"    - product.Lineage: {row[1]}")
        print(f"    - product.sovereign_lineage: {row[2]}")
        print(f"    - strain.canonical_lineage: {row[3]}")
        print(f"    - strain.sovereign_lineage: {row[4]}")
        print(f"    → EFFECTIVE: {row[5]}")

    conn.close()

if __name__ == "__main__":
    print("\n🧪 LINEAGE FLOW TEST SUITE")
    print("Testing: " + db_path)

    try:
        test_lineage_columns()
        test_lineage_read()
        test_lineage_write()
        test_lineage_priority()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS COMPLETED")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
