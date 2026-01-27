#!/usr/bin/env python3
"""
Emergency script to add sovereign_lineage column to products table.
Run this to immediately add the column without waiting for app restart.
"""

import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_sovereign_lineage_column(db_path):
    """Add sovereign_lineage column to products table if it doesn't exist."""
    try:
        # Skip obviously invalid/empty files early
        try:
            if os.path.getsize(db_path) == 0:
                logger.warning(f"⚠️  Skipping empty DB file: {db_path}")
                return False
        except OSError:
            # If file is not accessible for size check, continue and let sqlite report the error
            pass

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Confirm 'products' table exists before attempting schema changes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        table_exists = cursor.fetchone() is not None
        if not table_exists:
            logger.warning(f"⚠️  Skipping {db_path}: no 'products' table found")
            conn.close()
            return False

        # Check if column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'sovereign_lineage' in columns:
            logger.info(f"✅ sovereign_lineage column already exists in {db_path}")
            return True

        # Add the column
        logger.info(f"Adding sovereign_lineage column to {db_path}...")
        cursor.execute("ALTER TABLE products ADD COLUMN sovereign_lineage TEXT")
        conn.commit()
        logger.info(f"✅ Successfully added sovereign_lineage column to {db_path}")

        conn.close()
        return True

    except Exception as e:
        logger.error(f"❌ Error adding column to {db_path}: {e}")
        return False

def main():
    # Find all product databases in uploads directory
    base_dir = os.path.dirname(__file__)
    uploads_dir = os.path.join(base_dir, 'uploads')

    # Look for all .db files
    db_files = []

    # Check uploads directory
    if os.path.exists(uploads_dir):
        for root, dirs, files in os.walk(uploads_dir):
            for file in files:
                if file.endswith('.db') or file.endswith('.sqlite'):
                    db_files.append(os.path.join(root, file))

    # Also check base directory
    for file in os.listdir(base_dir):
        if file.endswith('.db') or file.endswith('.sqlite'):
            db_files.append(os.path.join(base_dir, file))

    if not db_files:
        logger.warning("No database files found in data directory")
        return

    logger.info(f"Found {len(db_files)} database file(s)")

    success_count = 0
    for db_path in db_files:
        logger.info(f"\nProcessing: {db_path}")
        if add_sovereign_lineage_column(db_path):
            success_count += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"Summary: Successfully updated {success_count}/{len(db_files)} databases")
    logger.info(f"{'='*60}")

if __name__ == '__main__':
    main()
