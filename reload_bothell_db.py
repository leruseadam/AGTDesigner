#!/usr/bin/env python3
"""
Reload Bothell database from Excel file with proper lineage handling.
"""

import sqlite3
import pandas as pd
import re
from collections import Counter

DB_PATH = 'uploads/product_database_AGT_Bothell.db'
EXCEL_FILE = 'uploads/1768253431_A Greener Today - Bothell_inventory_01-12-2026  8_32 AM.xlsx'

def normalize_lineage(lineage):
    """Normalize lineage to standard format."""
    if pd.isna(lineage) or not lineage or str(lineage).strip() == '':
        return 'HYBRID'
    
    lineage_str = str(lineage).strip().lower()
    
    # Map variations to standard uppercase formats
    lineage_map = {
        'sativa': 'SATIVA',
        'indica': 'INDICA',
        'hybrid': 'HYBRID',
        'cbd': 'CBD',
        'mixed': 'HYBRID',
        'sativa_hybrid': 'HYBRID/SATIVA',
        'sativa hybrid': 'HYBRID/SATIVA',
        'hybrid/sativa': 'HYBRID/SATIVA',
        'sativa/hybrid': 'HYBRID/SATIVA',
        'indica_hybrid': 'HYBRID/INDICA',
        'indica hybrid': 'HYBRID/INDICA',
        'hybrid/indica': 'HYBRID/INDICA',
        'indica/hybrid': 'HYBRID/INDICA',
    }
    
    return lineage_map.get(lineage_str, 'HYBRID')  # Default to HYBRID

print("Loading Excel file...")
df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
print(f"Loaded {len(df)} rows from Excel")

# Normalize column names
df.columns = df.columns.str.strip()

# Normalize lineages
if 'Lineage' in df.columns:
    df['Lineage'] = df['Lineage'].apply(normalize_lineage)
    print(f"\nLineage distribution:")
    print(df['Lineage'].value_counts())

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Clear existing products
print("\nClearing existing products...")
cursor.execute('DELETE FROM products')
conn.commit()

# Check if DOH column exists in database
cursor.execute("PRAGMA table_info(products)")
columns = [row[1] for row in cursor.fetchall()]
has_doh = 'DOH' in columns

if not has_doh:
    print("Adding DOH column to products table...")
    cursor.execute('ALTER TABLE products ADD COLUMN DOH TEXT')
    conn.commit()

# Insert products
print("Inserting products...")
for idx, row in df.iterrows():
    try:
        doh_value = row.get('DOH Compliant (Yes/No)', '')
        if pd.isna(doh_value):
            doh_value = ''
        
        cursor.execute('''
            INSERT INTO products (
                "Product Name*", "Product Type*", "Product Brand", 
                "Vendor/Supplier*", "Weight*", "Weight Unit*", 
                "Price*", "Quantity*", "Lineage", "Product Strain",
                canonical_lineage, currentLineage, DOH
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row.get('Product Name*'),
            row.get('Product Type*'),
            row.get('Product Brand'),
            row.get('Vendor/Supplier*'),
            row.get('Weight*'),
            row.get('Weight Unit* (grams/gm or ounces/oz)'),
            row.get('Price*'),
            row.get('Quantity*'),
            row.get('Lineage'),
            row.get('Product Strain'),
            row.get('Lineage'),  # canonical_lineage
            row.get('Lineage'),  # currentLineage
            doh_value
        ))
    except Exception as e:
        print(f"Error inserting row {idx}: {e}")
        continue

conn.commit()

# Get count
cursor.execute('SELECT COUNT(*) FROM products')
count = cursor.fetchone()[0]
print(f"\n✅ Inserted {count} products")

# Update strains with product data
print("\nUpdating strains from products...")

# Get all unique strains from products
cursor.execute('''
    SELECT DISTINCT "Product Strain" FROM products 
    WHERE "Product Strain" IS NOT NULL AND "Product Strain" != ''
''')
product_strains = [row[0] for row in cursor.fetchall()]

for strain_name in product_strains:
    # Get all lineages for this strain from products
    cursor.execute('''
        SELECT "Lineage" FROM products 
        WHERE "Product Strain" = ?
    ''', (strain_name,))
    
    lineages = [row[0] for row in cursor.fetchall() if row[0]]
    
    if not lineages:
        continue
    
    # Use most common lineage
    lineage_counter = Counter(lineages)
    most_common_lineage = lineage_counter.most_common(1)[0][0]
    
    # Check if strain exists
    cursor.execute('SELECT id FROM strains WHERE strain_name = ?', (strain_name,))
    existing = cursor.fetchone()
    
    if existing:
        # Update existing strain
        cursor.execute('''
            UPDATE strains 
            SET canonical_lineage = ?, last_seen_date = date('now'), updated_at = datetime('now')
            WHERE strain_name = ?
        ''', (most_common_lineage, strain_name))
    else:
        # Insert new strain
        normalized_name = strain_name.lower().strip()
        cursor.execute('''
            INSERT INTO strains (
                strain_name, normalized_name, canonical_lineage, 
                first_seen_date, last_seen_date, 
                total_occurrences, lineage_confidence,
                created_at, updated_at
            ) VALUES (?, ?, ?, date('now'), date('now'), 1, 1.0, datetime('now'), datetime('now'))
        ''', (strain_name, normalized_name, most_common_lineage))

conn.commit()

# Link products to strains via strain_id
print("\nLinking products to strains...")
cursor.execute('''
    UPDATE products
    SET strain_id = (
        SELECT id FROM strains WHERE strains.strain_name = products."Product Strain"
    )
    WHERE "Product Strain" IS NOT NULL AND "Product Strain" != ''
''')
conn.commit()

# Verification
print("\nVerification:")
cursor.execute('SELECT COUNT(*) FROM products')
print(f"Total products: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM strains')
print(f"Total strains: {cursor.fetchone()[0]}")

cursor.execute('SELECT "Product Type*", COUNT(*) FROM products GROUP BY "Product Type*" LIMIT 10')
print(f"\nTop product types:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

cursor.execute('SELECT Lineage, COUNT(*) FROM products GROUP BY Lineage')
print(f"\nLineage distribution in products:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

cursor.execute('SELECT canonical_lineage, COUNT(*) FROM strains GROUP BY canonical_lineage ORDER BY COUNT(*) DESC LIMIT 10')
print(f"\nTop strain lineages:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()
print("\n✅ Database reload complete!")
