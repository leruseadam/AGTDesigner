#!/usr/bin/env python3
"""
Test script to verify the CBD classic type fix using the actual ExcelProcessor.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import tempfile

def test_actual_excel_processor():
    """Test the actual ExcelProcessor with CBD products."""
    print("=== TESTING ACTUAL EXCEL PROCESSOR WITH CBD FIX ===")
    
    # Create test Excel data
    test_data = {
        'Product Name*': [
            'CBD Flower - Charlotte\'s Web',
            'THC Flower - Blue Dream', 
            'CBD Pre-Roll',
            'CBD Gummies',
            'CBD Vape Cart'
        ],
        'Product Type*': [
            'Flower',
            'Flower', 
            'Pre-roll',
            'Edible (Solid)',
            'Vape Cartridge'
        ],
        'Product Strain': [
            'CBD Blend',
            'Blue Dream',
            'CBD Blend', 
            'CBD Blend',
            'CBD Blend'
        ],
        'Lineage': [
            '',  # Empty - should get CBD
            'HYBRID',  # Should stay HYBRID
            '',  # Empty - should get CBD
            '',  # Empty - should get CBD or MIXED (edible)
            ''   # Empty - should get CBD
        ],
        'Weight*': ['3.5g', '3.5g', '1g', '10mg', '1g'],
        'Product Brand': ['Test Brand'] * 5,
        'Vendor/Supplier*': ['Test Vendor'] * 5,
        'Price*': ['$25.00'] * 5
    }
    
    df = pd.DataFrame(test_data)
    
    # Create a temporary Excel file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        df.to_excel(tmp_file.name, index=False)
        temp_file_path = tmp_file.name
    
    try:
        # Test with actual ExcelProcessor
        from src.core.data.excel_processor import ExcelProcessor
        
        processor = ExcelProcessor()
        success = processor.load_file(temp_file_path)
        
        if not success:
            print("❌ Failed to load test file")
            return
        
        print("✅ Successfully loaded test file")
        print(f"Processed {len(processor.df)} rows")
        
        # Check the results
        print("\nResults after processing:")
        for i, row in processor.df.iterrows():
            product_name = row.get('Product Name*', 'Unknown')
            product_type = row.get('Product Type*', 'Unknown')
            product_strain = row.get('Product Strain', 'Unknown')
            lineage = row.get('Lineage', 'Unknown')
            
            print(f"\n  {i+1}. {product_name}")
            print(f"     Type: {product_type}")
            print(f"     Strain: {product_strain}")
            print(f"     Lineage: '{lineage}'")
            
            # Check expected results
            if 'CBD Flower' in product_name:
                if lineage == 'CBD':
                    print(f"     ✅ CORRECT: CBD flower got CBD lineage")
                else:
                    print(f"     ❌ WRONG: Expected CBD, got '{lineage}'")
            
            elif 'CBD Pre-Roll' in product_name:
                if lineage == 'CBD':
                    print(f"     ✅ CORRECT: CBD pre-roll got CBD lineage")
                else:
                    print(f"     ❌ WRONG: Expected CBD, got '{lineage}'")
            
            elif 'THC Flower' in product_name:
                if lineage == 'HYBRID':
                    print(f"     ✅ CORRECT: THC flower kept HYBRID lineage")
                else:
                    print(f"     ❌ WRONG: Expected HYBRID, got '{lineage}'")
            
            elif 'CBD Gummies' in product_name:
                if lineage in ['CBD', 'MIXED']:
                    print(f"     ✅ ACCEPTABLE: Edible got '{lineage}' lineage")
                else:
                    print(f"     ❌ WRONG: Edible got unexpected lineage '{lineage}'")
            
            elif 'CBD Vape Cart' in product_name:
                if lineage == 'CBD':
                    print(f"     ✅ CORRECT: CBD vape cart got CBD lineage")
                else:
                    print(f"     ❌ WRONG: Expected CBD, got '{lineage}'")
        
        # Test styling implications
        print("\n=== STYLING IMPLICATIONS ===")
        from src.core.constants import CLASSIC_TYPES
        
        for i, row in processor.df.iterrows():
            product_name = row.get('Product Name*', 'Unknown')
            product_type = row.get('Product Type*', 'Unknown')
            lineage = row.get('Lineage', 'Unknown')
            
            is_classic = product_type.lower() in [ct.lower() for ct in CLASSIC_TYPES]
            
            if is_classic:
                styling = "Classic styling (shows lineage)"
                color = get_lineage_color(lineage)
            else:
                styling = "Non-classic styling (shows brand)"
                color = "blue"
            
            print(f"\n  {product_name}:")
            print(f"    Type: {product_type} ({'Classic' if is_classic else 'Non-Classic'})")
            print(f"    Lineage: {lineage}")
            print(f"    Expected Styling: {styling}")
            print(f"    Expected Color: {color}")
    
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except:
            pass

def get_lineage_color(lineage):
    """Get the expected color for a lineage."""
    colors = {
        'SATIVA': 'red',
        'INDICA': 'purple',
        'HYBRID': 'green',
        'HYBRID/SATIVA': 'red', 
        'HYBRID/INDICA': 'purple',
        'CBD': 'yellow',
        'MIXED': 'blue',
        'PARAPHERNALIA': 'pink'
    }
    return colors.get(lineage, 'unknown')

if __name__ == "__main__":
    test_actual_excel_processor()
    print("\n=== ACTUAL EXCEL PROCESSOR TEST COMPLETE ===")
