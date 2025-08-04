#!/usr/bin/env python3
"""
Detailed debug script to investigate missing product brand in double template.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_brand_missing_debug():
    """Debug missing product brand in double template."""
    
    print("Investigating Missing Product Brand")
    print("=" * 50)
    
    # Test data with different brand scenarios
    test_records = [
        {
            'Product Name*': 'Test Product 1',
            'ProductBrand': 'Test Brand 1',
            'Product Brand': 'Test Brand 1',
            'Price': '$25.00',
            'Description': 'Test description 1',
            'Lineage': 'HYBRID',
            'THC_CBD': 'THC: 20% CBD: 2%',
            'WeightUnits': '3.5g',
            'ProductType': 'flower',
            'Product Strain': 'Test Strain 1'
        },
        {
            'Product Name*': 'Test Product 2',
            'ProductBrand': 'Test Brand 2',
            'Product Brand': 'Test Brand 2',
            'Price': '$30.00',
            'Description': 'Test description 2',
            'Lineage': 'SATIVA',
            'THC_CBD': 'THC: 18% CBD: 1%',
            'WeightUnits': '1g',
            'ProductType': 'concentrate',
            'Product Strain': 'Test Strain 2'
        }
    ]
    
    try:
        print("\n1. Creating template processor...")
        double_processor = TemplateProcessor('double', {}, 1.0)
        
        print("\n2. Testing label context building...")
        # Test the label context building directly
        doc = double_processor._get_template_path()
        for i, record in enumerate(test_records):
            print(f"\n   Record {i+1}:")
            context = double_processor._build_label_context(record, None)
            
            # Check brand-related fields
            brand_fields = ['ProductBrand', 'Product Brand', 'Brand']
            found_brand = False
            for field in brand_fields:
                if field in context:
                    print(f"     {field}: '{context[field]}'")
                    found_brand = True
            
            if not found_brand:
                print("     ❌ No brand fields found in context")
            
            # Check if brand markers are present
            brand_markers = ['PRODUCTBRAND_CENTER_START', 'PRODUCTBRAND_CENTER_END']
            for marker in brand_markers:
                if marker in str(context):
                    print(f"     ✓ Found {marker} marker")
                else:
                    print(f"     ❌ Missing {marker} marker")
        
        print("\n3. Processing records...")
        result = double_processor.process_records(test_records)
        assert result is not None, "Template processing failed"
        
        print("\n4. Examining all cells in detail...")
        table = result.tables[0]
        
        for row_idx in range(len(table.rows)):
            for col_idx in range(len(table.columns)):
                cell = table.cell(row_idx, col_idx)
                if cell.text.strip():  # Only examine non-empty cells
                    print(f"\n   Cell ({row_idx}, {col_idx}):")
                    print(f"     Text: '{cell.text}'")
                    
                    # Split by lines and analyze
                    lines = cell.text.split('\n')
                    print(f"     Lines: {len(lines)}")
                    for line_idx, line in enumerate(lines):
                        if line.strip():
                            print(f"       Line {line_idx}: '{line}'")
                    
                    # Check for brand content
                    if 'Test Brand' in cell.text:
                        print("     ✓ Contains brand content")
                    else:
                        print("     ❌ No brand content found")
                    
                    # Check paragraph structure
                    for para_idx, para in enumerate(cell.paragraphs):
                        if para.text.strip():
                            print(f"     Paragraph {para_idx}: '{para.text}'")
                            print(f"       Runs: {len(para.runs)}")
                            for run_idx, run in enumerate(para.runs):
                                font_size = run.font.size.pt if run.font.size else "None"
                                print(f"         Run {run_idx}: '{run.text}' - Font: {font_size}pt")
        
        print("\n5. Checking template expansion...")
        # Check if the template has the ProductBrand placeholder
        template_doc = double_processor._expand_template_if_needed()
        template_table = template_doc.tables[0]
        
        productbrand_placeholders = 0
        for row in template_table.rows:
            for cell in row.cells:
                if 'ProductBrand' in cell.text:
                    productbrand_placeholders += 1
                    print(f"   Found ProductBrand placeholder in cell: '{cell.text[:100]}...'")
        
        print(f"   Total ProductBrand placeholders found: {productbrand_placeholders}")
        
        if productbrand_placeholders == 0:
            print("   ❌ No ProductBrand placeholders found in template!")
            print("   This could be why the brand is missing.")
        
        print("\n6. Summary...")
        # Check if any cell contains brand content
        brand_found = False
        for row in table.rows:
            for cell in row.cells:
                if 'Test Brand' in cell.text:
                    brand_found = True
                    break
            if brand_found:
                break
        
        if brand_found:
            print("   ✓ Brand content found in at least one cell")
        else:
            print("   ❌ No brand content found in any cell")
            print("   This indicates the brand is truly missing from the output.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ DEBUG FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_brand_missing_debug()
    sys.exit(0 if success else 1) 