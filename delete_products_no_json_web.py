#!/usr/bin/env python3
"""
Web: Delete products that have no JSON column value.
Run on PythonAnywhere. Update UPLOADS_DIR below if needed.
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# PythonAnywhere: project directory is typically /home/USERNAME/AGTDesigner
UPLOADS_DIR = '/home/adamcordova/AGTDesigner/uploads'


def delete_products_no_json(db_path, dry_run=False):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(products)")
        if "JSON" not in [row[1] for row in cursor.fetchall()]:
            conn.close()
            return 0
        cursor.execute(
            'SELECT COUNT(*) FROM products WHERE "JSON" IS NULL OR TRIM(COALESCE("JSON", \'\')) = \'\''
        )
        to_delete = cursor.fetchone()[0]
        if to_delete == 0:
            conn.close()
            return 0
        if dry_run:
            logger.info(f"  [DRY RUN] Would delete {to_delete} rows in {Path(db_path).name}")
            conn.close()
            return to_delete
        cursor.execute(
            'DELETE FROM products WHERE "JSON" IS NULL OR TRIM(COALESCE("JSON", \'\')) = \'\''
        )
        n = cursor.rowcount
        conn.commit()
        conn.close()
        logger.info(f"  Deleted {n} products in {Path(db_path).name}")
        return n
    except Exception as e:
        logger.error(f"Error: {e}")
        return 0


def main():
    uploads_dir = Path(UPLOADS_DIR)
    if not uploads_dir.exists():
        logger.error(f"UPLOADS_DIR not found: {UPLOADS_DIR}")
        return
    db_files = list(uploads_dir.glob("product_database_*.db"))
    logger.info(f"Found {len(db_files)} database(s)")
    total = 0
    for db_path in sorted(db_files):
        total += delete_products_no_json(str(db_path), dry_run=False)
    logger.info(f"Total deleted: {total}")


if __name__ == "__main__":
    main()
