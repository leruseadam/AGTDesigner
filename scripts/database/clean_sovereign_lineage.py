# Script to remove all 'SOVEREIGN' values from canonical_lineage, Lineage, and sovereign_lineage columns in products and strains tables
import sqlite3
from datetime import datetime

def clean_sovereign_values(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Clean products table only (Lineage column)
    cursor.execute("""
        UPDATE products
        SET "Lineage" = NULL
        WHERE "Lineage" = 'SOVEREIGN'
    """)
    conn.commit()
    print("All 'SOVEREIGN' values removed from database.")
    conn.close()

if __name__ == "__main__":
    # Update this path if needed
    db_path = "AGT_Bothell"
    clean_sovereign_values(db_path)
