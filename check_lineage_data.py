#!/usr/bin/env python3
"""
Diagnostic script to check lineage data correctness in the database.
Checks for:
1. Classic products with invalid lineages (MIXED, etc.)
2. Invalid lineage values
3. Strains with incorrect canonical_lineage
"""

import sqlite3
import sys
from pathlib import Path

# Find the database file - check for store-specific databases
base_dir = Path(__file__).parent
uploads_dir = base_dir / "uploads"

# Try to find AGT_Bothell database (based on error logs)
db_path = uploads_dir / "product_database_AGT_Bothell.db"
if not db_path.exists():
    # Try other common stores
    for store_db in uploads_dir.glob("product_database_*.db"):
        db_path = store_db
        print(f"📦 Using database: {db_path.name}")
        break
    else:
        # Fallback to generic database
        db_path = uploads_dir / "product_database.db"
        if not db_path.exists():
            print(f"❌ Database not found. Checked:")
            print(f"   - {uploads_dir / 'product_database_AGT_Bothell.db'}")
            print(f"   - {uploads_dir / 'product_database.db'}")
            sys.exit(1)
        else:
            print(f"📦 Using database: {db_path.name}")
else:
    print(f"📦 Using database: {db_path.name}")

# Classic product types
CLASSIC_TYPES = {
    'flower', 'pre-roll', 'concentrate', 'infused pre-roll', 
    'solventless concentrate', 'vape cartridge', 'rso/co2 tankers'
}

# Valid lineages for classic types
VALID_CLASSIC_LINEAGES = {
    'SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD', 'CBD_BLEND'
}

# Valid lineages for non-classic types
VALID_NONCLASSIC_LINEAGES = {
    'MIXED', 'CBD', 'CBD_BLEND', 'PARA', 'PARAPHERNALIA'
}

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("=" * 80)
print("LINEAGE DATA DIAGNOSTIC REPORT")
print("=" * 80)
print()

# Check 1: Classic products with MIXED lineage
print("1. Checking classic products with MIXED lineage...")
cursor.execute('''
    SELECT "Product Name*", "Product Type*", "Lineage", "Vendor/Supplier*", "Product Brand"
    FROM products
    WHERE LOWER("Product Type*") IN ('flower', 'pre-roll', 'concentrate', 'infused pre-roll', 
                                      'solventless concentrate', 'vape cartridge', 'rso/co2 tankers')
    AND UPPER(TRIM("Lineage")) = 'MIXED'
    LIMIT 20
''')
classic_with_mixed = cursor.fetchall()
if classic_with_mixed:
    print(f"   ⚠️  Found {len(classic_with_mixed)} classic products with MIXED lineage:")
    for name, ptype, lineage, vendor, brand in classic_with_mixed[:10]:
        print(f"      - {name} ({ptype}) - Lineage: {lineage} - Vendor: {vendor}")
    if len(classic_with_mixed) > 10:
        print(f"      ... and {len(classic_with_mixed) - 10} more")
else:
    print("   ✅ No classic products with MIXED lineage found")
print()

# Check 2: Classic products with invalid lineages
print("2. Checking classic products with invalid lineages...")
cursor.execute('''
    SELECT "Product Name*", "Product Type*", "Lineage", "Vendor/Supplier*"
    FROM products
    WHERE LOWER("Product Type*") IN ('flower', 'pre-roll', 'concentrate', 'infused pre-roll', 
                                      'solventless concentrate', 'vape cartridge', 'rso/co2 tankers')
    AND UPPER(TRIM("Lineage")) NOT IN ('SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD', 'CBD_BLEND', '')
    AND "Lineage" IS NOT NULL
    LIMIT 20
''')
classic_invalid = cursor.fetchall()
if classic_invalid:
    print(f"   ⚠️  Found {len(classic_invalid)} classic products with invalid lineages:")
    for name, ptype, lineage, vendor in classic_invalid[:10]:
        print(f"      - {name} ({ptype}) - Lineage: {lineage} - Vendor: {vendor}")
    if len(classic_invalid) > 10:
        print(f"      ... and {len(classic_invalid) - 10} more")
else:
    print("   ✅ No classic products with invalid lineages found")
print()

# Check 3: Strains with MIXED canonical_lineage used by classic products
print("3. Checking strains with MIXED canonical_lineage used by classic products...")
cursor.execute('''
    SELECT DISTINCT s.strain_name, s.canonical_lineage, COUNT(DISTINCT p."Product Name*") as product_count
    FROM strains s
    JOIN products p ON p."Product Strain" = s.strain_name
    WHERE UPPER(TRIM(s.canonical_lineage)) = 'MIXED'
    AND LOWER(p."Product Type*") IN ('flower', 'pre-roll', 'concentrate', 'infused pre-roll', 
                                      'solventless concentrate', 'vape cartridge', 'rso/co2 tankers')
    GROUP BY s.strain_name, s.canonical_lineage
    ORDER BY product_count DESC
    LIMIT 20
''')
strains_mixed = cursor.fetchall()
if strains_mixed:
    print(f"   ⚠️  Found {len(strains_mixed)} strains with MIXED canonical_lineage used by classic products:")
    for strain, lineage, count in strains_mixed[:10]:
        print(f"      - {strain}: {lineage} (used by {count} classic products)")
    if len(strains_mixed) > 10:
        print(f"      ... and {len(strains_mixed) - 10} more")
else:
    print("   ✅ No strains with MIXED canonical_lineage used by classic products")
print()

# Check 4: Overall lineage distribution
print("4. Overall lineage distribution...")
cursor.execute('''
    SELECT "Lineage", COUNT(*) as count
    FROM products
    WHERE "Lineage" IS NOT NULL AND TRIM("Lineage") != ''
    GROUP BY "Lineage"
    ORDER BY count DESC
''')
lineage_dist = cursor.fetchall()
if lineage_dist:
    print("   Lineage distribution:")
    for lineage, count in lineage_dist:
        print(f"      - {lineage}: {count} products")
print()

# Check 5: Strains canonical_lineage distribution
print("5. Strains canonical_lineage distribution...")
cursor.execute('''
    SELECT canonical_lineage, COUNT(*) as count
    FROM strains
    WHERE canonical_lineage IS NOT NULL AND TRIM(canonical_lineage) != ''
    GROUP BY canonical_lineage
    ORDER BY count DESC
    LIMIT 15
''')
strain_lineage_dist = cursor.fetchall()
if strain_lineage_dist:
    print("   Canonical lineage distribution:")
    for lineage, count in strain_lineage_dist:
        print(f"      - {lineage}: {count} strains")
print()

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)

total_issues = len(classic_with_mixed) + len(classic_invalid) + len(strains_mixed)
if total_issues == 0:
    print("✅ All lineages appear to be correct!")
else:
    print(f"⚠️  Found {total_issues} potential issues:")
    print(f"   - {len(classic_with_mixed)} classic products with MIXED lineage")
    print(f"   - {len(classic_invalid)} classic products with invalid lineages")
    print(f"   - {len(strains_mixed)} strains with MIXED canonical_lineage used by classic products")
    print()
    print("💡 Recommendation: Run a fix script to correct these issues.")

conn.close()
