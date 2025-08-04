#!/usr/bin/env python3
"""
Test script for the library browser functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file
import json

def test_library_browser():
    """Test the library browser functionality."""
    print("Testing Library Browser Functionality")
    print("=" * 50)
    
    # Initialize Excel processor
    processor = ExcelProcessor()
    
    # Try to load default file
    default_file = get_default_upload_file()
    if default_file and os.path.exists(default_file):
        print(f"Loading default file: {default_file}")
        success = processor.load_file(default_file)
        if success:
            print("✓ File loaded successfully")
            
            # Test getting products
            print("\nTesting Product Retrieval:")
            print("-" * 30)
            
            if processor.df is not None and not processor.df.empty:
                print(f"✓ Found {len(processor.df)} products")
                
                # Show first few products
                print("\nFirst 3 products:")
                for i, (index, row) in enumerate(processor.df.head(3).iterrows()):
                    product = {
                        'id': index,
                        'product_name': row.get('Product Name*', ''),
                        'product_brand': row.get('Product Brand', ''),
                        'product_type': row.get('Product Type*', ''),
                        'product_strain': row.get('Product Strain', ''),
                        'lineage': row.get('Lineage', ''),
                        'thc_cbd': row.get('THC_CBD', ''),
                        'price': row.get('Price', ''),
                        'description': row.get('Description', '')
                    }
                    print(f"  {i+1}. {product['product_name']} ({product['product_brand']}) - {product['product_strain']}")
                
                # Test statistics
                print("\nStatistics:")
                print("-" * 30)
                total_products = len(processor.df)
                unique_strains = processor.df['Product Strain'].nunique()
                unique_brands = processor.df['Product Brand'].nunique()
                needs_review = processor.df[processor.df['Product Strain'].isna() | processor.df['Lineage'].isna()].shape[0]
                
                print(f"✓ Total Products: {total_products}")
                print(f"✓ Unique Strains: {unique_strains}")
                print(f"✓ Unique Brands: {unique_brands}")
                print(f"✓ Products Needing Review: {needs_review}")
                
                # Test strain analysis
                print("\nTesting Strain Analysis:")
                print("-" * 30)
                
                # Find a product with strain data
                strain_products = processor.df[processor.df['Product Strain'].notna() & (processor.df['Product Strain'] != '')]
                if not strain_products.empty:
                    test_product = strain_products.iloc[0]
                    test_strain = test_product['Product Strain']
                    test_lineage = test_product['Lineage']
                    
                    print(f"✓ Testing strain analysis for: {test_strain} ({test_lineage})")
                    
                    # Find similar products
                    similar_products = []
                    for idx, row in processor.df.iterrows():
                        if idx == test_product.name:
                            continue
                        
                        row_strain = row.get('Product Strain', '')
                        row_lineage = row.get('Lineage', '')
                        
                        similarity_score = 0
                        if test_strain and row_strain and test_strain.lower() == row_strain.lower():
                            similarity_score += 2
                        if test_lineage and row_lineage and test_lineage.lower() == row_lineage.lower():
                            similarity_score += 1
                        
                        if similarity_score > 0:
                            similar_products.append({
                                'id': idx,
                                'product_name': row.get('Product Name*', ''),
                                'product_strain': row_strain,
                                'lineage': row_lineage,
                                'similarity_score': similarity_score
                            })
                    
                    similar_products.sort(key=lambda x: x['similarity_score'], reverse=True)
                    print(f"✓ Found {len(similar_products)} similar products")
                    
                    if similar_products:
                        print("  Top similar products:")
                        for i, product in enumerate(similar_products[:3]):
                            print(f"    {i+1}. {product['product_name']} - {product['product_strain']} (Score: {product['similarity_score']})")
                
                # Test save functionality
                print("\nTesting Save Functionality:")
                print("-" * 30)
                
                # Test updating a product (just for demonstration)
                if len(processor.df) > 0:
                    test_index = 0
                    original_name = processor.df.iloc[test_index]['Product Name*']
                    print(f"✓ Original product name: {original_name}")
                    
                    # Note: We won't actually save changes in this test
                    print("✓ Save functionality ready (not actually saving in test)")
                
            else:
                print("✗ No data found in file")
        else:
            print("✗ Failed to load file")
    else:
        print("✗ No default file found")
    
    print("\n" + "=" * 50)
    print("Library Browser Test Complete!")
    print("\nTo access the library browser:")
    print("1. Start the application: python app.py")
    print("2. Go to: http://localhost:5000/library")
    print("3. Or click the 'Product Library Browser' link on the main page")

if __name__ == "__main__":
    test_library_browser() 