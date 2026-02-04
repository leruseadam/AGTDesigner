#!/usr/bin/env python3
"""
Delete Products Without JSON
============================
Deletes database rows in the products table that have no JSON column value
(NULL or empty string).

Usage:
    Local:   python delete_products_no_json.py
    Dry run: python delete_products_no_json.py --dry-run
    Web:     python delete_products_no_json.py --web  # generates delete_products_no_json_web.py
"""

import argparse
import logging
import sqlite3
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def delete_products_no_json(db_path, dry_run=False):
    """Delete products where JSON is NULL or empty. Returns number deleted."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        if "JSON" not in columns:
            logger.warning(f"JSON column does not exist in {Path(db_path).name}")
            conn.close()
            return 0

        # Count rows to delete: JSON IS NULL OR JSON = '' or whitespace-only
        cursor.execute(
            'SELECT COUNT(*) FROM products WHERE "JSON" IS NULL OR TRIM(COALESCE("JSON", \'\')) = \'\''
        )
        to_delete = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM products")
        total = cursor.fetchone()[0]

        db_name = Path(db_path).name if isinstance(db_path, str) else db_path.name
        logger.info(f"  {db_name}: {total} total, {to_delete} without JSON (will delete)")

        if to_delete == 0:
            conn.close()
            return 0

        if dry_run:
            logger.info(f"  [DRY RUN] Would delete {to_delete} rows. Run without --dry-run to apply.")
            conn.close()
            return to_delete

        cursor.execute(
            'DELETE FROM products WHERE "JSON" IS NULL OR TRIM(COALESCE("JSON", \'\')) = \'\''
        )
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        logger.info(f"  ✅ Deleted {deleted} products without JSON in {db_name}")
        return deleted

    except Exception as e:
        db_name = Path(db_path).name if isinstance(db_path, str) else str(db_path)
        logger.error(f"Error in {db_name}: {e}")
        if "conn" in dir() and conn:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass
        return 0


def run_local(dry_run=False):
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        logger.error("uploads folder not found")
        return

    db_files = list(uploads_dir.glob("product_database_*.db"))
    logger.info(f"Found {len(db_files)} database(s)")

    if not db_files:
        logger.warning("No product_database_*.db files found")
        return

    total_deleted = 0
    for db_path in sorted(db_files):
        logger.info(f"\n{'='*60}\nProcessing: {db_path.name}")
        total_deleted += delete_products_no_json(str(db_path), dry_run=dry_run)

    logger.info(f"\n{'='*60}")
    if dry_run:
        logger.info(f"Dry run complete. Would delete {total_deleted} total rows.")
    else:
        logger.info(f"✅ Deleted {total_deleted} total products (no JSON).")


def generate_web_script():
    script = '''#!/usr/bin/env python3
"""
Web: Delete products that have no JSON column value.
Run on PythonAnywhere. Update UPLOADS_DIR below.
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

UPLOADS_DIR = '/home/YOUR_USERNAME/labelMaker/uploads'  # <-- UPDATE THIS


def delete_products_no_json(db_path, dry_run=False):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(products)")
        if "JSON" not in [row[1] for row in cursor.fetchall()]:
            conn.close()
            return 0
        cursor.execute(
            'SELECT COUNT(*) FROM products WHERE "JSON" IS NULL OR TRIM(COALESCE("JSON", \\'\\')) = \\'\\''
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
            'DELETE FROM products WHERE "JSON" IS NULL OR TRIM(COALESCE("JSON", \\'\\')) = \\'\\''
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
    total = 0
    for db_path in sorted(db_files):
        total += delete_products_no_json(str(db_path), dry_run=False)
    logger.info(f"Total deleted: {total}")


if __name__ == "__main__":
    main()
'''
    out = Path("delete_products_no_json_web.py")
    out.write_text(script, encoding="utf-8")
    logger.info(f"Generated {out}. Update UPLOADS_DIR and run on server.")


def main():
    parser = argparse.ArgumentParser(description="Delete products with no JSON column value")
    parser.add_argument("--dry-run", action="store_true", help="Only report counts, do not delete")
    parser.add_argument("--web", action="store_true", help="Generate script for web (PythonAnywhere)")
    args = parser.parse_args()

    if args.web:
        generate_web_script()
    else:
        run_local(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
