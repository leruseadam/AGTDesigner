#!/usr/bin/env python3
"""
Debug script to investigate the Mama J's vendor matching issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_mama_j_vendor():
    """Debug the Mama J's vendor matching issue."""
    
    print("=== DEBUGGING MAMA J'S VENDOR MATCHING ===\n")
    
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
    
    # Initialize JSON matcher
    json_matcher = JSONMatcher(excel_processor)
    
    # Build the cache
    json_matcher._build_sheet_cache()
    print("Built sheet cache for JSON matcher")
    
    # Test Mama J's vendor extraction
    test_names = [
        "Mama J's Hidden Pastry - 28g",
        "Mama J's Lemon Cherry Gelato - 28g", 
        "Mama J's Runtz - 28g",
        "Jack & Coke Pre-Roll by Mama J's - 1g x 5 Pack",
        "Bubblegum Gelato Pre-Roll by Mama J's - 1g x 2 Pack"
    ]
    
    print("=== VENDOR EXTRACTION TEST ===")
    for name in test_names:
        extracted = json_matcher._extract_vendor(name)
        print(f"'{name}' -> extracted vendor: '{extracted}'")
    
    # Check what vendors are available
    print(f"\n=== AVAILABLE VENDORS ===")
    available_vendors = list(json_matcher._indexed_cache['vendor_groups'].keys())
    mama_related_vendors = [v for v in available_vendors if 'mama' in v.lower() or 'j' in v.lower()]
    print(f"Mama-related vendors: {mama_related_vendors}")
    
    # Test fuzzy vendor matching for "mama"
    print(f"\n=== FUZZY VENDOR MATCHING TEST ===")
    json_vendor = "mama"
    fuzzy_matches = json_matcher._find_fuzzy_vendor_matches(json_vendor)
    
    print(f"Fuzzy matches for '{json_vendor}': {len(fuzzy_matches)} candidates")
    
    # Group fuzzy matches by vendor
    vendor_groups = {}
    for match in fuzzy_matches:
        vendor = str(match.get("vendor", "")).strip()
        if vendor not in vendor_groups:
            vendor_groups[vendor] = []
        vendor_groups[vendor].append(match['original_name'])
    
    print("Fuzzy matches by vendor:")
    for vendor, products in vendor_groups.items():
        print(f"  {vendor}: {len(products)} products")
        for product in products[:3]:  # Show first 3 products per vendor
            print(f"    - {product}")
    
    # Test the specific problematic case
    print(f"\n=== PROBLEMATIC CASE TEST ===")
    json_item = {
        "product_name": "Mama J's Hidden Pastry - 28g",
        "vendor": None,
        "brand": None
    }
    
    candidates = json_matcher._find_candidates_optimized(json_item)
    print(f"Found {len(candidates)} candidates for 'Mama J's Hidden Pastry - 28g'")
    
    # Check vendor distribution
    vendor_distribution = {}
    for candidate in candidates[:20]:
        vendor = str(candidate.get("vendor", "")).strip()
        if vendor not in vendor_distribution:
            vendor_distribution[vendor] = 0
        vendor_distribution[vendor] += 1
    
    print("Candidate vendor distribution:")
    for vendor, count in sorted(vendor_distribution.items(), key=lambda x: x[1], reverse=True):
        print(f"  {vendor}: {count} candidates")

if __name__ == "__main__":
    debug_mama_j_vendor() 