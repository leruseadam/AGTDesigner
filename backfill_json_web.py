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
import re
from pathlib import Path
from datetime import datetime

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
    """
    Load ORIGINAL Excel Description values (before any transformation).
    
    CRITICAL: This function reads the RAW Excel file BEFORE excel_processor transforms it.
    The Description values here should be the FULL original descriptions (e.g., "Product Name by Vendor - 1g"),
    NOT the shortened transformed versions (e.g., "Product Name").
    
    If the Excel file has already been processed and saved with transformed descriptions,
    this function will read transformed values. Make sure to use the ORIGINAL uploaded Excel file.
    """
    try:
        # Read Excel - get ALL rows DIRECTLY from file (no processing)
        # This should be the ORIGINAL Excel file before excel_processor transforms it
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        logger.info(f"  Reading Excel file: {Path(excel_path).name}")
        logger.info(f"  Excel columns found: {list(df.columns)}")
        logger.info(f"  Total rows in Excel file: {len(df)}")
        logger.info(f"  Non-null rows: {df.notna().any(axis=1).sum()}")
        logger.info(f"  ⚠️  IMPORTANT: This must be the ORIGINAL Excel file (before processing)")
        logger.info(f"     If descriptions look shortened, the file may have been processed already")

        # Find Description column - be flexible with name matching
        # Also check if Product Name column contains full descriptions (may be mislabeled)
        description_col = None
        for col in df.columns:
            col_clean = str(col).strip().lower()
            if 'description' in col_clean:
                description_col = col
                logger.info(f"  Found Description column: '{col}'")
                break
        
        # If no Description column found, check if Product Name column has full descriptions
        # (Sometimes the full descriptions are in Product Name column)
        if not description_col:
            logger.warning(f"  ⚠️  No 'Description' column found")
            logger.info(f"  Checking if Product Name column contains full descriptions...")
            
            # Try to find Product Name column first to check its content
            temp_product_name_col = None
            for col_name in ['Product Name*', 'ProductName', 'Product Name', 'ProductName*']:
                if col_name in df.columns:
                    temp_product_name_col = col_name
                    break
            
            if temp_product_name_col:
                # Sample Product Name values to see if they look like full descriptions
                sample_pnames = df[temp_product_name_col].dropna().head(3).tolist()
                avg_len = sum(len(str(p).strip()) for p in sample_pnames) / len(sample_pnames) if sample_pnames else 0
                
                # If Product Name values are long (like "Product by Vendor - Weight"), 
                # they might actually be the descriptions
                if avg_len > 30:  # Full descriptions are usually longer
                    logger.warning(f"  ⚠️  Product Name column contains long values (avg {avg_len:.1f} chars)")
                    logger.warning(f"     These may be the full descriptions")
                    logger.warning(f"     Sample: '{str(sample_pnames[0])[:80] if sample_pnames else 'N/A'}'")
                    logger.error(f"  ❌ Cannot proceed - need a 'Description' column with full product descriptions")
                    logger.error(f"  Available columns: {list(df.columns)}")
                    return {}
            
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
        
        # CRITICAL: Verify Description column has actual values (not empty)
        description_non_null = df[description_col].notna().sum()
        description_non_empty = (df[description_col].astype(str).str.strip() != '').sum()
        logger.info(f"  Description column stats:")
        logger.info(f"     Non-null values: {description_non_null}/{len(df)}")
        logger.info(f"     Non-empty values: {description_non_empty}/{len(df)}")
        
        if description_non_empty == 0:
            logger.error(f"  ❌ Description column is EMPTY - cannot backfill JSON column")
            logger.error(f"     All Description values are null or empty")
            return {}
        
        # Sample a few Description values to verify they're not Product Names
        # (Now that product_name_col is defined, we can safely use it)
        sample_descriptions = df[description_col].dropna().head(5).tolist()
        sample_product_names = df[product_name_col].head(5).tolist()
        logger.info(f"  Sample Description values (from '{description_col}' column):")
        for i, desc in enumerate(sample_descriptions[:5]):
            desc_str = str(desc)[:100]
            logger.info(f"     {i+1}. '{desc_str}'")
        logger.info(f"  Sample Product Name values (from '{product_name_col}' column, for comparison):")
        for i, pname in enumerate(sample_product_names[:5]):
            pname_str = str(pname)[:100]
            logger.info(f"     {i+1}. '{pname_str}'")
        
        # Check if Description values look transformed (shortened)
        desc_lengths = [len(str(d).strip()) for d in sample_descriptions if d]
        pname_lengths = [len(str(p).strip()) for p in sample_product_names if p]
        avg_desc_len = sum(desc_lengths) / len(desc_lengths) if desc_lengths else 0
        avg_pname_len = sum(pname_lengths) / len(pname_lengths) if pname_lengths else 0
        
        if avg_desc_len > 0 and avg_pname_len > 0:
            if avg_desc_len < avg_pname_len * 0.7:
                logger.warning(f"  ⚠️  WARNING: Description values are shorter than Product Names")
                logger.warning(f"     Avg Description length: {avg_desc_len:.1f} chars")
                logger.warning(f"     Avg Product Name length: {avg_pname_len:.1f} chars")
                logger.warning(f"     ⚠️  Description column may be TRANSFORMED")
                logger.warning(f"     ⚠️  Using Description values anyway - make sure you're using ORIGINAL Excel file")
                logger.warning(f"     ⚠️  Original Description should contain raw SKU format like:")
                logger.warning(f"        'Apple Fritter Full Spectrum Hash Rosin by Collections Cannabis - 1g'")
            elif avg_desc_len >= avg_pname_len:
                logger.info(f"  ✅ Description values look complete (avg length: {avg_desc_len:.1f} chars)")
            else:
                logger.info(f"  ℹ️  Description values (avg length: {avg_desc_len:.1f} chars) - proceeding")

        products_data = {}  # Store ALL products with product names
        skipped_empty_name = 0
        rows_with_descriptions = 0
        rows_without_descriptions = 0
        
        # Process EVERY SINGLE ROW - add ALL products with names, even without descriptions
        # CRITICAL: Read RAW Description values directly from Excel BEFORE any processing
        # These are the ORIGINAL untransformed descriptions that excel_processor captures into JSON
        for idx, row in df.iterrows():
            # Get product name - handle NaN/empty properly
            product_name_raw = row.get(product_name_col, '')
            if product_name_raw is None or (isinstance(product_name_raw, float) and pd.isna(product_name_raw)):
                product_name = ''
            else:
                product_name = str(product_name_raw).strip()
            
            # Skip if no product name (can't add product without a name)
            if not product_name:
                skipped_empty_name += 1
                continue
            
            # CRITICAL: Read from Description column (pre-transformed values)
            # Description column contains values like: "Pure Prana Pulse AIO Disposable - Rainbow Belts Live Resin - Hybrid - 1mL"
            # Product Name* column contains raw SKU like: "Rainbow Belts Pure Live Resin Disposable Vape by Bodhi High - 1g"
            # We want Description column values moved to JSON column
            description_raw = row.get(description_col, '')
            raw_description = ''
            
            if description_raw is not None:
                if isinstance(description_raw, float):
                    if not pd.isna(description_raw):
                        raw_description = str(description_raw).strip()
                else:
                    raw_description = str(description_raw).strip()
            
            # CRITICAL: Use Description column value AS-IS (no validation, no skipping)
            # Description may match Product Name - that's fine, use it anyway
            # Only skip if Description is truly empty/null
            
            # Clean up the raw description value
            description_lower = raw_description.lower().strip() if raw_description else ''
            if not raw_description or description_lower in ['nan', 'none', '', 'null', 'n/a', 'na']:
                # Empty Description - skip this row
                rows_without_descriptions += 1
                continue
            else:
                rows_with_descriptions += 1
            
            # Store ONLY the Description column value in JSON
            # CRITICAL: Moving Description column values (pre-transformed) to JSON column
            # Description contains values like: "Pure Prana Pulse AIO Disposable - Rainbow Belts Live Resin - Hybrid - 1mL"
            # NOT Product Name values like: "Rainbow Belts Pure Live Resin Disposable Vape by Bodhi High - 1g"
            description = raw_description
            
            # Debug logging for first few rows to verify what we're storing
            if rows_with_descriptions <= 3:
                logger.info(f"  📝 Sample row {rows_with_descriptions}:")
                logger.info(f"     Product Name* (raw SKU): '{product_name[:80]}'")
                logger.info(f"     Description (pre-transformed): '{row.get(description_col, '')[:80] if description_col else 'N/A'}'")
                logger.info(f"     JSON value to store: '{description[:80]}'")
                logger.info(f"     ✅ Moving Description column (pre-transformed) to JSON column")

            # Store by normalized product name - ONLY store if we have a description
            # products_data format: {product_name_lower: (product_name, description)}
            # - product_name = Product Name* column (raw SKU) - used ONLY for matching
            # - description = Description column (pre-transformed) - moved to JSON column
            product_name_lower = product_name.lower()
            if description:  # Only store if we have a Description value (no fallbacks)
                if product_name_lower in products_data:
                    existing_desc = products_data[product_name_lower][1]
                    # Keep the one with longer description (more likely to be complete)
                    if len(description) > len(existing_desc):
                        products_data[product_name_lower] = (product_name, description)
                        logger.debug(f"  Replaced duplicate '{product_name}' with longer description")
                else:
                    products_data[product_name_lower] = (product_name, description)
        
        logger.info(f"  ✅ Loaded {len(products_data)} products from Excel")
        logger.info(f"  📊 Products with descriptions: {rows_with_descriptions}")
        logger.info(f"  📊 Products without descriptions (skipped - no fallback): {rows_without_descriptions}")
        logger.info(f"  📈 Total products with descriptions: {len(products_data)}/{len(df)} rows ({100*len(products_data)/max(len(df),1):.1f}%)")
        logger.info(f"  ⚠️  IMPORTANT: Only products with Excel Description values will be updated")
        logger.info(f"     Products without descriptions will be skipped (no Product Name fallback)")
        if skipped_empty_name > 0:
            logger.info(f"  ℹ️  Skipped {skipped_empty_name} rows with empty product names")

        return products_data
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


def update_json_column(db_path, products_data):
    """Update JSON column from Excel data AND INSERT missing products."""
    try:
        if not products_data:
            logger.warning("No Excel products provided - skipping update")
            return 0

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, "Product Name*" FROM products')
        products = cursor.fetchall()
        
        total_products = len(products)
        logger.info(f"  Found {total_products} total products in database")
        logger.info(f"  Loaded {len(products_data)} Excel products to process")

        # Normalize Excel data for matching
        normalized_excel_data = {}
        for excel_name_lower, (original_name, json_value) in products_data.items():
            normalized_key = normalize_name(excel_name_lower)
            if normalized_key:
                normalized_excel_data[normalized_key] = (original_name, json_value)

        updated_from_excel = 0
        inserted_new_products = 0
        unmatched_excel = set(normalized_excel_data.keys())
        unmatched_db = []

        # Build a set of existing product names for quick lookup
        existing_products = {}
        for product_id, product_name in products:
            if product_name:
                db_name_normalized = normalize_name(product_name)
                existing_products[db_name_normalized] = product_id

        # Match and update existing products
        logger.info(f"  Matching and updating existing products...")
        for normalized_name, (original_name, json_value) in normalized_excel_data.items():
            # CRITICAL: original_name is ONLY used for matching, NEVER as JSON value
            # json_value comes from Excel Description column ONLY
            if normalized_name in existing_products:
                # Product exists - update JSON column with Excel Description ONLY
                product_id = existing_products[normalized_name]
                cursor.execute(
                    'UPDATE products SET "JSON" = ? WHERE id = ?',
                    (json_value, product_id)  # json_value = Excel Description, NOT Product Name
                )
                updated_from_excel += 1
                unmatched_excel.discard(normalized_name)
            else:
                # Product doesn't exist - will insert after updates
                pass
        
        # Commit updates first
        conn.commit()
        
        # Now INSERT all products that don't exist
        logger.info(f"  Inserting {len(unmatched_excel)} new products from Excel...")
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        today = datetime.now().strftime('%Y-%m-%d')
        
        for normalized_name in list(unmatched_excel):
            original_name, json_value = normalized_excel_data[normalized_name]
            # CRITICAL: original_name is Product Name (used for matching and required "Product Name*" field)
            # json_value is Excel Description ONLY - NEVER use Product Name as JSON value
            
            # Insert new product with minimal required fields
            try:
                cursor.execute('''
                    INSERT INTO products (
                        "Product Name*", 
                        normalized_name,
                        "Product Type*",
                        "Description",
                        "JSON",
                        first_seen_date,
                        last_seen_date,
                        created_at,
                        updated_at,
                        "State",
                        "Is Sample? (yes/no)",
                        "Is MJ product?(yes/no)",
                        "Discountable? (yes/no)",
                        "Room*",
                        "Is Archived? (yes/no)",
                        "Medical Only (Yes/No)",
                        "Source"
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    original_name,           # Product Name* (required field - NOT used as JSON)
                    normalized_name,         # normalized_name (for matching - NOT used as JSON)
                    'Unknown',               # Product Type* (required)
                    json_value,              # Description (Excel Description - NOT Product Name)
                    json_value,              # JSON (Excel Description ONLY - NEVER Product Name)
                    today,                   # first_seen_date
                    today,                   # last_seen_date
                    now,                     # created_at
                    now,                     # updated_at
                    'active',                # State
                    'no',                    # Is Sample?
                    'yes',                   # Is MJ product?
                    'yes',                   # Discountable?
                    'Default',               # Room*
                    'no',                    # Is Archived?
                    'No',                    # Medical Only
                    'Excel Backfill'         # Source
                ))
                inserted_new_products += 1
            except sqlite3.IntegrityError as e:
                # Product might already exist (race condition or unique constraint)
                logger.warning(f"  ⚠️  Could not insert '{original_name}': {e}")
                # Try to update it instead
                cursor.execute('SELECT id FROM products WHERE normalized_name = ?', (normalized_name,))
                result = cursor.fetchone()
                if result:
                    cursor.execute('UPDATE products SET "JSON" = ? WHERE id = ?', (json_value, result[0]))
                    updated_from_excel += 1
        
        # Commit inserts
        conn.commit()
        conn.close()
        
        total_processed = updated_from_excel + inserted_new_products
        logger.info(f"  ✅ Updated {updated_from_excel} existing products from Excel")
        logger.info(f"  ✅ Inserted {inserted_new_products} new products from Excel")
        logger.info(f"  📊 Total processed: {total_processed} products")
        
        return total_processed
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
    products_data = {}
    for excel_path in bothell_excel_files:
        logger.info(f"\nProcessing Excel: {excel_path.name}")
        excel_products = load_excel_descriptions(str(excel_path))
        if excel_products:
            products_data.update(excel_products)
            logger.info(f"  Loaded {len(excel_products)} products")

    if not products_data:
        logger.error("❌ No products found in Bothell Excel file(s) - nothing to backfill")
        return

    # Update Bothell database - process ALL products from Excel
    ensure_json_column_exists(str(db_path))
    updated = update_json_column(str(db_path), products_data)
    logger.info(f"✅ Processed {updated} products in Bothell database from Excel")

    logger.info("\n✅ Bothell backfill complete!")


if __name__ == '__main__':
    main()
