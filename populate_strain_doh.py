#!/usr/bin/env python3
"""
Populate DOH status in strains table from product data
"""
import sqlite3
from collections import Counter

db_path = 'uploads/product_database_AGT_Bothell.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all strains
cursor.execute("SELECT id, strain_name FROM strains")
strains = cursor.fetchall()

print(f"Processing {len(strains)} strains...")

updated = 0
for strain_id, strain_name in strains:
    # Find most common DOH status for this strain from products
    cursor.execute("""
        SELECT "DOH", "DOH Compliant (Yes/No)"
        FROM products 
        WHERE "Product Strain" = ? OR "Product Name*" LIKE ?
    """, (strain_name, f"%{strain_name}%"))
    
    products = cursor.fetchall()
    if not products:
        continue
    
    # Collect DOH values
    doh_values = []
    for doh1, doh2 in products:
        doh = doh1 or doh2
        if doh and str(doh).strip() and str(doh).upper() not in ['NONE', 'NO', '']:
            doh_values.append(str(doh).upper())
    
    if doh_values:
        # Get most common DOH status
        most_common = Counter(doh_values).most_common(1)[0][0]
        
        # Determine high_cbd and high_thc
        high_cbd = 1 if most_common == 'CBD' else 0
        high_thc = 1 if most_common == 'THC' else 0
        
        # Update strain
        cursor.execute("""
            UPDATE strains 
            SET doh_status = ?, high_cbd = ?, high_thc = ?
            WHERE id = ?
        """, (most_common, high_cbd, high_thc, strain_id))
        
        updated += 1
        print(f"  ✓ {strain_name}: {most_common} (CBD={high_cbd}, THC={high_thc})")

conn.commit()
conn.close()

print(f"\n✅ Updated {updated} strains with DOH status")
