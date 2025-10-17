#!/usr/bin/env python3
"""
Debug CBD text rendering in Word documents
"""

import sys
import os
import logging
import tempfile
import pandas as pd

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.core.data.excel_processor import ExcelProcessor
from src.core.generation.tag_generator import TagGenerator

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cbd_text_generation():
    """Test that CBD text is actually rendered in the Word document."""
    print("=== CBD TEXT GENERATION TEST ===")
    
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
        
        # Process through ExcelProcessor
        processor = ExcelProcessor()
        success = processor.load_and_process_file(temp_file_path)
        
        if success:
            print(f"✅ File processed successfully")
            print(f"DataFrame shape: {processor.df.shape}")
            print("\nProcessed data:")
            for i, row in processor.df.iterrows():
                product_name = row.get('ProductName', row.get('Product Name*', ''))
                lineage = row.get('Lineage', '')
                print(f"  {product_name}: Lineage = '{lineage}'")
            
            # Now test Word document generation
            print("\n=== WORD DOCUMENT GENERATION ===")
            
            # Convert to list of dictionaries for tag generator
            tags_data = processor.df.to_dict('records')
            
            # Generate Word document using TagGenerator
            tag_generator = TagGenerator()
            
            # Create output file path
            output_path = "/Users/adamcordova/Desktop/labelMaker_ QR copy final copy 10/cbd_text_test.docx"
            
            try:
                result = tag_generator.generate_tags_document(tags_data, output_path)
                
                if result.get('success'):
                    print(f"✅ Word document generated successfully: {output_path}")
                    print(f"Generated {result.get('total_tags', 0)} tags")
                    
                    # Let's manually check what was set in the label contexts
                    print("\n=== CHECKING LABEL CONTEXTS ===")
                    for i, tag in enumerate(tags_data):
                        product_name = tag.get('ProductName', tag.get('Product Name*', ''))
                        lineage = tag.get('Lineage', '')
                        print(f"Tag {i+1}: {product_name}")
                        print(f"  - Input Lineage: '{lineage}'")
                        
                        # Check if this is a CBD product
                        if 'CBD' in product_name.upper():
                            if lineage == 'CBD':
                                print(f"  ✅ CBD product has CBD lineage")
                            else:
                                print(f"  ❌ CBD product has wrong lineage: '{lineage}'")
                    
                else:
                    print(f"❌ Word document generation failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Word document generation error: {e}")
                import traceback
                traceback.print_exc()
            
        else:
            print(f"❌ File processing failed")
            
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    test_cbd_text_generation()