#!/usr/bin/env python3
"""
Improved backfill script for JSON column with better matching and error handling
"""
import os
import sys
import pandas as pd
import sqlite3
import logging
from pathlib import Path
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def improved_backfill_json():
    """Improved backfill with better matching logic"""

    db_path = 'uploads/product_database_AGT_Bothell.db'

    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verify JSON column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'JSON' not in column_names:
            logger.error("JSON column does not exist in database")
            return False

        # Get current status
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM products WHERE JSON IS NULL OR JSON = ''")
        empty_json = cursor.fetchone()[0]

        logger.info(f"📊 Starting backfill: {total_products} total products, {empty_json} need JSON data")

        if empty_json == 0:
            logger.info("✅ All products already have JSON data - no backfill needed")
            return True

        # Get all products that need backfilling
        cursor.execute("""
            SELECT id, "Product Name*", ProductName, "Product Type*"
            FROM products
            WHERE JSON IS NULL OR JSON = ''
        """)
        products_to_fill = cursor.fetchall()

        logger.info(f"📋 Retrieved {len(products_to_fill)} products for backfilling")

        # Find Excel files
        uploads_dir = Path('uploads')
        excel_files = list(uploads_dir.glob('*.xlsx'))

        if not excel_files:
            logger.warning("No Excel files found in uploads directory")
            return False

        logger.info(f"📁 Found {len(excel_files)} Excel files to process")

        # Build a map of product names to descriptions from Excel files
        product_descriptions = defaultdict(list)  # product_name -> list of descriptions

        for excel_file in excel_files:
            try:
                logger.info(f"📖 Processing Excel file: {excel_file.name}")

                df = pd.read_excel(excel_file)

                if 'Description' not in df.columns:
                    logger.warning(f"   No Description column in {excel_file.name}")
                    continue

                # Process descriptions
                original_descriptions = df['Description'].fillna('').astype(str)

                processed_count = 0
                for idx, row in df.iterrows():
                    # Get product name (try multiple column names)
                    product_name = None
                    for col_name in ['Product Name*', 'ProductName', 'Product Name']:
                        if col_name in df.columns:
                            product_name = str(row.get(col_name, '')).strip()
                            if product_name:
                                break

                    if not product_name:
                        continue

                    # Get description
                    description = original_descriptions.iloc[idx] if idx < len(original_descriptions) else ''
                    if description:
                        product_descriptions[product_name].append(description)
                        processed_count += 1

                logger.info(f"   ✅ Extracted {processed_count} descriptions from {excel_file.name}")

            except Exception as e:
                logger.error(f"   ❌ Error processing {excel_file.name}: {e}")
                continue

        logger.info(f"📊 Collected descriptions for {len(product_descriptions)} unique product names")

        # Now backfill the database
        backfilled_count = 0
        skipped_count = 0

        for product_id, db_product_name, db_product_name_alt, product_type in products_to_fill:
            # Try multiple product name variations for matching
            candidate_names = []
            if db_product_name:
                candidate_names.append(db_product_name.strip())
            if db_product_name_alt:
                candidate_names.append(db_product_name_alt.strip())

            # Remove duplicates
            candidate_names = list(set(candidate_names))

            best_description = None
            for candidate in candidate_names:
                if candidate in product_descriptions:
                    # Use the first (most common) description for this product
                    best_description = product_descriptions[candidate][0]
                    break

            if best_description:
                try:
                    cursor.execute("""
                        UPDATE products
                        SET JSON = ?
                        WHERE id = ? AND (JSON IS NULL OR JSON = '')
                    """, (best_description, product_id))

                    if cursor.rowcount > 0:
                        backfilled_count += 1
                        logger.debug(f"✅ Backfilled: {candidate_names[0]} -> {best_description[:50]}...")
                    else:
                        skipped_count += 1

                except Exception as e:
                    logger.warning(f"❌ Error updating product {product_id}: {e}")
                    skipped_count += 1
            else:
                skipped_count += 1
                logger.debug(f"❌ No description found for: {candidate_names}")

        conn.commit()

        # Final verification
        cursor.execute("SELECT COUNT(*) FROM products WHERE JSON IS NOT NULL AND JSON != ''")
        final_filled = cursor.fetchone()[0]

        fill_rate = (final_filled / total_products * 100) if total_products > 0 else 0

        logger.info("🎉 BACKFILL COMPLETE!")
        logger.info(f"   ✅ Backfilled: {backfilled_count} products")
        logger.info(f"   ⏭️  Skipped: {skipped_count} products")
        logger.info(f"   📊 Final status: {final_filled}/{total_products} products have JSON data ({fill_rate:.1f}%)")

        return backfilled_count > 0

    except Exception as e:
        logger.error(f"Backfill failed: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

if __name__ == "__main__":
    success = improved_backfill_json()
    sys.exit(0 if success else 1)
