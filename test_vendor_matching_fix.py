#!/usr/bin/env python3
"""
Test script to verify that the vendor matching fix works for specific products.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor

def test_vendor_matching_fix():
    """Test that the vendor matching fix allows products to be matched even when vendors don't exist."""
    
    # Test products from user's question
    test_products = [
        {
            "product_name": "Phat Panda Flower (Cenex/14g)",
            "description": "Phat Panda Flower (Cenex/14g)"
        },
        {
            "product_name": "Platinum Flower (Chicken & Waffles - Platinum Line/14g)",
            "description": "Platinum Flower (Chicken & Waffles - Platinum Line/14g)"
        }
    ]
    
    print("=== VENDOR MATCHING FIX TEST ===")
    
    try:
        # Initialize the JSON matcher
        excel_processor = ExcelProcessor()
        json_matcher = JSONMatcher(excel_processor)
        
        # Build the indexed cache (this would normally be done when loading Excel data)
        # For testing, we'll create some sample data
        sample_data = [
            {"idx": 1, "original_name": "Phat Panda Flower (Golden Pineapple/14g)", "vendor": "Phat Panda"},
            {"idx": 2, "original_name": "Platinum Flower (Rainbow Belts/7g)", "vendor": "Platinum"},
            {"idx": 3, "original_name": "Some Other Flower (Strain Name/3.5g)", "vendor": "Other Vendor"},
        ]
        
        # Build a simple indexed cache for testing
        json_matcher._sheet_cache = sample_data
        
        # Manually build the indexed cache
        indexed_cache = {
            'exact_names': {},
            'vendor_groups': {},
            'key_terms': {},
            'normalized_names': {},
        }
        
        for item in sample_data:
            # Add to exact names
            exact_name = item['original_name'].lower().strip()
            if exact_name:
                indexed_cache['exact_names'][exact_name] = item
            
            # Add to vendor groups
            vendor_lower = item['vendor'].lower().strip()
            if vendor_lower:
                if vendor_lower not in indexed_cache['vendor_groups']:
                    indexed_cache['vendor_groups'][vendor_lower] = []
                indexed_cache['vendor_groups'][vendor_lower].append(item)
            
            # Add to key terms (simplified)
            words = item['original_name'].lower().split()
            for word in words:
                if len(word) >= 3:  # Only meaningful words
                    if word not in indexed_cache['key_terms']:
                        indexed_cache['key_terms'][word] = []
                    indexed_cache['key_terms'][word].append(item)
        
        json_matcher._indexed_cache = indexed_cache
        
        print(f"Built indexed cache with {len(json_matcher._indexed_cache['vendor_groups'])} vendors")
        print(f"Available vendors: {list(json_matcher._indexed_cache['vendor_groups'].keys())}")
        
        for i, product in enumerate(test_products, 1):
            print(f"\n{i}. Testing: {product['product_name']}")
            
            # Extract vendor
            extracted_vendor = json_matcher._extract_vendor(product['product_name'])
            print(f"   Extracted vendor: '{extracted_vendor}'")
            
            # Find candidates
            candidates = json_matcher._find_candidates_optimized(product)
            print(f"   Found {len(candidates)} candidates")
            
            if candidates:
                print("   Candidates:")
                for j, candidate in enumerate(candidates[:3], 1):  # Show first 3
                    print(f"     {j}. {candidate.get('original_name', 'Unknown')}")
            else:
                print("   No candidates found - this is the issue we're trying to fix")
                
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vendor_matching_fix()
