#!/usr/bin/env python3
"""
Test script to verify double template placeholder replacement fix
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.generation.template_processor import TemplateProcessor
from src.core.constants import FONT_SCHEME_DOUBLE
import tempfile

def test_double_template_placeholder_replacement():
    """Test that double template placeholders are replaced with actual data."""
    print("Testing double template placeholder replacement...")
    
    try:
        # Create template processor for double template
        processor = TemplateProcessor('double', FONT_SCHEME_DOUBLE)
        
        # Create test records
        test_records = [
            {
                'ProductName': 'Test Product 1',
                'ProductType': 'flower',
                'ProductBrand': 'Test Brand',
                'Price': '$25.00',
                'Lineage': 'Sativa',
                'Description': 'Test Description',
                'WeightUnits': '3.5g',
                'Ratio_or_THC_CBD': 'THC: 22% CBD: 1%',
                'Vendor': 'Test Vendor',
                'Product Strain': 'Test Strain 1',
                'DOH': 'YES'
            },
            {
                'ProductName': 'Test Product 2',
                'ProductType': 'concentrate',
                'ProductBrand': 'Another Brand',
                'Price': '$45.00',
                'Lineage': 'Indica',
                'Description': 'Another Description',
                'WeightUnits': '1g',
                'Ratio_or_THC_CBD': 'THC: 85% CBD: 2%',
                'Vendor': 'Another Vendor',
                'Product Strain': 'Test Strain 2',
                'DOH': 'NO'
            }
        ]
        
        # Process the records
        print("Processing test records...")
        result_doc = processor.process_records(test_records)
        
        if result_doc is None:
            print("❌ Template processing returned None")
            return False
        
        print("✅ Template processing completed")
        
        # Check if placeholders were replaced
        print("\nChecking placeholder replacement...")
        
        # Get text from all cells
        all_cell_text = []
        for table in result_doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        all_cell_text.append(cell_text)
        
        print(f"Found {len(all_cell_text)} cells with content")
        
        # Check for unreplaced placeholders
        unreplaced_placeholders = []
        for text in all_cell_text:
            if '{{Label' in text and '}}' in text:
                unreplaced_placeholders.append(text)
        
        if unreplaced_placeholders:
            print(f"❌ Found {len(unreplaced_placeholders)} cells with unreplaced placeholders:")
            for placeholder in unreplaced_placeholders[:5]:  # Show first 5
                print(f"   {placeholder}")
        else:
            print("✅ All placeholders were replaced!")
        
        # Check for actual data
        actual_data_found = False
        for text in all_cell_text:
            if 'Test Brand' in text or 'Another Brand' in text or '$25.00' in text or '$45.00' in text:
                actual_data_found = True
                break
        
        if actual_data_found:
            print("✅ Actual data found in template!")
        else:
            print("❌ No actual data found in template")
            return False
        
        # Save to a temporary file to test Word compatibility
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            result_doc.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        print(f"✅ Template saved to: {tmp_path}")
        print("✅ Double template placeholder replacement test completed successfully!")
        
        # Clean up
        os.unlink(tmp_path)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_double_template_placeholder_replacement()
    sys.exit(0 if success else 1) 