#!/usr/bin/env python3
"""
Debug script to understand why only 2 out of 86 matches are being processed.
"""

import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

from src.core.data.excel_processor import ExcelProcessor
from src.core.constants import EXCLUDED_PRODUCT_PATTERNS, EXCLUDED_PRODUCT_TYPES

def debug_excel_filtering():
    """Debug Excel filtering to understand why only 2 records are processed."""
    print("Debugging Excel Filtering")
    print("=" * 50)
    
    # Initialize Excel processor
    try:
        excel_processor = ExcelProcessor()
        print("✓ Excel processor initialized")
        
        # Check if data is loaded
        if not hasattr(excel_processor, 'df') or excel_processor.df is None:
            print("❌ No data loaded in Excel processor")
            return
        
        print(f"✓ Data loaded: {len(excel_processor.df)} total records")
        
        # Check available columns
        print(f"\nAvailable columns: {list(excel_processor.df.columns)}")
        
        # Check for product name column
        product_name_col = None
        possible_cols = ['ProductName', 'Product Name*', 'Product Name', 'Description']
        for col in possible_cols:
            if col in excel_processor.df.columns:
                product_name_col = col
                break
        
        if not product_name_col:
            print("❌ No product name column found")
            return
        
        print(f"✓ Using product name column: {product_name_col}")
        
        # Check selected tags
        selected_tags = excel_processor.get_selected_tags()
        print(f"\nSelected tags: {selected_tags}")
        print(f"Number of selected tags: {len(selected_tags)}")
        
        # Analyze the data to see what's being filtered
        print(f"\nAnalyzing data for filtering patterns...")
        
        # Check for excluded patterns in product names
        excluded_patterns_found = []
        sample_products = []
        trade_sample_products = []
        
        for idx, row in excel_processor.df.iterrows():
            product_name = str(row.get(product_name_col, '')).strip()
            product_type = str(row.get('Product Type*', '')).strip()
            
            # Check for excluded patterns
            for pattern in EXCLUDED_PRODUCT_PATTERNS:
                if pattern.lower() in product_name.lower():
                    excluded_patterns_found.append({
                        'row': idx,
                        'product_name': product_name,
                        'pattern': pattern
                    })
            
            # Check for sample products
            if 'sample' in product_name.lower():
                sample_products.append({
                    'row': idx,
                    'product_name': product_name,
                    'product_type': product_type
                })
            
            # Check for trade sample products
            if 'trade sample' in product_name.lower():
                trade_sample_products.append({
                    'row': idx,
                    'product_name': product_name,
                    'product_type': product_type
                })
        
        print(f"\nFiltering Analysis:")
        print(f"  Records with excluded patterns: {len(excluded_patterns_found)}")
        print(f"  Records with 'sample' in name: {len(sample_products)}")
        print(f"  Records with 'trade sample' in name: {len(trade_sample_products)}")
        
        if excluded_patterns_found:
            print(f"\nSample excluded records:")
            for i, record in enumerate(excluded_patterns_found[:5]):
                print(f"  {i+1}. Row {record['row']}: '{record['product_name']}' (pattern: {record['pattern']})")
        
        if sample_products:
            print(f"\nSample 'sample' records:")
            for i, record in enumerate(sample_products[:5]):
                print(f"  {i+1}. Row {record['row']}: '{record['product_name']}' (type: {record['product_type']})")
        
        if trade_sample_products:
            print(f"\nSample 'trade sample' records:")
            for i, record in enumerate(trade_sample_products[:5]):
                print(f"  {i+1}. Row {record['row']}: '{record['product_name']}' (type: {record['product_type']})")
        
        # Check what happens when we try to get selected records
        print(f"\nTesting get_selected_records...")
        try:
            records = excel_processor.get_selected_records('horizontal')
            print(f"✓ get_selected_records returned {len(records)} records")
            
            if records:
                print(f"\nFirst few processed records:")
                for i, record in enumerate(records[:3]):
                    print(f"  {i+1}. {record.get('ProductName', 'Unknown')}")
                    print(f"     Description: {record.get('Description', 'Unknown')}")
                    print(f"     ProductBrand: {record.get('ProductBrand', 'Unknown')}")
                    print(f"     Lineage: {record.get('Lineage', 'Unknown')}")
                    print(f"     DOH: {record.get('DOH', 'Unknown')}")
                    print()
        except Exception as e:
            print(f"❌ Error in get_selected_records: {e}")
            import traceback
            traceback.print_exc()
        
        # Check the actual filtering logic
        print(f"\nChecking filtering logic in get_available_tags...")
        try:
            available_tags = excel_processor.get_available_tags()
            print(f"✓ get_available_tags returned {len(available_tags)} tags")
            
            if available_tags:
                print(f"\nFirst few available tags:")
                for i, tag in enumerate(available_tags[:3]):
                    print(f"  {i+1}. {tag.get('productName', 'Unknown')}")
                    print(f"     Brand: {tag.get('productBrand', 'Unknown')}")
                    print(f"     Type: {tag.get('productType', 'Unknown')}")
                    print(f"     Weight: {tag.get('weight', 'Unknown')}")
                    print()
        except Exception as e:
            print(f"❌ Error in get_available_tags: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error initializing Excel processor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_excel_filtering()
