#!/usr/bin/env python3
"""
Integration test to verify CBD lineage is preserved through the entire Excel loading process.
This test simulates the actual file loading process to ensure CBD lineage isn't overridden.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import tempfile
from src.core.data.excel_processor import ExcelProcessor

def test_cbd_lineage_integration():
    """Test CBD lineage preservation through the complete file loading process."""
    print("=== INTEGRATION TEST: CBD LINEAGE PRESERVATION ===")
    
    # Create test Excel data that matches the real scenario
    test_data = {
        'Product Name*': [
            'CBD Huckleberry Web - 1g',
            'Terpgasm - 1g', 
            'GMO - 1g',
            'CBD Pre-Roll - 1g',
            'Regular Flower - 1g'
        ],
        'Product Type*': [
            'Flower',
            'Flower', 
            'Flower',
            'Pre-Roll',
            'Flower'
        ],
        'Product Strain': [
            'CBD Huckleberry Web',
            'Terpgasm',
            'GMO',
            'CBD Blend',
            'Regular Strain'
        ],
        'Lineage': [
            'HYBRID',  # Should become CBD
            'HYBRID',  # Should stay HYBRID
            'SATIVA',  # Should stay SATIVA
            '',        # Should become CBD (empty lineage)
            ''         # Should become HYBRID (empty lineage)
        ],
        'Vendor': ['Test Vendor'] * 5,
        'Price': [10.0] * 5,
        'Weight*': [1.0] * 5,
        'Ratio': [''] * 5,  # Add missing Ratio column
        'Units': ['g'] * 5,  # Add missing Units column
        'Quantity*': [1] * 5,  # Add missing Quantity column
        'THC test result': [0.0] * 5,  # Add missing THC column
        'CBD test result': [0.0] * 5,  # Add missing CBD column
        'Test result unit (% or mg)': ['%'] * 5  # Add missing test result unit column
    }
    
    # Create a temporary Excel file
    df = pd.DataFrame(test_data)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        df.to_excel(tmp_file.name, index=False)
        temp_file_path = tmp_file.name
    
    try:
        print("Original test data:")
        for i, row in df.iterrows():
            print(f"  {i+1}. {row['Product Name*']} ({row['Product Type*']}) - Lineage: '{row['Lineage']}'")
        
        # Load the file using ExcelProcessor (this simulates the real loading process)
        processor = ExcelProcessor()
        success = processor.load_file(temp_file_path)
        
        if not success:
            print("❌ FAILED: Could not load test file")
            return False
        
        print(f"\nFile loaded successfully. DataFrame shape: {processor.df.shape}")
        
        # Check the results
        print("\nResults after complete loading process:")
        all_correct = True
        
        for i, row in processor.df.iterrows():
            # Use ProductName (the processed column name) instead of Product Name*
            product_name = row.get('ProductName', row.get('Product Name*', 'Unknown'))
            product_type = row['Product Type*']
            lineage = row['Lineage']
            
            print(f"\n  {i+1}. {product_name}")
            print(f"     Type: {product_type}")
            print(f"     Final Lineage: '{lineage}'")
            
            # Check expected results
            if 'CBD' in product_name:
                expected = 'CBD'
                if lineage == expected:
                    print(f"     ✅ CORRECT: CBD product got CBD lineage")
                else:
                    print(f"     ❌ WRONG: Expected {expected}, got {lineage}")
                    all_correct = False
            elif product_name == 'Terpgasm - 1g' or product_name == 'Terpgasm':
                expected = 'HYBRID'
                if lineage == expected:
                    print(f"     ✅ CORRECT: Non-CBD classic type got HYBRID lineage")
                else:
                    print(f"     ❌ WRONG: Expected {expected}, got {lineage}")
                    all_correct = False
            elif product_name == 'GMO - 1g' or product_name == 'GMO':
                expected = 'SATIVA'
                if lineage == expected:
                    print(f"     ✅ CORRECT: Non-CBD classic type kept original lineage")
                else:
                    print(f"     ❌ WRONG: Expected {expected}, got {lineage}")
                    all_correct = False
            elif 'Regular Flower' in product_name:
                expected = 'HYBRID'
                if lineage == expected:
                    print(f"     ✅ CORRECT: Regular flower got default HYBRID lineage")
                else:
                    print(f"     ❌ WRONG: Expected {expected}, got {lineage}")
                    all_correct = False
        
        print(f"\n=== INTEGRATION TEST SUMMARY ===")
        if all_correct:
            print("✅ ALL TESTS PASSED - CBD lineage preservation works through complete loading process!")
            print("🎉 The fix successfully prevents CBD lineage from being overridden")
        else:
            print("❌ SOME TESTS FAILED - CBD lineage is still being overridden somewhere")
            
        return all_correct
        
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except:
            pass

def test_specific_product_names():
    """Test with specific product names that were problematic."""
    print("\n=== SPECIFIC PRODUCT NAME TEST ===")
    
    # Test the exact product from the Word document
    test_data = {
        'Product Name*': [
            'CBD Huckleberry Web - 1g',
            'Grapefruit - 1g'
        ],
        'Product Type*': [
            'Flower',
            'Flower'
        ],
        'Product Strain': [
            'CBD Huckleberry Web',
            'Grapefruit'
        ],
        'Lineage': [
            'HYBRID',  # This was the problem - should become CBD
            'SATIVA'   # This should stay SATIVA
        ],
        'Vendor': ['Test Vendor'] * 2,
        'Price': [10.0] * 2,
        'Weight*': [1.0] * 2,
        'Ratio': [''] * 2,  # Add missing Ratio column
        'Units': ['g'] * 2,  # Add missing Units column
        'Quantity*': [1] * 2,  # Add missing Quantity column
        'THC test result': [0.0] * 2,  # Add missing THC column
        'CBD test result': [0.0] * 2,  # Add missing CBD column
        'Test result unit (% or mg)': ['%'] * 2  # Add missing test result unit column
    }
    
    df = pd.DataFrame(test_data)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        df.to_excel(tmp_file.name, index=False)
        temp_file_path = tmp_file.name
    
    try:
        processor = ExcelProcessor()
        success = processor.load_file(temp_file_path)
        
        if success:
            # Use ProductName (the processed column name) instead of Product Name*
            cbd_huckleberry = processor.df[processor.df['ProductName'].str.contains('CBD Huckleberry', na=False)]
            grapefruit = processor.df[processor.df['ProductName'].str.contains('Grapefruit', na=False)]
            
            if not cbd_huckleberry.empty:
                cbd_lineage = cbd_huckleberry.iloc[0]['Lineage']
                print(f"CBD Huckleberry Web - 1g: Lineage = '{cbd_lineage}'")
                if cbd_lineage == 'CBD':
                    print("✅ PERFECT: CBD Huckleberry Web got CBD lineage!")
                else:
                    print(f"❌ PROBLEM: CBD Huckleberry Web got '{cbd_lineage}' instead of 'CBD'")
            
            if not grapefruit.empty:
                grapefruit_lineage = grapefruit.iloc[0]['Lineage']
                print(f"Grapefruit - 1g: Lineage = '{grapefruit_lineage}'")
                if grapefruit_lineage == 'SATIVA':
                    print("✅ CORRECT: Grapefruit kept SATIVA lineage")
                else:
                    print(f"❌ UNEXPECTED: Grapefruit got '{grapefruit_lineage}' instead of 'SATIVA'")
        
    finally:
        try:
            os.unlink(temp_file_path)
        except:
            pass

if __name__ == "__main__":
    success = test_cbd_lineage_integration()
    test_specific_product_names()
    
    print(f"\n=== INTEGRATION TEST COMPLETE ===")
    
    if success:
        print("🎯 The CBD lineage fix is working correctly through the complete loading process")
        print("🔄 Restart the web application to apply the changes")
        print("📋 'CBD Huckleberry Web' should now show yellow CBD styling instead of green HYBRID")
    else:
        print("🚨 There are still issues with CBD lineage preservation")
    
    sys.exit(0 if success else 1)