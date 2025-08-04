#!/usr/bin/env python3
"""
Comprehensive test to check for any remaining cross-vendor matches in JSON matching.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def comprehensive_vendor_test():
    """Comprehensive test to check for cross-vendor matches."""
    
    print("=== COMPREHENSIVE VENDOR FILTERING TEST ===\n")
    
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
    
    # Test cases that should NOT cross vendors
    problematic_test_cases = [
        {
            "name": "Dank Czar vs Airo Pro",
            "json_item": {
                "product_name": "Medically Compliant - Dank Czar Liquid Diamond Caviar All-In-One - Lemon Time - 1g",
                "vendor": None,
                "brand": None
            },
            "forbidden_vendors": ["harmony farms", "airo", "airo pro"]
        },
        {
            "name": "Omega vs Dank Czar", 
            "json_item": {
                "product_name": "Medically Compliant - Omega Distillate Cartridge - Cherry Lemonheadz - 1g",
                "vendor": None,
                "brand": None
            },
            "forbidden_vendors": ["dcz holdings inc", "dank czar", "dank"]
        },
        {
            "name": "Airo Pro vs Omega",
            "json_item": {
                "product_name": "Black Mamba Distillate Cartridge by Airo Pro - 1g",
                "vendor": None,
                "brand": None
            },
            "forbidden_vendors": ["jsm llc", "omega", "omega labs"]
        },
        {
            "name": "Mama J's vs 1555 Industrial (should match - same vendor)",
            "json_item": {
                "product_name": "Mama J's Hidden Pastry - 28g",
                "vendor": None,
                "brand": None
            },
            "forbidden_vendors": ["dcz holdings inc", "jsm llc", "harmony farms"]  # Should NOT match these vendors
        }
    ]
    
    all_passed = True
    
    for test_case in problematic_test_cases:
        print(f"\n--- {test_case['name']} ---")
        
        # Extract vendor
        extracted_vendor = json_matcher._extract_vendor(test_case['json_item']['product_name'])
        print(f"Extracted vendor: '{extracted_vendor}'")
        
        # Find candidates
        candidates = json_matcher._find_candidates_optimized(test_case['json_item'])
        print(f"Found {len(candidates)} candidates")
        
        # Check for forbidden vendor matches
        forbidden_matches = []
        allowed_matches = []
        
        for candidate in candidates[:20]:  # Check first 20 candidates
            candidate_vendor = str(candidate.get("vendor", "")).strip().lower()
            if candidate_vendor:
                is_forbidden = any(forbidden in candidate_vendor for forbidden in test_case['forbidden_vendors'])
                if is_forbidden:
                    forbidden_matches.append(f"❌ {candidate['original_name']} (vendor: {candidate_vendor})")
                else:
                    allowed_matches.append(f"✅ {candidate['original_name']} (vendor: {candidate_vendor})")
        
        if forbidden_matches:
            print(f"❌ FORBIDDEN VENDOR MATCHES FOUND ({len(forbidden_matches)}):")
            for match in forbidden_matches[:5]:
                print(f"  {match}")
            all_passed = False
        else:
            print(f"✅ No forbidden vendor matches found!")
            print(f"Allowed matches ({len(allowed_matches)}):")
            for match in allowed_matches[:3]:
                print(f"  {match}")
    
    # Test with actual JSON data to see real-world behavior
    print(f"\n=== TESTING WITH ACTUAL JSON DATA ===")
    
    # Simulate JSON inventory with mixed vendors
    json_inventory = [
        {
            "product_name": "Medically Compliant - Dank Czar Liquid Diamond Caviar All-In-One - Lemon Time - 1g",
            "vendor": "Dank Czar",
            "brand": "Dank Czar"
        },
        {
            "product_name": "Medically Compliant - Omega Distillate Cartridge - Cherry Lemonheadz - 1g", 
            "vendor": "Omega",
            "brand": "Omega"
        },
        {
            "product_name": "Black Mamba Distillate Cartridge by Airo Pro - 1g",
            "vendor": "Airo Pro",
            "brand": "Airo Pro"
        }
    ]
    
    for i, json_item in enumerate(json_inventory):
        print(f"\n--- JSON Item {i+1}: {json_item['product_name']} ---")
        
        # Find candidates
        candidates = json_matcher._find_candidates_optimized(json_item)
        print(f"Found {len(candidates)} candidates")
        
        # Group by vendor
        vendor_groups = {}
        for candidate in candidates[:10]:
            vendor = str(candidate.get("vendor", "")).strip()
            if vendor not in vendor_groups:
                vendor_groups[vendor] = []
            vendor_groups[vendor].append(candidate['original_name'])
        
        print("Candidates by vendor:")
        for vendor, products in vendor_groups.items():
            print(f"  {vendor}: {len(products)} products")
            for product in products[:2]:  # Show first 2 products per vendor
                print(f"    - {product}")
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED! No cross-vendor matches found.")
    else:
        print(f"\n❌ SOME TESTS FAILED! Cross-vendor matches were found.")
    
    return all_passed

if __name__ == "__main__":
    comprehensive_vendor_test() 