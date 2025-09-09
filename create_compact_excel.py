#!/usr/bin/env python3
"""
Create Compact Excel File
Creates a smaller Excel file with just the essential product data
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

def create_compact_excel():
    """Create a compact Excel file with essential product data."""
    print("Creating compact Excel file with all products...")
    
    try:
        # Connect to database
        conn = sqlite3.connect('product_database.db')
        
        # Get all products with essential columns
        query = """
        SELECT 
            "Product Name*",
            "Product Brand",
            "Product Type*",
            "Vendor/Supplier*",
            "Lineage",
            "THC%",
            "CBD%",
            "Weight*",
            "WeightUnits",
            "Quantity*",
            "Price",
            "Description"
        FROM products
        WHERE "Product Name*" IS NOT NULL
        ORDER BY "Product Name*"
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        print(f"Found {len(df)} products")
        
        # Create compact Excel file
        output_file = f"compact_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Products', index=False)
        
        file_size = os.path.getsize(output_file)
        print(f"✅ Compact Excel file created: {output_file}")
        print(f"File size: {file_size:,} bytes ({file_size / (1024*1024):.1f} MB)")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error creating compact Excel: {e}")
        return None

def main():
    """Main function."""
    print("Create Compact Excel File")
    print("=" * 30)
    
    excel_file = create_compact_excel()
    if excel_file:
        print(f"\n🎉 Compact Excel file created successfully!")
        print(f"You can now upload {excel_file} to the application.")
        print("This file contains all {len(pd.read_excel(excel_file))} products in a smaller format.")

if __name__ == "__main__":
    main()
