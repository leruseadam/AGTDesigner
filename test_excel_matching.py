#!/usr/bin/env python3
"""
Test script to check Excel database matching specifically
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.json_matcher import JSONMatcher
from src.core.data.excel_processor import ExcelProcessor

def test_excel_matching():
    """Test the Excel matching logic specifically"""
    print("🔍 Testing Excel database matching...")
    
    try:
        # Initialize components
        excel_processor = ExcelProcessor()
        json_matcher = JSONMatcher(excel_processor)
        
        # Check if Excel data is loaded
        if excel_processor.df is None:
            print("❌ No Excel data loaded. Please load an Excel file first.")
            return 0, 0
        
        print(f"📊 Excel database has {len(excel_processor.df)} products")
        print(f"📋 Excel columns: {list(excel_processor.df.columns)}")
        
        # Show some sample products from Excel
        print(f"\n📋 Sample Excel products:")
        for i, (idx, row) in enumerate(excel_processor.df.head(5).iterrows()):
            product_name = row.get('Product Name*', row.get('ProductName', 'Unknown'))
            vendor = row.get('Vendor/Supplier*', row.get('Vendor', 'Unknown'))
            print(f"  {i+1}. {product_name} (Vendor: {vendor})")
        
        # Test matching with sample JSON data
        test_products = [
            "Blue Dream",
            "Wedding Cake", 
            "Gelato",
            "OG Kush",
            "Strawberry Cough"
        ]
        
        print(f"\n🔍 Testing matching for {len(test_products)} test products...")
        
        matched_count = 0
        for product_name in test_products:
            print(f"\n🔍 Testing: {product_name}")
            
            # Test the matching logic directly
            try:
                # This simulates what happens in the matching process
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
                        
                        # Exact name match (highest priority)
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
                                if similarity >= 50:  # Lowered threshold
                                    score += similarity * 0.5  # Convert to score
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
                    
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
        
        print(f"\n🎯 Total matches: {matched_count}/{len(test_products)}")
        success_rate = (matched_count / len(test_products)) * 100
        print(f"📊 Success rate: {success_rate:.1f}%")
        
        return matched_count, len(test_products)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0

if __name__ == "__main__":
    matched_count, total_count = test_excel_matching()
    
    if matched_count == total_count:
        print("🎉 EXCELLENT: All products matched against Excel database!")
    elif matched_count > total_count * 0.5:
        print("✅ GOOD: Most products matched against Excel database.")
    else:
        print("⚠️  ISSUE: Few products matched against Excel database. Need to investigate matching logic.")
