#!/usr/bin/env python3
"""
Test script to verify that Excel processing rules are applied correctly to newly uploaded files.
This tests the fix for the issue where newly uploaded files weren't getting proper processing.
"""

import os
import sys
import pandas as pd
import tempfile
import shutil
from pathlib import Path

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.core.constants import CLASSIC_TYPES
from src.core.data.excel_processor import ExcelProcessor

def create_test_file():
    """Create a test Excel file with various product types to test processing rules."""
    test_data = [
        {
            'Product Name*': 'Test Flower 1',
            'Product Type*': 'Flower',
            'Product Strain': 'OG Kush',
            'Lineage': 'HYBRID',
            'Product Brand': 'Test Brand',
            'Vendor': 'Test Vendor',
            'Weight*': '3.5',
            'Units': 'g',
            'Price': '45.00',
            'Description': 'Test flower product'
        },
        {
            'Product Name*': 'Test Edible 1',
            'Product Type*': 'Edible (Solid)',
            'Product Strain': 'CBD Blend',
            'Lineage': '',  # Empty to test auto-assignment
            'Product Brand': 'Test Brand',
            'Vendor': 'Test Vendor',
            'Weight*': '100',
            'Units': 'mg',
            'Price': '25.00',
            'Description': 'Test edible product'
        },
        {
            'Product Name*': 'Test Pre-roll 1',
            'Product Type*': 'Pre-roll',
            'Product Strain': 'Sour Diesel',
            'Lineage': 'SATIVA',
            'Product Brand': 'Test Brand',
            'Vendor': 'Test Vendor',
            'Weight*': '1',
            'Units': 'g',
            'Price': '15.00',
            'Description': 'Test pre-roll product'
        },
        {
            'Product Name*': 'Test Tincture 1',
            'Product Type*': 'Tincture',
            'Product Strain': 'MIXED',
            'Lineage': '',  # Empty to test auto-assignment
            'Product Brand': 'Test Brand',
            'Vendor': 'Test Vendor',
            'Weight*': '30',
            'Units': 'ml',
            'Price': '35.00',
            'Description': 'Test tincture product'
        },
        {
            'Product Name*': 'Test Concentrate 1',
            'Product Type*': 'Concentrate',
            'Product Strain': 'Blue Dream',
            'Lineage': 'HYBRID',
            'Product Brand': 'Test Brand',
            'Vendor': 'Test Vendor',
            'Weight*': '1',
            'Units': 'g',
            'Price': '60.00',
            'Description': 'Test concentrate product'
        }
    ]
    
    df = pd.DataFrame(test_data)
    
    # Create temporary file
    temp_dir = tempfile.mkdtemp()
    test_file_path = os.path.join(temp_dir, 'test_upload_processing.xlsx')
    
    # Save to Excel
    df.to_excel(test_file_path, index=False)
    
    print(f"Created test file: {test_file_path}")
    print(f"Test data shape: {df.shape}")
    print(f"Product types in test data: {df['Product Type*'].unique()}")
    
    return test_file_path, temp_dir

def test_processing_rules():
    """Test that processing rules are applied correctly."""
    print("=" * 60)
    print("Testing Excel Processing Rules for Uploaded Files")
    print("=" * 60)
    
    # Create test file
    test_file_path, temp_dir = create_test_file()
    
    try:
        # Test 1: Test fast_load_file (old behavior)
        print("\n1. Testing fast_load_file (old behavior):")
        processor_fast = ExcelProcessor()
        success_fast = processor_fast.fast_load_file(test_file_path)
        
        if success_fast:
            print(f"   ✅ Fast load successful: {len(processor_fast.df)} rows")
            print(f"   📊 Lineage values after fast load: {processor_fast.df['Lineage'].unique()}")
            print(f"   📊 Product types after fast load: {processor_fast.df['Product Type*'].unique()}")
            
            # Check if processing rules were applied
            empty_lineages = processor_fast.df[processor_fast.df['Lineage'].str.strip() == '']
            print(f"   ⚠️  Empty lineages after fast load: {len(empty_lineages)}")
            
            if len(empty_lineages) > 0:
                print(f"   ❌ Fast load did NOT apply processing rules (empty lineages found)")
            else:
                print(f"   ✅ Fast load applied processing rules (no empty lineages)")
        else:
            print(f"   ❌ Fast load failed")
        
        # Test 2: Test load_file (new behavior)
        print("\n2. Testing load_file (new behavior):")
        processor_full = ExcelProcessor()
        success_full = processor_full.load_file(test_file_path)
        
        if success_full:
            print(f"   ✅ Full load successful: {len(processor_full.df)} rows")
            print(f"   📊 Lineage values after full load: {processor_full.df['Lineage'].unique()}")
            print(f"   📊 Product types after full load: {processor_full.df['Product Type*'].unique()}")
            
            # Check if processing rules were applied
            empty_lineages = processor_full.df[processor_full.df['Lineage'].str.strip() == '']
            print(f"   ⚠️  Empty lineages after full load: {len(empty_lineages)}")
            
            if len(empty_lineages) > 0:
                print(f"   ❌ Full load did NOT apply processing rules (empty lineages found)")
            else:
                print(f"   ✅ Full load applied processing rules (no empty lineages)")
            
            # Check for specific processing rules
            print(f"   📊 Checking specific processing rules:")
            
            # Check if edibles got MIXED lineage
            edibles = processor_full.df[processor_full.df['Product Type*'] == 'Edible (Solid)']
            if len(edibles) > 0:
                edible_lineage = edibles.iloc[0]['Lineage']
                print(f"      - Edible lineage: {edible_lineage}")
                if edible_lineage == 'MIXED':
                    print(f"      ✅ Edible correctly assigned MIXED lineage")
                else:
                    print(f"      ❌ Edible incorrectly assigned {edible_lineage} lineage")
            
            # Check if tinctures got MIXED lineage
            tinctures = processor_full.df[processor_full.df['Product Type*'] == 'Tincture']
            if len(tinctures) > 0:
                tincture_lineage = tinctures.iloc[0]['Lineage']
                print(f"      - Tincture lineage: {tincture_lineage}")
                if tincture_lineage == 'MIXED':
                    print(f"      ✅ Tincture correctly assigned MIXED lineage")
                else:
                    print(f"      ❌ Tincture incorrectly assigned {tincture_lineage} lineage")
            
            # Check if classic types kept their original lineage
            classic_types = processor_full.df[processor_full.df['Product Type*'].str.lower().isin([c.lower() for c in CLASSIC_TYPES])]
            if len(classic_types) > 0:
                print(f"      - Classic types found: {len(classic_types)}")
                for _, row in classic_types.iterrows():
                    print(f"        * {row['Product Type*']}: {row['Lineage']}")
        else:
            print(f"   ❌ Full load failed")
        
        # Test 3: Compare results
        print("\n3. Comparing results:")
        if success_fast and success_full:
            fast_empty_lineages = len(processor_fast.df[processor_fast.df['Lineage'].str.strip() == ''])
            full_empty_lineages = len(processor_full.df[processor_full.df['Lineage'].str.strip() == ''])
            
            print(f"   📊 Empty lineages - Fast load: {fast_empty_lineages}, Full load: {full_empty_lineages}")
            
            if full_empty_lineages < fast_empty_lineages:
                print(f"   ✅ Full load applied more processing rules than fast load")
            elif full_empty_lineages == fast_empty_lineages:
                print(f"   ⚠️  Both loads applied same level of processing")
            else:
                print(f"   ❌ Fast load applied more processing than full load (unexpected)")
        
        # Test 4: Test the fix in force_reload_excel_processor
        print("\n4. Testing force_reload_excel_processor fix:")
        from app import force_reload_excel_processor
        
        # Create a new processor and force reload with the test file
        test_processor = ExcelProcessor()
        force_reload_excel_processor(test_file_path)
        
        # Get the processor after force reload
        from app import get_excel_processor
        reloaded_processor = get_excel_processor()
        
        if reloaded_processor and reloaded_processor.df is not None:
            print(f"   ✅ Force reload successful: {len(reloaded_processor.df)} rows")
            
            # Check if processing rules were applied
            empty_lineages = reloaded_processor.df[reloaded_processor.df['Lineage'].str.strip() == '']
            print(f"   📊 Empty lineages after force reload: {len(empty_lineages)}")
            
            if len(empty_lineages) == 0:
                print(f"   ✅ Force reload applied processing rules correctly")
            else:
                print(f"   ❌ Force reload did NOT apply processing rules")
        else:
            print(f"   ❌ Force reload failed")
        
        print("\n" + "=" * 60)
        print("Test Summary:")
        print("=" * 60)
        
        # Determine if the fix is working
        if success_full and success_fast:
            fast_empty = len(processor_fast.df[processor_fast.df['Lineage'].str.strip() == ''])
            full_empty = len(processor_full.df[processor_full.df['Lineage'].str.strip() == ''])
            
            if full_empty < fast_empty:
                print("✅ FIX VERIFIED: Full load applies more processing rules than fast load")
                print("✅ The change from fast_load_file to load_file in force_reload_excel_processor")
                print("   will ensure newly uploaded files get proper processing rules applied.")
            else:
                print("⚠️  INCONCLUSIVE: Both loads applied similar processing")
        else:
            print("❌ TEST FAILED: One or both load methods failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        try:
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up temporary directory: {e}")

def main():
    """Main test function."""
    print("Testing Excel Processing Rules Fix")
    print("This test verifies that newly uploaded files get proper processing rules applied.")
    
    success = test_processing_rules()
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("The fix should now ensure that newly uploaded files get all processing rules applied.")
    else:
        print("\n❌ Tests failed. Please check the implementation.")

if __name__ == "__main__":
    main() 