"""Script to safely remove 'SOVEREIGN' values from product lineage fields.

This performs per-row fixes and writes audit entries to `lineage_audit` rather than doing a bulk UPDATE.
"""
import sqlite3
from datetime import datetime
import sys
from pathlib import Path

def clean_sovereign_values(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, "Product Name*", sovereign_lineage, "Lineage", canonical_lineage
        FROM products
        WHERE UPPER(TRIM(sovereign_lineage)) = 'SOVEREIGN'
           OR UPPER(TRIM("Lineage")) = 'SOVEREIGN'
           OR UPPER(TRIM(canonical_lineage)) = 'SOVEREIGN'
    ''')
    rows = cursor.fetchall()
    if not rows:
        print("No 'SOVEREIGN' values found in products")
        conn.close()
        return

    now = datetime.utcnow().isoformat()
    fixed = 0
    for pid, name, sov, lin, canon in rows:
        try:
            cursor.execute('''
                INSERT INTO lineage_audit (product_id, product_name, old_lineage, old_sovereign_lineage, new_lineage, updated_by, source, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (pid, name, lin, sov, canon if canon and str(canon).strip().upper() != 'SOVEREIGN' else None, 'maintenance_script', 'clean_sovereign_lineage', now))

            if sov and str(sov).strip().upper() == 'SOVEREIGN':
                cursor.execute('UPDATE products SET sovereign_lineage = NULL WHERE id = ?', (pid,))
            if lin and str(lin).strip().upper() == 'SOVEREIGN':
                cursor.execute('UPDATE products SET "Lineage" = NULL WHERE id = ?', (pid,))
            if canon and str(canon).strip().upper() == 'SOVEREIGN':
                cursor.execute('UPDATE products SET canonical_lineage = NULL WHERE id = ?', (pid,))

            fixed += 1
        except Exception as e:
            print(f"Failed to clean product id={pid} ({name}): {e}")

    conn.commit()
    print(f"Cleaned {fixed} product(s) with 'SOVEREIGN' values")
    conn.close()

if __name__ == '__main__':
    # Default DB path inside uploads directory
    base_dir = Path(__file__).parents[2]
    uploads_dir = base_dir / 'uploads'
    db_file = uploads_dir / 'product_database_AGT_Bothell.db'
    if not db_file.exists():
        print(f"Database not found: {db_file}")
        sys.exit(1)
    clean_sovereign_values(str(db_file))
