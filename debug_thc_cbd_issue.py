#!/usr/bin/env python3
"""
Debug why THC/CBD values are showing as 0.0%
"""

import sqlite3
import os
from src.core.data.excel_processor import ExcelProcessor

def debug_thc_cbd_issue():
    """Debug why THC/CBD values are showing as 0.0%."""
    
    print("🔍 Debugging THC/CBD issue...")
    
    # Check database
    db_path = "product_database.db"
    if os.path.exists(db_path):
        print("\n📊 Database check:")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total_count = cursor.fetchone()[0]
        print(f"   Total products in database: {total_count}")
        
        # Check products with THC/CBD data
        cursor.execute("SELECT COUNT(*) FROM products WHERE \"THC\" IS NOT NULL AND \"THC\" != ''")
        thc_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM products WHERE \"CBD\" IS NOT NULL AND \"CBD\" != ''")
        cbd_count = cursor.fetchone()[0]
        print(f"   Products with THC data: {thc_count}")
        print(f"   Products with CBD data: {cbd_count}")
        
        # Show sample products
        cursor.execute("SELECT \"Product Name*\", \"THC\", \"CBD\" FROM products LIMIT 5")
        samples = cursor.fetchall()
        print(f"   Sample products:")
        for name, thc, cbd in samples:
            print(f"     {name}: THC='{thc}', CBD='{cbd}'")
        
        conn.close()
    else:
        print("❌ Database not found")
    
    # Check Excel processor
    print("\n📊 Excel processor check:")
    try:
        processor = ExcelProcessor()
        
        # Try to load a file
        default_files = [
            "uploads/A Greener Today - Bothell_inventory_08-29-2025  8_38 PM.xlsx",
            "uploads/AGT_CONSTELLATION_CANNAB_HORIZ_H_Infused_Pre_Rol_51tags_20250912_130254.xlsx"
        ]
        
        loaded = False
        for file_path in default_files:
            if os.path.exists(file_path):
                print(f"   Loading file: {file_path}")
                processor.load_file(file_path)
                loaded = True
                break
        
        if not loaded:
            print("   No Excel files found to load")
            return
        
        if processor.df is not None and not processor.df.empty:
            print(f"   Excel data loaded: {len(processor.df)} rows")
            print(f"   Columns: {list(processor.df.columns)}")
            
            # Check for THC/CBD columns
            thc_columns = [col for col in processor.df.columns if 'THC' in col.upper()]
            cbd_columns = [col for col in processor.df.columns if 'CBD' in col.upper()]
            print(f"   THC columns: {thc_columns}")
            print(f"   CBD columns: {cbd_columns}")
            
            # Check for products with THC/CBD data
            if 'THC' in processor.df.columns:
                thc_data = processor.df['THC'].dropna()
                print(f"   Products with THC data: {len(thc_data)}")
                if len(thc_data) > 0:
                    print(f"   Sample THC values: {thc_data.head().tolist()}")
            
            if 'CBD' in processor.df.columns:
                cbd_data = processor.df['CBD'].dropna()
                print(f"   Products with CBD data: {len(cbd_data)}")
                if len(cbd_data) > 0:
                    print(f"   Sample CBD values: {cbd_data.head().tolist()}")
            
            # Check for products that might be in the image
            image_products = [
                "Carbon Fiber Infused Pre-Roll",
                "Gelato Cookies Infused Pre-Roll", 
                "Jomo Infused Pre-Roll",
                "Rainbow Flame Infused Pre-Roll",
                "The Soap Infused Pre-Roll",
                "Super Boof x Medellin Rosin Roll Infused Pre-Roll"
            ]
            
            print(f"\n📋 Checking for products from image:")
            for product in image_products:
                # Check if product exists in Excel data
                if 'Product Name*' in processor.df.columns:
                    matches = processor.df[processor.df['Product Name*'].str.contains(product, case=False, na=False)]
                    if len(matches) > 0:
                        print(f"   Found '{product}': {len(matches)} matches")
                        for _, row in matches.iterrows():
                            thc_val = row.get('THC', 'N/A')
                            cbd_val = row.get('CBD', 'N/A')
                            print(f"     THC: '{thc_val}', CBD: '{cbd_val}'")
                    else:
                        print(f"   Not found: '{product}'")
                else:
                    print(f"   No Product Name* column found")
        else:
            print("   Excel data is empty or not loaded")
    
    except Exception as e:
        print(f"❌ Error checking Excel processor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_thc_cbd_issue()
