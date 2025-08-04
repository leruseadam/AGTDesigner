#!/usr/bin/env python3
"""
Test script to check the current state of vendor filtering in JSON matching.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_current_vendor_filtering():
    """Test the current state of vendor filtering."""
    
    print("=== TESTING CURRENT VENDOR FILTERING ===\n")
    
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
    
    # Test cases with different vendor scenarios
    test_cases = [
        {
            "name": "Test 1: Dank Czar product",
            "json_item": {
                "product_name": "Medically Compliant - Dank Czar Liquid Diamond Caviar All-In-One - Lemon Time - 1g",
                "vendor": None,
                "brand": None
            }
        },
        {
            "name": "Test 2: Omega product", 
            "json_item": {
                "product_name": "Medically Compliant - Omega Distillate Cartridge - Cherry Lemonheadz - 1g",
                "vendor": None,
                "brand": None
            }
        },
        {
            "name": "Test 3: Airo Pro product",
            "json_item": {
                "product_name": "Black Mamba Distillate Cartridge by Airo Pro - 1g",
                "vendor": None,
                "brand": None
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        
        # Extract vendor
        extracted_vendor = json_matcher._extract_vendor(test_case['json_item']['product_name'])
        print(f"Extracted vendor: '{extracted_vendor}'")
        
        # Find candidates
        candidates = json_matcher._find_candidates_optimized(test_case['json_item'])
        print(f"Found {len(candidates)} candidates")
        
        # Check vendor consistency
        vendor_mismatches = []
        vendor_matches = []
        
        for candidate in candidates[:10]:  # Check first 10 candidates
            candidate_vendor = str(candidate.get("vendor", "")).strip().lower()
            if candidate_vendor:
                if candidate_vendor != extracted_vendor:
                    # Check if it's a fuzzy match
                    fuzzy_matches = json_matcher._find_fuzzy_vendor_matches(extracted_vendor)
                    fuzzy_vendors = set()
                    for fm in fuzzy_matches:
                        fm_vendor = str(fm.get("vendor", "")).strip().lower()
                        if fm_vendor:
                            fuzzy_vendors.add(fm_vendor)
                    
                    if candidate_vendor in fuzzy_vendors:
                        vendor_matches.append(f"✅ {candidate['original_name']} (vendor: {candidate_vendor})")
                    else:
                        vendor_mismatches.append(f"❌ {candidate['original_name']} (vendor: {candidate_vendor})")
                else:
                    vendor_matches.append(f"✅ {candidate['original_name']} (vendor: {candidate_vendor})")
        
        print(f"Vendor matches ({len(vendor_matches)}):")
        for match in vendor_matches[:5]:
            print(f"  {match}")
        
        if vendor_mismatches:
            print(f"Vendor mismatches ({len(vendor_mismatches)}):")
            for mismatch in vendor_mismatches[:5]:
                print(f"  {mismatch}")
        else:
            print("✅ No vendor mismatches found!")

if __name__ == "__main__":
    test_current_vendor_filtering() 