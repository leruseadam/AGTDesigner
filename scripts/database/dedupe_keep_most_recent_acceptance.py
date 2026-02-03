#!/usr/bin/env python3
"""
Deduplicate products: keep the row with the most recent Accepted Date (or updated_at).
====================================================================================
Finds duplicates by (normalized_name, Vendor/Supplier*, Product Brand) and keeps
only the row with the latest acceptance date; deletes the rest.

Works on:
  - Local: uploads/product_database_*.db (or --db path)
  - PythonAnywhere: set UPLOADS_DIR or pass --db

Usage:
  python dedupe_keep_most_recent_acceptance.py                    # all DBs in uploads
  python dedupe_keep_most_recent_acceptance.py --db path/to.db    # single DB
  python dedupe_keep_most_recent_acceptance.py --dry-run          # report only, no deletes
"""

import os
import re
import sys
import sqlite3
import logging
import argparse
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Project root: script may live in scripts/database/ or repo root
SCRIPT_DIR = Path(__file__).resolve().parent
_candidates = [SCRIPT_DIR.parent, SCRIPT_DIR.parent.parent, Path.cwd()]
BASE_DIR = next((r for r in _candidates if (r / "uploads").is_dir()), SCRIPT_DIR.parent)
UPLOADS_DIR = os.environ.get("UPLOADS_DIR", str(BASE_DIR / "uploads"))

# Date parsing: support common formats
DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%m/%d/%Y",
    "%m-%d-%Y",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
]


def parse_date(s):
    """Parse a date string; return (datetime or None, sort_key). Null/empty -> (None, '')."""
    if s is None or (isinstance(s, str) and not s.strip()):
        return None, ""
    s = str(s).strip()
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(s[: len(fmt) + 12].split(".")[0].split("+")[0], fmt)
            return dt, dt.isoformat()
        except ValueError:
            continue
    # Fallback: try YYYY-MM-DD substring
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        try:
            dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return dt, dt.isoformat()
        except ValueError:
            pass
    return None, ""


def get_products_columns(cursor):
    """Return list of product column names."""
    cursor.execute("PRAGMA table_info(products)")
    return [row[1] for row in cursor.fetchall()]


def run_dedupe(db_path: str, dry_run: bool = False) -> dict:
    """
    Deduplicate products in the DB: keep most recent by Accepted Date (then updated_at).
    Returns dict with deleted_count, duplicate_groups, final_count, success, message.
    """
    if not os.path.isfile(db_path):
        return {"success": False, "error": f"File not found: {db_path}", "deleted_count": 0}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cols = get_products_columns(cursor)
    has_accepted = '"Accepted Date"' in cols
    if not has_accepted:
        logger.warning(f"DB has no 'Accepted Date' column; using updated_at only: {db_path}")

    # Duplicate key: same normalized_name, vendor, brand
    cursor.execute("""
        SELECT normalized_name, "Vendor/Supplier*", "Product Brand", COUNT(*) AS cnt
        FROM products
        GROUP BY normalized_name, "Vendor/Supplier*", "Product Brand"
        HAVING cnt > 1
    """)
    duplicate_groups = cursor.fetchall()
    total_groups = len(duplicate_groups)
    deleted_count = 0

    select_cols = 'id, "Product Name*", updated_at'
    if has_accepted:
        select_cols = 'id, "Product Name*", "Accepted Date", updated_at'

    for row in duplicate_groups:
        norm_name, vendor, brand = row[0], row[1], row[2]
        # Skip groups with NULL keys: WHERE col = NULL matches no rows in SQL
        if norm_name is None or vendor is None or brand is None:
            logger.debug("Skipping duplicate group with NULL key")
            continue
        cursor.execute(f"""
            SELECT {select_cols}
            FROM products
            WHERE normalized_name = ? AND "Vendor/Supplier*" = ? AND "Product Brand" = ?
        """, (norm_name, vendor, brand))
        entries = [dict(r) for r in cursor.fetchall()]
        if not entries:
            logger.warning("Duplicate group returned no rows (skipping): %r", (norm_name, vendor, brand))
            continue

        def sort_key(e):
            accepted = e.get("Accepted Date") if has_accepted else None
            updated = e.get("updated_at") or ""
            _, accepted_key = parse_date(accepted)
            _, updated_key = parse_date(updated) if updated else (None, "")
            primary = accepted_key if accepted_key else updated_key
            return (primary, updated_key)

        entries_sorted = sorted(entries, key=sort_key, reverse=True)
        keep_id = entries_sorted[0]["id"]
        ids_to_delete = [e["id"] for e in entries_sorted[1:]]

        if dry_run:
            logger.info(
                f"[DRY-RUN] Would keep id={keep_id} '{entries_sorted[0]['Product Name*']}', "
                f"delete ids={ids_to_delete}"
            )
            deleted_count += len(ids_to_delete)
            continue

        for pid in ids_to_delete:
            cursor.execute("DELETE FROM products WHERE id = ?", (pid,))
            deleted_count += 1
        logger.debug(f"Kept id={keep_id}, deleted {len(ids_to_delete)} duplicates")

    if not dry_run:
        conn.commit()

    cursor.execute("SELECT COUNT(*) FROM products")
    final_count = cursor.fetchone()[0]
    conn.close()

    return {
        "success": True,
        "db_path": db_path,
        "duplicate_groups": total_groups,
        "deleted_count": deleted_count,
        "final_product_count": final_count,
        "message": f"Deleted {deleted_count} duplicate(s) from {total_groups} groups. {final_count} products remaining.",
    }


def main():
    ap = argparse.ArgumentParser(description="Dedupe products, keeping most recent Accepted Date.")
    ap.add_argument("--db", type=str, help="Path to a single product_database_*.db file")
    ap.add_argument("--dry-run", action="store_true", help="Only report what would be deleted")
    ap.add_argument("--uploads", type=str, default=UPLOADS_DIR, help="Uploads directory (default: project uploads)")
    args = ap.parse_args()

    if args.db:
        paths = [args.db]
    else:
        uploads = Path(args.uploads)
        if not uploads.is_dir():
            logger.error(f"Uploads directory not found: {uploads}")
            sys.exit(1)
        paths = sorted(uploads.glob("product_database_*.db"))

    if not paths:
        logger.warning("No product_database_*.db files found.")
        sys.exit(0)

    mode = " [DRY-RUN]" if args.dry_run else ""
    logger.info(f"Running duplicate cleanup (keep most recent acceptance date){mode} on {len(paths)} DB(s)")

    total_deleted = 0
    for db_path in paths:
        db_path = str(db_path)
        logger.info(f"Processing: {db_path}")
        result = run_dedupe(db_path, dry_run=args.dry_run)
        if not result["success"]:
            logger.error(result.get("error", result.get("message", "Unknown error")))
            continue
        total_deleted += result["deleted_count"]
        logger.info(result["message"])

    logger.info(f"Done. Total rows removed across all DBs: {total_deleted}")


if __name__ == "__main__":
    main()
