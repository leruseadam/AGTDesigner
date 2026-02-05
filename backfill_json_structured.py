#!/usr/bin/env python3
"""
Script to backfill existing database records with structured JSON data
including lineage information for DOCX generation.
"""

import sqlite3
import json
import sys
import os

# Add src to path
sys.path.append('src')

def backfill_json_column():
    """Update existing database records with structured JSON data."""

    db_path = "uploads/product_database_AGT_Bothell.db"

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all products with existing data
        cursor.execute("""
            SELECT id, "Product Name*", Description, "Product Type*", "Product Brand",
                   "Product Strain", Vendor, Price, "Weight*", Units, "THC test result",
                   "CBD test result", DOH, Ratio, Lineage
            FROM products
            WHERE "Product Name*" IS NOT NULL AND "Product Name*" != ''
        """)

        rows = cursor.fetchall()
        print(f"Found {len(rows)} products to update")

        updated_count = 0
        for row in rows:
            (product_id, product_name, description, product_type, product_brand,
             product_strain, vendor, price, weight, units, thc_result,
             cbd_result, doh, ratio, lineage) = row

            # Create structured JSON object
            product_json = {
                "product_name": product_name or "",
                "description": description or "",
                "lineage": lineage or "HYBRID",
                "product_type": product_type or "",
                "product_brand": product_brand or "",
                "product_strain": product_strain or "",
                "vendor": vendor or "",
                "price": str(price) if price else "",
                "weight": str(weight) if weight else "",
                "units": units or "",
                "thc_result": str(thc_result) if thc_result else "",
                "cbd_result": str(cbd_result) if cbd_result else "",
                "doh": doh or "",
                "ratio": ratio or "",
                "source": "Database Backfill"
            }

            # Convert to JSON string
            json_str = json.dumps(product_json, ensure_ascii=False)

            # Update the record
            cursor.execute("""
                UPDATE products
                SET "JSON" = ?
                WHERE id = ?
            """, (json_str, product_id))

            updated_count += 1

            if updated_count % 100 == 0:
                print(f"Updated {updated_count} records...")

        conn.commit()
        print(f"✅ Successfully updated {updated_count} records with structured JSON data")

        # Verify the update
        cursor.execute("""
            SELECT "JSON" FROM products
            WHERE "JSON" IS NOT NULL AND "JSON" != ''
            LIMIT 1
        """)
        sample_json = cursor.fetchone()
        if sample_json:
            try:
                parsed = json.loads(sample_json[0])
                print(f"✅ Sample parsed JSON contains lineage: {parsed.get('lineage')}")
            except:
                print("❌ Sample JSON parsing failed")

    except Exception as e:
        print(f"❌ Error during backfill: {e}")
        conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    backfill_json_column()