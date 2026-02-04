#!/usr/bin/env python3
"""
Import All Excel Files from Uploads into Database
==================================================
Finds all .xlsx/.xls in the uploads folder, processes each with ExcelProcessor
(which copies Description -> JSON before any transformation), and stores
results into the store-specific product database.

Does NOT override existing rows: only inserts new products (insert_only=True).

Usage:
    Local:  python import_all_excel_to_db.py
    Web:    python import_all_excel_to_db.py   (set UPLOADS_DIR below or use default)
"""

import logging
import os
import sys
from pathlib import Path

# Project root (directory containing uploads/)
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Uploads dir: default is project uploads/ (override with env UPLOADS_DIR)
UPLOADS_DIR = os.environ.get("UPLOADS_DIR", str(SCRIPT_DIR / "uploads"))

# Store name extraction (matches app.extract_store_from_filename)
STORE_PATTERNS = [
    ("AGT BOTHELL", "AGT_Bothell"),
    ("AGT_BOTHELL", "AGT_Bothell"),
    ("AGT BURIEN", "AGT_Burien"),
    ("AGT_BURIEN", "AGT_Burien"),
    ("AGT GOLDBAR", "AGT_Goldbar"),
    ("AGT_GOLDBAR", "AGT_Goldbar"),
    ("AGT LYNNWOOD", "AGT_Lynnwood"),
    ("AGT_LYNNWOOD", "AGT_Lynnwood"),
    ("AGT SEATTLE", "AGT_Seattle"),
    ("AGT_SEATTLE", "AGT_Seattle"),
    ("AGT SHORELINE", "AGT_Shoreline"),
    ("AGT_SHORELINE", "AGT_Shoreline"),
    ("AGT WALLA WALLA", "AGT_Walla_Walla"),
    ("AGT_WALLA_WALLA", "AGT_Walla_Walla"),
    ("AGT WALLAWALLA", "AGT_Walla_Walla"),
    ("BOTHELL", "AGT_Bothell"),
    ("BURIEN", "AGT_Burien"),
    ("GOLDBAR", "AGT_Goldbar"),
    ("LYNNWOOD", "AGT_Lynnwood"),
    ("SEATTLE", "AGT_Seattle"),
    ("SHORELINE", "AGT_Shoreline"),
    ("WALLA WALLA", "AGT_Walla_Walla"),
    ("WALLAWALLA", "AGT_Walla_Walla"),
]


def extract_store_from_filename(filename: str):
    """Extract store name from filename. Returns e.g. 'AGT_Bothell' or None."""
    if not filename:
        return None
    name_upper = filename.upper().replace("_", " ").replace("-", " ")
    for pattern, store_name in STORE_PATTERNS:
        pattern_n = pattern.replace("_", " ").replace("-", " ")
        if pattern_n in name_upper or pattern in filename.upper():
            return store_name
    return None


def run():
    uploads = Path(UPLOADS_DIR)
    if not uploads.is_dir():
        logger.error("Uploads directory not found: %s", UPLOADS_DIR)
        return

    excel_files = sorted(
        list(uploads.glob("*.xlsx")) + list(uploads.glob("*.xls")),
        key=lambda p: p.name,
    )
    if not excel_files:
        logger.warning("No .xlsx or .xls files found in %s", UPLOADS_DIR)
        return

    logger.info("Found %d Excel file(s) in %s", len(excel_files), UPLOADS_DIR)

    from src.core.data.excel_processor import ExcelProcessor
    from src.core.data.product_database import ProductDatabase

    total_stored = 0
    total_updated = 0
    errors = 0

    for path in excel_files:
        fname = path.name
        store = extract_store_from_filename(fname)
        if not store:
            logger.warning("Skipping %s: no store name in filename (e.g. Bothell, Seattle)", fname)
            continue

        db_path = uploads / f"product_database_{store}.db"
        if not db_path.exists():
            logger.warning("Skipping %s: database not found: %s", fname, db_path.name)
            continue

        logger.info("Processing: %s -> %s", fname, db_path.name)
        try:
            processor = ExcelProcessor(store_name=store)
            if not processor.load_file(str(path)):
                logger.error("Failed to load %s", fname)
                errors += 1
                continue
            if processor.df is None or processor.df.empty:
                logger.warning("No rows in %s", fname)
                continue

            product_db = ProductDatabase(db_path=str(db_path))
            product_db.init_database()
            result = product_db.store_excel_data(processor.df, source_file=fname, insert_only=True)
            stored = result.get("stored", 0)
            updated = result.get("updated", 0)
            total_stored += stored
            total_updated += updated
            logger.info("  -> stored=%s updated=%s", stored, updated)
        except Exception as e:
            logger.exception("Error processing %s: %s", fname, e)
            errors += 1

    logger.info("Done. Total stored=%s updated=%s errors=%s", total_stored, total_updated, errors)


if __name__ == "__main__":
    run()
