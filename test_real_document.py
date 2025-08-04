#!/usr/bin/env python3
"""
Test to generate a real document with actual data to check formatting
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

def test_real_document():
    """Generate a real document with actual data to check formatting."""
    print("Generating real document with actual data...")
    
    try:
        # Create template processor for double template
        processor = TemplateProcessor('double', FONT_SCHEME_DOUBLE)
        
        # Create realistic test records
        test_records = [
            {
                'ProductName': 'HUSTLER\'S AMBITION Cheesecake',
                'ProductType': 'flower',
                'ProductBrand': 'HUSTLER\'S AMBITION',
                'Price': '$100',
                'Lineage': 'HYBRID',
                'Description': 'Cheesecake',
                'WeightUnits': '14g',
                'Ratio_or_THC_CBD': 'THC: 24.95% CBD: 0.05%',
                'Vendor': 'Test Vendor',
                'Product Strain': 'Cheesecake',
                'DOH': 'YES'
            },
            {
                'ProductName': 'HUSTLER\'S AMBITION Churros',
                'ProductType': 'flower',
                'ProductBrand': 'HUSTLER\'S AMBITION',
                'Price': '$100',
                'Lineage': 'HYBRID',
                'Description': 'Churros',
                'WeightUnits': '14g',
                'Ratio_or_THC_CBD': 'THC: 19.0% CBD: 0.03%',
                'Vendor': 'Test Vendor',
                'Product Strain': 'Churros',
                'DOH': 'YES'
            }
        ]
        
        # Process the records
        print("Processing test records...")
        result_doc = processor.process_records(test_records)
        
        if result_doc is None:
            print("❌ Template processing returned None")
            return False
        
        print("✅ Template processing completed")
        
        # Save to a file
        output_path = "test_double_template_output.docx"
        result_doc.save(output_path)
        
        print(f"✅ Document saved to: {output_path}")
        print("✅ Real document test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_document()
    sys.exit(0 if success else 1) 