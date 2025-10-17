#!/usr/bin/env python3
"""
Simple debug script to check what happens to CBD lineage values
"""

import sys
import os
import logging
import tempfile
import pandas as pd

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.core.data.excel_processor import ExcelProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_cbd_lineage_processing():
    """Debug CBD lineage values through the processing pipeline."""
    print("=== CBD LINEAGE PROCESSING DEBUG ===")
    
    # Create test data with CBD products
    test_data = {
        'Product Name*': ['CBD Huckleberry Web - 1g', 'Regular Product - 1g'],
        'Product Type*': ['Flower', 'Flower'],
        'Product Strain': ['', ''],
        'Lineage': ['CBD', 'HYBRID'],
        'Vendor': ['Test Vendor', 'Test Vendor'],
        'Price': ['$10', '$10'],
        'Weight*': ['1g', '1g'],
        'Ratio': ['', ''],
        'Units': ['', ''],
        'Quantity*': [1, 1],
        'THC test result': ['', ''],
        'CBD test result': ['', ''],
        'Test result unit (% or mg)': ['', '']
    }
    
    # Create Excel file
    df = pd.DataFrame(test_data)
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
        df.to_excel(temp_file.name, index=False)
        temp_file_path = temp_file.name
    
    try:
        print(f"Created test Excel file: {temp_file_path}")
        print("Initial data:")
        for i, row in df.iterrows():
            print(f"  {row['Product Name*']}: Lineage = '{row['Lineage']}'")
        
        # Process through ExcelProcessor
        processor = ExcelProcessor()
        success = processor.load_file(temp_file_path)
        
        if success:
            print(f"\n✅ File processed successfully")
            print(f"DataFrame shape: {processor.df.shape}")
            print("\nProcessed data:")
            for i, row in processor.df.iterrows():
                product_name = row.get('ProductName', row.get('Product Name*', ''))
                lineage = row.get('Lineage', '')
                print(f"  {product_name}: Lineage = '{lineage}' (type: {type(lineage)})")
                
                # Check if this is the CBD product
                if 'CBD' in product_name.upper():
                    if lineage == 'CBD':
                        print(f"    ✅ CBD product correctly has CBD lineage")
                    elif lineage == '':
                        print(f"    ❌ CBD product has EMPTY lineage!")
                    else:
                        print(f"    ❌ CBD product has wrong lineage: '{lineage}'")
                        
            # Now let's convert to the format used for Word generation
            print("\n=== CONVERSION TO WORD GENERATION FORMAT ===")
            tags_data = processor.df.to_dict('records')
            
            for i, tag in enumerate(tags_data):
                product_name = tag.get('ProductName', tag.get('Product Name*', ''))
                lineage = tag.get('Lineage', '')
                print(f"Tag {i+1}: {product_name}")
                print(f"  - Lineage field: '{lineage}' (type: {type(lineage)})")
                print(f"  - All tag keys: {list(tag.keys())}")
                
                # Check for CBD
                if 'CBD' in product_name.upper():
                    if lineage == 'CBD':
                        print(f"    ✅ CBD tag ready for Word generation with CBD lineage")
                    else:
                        print(f"    ❌ CBD tag problem - lineage is '{lineage}' not 'CBD'")
                        
        else:
            print(f"❌ File processing failed")
            
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    debug_cbd_lineage_processing()