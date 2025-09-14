#!/usr/bin/env python3
"""
Test script to load Excel database and test matching
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor

def test_excel_loading_and_matching():
    """Test loading Excel database and matching"""
    print("🔍 Testing Excel database loading and matching...")
    
    try:
        # Initialize components
        excel_processor = ExcelProcessor()
        
        # Try to load the main database file
        excel_file = "comprehensive_product_database_with_pricing.xlsx"
        print(f"📂 Loading Excel file: {excel_file}")
        
        if not os.path.exists(excel_file):
            print(f"❌ Excel file not found: {excel_file}")
            return False
        
        # Load the Excel file
        success = excel_processor.load_file(excel_file)
        
        if not success:
            print("❌ Failed to load Excel file")
            return False
        
        print(f"✅ Excel file loaded successfully!")
        print(f"📊 Database has {len(excel_processor.df)} products")
        print(f"📋 Columns: {list(excel_processor.df.columns)}")
        
        # Show some sample products
        print(f"\n📋 Sample products from database:")
        for i, (idx, row) in enumerate(excel_processor.df.head(10).iterrows()):
            product_name = row.get('Product Name*', row.get('ProductName', 'Unknown'))
            vendor = row.get('Vendor/Supplier*', row.get('Vendor', 'Unknown'))
            print(f"  {i+1}. {product_name} (Vendor: {vendor})")
        
        # Now test JSON matching
        print(f"\n🔍 Testing JSON matching against loaded database...")
        
        json_matcher = JSONMatcher(excel_processor)
        
        # Test with sample JSON data
        test_products = [
            "Blue Dream",
            "Wedding Cake", 
            "Gelato",
            "OG Kush",
            "Strawberry Cough",
            "Purple Haze",
            "Sour Diesel",
            "White Widow"
        ]
        
        matched_count = 0
        for product_name in test_products:
            print(f"\n🔍 Testing: {product_name}")
            
            # Test the matching logic
            df = excel_processor.df
            best_match = None
            best_score = 0.0
            
            for idx, row in df.iterrows():
                try:
                    # Get product name from Excel row
                    excel_product_name = str(row.get('Product Name*', '') or row.get('ProductName', '') or row.get('Description', '')).strip().lower()
                    
                    if not excel_product_name:
                        continue
                    
                    # Calculate match score
                    score = 0.0
                    
                    # Exact name match
                    if product_name.lower() == excel_product_name:
                        score += 100.0
                        print(f"  ✅ EXACT MATCH: {excel_product_name} (score: {score})")
                    
                    # Partial name match
                    elif product_name.lower() in excel_product_name or excel_product_name in product_name.lower():
                        score += 40.0
                        print(f"  🔍 PARTIAL MATCH: {excel_product_name} (score: {score})")
                    
                    # Fuzzy string similarity
                    else:
                        try:
                            from fuzzywuzzy import fuzz
                            similarity = fuzz.ratio(product_name.lower(), excel_product_name)
                            if similarity >= 50:
                                score += similarity * 0.5
                                print(f"  🔍 FUZZY MATCH: {excel_product_name} (similarity: {similarity}%, score: {score})")
                        except ImportError:
                            pass
                    
                    # Update best match
                    if score > best_score:
                        best_score = score
                        best_match = row
                        
                except Exception as e:
                    continue
            
            if best_match is not None and best_score >= 5.0:
                matched_count += 1
                excel_name = best_match.get('Product Name*', best_match.get('ProductName', 'Unknown'))
                print(f"  ✅ BEST MATCH: {excel_name} (score: {best_score:.1f})")
            else:
                print(f"  ❌ NO MATCH FOUND (best score: {best_score:.1f})")
        
        print(f"\n🎯 Total matches: {matched_count}/{len(test_products)}")
        success_rate = (matched_count / len(test_products)) * 100
        print(f"📊 Success rate: {success_rate:.1f}%")
        
        return success_rate >= 50
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_excel_loading_and_matching()
    
    if success:
        print("🎉 SUCCESS: Excel database loaded and matching is working!")
    else:
        print("⚠️  ISSUE: Excel database loading or matching needs attention.")
