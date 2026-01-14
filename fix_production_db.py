#!/usr/bin/env python3
"""
Fix production database - add DOH to strains, populate lineage columns
Run this on PythonAnywhere
"""
import sqlite3
from collections import Counter

db_path = 'uploads/product_database_AGT_Bothell.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Fixing Production Database ===\n")

# Step 1: Add columns to strains table if they don't exist
print("Step 1: Adding DOH columns to strains table...")
try:
    cursor.execute("ALTER TABLE strains ADD COLUMN doh_status TEXT DEFAULT NULL")
    print("  ✓ Added doh_status column")
except Exception as e:
    if "duplicate column" in str(e).lower():
        print("  ⊘ doh_status already exists")
    else:
        print(f"  ✗ Error: {e}")

try:
    cursor.execute("ALTER TABLE strains ADD COLUMN high_cbd INTEGER DEFAULT 0")
    print("  ✓ Added high_cbd column")
except Exception as e:
    if "duplicate column" in str(e).lower():
        print("  ⊘ high_cbd already exists")
    else:
        print(f"  ✗ Error: {e}")

try:
    cursor.execute("ALTER TABLE strains ADD COLUMN high_thc INTEGER DEFAULT 0")
    print("  ✓ Added high_thc column")
except Exception as e:
    if "duplicate column" in str(e).lower():
        print("  ⊘ high_thc already exists")
    else:
        print(f"  ✗ Error: {e}")

conn.commit()

# Step 2: Populate DOH data in strains from products
print("\nStep 2: Populating DOH data in strains from products...")
cursor.execute("SELECT id, strain_name FROM strains")
strains = cursor.fetchall()

updated = 0
for strain_id, strain_name in strains:
    cursor.execute("""
        SELECT "DOH", "DOH Compliant (Yes/No)"
        FROM products 
        WHERE "Product Strain" = ? OR "Product Name*" LIKE ?
    """, (strain_name, f"%{strain_name}%"))
    
    products = cursor.fetchall()
    if not products:
        continue
    
    doh_values = []
    for doh1, doh2 in products:
        doh = doh1 or doh2
        if doh and str(doh).strip() and str(doh).upper() not in ['NONE', 'NO', '']:
            doh_values.append(str(doh).upper())
    
    if doh_values:
        most_common = Counter(doh_values).most_common(1)[0][0]
        high_cbd = 1 if most_common == 'CBD' else 0
        high_thc = 1 if most_common == 'THC' else 0
        
        cursor.execute("""
            UPDATE strains 
            SET doh_status = ?, high_cbd = ?, high_thc = ?
            WHERE id = ?
        """, (most_common, high_cbd, high_thc, strain_id))
        
        updated += 1

conn.commit()
print(f"  ✓ Updated {updated} strains with DOH status")

# Step 3: Add lineage columns to products if they don't exist
print("\nStep 3: Adding lineage columns to products table...")
try:
    cursor.execute("ALTER TABLE products ADD COLUMN canonical_lineage TEXT")
    print("  ✓ Added canonical_lineage column")
except Exception as e:
    if "duplicate column" in str(e).lower():
        print("  ⊘ canonical_lineage already exists")
    else:
        print(f"  ✗ Error: {e}")

try:
    cursor.execute("ALTER TABLE products ADD COLUMN currentLineage TEXT")
    print("  ✓ Added currentLineage column")
except Exception as e:
    if "duplicate column" in str(e).lower():
        print("  ⊘ currentLineage already exists")
    else:
        print(f"  ✗ Error: {e}")

conn.commit()

# Step 4: Populate lineage columns
print("\nStep 4: Populating lineage columns in products...")
cursor.execute("""
    UPDATE products 
    SET canonical_lineage = Lineage 
    WHERE Lineage IS NOT NULL AND Lineage != '' AND Lineage != 'None'
    AND (canonical_lineage IS NULL OR canonical_lineage = '')
""")
rows_updated = cursor.rowcount
print(f"  ✓ Updated {rows_updated} products with canonical_lineage")

cursor.execute("""
    UPDATE products 
    SET currentLineage = canonical_lineage 
    WHERE canonical_lineage IS NOT NULL
    AND (currentLineage IS NULL OR currentLineage = '')
""")
rows_updated = cursor.rowcount
print(f"  ✓ Updated {rows_updated} products with currentLineage")

conn.commit()

# Step 5: Verify
print("\nStep 5: Verifying changes...")
cursor.execute("SELECT COUNT(*) FROM strains WHERE doh_status IS NOT NULL")
strain_doh_count = cursor.fetchone()[0]
print(f"  ✓ {strain_doh_count} strains have DOH status")

cursor.execute("SELECT COUNT(*) FROM products WHERE canonical_lineage IS NOT NULL AND canonical_lineage != ''")
product_lineage_count = cursor.fetchone()[0]
print(f"  ✓ {product_lineage_count} products have canonical_lineage")

cursor.execute("SELECT COUNT(*) FROM products WHERE DOH IS NOT NULL AND DOH != ''")
product_doh_count = cursor.fetchone()[0]
print(f"  ✓ {product_doh_count} products have DOH data")

conn.close()

print("\n=== Database Fix Complete ===")
