#!/usr/bin/env python3
"""
Debug script to test vendor extraction and matching for specific products.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher, extract_vendor_info
from src.core.data.excel_processor import ExcelProcessor

def test_vendor_extraction():
    """Test vendor extraction for the specific products mentioned."""
    
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
    
    print("=== VENDOR EXTRACTION TEST ===")
    
    for i, product in enumerate(test_products, 1):
        print(f"\n{i}. Testing: {product['product_name']}")
        
        # Test extract_vendor_info function
        vendor_info = extract_vendor_info(product)
        print(f"   extract_vendor_info result: '{vendor_info}'")
        
        # Test _extract_vendor method (we'll need to create a JSONMatcher instance)
        try:
            excel_processor = ExcelProcessor()
            json_matcher = JSONMatcher(excel_processor)
            
            # Extract vendor from product name using the method
            extracted_vendor = json_matcher._extract_vendor(product['product_name'])
            print(f"   _extract_vendor result: '{extracted_vendor}'")
            
            # Debug the parentheses parsing manually
            name_lower = product['product_name'].lower()
            print(f"   Original name (lower): '{name_lower}'")
            
            if "(" in name_lower and ")" in name_lower:
                start = name_lower.find("(") + 1
                end = name_lower.find(")")
                print(f"   Parentheses found: start={start}, end={end}")
                if start < end:
                    vendor_part = name_lower[start:end].strip()
                    print(f"   Raw vendor part: '{vendor_part}'")
                    
                    # Remove any trailing weight/size info (e.g., "/14g", "/7g", etc.)
                    if "/" in vendor_part:
                        vendor_part = vendor_part.split("/")[0].strip()
                        print(f"   After removing /: '{vendor_part}'")
                    
                    # Remove any trailing weight/size info with dashes (e.g., " - Platinum Line")
                    if " - " in vendor_part:
                        vendor_part = vendor_part.split(" - ")[0].strip()
                        print(f"   After removing -: '{vendor_part}'")
                    
                    print(f"   Final vendor part: '{vendor_part}'")
            
        except Exception as e:
            print(f"   Error testing _extract_vendor: {e}")
    
    print("\n=== VENDOR MATCHING ANALYSIS ===")
    print("The issue is likely that the extracted vendors ('Cenex' and 'Chicken & Waffles')")
    print("are not present in the Excel data's vendor groups, so no matches are found.")
    print("\nThis happens because the JSON matching system uses strict vendor-based filtering.")
    print("If a vendor from the JSON is not found in the Excel data, no products will be matched.")

if __name__ == "__main__":
    test_vendor_extraction()
