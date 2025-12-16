#!/usr/bin/env python3
"""
Simple database sync from Excel - no app dependencies.
"""

import sys
import os
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime

def find_latest_excel():
    """Find the most recent Excel upload."""
    uploads_dir = Path(__file__).parent / 'uploads'
    
    excel_files = []
    for file in uploads_dir.glob('*.xlsx'):
        if 'product_database' not in file.name.lower():
            excel_files.append(file)
    
    if not excel_files:
        print("No Excel files found")
        return None
    
    excel_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return excel_files[0]

def normalize_product_name(name):
    """Normalize product name for matching."""
    if not name:
        return ""
    return str(name).strip().lower()

def sync_products_from_excel(excel_path, db_path):
    """Sync products from Excel to database."""
    
    print("="*80)
    print("SYNCING DATABASE FROM EXCEL")
    print("="*80)
    print(f"Excel: {excel_path.name}")
    print(f"Database: {db_path.name}")
    print()
    
    # Load Excel
    print("Loading Excel file...")
    df = pd.read_excel(excel_path, engine='openpyxl')
    print(f"  Loaded {len(df)} rows")
    print()
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    updated_count = 0
    added_count = 0
    skipped_count = 0
    
    print("Syncing products...")
    for idx, row in df.iterrows():
        try:
            # Get product data
            product_name = row.get('Product Name*', '')
            if not product_name or pd.isna(product_name):
                skipped_count += 1
                continue
            
            product_brand = row.get('Product Brand', '')
            vendor = row.get('Vendor/Supplier*', '')
            weight = row.get('Weight*', '')
            units = row.get('Units', '')
            
            normalized_name = normalize_product_name(product_name)
            
            # Check if product exists
            cursor.execute('''
                SELECT id FROM products
                WHERE normalized_name = ? AND "Product Brand" = ? AND "Vendor/Supplier*" = ?
            ''', (normalized_name, product_brand, vendor))
            
            existing = cursor.fetchone()
            
            current_date = datetime.now().isoformat()
            
            if existing:
                # Update existing product
                product_id = existing[0]
                
                cursor.execute('''
                    UPDATE products
                    SET "Product Name*" = ?,
                        "Product Type*" = ?,
                        "Weight*" = ?,
                        "Units" = ?,
                        "Price" = ?,
                        "Quantity*" = ?,
                        "Description" = ?,
                        "Lineage" = ?,
                        "Product Strain" = ?,
                        "DOH" = ?,
                        "Concentrate Type" = ?,
                        "Ratio" = ?,
                        "JointRatio" = ?,
                        "THC test result" = ?,
                        "CBD test result" = ?,
                        "Total THC" = ?,
                        "THC" = ?,
                        "CBD" = ?,
                        "last_seen_date" = ?,
                        "updated_at" = ?
                    WHERE id = ?
                ''', (
                    product_name,
                    row.get('Product Type*', ''),
                    weight,
                    units,
                    row.get('Price', ''),
                    row.get('Quantity*', ''),
                    row.get('Description', ''),
                    row.get('Lineage', ''),
                    row.get('Product Strain', ''),
                    row.get('DOH', ''),
                    row.get('Concentrate Type', ''),
                    row.get('Ratio', ''),
                    row.get('JointRatio', ''),
                    row.get('THC test result', ''),
                    row.get('CBD test result', ''),
                    row.get('Total THC', ''),
                    row.get('THC', ''),
                    row.get('CBD', ''),
                    current_date,
                    current_date,
                    product_id
                ))
                
                updated_count += 1
            else:
                # Insert new product
                cursor.execute('''
                    INSERT INTO products (
                        "Product Name*", normalized_name, "Product Type*",
                        "Vendor/Supplier*", "Product Brand", "Weight*", "Units",
                        "Price", "Quantity*", "Description", "Lineage",
                        "Product Strain", "DOH", "Concentrate Type", "Ratio",
                        "JointRatio", "THC test result", "CBD test result",
                        "Total THC", "THC", "CBD",
                        first_seen_date, last_seen_date, created_at, updated_at,
                        total_occurrences
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    product_name,
                    normalized_name,
                    row.get('Product Type*', ''),
                    vendor,
                    product_brand,
                    weight,
                    units,
                    row.get('Price', ''),
                    row.get('Quantity*', ''),
                    row.get('Description', ''),
                    row.get('Lineage', ''),
                    row.get('Product Strain', ''),
                    row.get('DOH', ''),
                    row.get('Concentrate Type', ''),
                    row.get('Ratio', ''),
                    row.get('JointRatio', ''),
                    row.get('THC test result', ''),
                    row.get('CBD test result', ''),
                    row.get('Total THC', ''),
                    row.get('THC', ''),
                    row.get('CBD', ''),
                    current_date,
                    current_date,
                    current_date,
                    current_date
                ))
                
                added_count += 1
            
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(df)} rows...")
                conn.commit()  # Commit every 100 rows
        
        except Exception as e:
            print(f"  Error processing row {idx}: {e}")
            skipped_count += 1
    
    conn.commit()
    conn.close()
    
    print()
    print("="*80)
    print("SYNC COMPLETE")
    print("="*80)
    print(f"  Added: {added_count} new products")
    print(f"  Updated: {updated_count} existing products")
    print(f"  Skipped: {skipped_count} rows")
    print(f"  Total processed: {added_count + updated_count}")
    print()

if __name__ == "__main__":
    excel_file = find_latest_excel()
    if not excel_file:
        print("ERROR: No Excel files found")
        sys.exit(1)
    
    db_path = Path(__file__).parent / 'uploads' / 'product_database_AGT_Bothell.db'
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        sys.exit(1)
    
    sync_products_from_excel(excel_file, db_path)
    
    print("RECOMMENDATION:")
    print("  Run 'python fix_database_weights.py moonshots' to normalize Constellation Moonshots")

