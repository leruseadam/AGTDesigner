#!/usr/bin/env python3
"""
Debug script to examine vendor extraction and matching.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_vendor_extraction():
    """Debug vendor extraction and matching."""
    
    print("=== DEBUGGING VENDOR EXTRACTION ===\n")
    
    # Initialize Excel processor
    excel_processor = ExcelProcessor()
    
    # Load test data
    test_file = "uploads/A Greener Today - Bothell_inventory_07-15-2025  7_04 PM.xlsx"
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return
    
    excel_processor.load_file(test_file)
    print(f"Loaded Excel file with {len(excel_processor.df)} records")
    
    # Initialize JSON matcher
    json_matcher = JSONMatcher(excel_processor)
    
    # Build the cache
    json_matcher._build_sheet_cache()
    print("Built sheet cache for JSON matcher")
    
    # Check what vendors are in the Excel data
    print("\n=== AVAILABLE VENDORS IN EXCEL DATA ===")
    vendors = excel_processor.df['Vendor'].dropna().unique()
    vendors_sorted = sorted(vendors)
    print(f"Total unique vendors: {len(vendors)}")
    print("First 20 vendors:")
    for i, vendor in enumerate(vendors_sorted[:20]):
        print(f"  {i+1}. {vendor}")
    
    # Test vendor extraction from different product name formats
    print("\n=== TESTING VENDOR EXTRACTION ===")
    test_names = [
        "Medically Compliant - Dank Czar Live Hash Rosin Reserve - GMO - 1g (Boxed 5ml)",
        "Medically Compliant - Omega Distillate Cartridge - Cherry Lemonheadz - 1g",
        "Black Mamba Distillate Cartridge by Airo Pro - 1g",
        "Dank Czar Hash Research Dab Mat",
        "Omega Distillate Cartridge - Cherry Lemonheadz - 1g"
    ]
    
    for name in test_names:
        extracted_vendor = json_matcher._extract_vendor(name)
        print(f"'{name}' -> extracted vendor: '{extracted_vendor}'")
    
    # Test specific problematic cases
    print("\n=== TESTING SPECIFIC CASES ===")
    
    # Case 1: Omega products
    print("\nCase 1: Omega products")
    omega_products = excel_processor.df[excel_processor.df['ProductName'].str.contains('Omega', case=False, na=False)]
    print(f"Found {len(omega_products)} Omega products")
    for _, row in omega_products.head(5).iterrows():
        product_name = row['ProductName']
        vendor = row['Vendor']
        extracted = json_matcher._extract_vendor(product_name)
        print(f"  '{product_name}' -> Excel vendor: '{vendor}', extracted: '{extracted}'")
    
    # Case 2: Airo Pro products
    print("\nCase 2: Airo Pro products")
    airo_products = excel_processor.df[excel_processor.df['ProductName'].str.contains('Airo Pro', case=False, na=False)]
    print(f"Found {len(airo_products)} Airo Pro products")
    for _, row in airo_products.head(5).iterrows():
        product_name = row['ProductName']
        vendor = row['Vendor']
        extracted = json_matcher._extract_vendor(product_name)
        print(f"  '{product_name}' -> Excel vendor: '{vendor}', extracted: '{extracted}'")
    
    # Case 3: Dank Czar products
    print("\nCase 3: Dank Czar products")
    dank_products = excel_processor.df[excel_processor.df['ProductName'].str.contains('Dank Czar', case=False, na=False)]
    print(f"Found {len(dank_products)} Dank Czar products")
    for _, row in dank_products.head(5).iterrows():
        product_name = row['ProductName']
        vendor = row['Vendor']
        extracted = json_matcher._extract_vendor(product_name)
        print(f"  '{product_name}' -> Excel vendor: '{vendor}', extracted: '{extracted}'")
    
    # Test fuzzy vendor matching
    print("\n=== TESTING FUZZY VENDOR MATCHING ===")
    test_vendors = ["dank czar", "omega", "airo pro", "dcz holdings inc"]
    
    for test_vendor in test_vendors:
        print(f"\nTesting fuzzy matching for '{test_vendor}':")
        matches = json_matcher._find_fuzzy_vendor_matches(test_vendor)
        print(f"  Found {len(matches)} fuzzy matches")
        if matches:
            unique_vendors = set()
            for match in matches[:5]:  # Show first 5
                vendor = match.get("vendor", "")
                if vendor:
                    unique_vendors.add(vendor)
            print(f"  Unique vendors: {list(unique_vendors)}")

if __name__ == "__main__":
    debug_vendor_extraction() 