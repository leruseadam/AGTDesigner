#!/usr/bin/env python3
"""
Debug script to compare local vs web JSON matching behavior
and identify why web version produces fewer results.
"""

import sys
import os
import json
import base64
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
from src.core.data.json_matcher import JSONMatcher
from src.core.data.enhanced_json_matcher import EnhancedJSONMatcher

def create_test_json():
    """Create test JSON data with variety of vendors"""
    return {
        "from_license_name": "Test Vendor LLC",
        "inventory_transfer_items": [
            {
                "product_name": "Blue Dream 1/8oz Pre-Pack",
                "vendor": "Test Vendor LLC",
                "inventory_type": "Flower for Inhalation",
                "strain_name": "Blue Dream",
                "weight": "3.5g"
            },
            {
                "product_name": "OG Kush Cartridge 1g", 
                "vendor": "Different Vendor Inc",
                "inventory_type": "Vape Cartridge",
                "strain_name": "OG Kush",
                "weight": "1g"
            },
            {
                "product_name": "Wedding Cake Sugar Wax",
                "vendor": "Unknown Vendor",
                "inventory_type": "Concentrate for Inhalation", 
                "strain_name": "Wedding Cake",
                "weight": "1g"
            },
            {
                "product_name": "Some Product Without Vendor",
                "inventory_type": "Capsule",
                "strain_name": "Mixed",
                "weight": "500mg"
            }
        ]
    }

def test_local_vs_web_matching():
    """Compare local JSONMatcher vs web EnhancedJSONMatcher behavior"""
    print("🔍 DEBUGGING JSON MATCHING DIFFERENCES")
    print("=" * 50)
    
    # Create test data
    test_data = create_test_json()
    json_str = json.dumps(test_data)
    encoded_data = base64.b64encode(json_str.encode()).decode()
    data_url = f"data:application/json;base64,{encoded_data}"
    
    print(f"Test JSON contains {len(test_data['inventory_transfer_items'])} items:")
    for i, item in enumerate(test_data['inventory_transfer_items']):
        vendor = item.get('vendor', 'NO VENDOR')
        print(f"  {i+1}. {item['product_name']} (vendor: {vendor})")
    print()
    
    # Test with basic JSONMatcher (local version)
    print("🏠 TESTING LOCAL JSONMatcher:")
    try:
        excel_processor = ExcelProcessor()
        # Load some Excel data if available
        excel_files = ['uploads/products.xlsx', 'uploads/bothell_products.xlsx', 'uploads/combined_database.xlsx']
        for excel_file in excel_files:
            if os.path.exists(excel_file):
                excel_processor.load_file(excel_file)
                print(f"   Loaded Excel file: {excel_file}")
                break
        
        json_matcher = JSONMatcher(excel_processor)
        local_results = json_matcher.fetch_and_match(data_url)
        
        print(f"   LOCAL RESULTS: {len(local_results)} products matched")
        for i, product in enumerate(local_results[:10]):  # Show first 10
            name = product.get('Product Name*', product.get('ProductName', 'Unknown'))
            vendor = product.get('Vendor/Supplier*', product.get('Vendor', 'Unknown'))
            print(f"   {i+1}. {name} (vendor: {vendor})")
            
    except Exception as e:
        print(f"   LOCAL ERROR: {e}")
        local_results = []
    
    print()
    
    # Test with EnhancedJSONMatcher (web version)
    print("🌐 TESTING WEB EnhancedJSONMatcher:")
    try:
        excel_processor = ExcelProcessor()
        # Load some Excel data if available  
        excel_files = ['uploads/products.xlsx', 'uploads/bothell_products.xlsx', 'uploads/combined_database.xlsx']
        for excel_file in excel_files:
            if os.path.exists(excel_file):
                excel_processor.load_file(excel_file)
                break
                
        enhanced_matcher = EnhancedJSONMatcher(excel_processor)
        web_results = enhanced_matcher.fetch_and_match(data_url)
        
        print(f"   WEB RESULTS: {len(web_results)} products matched")
        for i, product in enumerate(web_results[:10]):  # Show first 10
            name = product.get('Product Name*', product.get('ProductName', 'Unknown'))
            vendor = product.get('Vendor/Supplier*', product.get('Vendor', 'Unknown'))
            score = product.get('Match_Score', 'N/A')
            print(f"   {i+1}. {name} (vendor: {vendor}, score: {score})")
            
    except Exception as e:
        print(f"   WEB ERROR: {e}")
        web_results = []
    
    print()
    
    # Compare results
    print("📊 COMPARISON ANALYSIS:")
    print(f"   Local matcher found: {len(local_results)} products")
    print(f"   Web matcher found: {len(web_results)} products") 
    print(f"   Difference: {len(local_results) - len(web_results)} products")
    
    if len(local_results) != len(web_results):
        print(f"   🚨 DISCREPANCY DETECTED!")
        
        if len(web_results) < len(local_results):
            print(f"   💡 LIKELY CAUSE: Web version (EnhancedJSONMatcher) applies vendor filtering")
            print(f"      that restricts matches to same vendor, reducing results when")
            print(f"      vendor information doesn't match exactly between JSON and database.")
            
            # Show vendor analysis
            print("\n   🏢 VENDOR ANALYSIS:")
            json_vendors = set()
            for item in test_data['inventory_transfer_items']:
                vendor = item.get('vendor')
                if vendor:
                    json_vendors.add(vendor)
            print(f"   JSON vendors: {sorted(list(json_vendors))}")
            
            if local_results:
                db_vendors = set()
                for product in local_results[:20]:  # Sample first 20
                    vendor = product.get('Vendor/Supplier*', product.get('Vendor', ''))
                    if vendor:
                        db_vendors.add(vendor)
                print(f"   Database vendors (sample): {sorted(list(db_vendors))[:10]}")
                
                # Check for vendor mismatches
                print(f"   💭 VENDOR MISMATCH ANALYSIS:")
                print(f"      If JSON vendors don't exactly match database vendors,")
                print(f"      the enhanced matcher will filter out products, causing")
                print(f"      the web version to return fewer results than local version.")
        
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    test_local_vs_web_matching()