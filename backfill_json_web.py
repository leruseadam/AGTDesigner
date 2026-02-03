#!/usr/bin/env python3
"""
Web Database JSON Column Backfill Script
=========================================
Run this script on PythonAnywhere to backfill the JSON column.

Usage:
    1. Upload this script to your PythonAnywhere account
    2. Open a Bash console
    3. cd to your project directory
    4. Run: python backfill_json_web.py
"""

import os
import sys
import sqlite3
import pandas as pd
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Update this path to match your PythonAnywhere setup
UPLOADS_DIR = '/home/adamcordova/AGTDesigner/uploads'  # <-- UPDATE THIS

STORE_PATTERNS = {
    'bothell': 'AGT_Bothell',
    'burien': 'AGT_Burien',
    'goldbar': 'AGT_Goldbar',
    'lynnwood': 'AGT_Lynnwood',
    'seattle': 'AGT_Seattle',
    'shoreline': 'AGT_Shoreline',
    'walla': 'AGT_Walla_Walla',
}


def get_store_from_filename(filename):
    filename_lower = filename.lower()
    for pattern, store_name in STORE_PATTERNS.items():
        if pattern in filename_lower:
            return store_name
    return None


def ensure_json_column_exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'JSON' not in columns:
            logger.info(f"Adding JSON column to {db_path}")
            cursor.execute('ALTER TABLE products ADD COLUMN "JSON" TEXT')
            conn.commit()

        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False


def load_excel_descriptions(excel_path):
    try:
        # Read Excel - get ALL rows
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        logger.info(f"  Excel columns found: {list(df.columns)}")
        logger.info(f"  Total rows in Excel file: {len(df)}")
        logger.info(f"  Non-null rows: {df.notna().any(axis=1).sum()}")

        # Find Description column - be flexible with name matching
        description_col = None
        for col in df.columns:
            col_clean = str(col).strip().lower()
            if 'description' in col_clean:
                description_col = col
                logger.info(f"  Found Description column: '{col}'")
                break
        
        if not description_col:
            logger.error(f"  ❌ No Description column found in Excel file")
            logger.error(f"  Available columns: {list(df.columns)}")
            return {}

        # Find Product Name column - be flexible
        product_name_col = None
        for col_name in ['Product Name*', 'ProductName', 'Product Name', 'ProductName*']:
            if col_name in df.columns:
                product_name_col = col_name
                logger.info(f"  Found Product Name column: '{col_name}'")
                break
        
        # If still not found, try case-insensitive match
        if not product_name_col:
            for col in df.columns:
                col_clean = str(col).strip().lower()
                if 'product' in col_clean and 'name' in col_clean:
                    product_name_col = col
                    logger.info(f"  Found Product Name column (flexible match): '{col}'")
                    break

        if not product_name_col:
            logger.error(f"  ❌ No Product Name column found in Excel file")
            logger.error(f"  Available columns: {list(df.columns)}")
            return {}

        descriptions = {}
        skipped_empty_name = 0
        skipped_empty_desc = 0
        processed = 0
        
        # Process EVERY SINGLE ROW - don't skip anything
        for idx, row in df.iterrows():
            # Get product name - handle NaN/empty properly
            product_name_raw = row.get(product_name_col, '')
            if product_name_raw is None or (isinstance(product_name_raw, float) and pd.isna(product_name_raw)):
                product_name = ''
            else:
                product_name = str(product_name_raw).strip()
            
            # Get description - handle NaN/empty properly  
            description_raw = row.get(description_col, '')
            if description_raw is None or (isinstance(description_raw, float) and pd.isna(description_raw)):
                description = ''
            else:
                description = str(description_raw).strip()
            
            # Skip ONLY if description is truly empty
            if not description or description.lower() in ['nan', 'none', '']:
                skipped_empty_desc += 1
                continue
            
            # If no product name, skip this row (can't match without product name)
            if not product_name:
                skipped_empty_name += 1
                continue

            # Store by normalized product name - PROCESS ALL VALID DESCRIPTIONS
            product_name_lower = product_name.lower()
            descriptions[product_name_lower] = description
            processed += 1
        
        logger.info(f"  ✅ Loaded {len(descriptions)} product descriptions from Excel")
        logger.info(f"  📊 Processed {processed} valid rows out of {len(df)} total rows")
        logger.info(f"  📈 Description coverage: {len(descriptions)}/{len(df)} rows ({100*len(descriptions)/max(len(df),1):.1f}%)")
        if skipped_empty_name > 0:
            logger.warning(f"  ⚠️  Skipped {skipped_empty_name} rows with empty product names (had descriptions but can't match)")
        if skipped_empty_desc > 0:
            logger.info(f"  ℹ️  Skipped {skipped_empty_desc} rows with empty descriptions")

        return descriptions
    except Exception as e:
        logger.error(f"Error loading Excel: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {}


def normalize_name(name):
    """Normalize product name for better matching."""
    if not name:
        return ""
    # Lowercase, strip, normalize whitespace
    normalized = " ".join(str(name).strip().lower().split())
    return normalized


def update_json_column(db_path, descriptions):
    """Update JSON column ONLY from Excel descriptions. No database fallbacks."""
    try:
        if not descriptions:
            logger.warning("No Excel descriptions provided - skipping update")
            return 0

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, "Product Name*" FROM products')
        products = cursor.fetchall()
        
        total_products = len(products)
        logger.info(f"  Found {total_products} total products in database")
        logger.info(f"  Loaded {len(descriptions)} Excel descriptions")

        # Normalize Excel descriptions keys for better matching
        normalized_descriptions = {}
        for excel_name, desc in descriptions.items():
            normalized_key = normalize_name(excel_name)
            if normalized_key:
                normalized_descriptions[normalized_key] = desc

        updated_from_excel = 0
        unmatched_excel = set(normalized_descriptions.keys())
        unmatched_db = []

        # Match products from Excel descriptions
        logger.info(f"  Matching products...")
        for product_id, product_name in products:
            if not product_name:
                unmatched_db.append((product_id, None))
                continue

            db_name_normalized = normalize_name(product_name)
            
            # Try exact match first
            if db_name_normalized in normalized_descriptions:
                desc_value = normalized_descriptions[db_name_normalized]
                cursor.execute(
                    'UPDATE products SET "JSON" = ? WHERE id = ?',
                    (desc_value, product_id)
                )
                updated_from_excel += 1
                unmatched_excel.discard(db_name_normalized)
            else:
                unmatched_db.append((product_id, product_name))
        
        # Commit all updates at once
        conn.commit()

        conn.close()
        
        logger.info(f"  ✅ Updated {updated_from_excel} products from Excel")
        logger.info(f"  📊 Match rate: {updated_from_excel}/{total_products} products ({100*updated_from_excel/max(total_products,1):.1f}%)")
        
        # Show diagnostics for unmatched products
        if unmatched_excel:
            logger.warning(f"  ⚠️  {len(unmatched_excel)} Excel products had no database match:")
            sample_unmatched = list(unmatched_excel)[:5]
            for excel_name in sample_unmatched:
                logger.warning(f"     - Excel: '{excel_name}'")
        
        if unmatched_db:
            logger.info(f"  ℹ️  {len(unmatched_db)} database products had no Excel match")
            if len(unmatched_db) <= 5:
                for product_id, db_name in unmatched_db:
                    logger.info(f"     - DB: '{db_name}'")
        
        return updated_from_excel
    except Exception as e:
        logger.error(f"Error: {e}")
        return 0


def main():
    uploads_dir = Path(UPLOADS_DIR)

    if not uploads_dir.exists():
        logger.error(f"uploads folder not found: {UPLOADS_DIR}")
        logger.error("Please update UPLOADS_DIR at the top of this script")
        return

    # Only process Bothell database
    store_name = 'AGT_Bothell'
    db_path = uploads_dir / f"product_database_{store_name}.db"
    
    if not db_path.exists():
        logger.error(f"Bothell database not found: {db_path}")
        return

    logger.info(f"Processing Bothell database only: {db_path.name}")

    # Find Excel files that match Bothell - REQUIRED
    excel_files = list(uploads_dir.glob('*.xlsx')) + list(uploads_dir.glob('*.xls'))
    bothell_excel_files = [f for f in excel_files if 'bothell' in f.name.lower()]
    
    if not bothell_excel_files:
        logger.error("❌ No Bothell Excel files found - backfill requires a Bothell Excel file")
        logger.error("   Please upload a Bothell Excel file and try again")
        return

    logger.info(f"Found {len(bothell_excel_files)} Bothell Excel file(s)")

    # Process Bothell Excel files - REQUIRED
    descriptions = {}
    for excel_path in bothell_excel_files:
        logger.info(f"\nProcessing Excel: {excel_path.name}")
        excel_descriptions = load_excel_descriptions(str(excel_path))
        if excel_descriptions:
            descriptions.update(excel_descriptions)
            logger.info(f"  Loaded {len(excel_descriptions)} product descriptions")

    if not descriptions:
        logger.error("❌ No descriptions found in Bothell Excel file(s) - nothing to backfill")
        return

    # Update Bothell database - ONLY from Excel, no database fallbacks
    ensure_json_column_exists(str(db_path))
    updated = update_json_column(str(db_path), descriptions)
    logger.info(f"✅ Updated {updated} products in Bothell database from Excel")

    logger.info("\n✅ Bothell backfill complete!")


if __name__ == '__main__':
    main()
