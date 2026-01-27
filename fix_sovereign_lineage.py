#!/usr/bin/env python3
"""
Fix script to remove invalid "SOVEREIGN" lineage values from the database.
"SOVEREIGN" is a field name, not a valid lineage value.
"""

import sqlite3
import sys
import argparse
from pathlib import Path
import subprocess

# Find the database file
parser = argparse.ArgumentParser(description="Fix invalid 'SOVEREIGN' lineage values in SQLite DB")
parser.add_argument('--db', '-d', help='Path to SQLite database file (overrides default uploads path)')
args = parser.parse_args()

base_dir = Path(__file__).parent
uploads_dir = base_dir / "uploads"
default_db = uploads_dir / "product_database_AGT_Bothell.db"
db_path = Path(args.db) if args.db else default_db

if not db_path.exists():
    print(f"❌ Database not found at {db_path}")
    sys.exit(1)

# Try connecting and provide a helpful diagnostic if the file isn't a valid SQLite DB
try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
except sqlite3.DatabaseError as e:
    print(f"❌ sqlite3.DatabaseError when opening {db_path}: {e}")
    print("This usually means the file is not a SQLite database or is corrupted.")
    print("Run the following commands to inspect the file (shell):")
    print(f"  file '{db_path}'")
    print(f"  hexdump -C -n 64 '{db_path}' | head -n 5")
    # Try to run `file` tool for convenience if available
    try:
        out = subprocess.check_output(['file', str(db_path)], stderr=subprocess.STDOUT)
        print('\nfile output:')
        print(out.decode('utf-8').strip())
    except Exception:
        pass
    sys.exit(2)

print("=" * 80)
print("FIXING INVALID 'SOVEREIGN' LINEAGE VALUES")
print("=" * 80)
print()

# Check products table
print("1. Checking products table for 'SOVEREIGN' lineage...")
cursor.execute('''
    SELECT COUNT(*) FROM products
    WHERE UPPER(TRIM(sovereign_lineage)) = 'SOVEREIGN'
       OR UPPER(TRIM("Lineage")) = 'SOVEREIGN'
       OR UPPER(TRIM(canonical_lineage)) = 'SOVEREIGN'
''')
count = cursor.fetchone()[0]

if count > 0:
    print(f"   ⚠️  Found {count} products with 'SOVEREIGN' lineage")
    
    # Get sample products
    cursor.execute('''
        SELECT "Product Name*", sovereign_lineage, "Lineage", canonical_lineage
        FROM products
        WHERE UPPER(TRIM(sovereign_lineage)) = 'SOVEREIGN'
           OR UPPER(TRIM("Lineage")) = 'SOVEREIGN'
           OR UPPER(TRIM(canonical_lineage)) = 'SOVEREIGN'
        LIMIT 10
    ''')
    samples = cursor.fetchall()
    print("   Sample products:")
    for name, sov, lin, canon in samples:
        print(f"      - {name}: sovereign={sov}, Lineage={lin}, canonical={canon}")
    
    # Fix products - set SOVEREIGN to NULL so it falls back to other lineage fields
    cursor.execute('''
        UPDATE products
        SET sovereign_lineage = NULL
        WHERE UPPER(TRIM(sovereign_lineage)) = 'SOVEREIGN'
    ''')
    fixed_products = cursor.rowcount
    
    cursor.execute('''
        UPDATE products
        SET "Lineage" = NULL
        WHERE UPPER(TRIM("Lineage")) = 'SOVEREIGN'
    ''')
    fixed_lineage = cursor.rowcount
    
    cursor.execute('''
        UPDATE products
        SET canonical_lineage = NULL
        WHERE UPPER(TRIM(canonical_lineage)) = 'SOVEREIGN'
    ''')
    fixed_canonical = cursor.rowcount
    
    conn.commit()
    print(f"   ✅ Fixed {fixed_products} products with sovereign_lineage='SOVEREIGN'")
    print(f"   ✅ Fixed {fixed_lineage} products with Lineage='SOVEREIGN'")
    print(f"   ✅ Fixed {fixed_canonical} products with canonical_lineage='SOVEREIGN'")
else:
    print("   ✅ No products with 'SOVEREIGN' lineage found")
print()

# Check strains table
print("2. Checking strains table for 'SOVEREIGN' lineage...")
cursor.execute('''
    SELECT COUNT(*) FROM strains
    WHERE UPPER(TRIM(sovereign_lineage)) = 'SOVEREIGN'
       OR UPPER(TRIM(canonical_lineage)) = 'SOVEREIGN'
''')
count = cursor.fetchone()[0]

if count > 0:
    print(f"   ⚠️  Found {count} strains with 'SOVEREIGN' lineage")
    
    # Get sample strains
    cursor.execute('''
        SELECT strain_name, sovereign_lineage, canonical_lineage
        FROM strains
        WHERE UPPER(TRIM(sovereign_lineage)) = 'SOVEREIGN'
           OR UPPER(TRIM(canonical_lineage)) = 'SOVEREIGN'
        LIMIT 10
    ''')
    samples = cursor.fetchall()
    print("   Sample strains:")
    for strain, sov, canon in samples:
        print(f"      - {strain}: sovereign={sov}, canonical={canon}")
    
    # Fix strains - set SOVEREIGN to NULL
    cursor.execute('''
        UPDATE strains
        SET sovereign_lineage = NULL
        WHERE UPPER(TRIM(sovereign_lineage)) = 'SOVEREIGN'
    ''')
    fixed_sovereign = cursor.rowcount
    
    cursor.execute('''
        UPDATE strains
        SET canonical_lineage = NULL
        WHERE UPPER(TRIM(canonical_lineage)) = 'SOVEREIGN'
    ''')
    fixed_canonical = cursor.rowcount
    
    conn.commit()
    print(f"   ✅ Fixed {fixed_sovereign} strains with sovereign_lineage='SOVEREIGN'")
    print(f"   ✅ Fixed {fixed_canonical} strains with canonical_lineage='SOVEREIGN'")
else:
    print("   ✅ No strains with 'SOVEREIGN' lineage found")
print()

# Verify fix
print("3. Verifying fixes...")
cursor.execute('''
    SELECT COUNT(*) FROM products
    WHERE UPPER(TRIM(sovereign_lineage)) = 'SOVEREIGN'
       OR UPPER(TRIM("Lineage")) = 'SOVEREIGN'
       OR UPPER(TRIM(canonical_lineage)) = 'SOVEREIGN'
''')
remaining_products = cursor.fetchone()[0]

cursor.execute('''
    SELECT COUNT(*) FROM strains
    WHERE UPPER(TRIM(sovereign_lineage)) = 'SOVEREIGN'
       OR UPPER(TRIM(canonical_lineage)) = 'SOVEREIGN'
''')
remaining_strains = cursor.fetchone()[0]

if remaining_products == 0 and remaining_strains == 0:
    print("   ✅ All 'SOVEREIGN' values removed!")
else:
    print(f"   ⚠️  Still found {remaining_products} products and {remaining_strains} strains with 'SOVEREIGN'")

print()
print("=" * 80)
print("FIX COMPLETE")
print("=" * 80)

conn.close()
