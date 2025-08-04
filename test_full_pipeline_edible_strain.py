#!/usr/bin/env python3
"""
Test that simulates the full file processing pipeline to verify the edible Product Strain fix.
"""

import pandas as pd
import sys
import os
import tempfile

# Add the src directory to the path so we can import the ExcelProcessor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.data.excel_processor import ExcelProcessor

def test_full_pipeline_edible_strain():
    """Test the edible Product Strain logic in the full processing pipeline."""
    
    # Create test data that matches what we see in the image
    test_data = [
        {
            'Product Name*': '20:20:1 Sour Watermelon Gummies',
            'Product Type*': 'edible (solid)',
            'Description': 'Delicious gummy bears with CBD for relaxation',
            'Expected Product Strain': 'CBD Blend'
        },
        {
            'Product Name*': '1:1:1 Indica Boysenberry Gummies',
            'Product Type*': 'edible (solid)',
            'Description': 'Boysenberry gummies with CBN for sleep',
            'Expected Product Strain': 'CBD Blend'
        },
        {
            'Product Name*': 'MAX Pink Lemonade Gummie Single',
            'Product Type*': 'edible (solid)',
            'Description': 'Pink lemonade gummies with CBG for wellness',
            'Expected Product Strain': 'CBD Blend'
        },
        {
            'Product Name*': 'CBD Watermelon Fruit Chews',
            'Product Type*': 'edible (solid)',
            'Description': 'Watermelon fruit chews with CBD',
            'Expected Product Strain': 'CBD Blend'
        },
        {
            'Product Name*': '2:1 CBD Hybrid Peach Gummies',
            'Product Type*': 'edible (solid)',
            'Description': 'Peach gummies with CBD and THC',
            'Expected Product Strain': 'CBD Blend'
        },
        {
            'Product Name*': 'Regular THC Gummies',
            'Product Type*': 'edible (solid)',
            'Description': 'Delicious THC gummies for recreational use',
            'Expected Product Strain': 'Mixed'
        },
        {
            'Product Name*': 'Blue Dream Flower',
            'Product Type*': 'flower',
            'Description': 'High-quality Blue Dream flower',
            'Expected Product Strain': 'Blue Dream'  # Should keep original
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Add required columns that ExcelProcessor expects
    df['Product Brand'] = 'Test Brand'
    df['Vendor'] = 'Test Vendor'
    df['Lineage'] = ''
    df['Product Strain'] = ''  # Start with empty Product Strain
    df['Ratio'] = ''
    df['Price'] = '10.00'
    df['Weight*'] = '1.0'
    df['Units'] = 'oz'
    
    # Create a temporary Excel file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        df.to_excel(tmp_file.name, index=False)
        temp_file_path = tmp_file.name
    
    try:
        # Create ExcelProcessor instance
        processor = ExcelProcessor()
        
        # Load the file using the full pipeline
        success = processor.load_file(temp_file_path)
        
        if not success:
            print("❌ Failed to load file")
            return False
        
        print("=== Full Pipeline Results ===")
        results = []
        
        for idx, row in processor.df.iterrows():
            product_name = row.get('ProductName', row.get('Product Name*', 'Unknown'))
            product_type = row['Product Type*']
            description = row['Description']
            actual_strain = row['Product Strain']
            expected_strain = row['Expected Product Strain']
            
            # Check if it's an edible
            edible_types = {"edible (solid)", "edible (liquid)", "high cbd edible liquid", "tincture", "topical", "capsule"}
            is_edible = product_type.lower() in edible_types
            
            # Check if description contains cannabinoids
            has_cannabinoids = bool(pd.Series([description]).str.contains(r"CBD|CBG|CBN|CBC", case=False, na=False).iloc[0])
            
            result = {
                'Product': product_name,
                'Type': product_type,
                'Is Edible': is_edible,
                'Has Cannabinoids': has_cannabinoids,
                'Actual Strain': actual_strain,
                'Expected Strain': expected_strain,
                'Correct': actual_strain == expected_strain
            }
            results.append(result)
            
            status = "✅ PASS" if actual_strain == expected_strain else "❌ FAIL"
            print(f"{status} | {product_name} | {product_type} | Cannabinoids: {has_cannabinoids} | Actual: {actual_strain} | Expected: {expected_strain}")
        
        # Summary
        correct_count = sum(1 for r in results if r['Correct'])
        total_count = len(results)
        
        print(f"\n=== Summary ===")
        print(f"Total tests: {total_count}")
        print(f"Passed: {correct_count}")
        print(f"Failed: {total_count - correct_count}")
        print(f"Success rate: {correct_count/total_count*100:.1f}%")
        
        if correct_count == total_count:
            print("🎉 All tests passed! The fix works in the full pipeline.")
        else:
            print("⚠️  Some tests failed. The fix needs more work.")
        
        return correct_count == total_count
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass

if __name__ == "__main__":
    success = test_full_pipeline_edible_strain()
    sys.exit(0 if success else 1) 