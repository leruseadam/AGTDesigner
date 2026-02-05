#!/usr/bin/env python3
"""
Fix script to correct lineage issues in the database.
Fixes:
1. Strains with MIXED canonical_lineage used by classic products -> change to HYBRID
"""

import sqlite3
import sys
from pathlib import Path

# Find the database file
base_dir = Path(__file__).parent
uploads_dir = base_dir / "uploads"
db_path = uploads_dir / "product_database_AGT_Bothell.db"

if not db_path.exists():
    print(f"❌ Database not found at {db_path}")
    sys.exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("=" * 80)
print("LINEAGE FIX SCRIPT")
print("=" * 80)
print()

# Fix 1: Strains with MIXED canonical_lineage used by classic products
print("1. Fixing strains with MIXED canonical_lineage used by classic products...")
cursor.execute('''
    SELECT DISTINCT s.strain_name, s.canonical_lineage, COUNT(DISTINCT p."Product Name*") as product_count
    FROM strains s
    JOIN products p ON p."Product Strain" = s.strain_name
    WHERE UPPER(TRIM(s.canonical_lineage)) = 'MIXED'
    AND LOWER(p."Product Type*") IN ('flower', 'pre-roll', 'concentrate', 'infused pre-roll', 
                                      'solventless concentrate', 'vape cartridge', 'rso/co2 tankers')
    GROUP BY s.strain_name, s.canonical_lineage
''')
strains_to_fix = cursor.fetchall()

if strains_to_fix:
    print(f"   Found {len(strains_to_fix)} strains to fix:")
    for strain, lineage, count in strains_to_fix:
        print(f"      - {strain}: {lineage} (used by {count} classic products) -> changing to HYBRID")
        
        # Update the strain's canonical_lineage to HYBRID
        cursor.execute('''
            UPDATE strains
            SET canonical_lineage = 'HYBRID'
            WHERE strain_name = ? AND UPPER(TRIM(canonical_lineage)) = 'MIXED'
        ''', (strain,))
        
        print(f"      ✅ Fixed {strain}")
    
    conn.commit()
    print(f"   ✅ Fixed {len(strains_to_fix)} strains")
else:
    print("   ✅ No strains to fix")

print()

# Verify the fix
print("2. Verifying fixes...")
cursor.execute('''
    SELECT DISTINCT s.strain_name, s.canonical_lineage, COUNT(DISTINCT p."Product Name*") as product_count
    FROM strains s
    JOIN products p ON p."Product Strain" = s.strain_name
    WHERE UPPER(TRIM(s.canonical_lineage)) = 'MIXED'
    AND LOWER(p."Product Type*") IN ('flower', 'pre-roll', 'concentrate', 'infused pre-roll', 
                                      'solventless concentrate', 'vape cartridge', 'rso/co2 tankers')
    GROUP BY s.strain_name, s.canonical_lineage
''')
remaining_issues = cursor.fetchall()

if remaining_issues:
    print(f"   ⚠️  Still found {len(remaining_issues)} issues:")
    for strain, lineage, count in remaining_issues:
        print(f"      - {strain}: {lineage} (used by {count} classic products)")
else:
    print("   ✅ All issues fixed!")

print()
print("=" * 80)
print("FIX COMPLETE")
print("=" * 80)

conn.close()
