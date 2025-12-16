#!/usr/bin/env python3
"""Diagnose lineage mismatch between UI, export, and database."""

import sqlite3
import os

# Find the database
db_files = [
    'uploads/product_database_AGT_Bothell.db',
    'uploads/product_database_AGT_Lynnwood.db',
    'bothell_products.db'
]

db_path = None
for db_file in db_files:
    if os.path.exists(db_file):
        db_path = db_file
        break

if not db_path:
    print("❌ No database found")
    exit(1)

print(f"📊 Using database: {db_path}\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Search for Mt Baker Homegrown products with 14g
print("=" * 80)
print("🔍 Mt Baker Homegrown - 14g Products")
print("=" * 80)

cursor.execute('''
    SELECT p."Product Name*", 
           p."Lineage" as products_lineage,
           p."Product Strain",
           s.sovereign_lineage,
           s.canonical_lineage,
           COALESCE(s.sovereign_lineage, s.canonical_lineage, p."Lineage") as effective_lineage
    FROM products p
    LEFT JOIN strains s ON p.strain_id = s.id
    WHERE (p."Product Name*" LIKE '%Mt Baker Homegrown%' OR p."Vendor/Supplier*" LIKE '%Mt Baker%')
      AND (p."Product Name*" LIKE '%14g%' OR p."Weight*" LIKE '%14%')
    ORDER BY p."Product Name*"
    LIMIT 20
''')

results = cursor.fetchall()

print(f"\nFound {len(results)} products:\n")
for i, row in enumerate(results, 1):
    name, products_lineage, strain, sovereign, canonical, effective = row
    print(f"{i}. {name}")
    print(f"   Products.Lineage: {products_lineage}")
    print(f"   sovereign_lineage: {sovereign or 'None'}")
    print(f"   canonical_lineage: {canonical or 'None'}")
    print(f"   ✅ Effective (what should be used): {effective}")
    print()

conn.close()
