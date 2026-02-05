#!/usr/bin/env python3
"""
Bulk update: For all products of classic types, set Lineage and sovereign_lineage to the canonical_lineage of their strain.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from core.data.product_database import ProductDatabase

# Set your store name here (edit if needed)
STORE_NAME = 'AGT_Bothell'

# Classic types to update
CLASSIC_TYPES = {'SATIVA', 'INDICA', 'HYBRID', 'HYBRID/SATIVA', 'HYBRID/INDICA', 'CBD'}

def main():
    db = ProductDatabase(STORE_NAME)
    conn = db._get_connection()
    cursor = conn.cursor()

    # Get all strains with a canonical_lineage in classic types
    cursor.execute('''
        SELECT id, canonical_lineage FROM strains
        WHERE canonical_lineage IN (?, ?, ?, ?, ?, ?)
    ''', tuple(CLASSIC_TYPES))
    strain_map = {row[0]: row[1] for row in cursor.fetchall()}

    updated = 0
    for strain_id, canonical in strain_map.items():
        # Update all products for this strain
        cursor.execute('''
            UPDATE products
            SET "Lineage" = ?, sovereign_lineage = ?, updated_at = CURRENT_TIMESTAMP
            WHERE strain_id = ?
        ''', (canonical, canonical, strain_id))
        updated += cursor.rowcount
    conn.commit()
    print(f"Updated {updated} products to match canonical_lineage for classic types.")
    conn.close()

if __name__ == '__main__':
    main()
