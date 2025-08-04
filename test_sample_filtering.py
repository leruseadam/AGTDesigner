#!/usr/bin/env python3
"""
Test script to verify that sample filtering is working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
from src.core.constants import EXCLUDED_PRODUCT_TYPES, EXCLUDED_PRODUCT_PATTERNS

def test_sample_filtering():
    """Test that sample products are being filtered out correctly."""
    
    print("🧪 Testing Sample Filtering")
    print("=" * 50)
    
    # Test the constants
    print(f"📋 EXCLUDED_PRODUCT_TYPES: {EXCLUDED_PRODUCT_TYPES}")
    print(f"📋 EXCLUDED_PRODUCT_PATTERNS: {EXCLUDED_PRODUCT_PATTERNS}")
    print()
    
    # Test pattern matching
    test_products = [
        "Normal Product",
        "Sample Product",
        "Trade Sample Product", 
        "TRADE SAMPLE - Not For Sale",
        "Sample - Vendor Product",
        "Regular Product with Sample in description",
        "Product with Trade Sample in name",
        "Clean Product Name"
    ]
    
    print("🔍 Testing product name filtering:")
    for product in test_products:
        product_lower = product.lower()
        should_exclude = (
            'sample' in product_lower or 
            'trade sample' in product_lower or
            any(pattern.lower() in product_lower for pattern in EXCLUDED_PRODUCT_PATTERNS)
        )
        status = "❌ EXCLUDE" if should_exclude else "✅ INCLUDE"
        print(f"  {status}: {product}")
    
    print()
    
    # Test with actual Excel processor if file exists
    try:
        processor = ExcelProcessor()
        # Look for default file in common locations
        import glob
        default_files = []
        default_files.extend(glob.glob("*.xlsx"))
        default_files.extend(glob.glob("*.xls"))
        default_files.extend(glob.glob("uploads/*.xlsx"))
        default_files.extend(glob.glob("uploads/*.xls"))
        
        default_file = None
        if default_files:
            default_file = default_files[0]  # Use first found file
        
        if default_file and os.path.exists(default_file):
            print(f"📁 Testing with actual file: {default_file}")
            
            # Load the file
            success = processor.load_file(default_file)
            if success:
                print(f"✅ File loaded successfully")
                print(f"📊 Total records: {len(processor.df)}")
                
                # Get available tags
                available_tags = processor.get_available_tags()
                print(f"📊 Available tags after filtering: {len(available_tags)}")
                
                # Check for any sample products that might have slipped through
                sample_products = []
                for tag in available_tags:
                    product_name = tag.get('Product Name*', '')
                    if 'sample' in product_name.lower() or 'trade sample' in product_name.lower():
                        sample_products.append(product_name)
                
                if sample_products:
                    print(f"⚠️  Found {len(sample_products)} sample products that weren't filtered:")
                    for product in sample_products[:5]:  # Show first 5
                        print(f"    - {product}")
                    if len(sample_products) > 5:
                        print(f"    ... and {len(sample_products) - 5} more")
                else:
                    print("✅ No sample products found in available tags - filtering working correctly!")
                
                # Show some sample of what IS included
                print(f"\n📋 Sample of included products:")
                for i, tag in enumerate(available_tags[:5]):
                    print(f"  {i+1}. {tag.get('Product Name*', 'Unknown')}")
                
            else:
                print("❌ Failed to load file")
        else:
            print("⚠️  No default file found for testing")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Sample filtering test complete!")

if __name__ == "__main__":
    test_sample_filtering() 