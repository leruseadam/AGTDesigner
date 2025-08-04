#!/usr/bin/env python3
"""
Test script to verify that JSON matching vendor filtering is working correctly.
This script tests that items from different vendors are not being matched incorrectly.
"""

import sys
import os
import logging
import pandas as pd

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_vendor_filtering():
    """Test that vendor filtering prevents cross-vendor matches."""
    
    print("=== Testing Vendor Filtering Fix ===\n")
    
    # Initialize Excel processor and load data
    excel_processor = ExcelProcessor()
    
    # Try to load the default file
    from src.core.data.excel_processor import get_default_upload_file
    default_file = get_default_upload_file()
    
    if not default_file or not os.path.exists(default_file):
        print(f"❌ Default file not found: {default_file}")
        return False
    
    print(f"📁 Loading data from: {default_file}")
    success = excel_processor.load_file(default_file)
    
    if not success:
        print("❌ Failed to load Excel file")
        return False
    
    print(f"✅ Loaded {len(excel_processor.df)} records")
    
    # Initialize JSON matcher
    json_matcher = JSONMatcher(excel_processor)
    
    # Build the cache
    print("🔧 Building cache...")
    json_matcher._build_sheet_cache()
    
    if not json_matcher._sheet_cache:
        print("❌ Failed to build cache")
        return False
    
    print(f"✅ Built cache with {len(json_matcher._sheet_cache)} items")
    
    # Test cases with different vendors
    test_cases = [
        {
            "name": "Dank Czar Rosin - GMO - 1g",
            "vendor": "dank czar",
            "expected_vendor_match": True
        },
        {
            "name": "Dank Czar Rosin - GMO - 1g", 
            "vendor": "dcz holdings inc",
            "expected_vendor_match": True
        },
        {
            "name": "Dank Czar Rosin - GMO - 1g",
            "vendor": "different vendor",
            "expected_vendor_match": False
        },
        {
            "name": "Hustler's Ambition Pre-Roll - Wedding Cake - 1g",
            "vendor": "hustler's ambition",
            "expected_vendor_match": True
        },
        {
            "name": "Hustler's Ambition Pre-Roll - Wedding Cake - 1g",
            "vendor": "1555 industrial llc",
            "expected_vendor_match": True
        },
        {
            "name": "Hustler's Ambition Pre-Roll - Wedding Cake - 1g",
            "vendor": "completely different vendor",
            "expected_vendor_match": False
        }
    ]
    
    print("\n🧪 Testing vendor filtering...")
    
    all_tests_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} (vendor: {test_case['vendor']}) ---")
        
        # Create a mock JSON item
        json_item = {
            "product_name": test_case["name"],
            "vendor": test_case["vendor"],
            "product_type": "concentrate"
        }
        
        # Find candidates
        candidates = json_matcher._find_candidates_optimized(json_item)
        
        print(f"Found {len(candidates)} candidates")
        
        if candidates:
            # Check if any candidates have the expected vendor
            found_expected_vendor = False
            for candidate in candidates[:5]:  # Check first 5 candidates
                candidate_vendor = candidate.get("vendor", "").lower()
                print(f"  Candidate vendor: '{candidate_vendor}'")
                
                # Check if this is the expected vendor or a known variation
                if test_case["expected_vendor_match"]:
                    if candidate_vendor == test_case["vendor"]:
                        found_expected_vendor = True
                        break
                    # Check known variations
                    vendor_variations = {
                        'dank czar': ['dcz holdings inc', 'dcz holdings inc.', 'dcz', 'dank czar holdings'],
                        'dcz holdings inc': ['dank czar', 'dcz', 'dcz holdings', 'dcz holdings inc.'],
                        'dcz holdings inc.': ['dank czar', 'dcz', 'dcz holdings', 'dcz holdings inc'],
                        'hustler\'s ambition': ['1555 industrial llc', 'hustlers ambition'],
                        '1555 industrial llc': ['hustler\'s ambition', 'hustlers ambition'],
                    }
                    for main_vendor, variations in vendor_variations.items():
                        if (test_case["vendor"] in [main_vendor] + variations and 
                            candidate_vendor in [main_vendor] + variations):
                            found_expected_vendor = True
                            break
                else:
                    # For non-matching vendors, we shouldn't find any candidates with the same vendor
                    if candidate_vendor == test_case["vendor"]:
                        found_expected_vendor = True
                        break
            
            # Determine test result
            if test_case["expected_vendor_match"]:
                if found_expected_vendor:
                    print("✅ PASS: Found expected vendor in candidates")
                else:
                    print("❌ FAIL: Expected vendor not found in candidates")
                    all_tests_passed = False
            else:
                if not found_expected_vendor:
                    print("✅ PASS: No unexpected vendor matches found")
                else:
                    print("❌ FAIL: Found unexpected vendor match")
                    all_tests_passed = False
        else:
            if not test_case["expected_vendor_match"]:
                print("✅ PASS: No candidates found (expected for different vendor)")
            else:
                print("❌ FAIL: No candidates found (unexpected for matching vendor)")
                all_tests_passed = False
    
    print(f"\n{'='*50}")
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Vendor filtering is working correctly.")
    else:
        print("❌ SOME TESTS FAILED! Vendor filtering needs more work.")
    
    return all_tests_passed

def test_matching_threshold():
    """Test that the matching threshold is high enough to prevent poor matches."""
    
    print("\n=== Testing Matching Threshold ===\n")
    
    # Initialize Excel processor and load data
    excel_processor = ExcelProcessor()
    
    from src.core.data.excel_processor import get_default_upload_file
    default_file = get_default_upload_file()
    
    if not default_file or not os.path.exists(default_file):
        print("❌ Default file not found")
        return False
    
    success = excel_processor.load_file(default_file)
    if not success:
        print("❌ Failed to load Excel file")
        return False
    
    # Initialize JSON matcher
    json_matcher = JSONMatcher(excel_processor)
    json_matcher._build_sheet_cache()
    
    # Test cases with poor matches that should be rejected
    poor_match_tests = [
        {
            "json_item": {
                "product_name": "Dank Czar Rosin - GMO - 1g",
                "vendor": "dank czar",
                "product_type": "concentrate"
            },
            "cache_item": {
                "original_name": "Different Vendor Product - GMO - 1g",
                "vendor": "different vendor",
                "product_type": "concentrate"
            },
            "expected_score": "low"  # Should be low due to vendor mismatch
        },
        {
            "json_item": {
                "product_name": "Hustler's Ambition Pre-Roll - Wedding Cake - 1g",
                "vendor": "hustler's ambition", 
                "product_type": "pre-roll"
            },
            "cache_item": {
                "original_name": "Another Vendor Pre-Roll - Wedding Cake - 1g",
                "vendor": "another vendor",
                "product_type": "pre-roll"
            },
            "expected_score": "low"  # Should be low due to vendor mismatch
        }
    ]
    
    print("🧪 Testing matching threshold...")
    
    all_tests_passed = True
    
    for i, test_case in enumerate(poor_match_tests, 1):
        print(f"\n--- Threshold Test {i} ---")
        print(f"JSON: {test_case['json_item']['product_name']} (vendor: {test_case['json_item']['vendor']})")
        print(f"Cache: {test_case['cache_item']['original_name']} (vendor: {test_case['cache_item']['vendor']})")
        
        # Calculate match score
        score = json_matcher._calculate_match_score(test_case['json_item'], test_case['cache_item'])
        print(f"Score: {score:.3f}")
        
        # Check if score is appropriately low
        if score < 0.3:  # Should be below the acceptance threshold
            print("✅ PASS: Score is appropriately low")
        else:
            print("❌ FAIL: Score is too high for vendor mismatch")
            all_tests_passed = False
    
    print(f"\n{'='*50}")
    if all_tests_passed:
        print("🎉 ALL THRESHOLD TESTS PASSED!")
    else:
        print("❌ SOME THRESHOLD TESTS FAILED!")
    
    return all_tests_passed

if __name__ == "__main__":
    print("🚀 Starting JSON Matching Vendor Filtering Tests\n")
    
    # Run vendor filtering tests
    vendor_tests_passed = test_vendor_filtering()
    
    # Run threshold tests
    threshold_tests_passed = test_matching_threshold()
    
    print(f"\n{'='*60}")
    print("📊 FINAL RESULTS:")
    print(f"Vendor Filtering Tests: {'✅ PASSED' if vendor_tests_passed else '❌ FAILED'}")
    print(f"Threshold Tests: {'✅ PASSED' if threshold_tests_passed else '❌ FAILED'}")
    
    if vendor_tests_passed and threshold_tests_passed:
        print("\n🎉 ALL TESTS PASSED! The vendor filtering fix is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED! The vendor filtering fix needs more work.")
        sys.exit(1) 