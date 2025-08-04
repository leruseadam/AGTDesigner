#!/usr/bin/env python3
"""
Check what vendor Mama J's products actually have in the Excel data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
import pandas as pd

def check_mama_j_vendor():
    """Check what vendor Mama J's products have in the Excel data."""
    
    print("=== CHECKING MAMA J'S VENDOR IN EXCEL DATA ===\n")
    
    # Initialize Excel processor
    excel_processor = ExcelProcessor()
    
    # Load test data
    test_file = "uploads/A Greener Today - Bothell_inventory_07-15-2025  7_04 PM.xlsx"
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return
    
    # Load Excel data
    excel_processor.load_file(test_file)
    print(f"Loaded Excel file with {len(excel_processor.df)} records")
    
    # Find Mama J's products
    mama_j_products = excel_processor.df[
        excel_processor.df['ProductName'].str.contains('Mama J', case=False, na=False) |
        excel_processor.df['ProductName'].str.contains("Mama J's", case=False, na=False)
    ]
    
    print(f"Found {len(mama_j_products)} Mama J's products")
    
    if len(mama_j_products) > 0:
        print("\nMama J's products and their vendors:")
        for _, product in mama_j_products.iterrows():
            product_name = product.get('ProductName', '')
            vendor = product.get('Vendor', '')
            brand = product.get('Product Brand', '')
            print(f"  Product: {product_name}")
            print(f"    Vendor: {vendor}")
            print(f"    Brand: {brand}")
            print()
    
    # Check all vendors that contain "mama" or "j"
    all_vendors = excel_processor.df['Vendor'].unique()
    mama_related_vendors = [v for v in all_vendors if v and ('mama' in str(v).lower() or 'j' in str(v).lower())]
    
    print(f"All vendors containing 'mama' or 'j': {mama_related_vendors}")
    
    # Check if there are any products with "Mama J" in the name but different vendor
    mama_j_name_products = excel_processor.df[
        excel_processor.df['ProductName'].str.contains('Mama J', case=False, na=False)
    ]
    
    print(f"\nAll products with 'Mama J' in name:")
    for _, product in mama_j_name_products.iterrows():
        product_name = product.get('ProductName', '')
        vendor = product.get('Vendor', '')
        print(f"  {product_name} -> Vendor: {vendor}")

if __name__ == "__main__":
    check_mama_j_vendor() 