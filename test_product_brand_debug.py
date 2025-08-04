#!/usr/bin/env python3
"""
Debug script to examine product brand content in double template.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_product_brand_debug():
    """Debug product brand content in double template."""
    
    print("Debugging Product Brand in Double Template")
    print("=" * 50)
    
    # Test data
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
        }
    ]
    
    try:
        print("\n1. Creating template processor...")
        double_processor = TemplateProcessor('double', {}, 1.0)
        
        print("\n2. Processing records...")
        result = double_processor.process_records(test_records)
        assert result is not None, "Template processing failed"
        
        print("\n3. Examining table structure...")
        table = result.tables[0]
        print(f"   Table: {len(table.rows)} rows x {len(table.columns)} columns")
        
        print("\n4. Examining first cell content in detail...")
        first_cell = table.cell(0, 0)
        
        print(f"   Cell text: '{first_cell.text}'")
        print(f"   Cell text length: {len(first_cell.text)}")
        
        # Split by lines
        lines = first_cell.text.split('\n')
        print(f"   Number of lines: {len(lines)}")
        for i, line in enumerate(lines):
            print(f"   Line {i}: '{line}'")
        
        print("\n5. Examining paragraph structure...")
        for i, para in enumerate(first_cell.paragraphs):
            if para.text.strip():
                print(f"   Paragraph {i}: '{para.text}'")
                print(f"   Paragraph runs: {len(para.runs)}")
                for j, run in enumerate(para.runs):
                    font_size_pt = run.font.size.pt if run.font.size else "None"
                    print(f"     Run {j}: '{run.text}' - Font size: {font_size_pt}pt")
        
        print("\n6. Checking for specific content...")
        cell_text = first_cell.text
        
        # Check for lineage content
        if 'HYBRID' in cell_text:
            print("   ✓ Found 'HYBRID' (lineage)")
        else:
            print("   ❌ Missing 'HYBRID' (lineage)")
        
        # Check for brand content
        if 'Test Brand 1' in cell_text:
            print("   ✓ Found 'Test Brand 1' (brand)")
        else:
            print("   ❌ Missing 'Test Brand 1' (brand)")
        
        # Check for strain content
        if 'Test Strain 1' in cell_text:
            print("   ✓ Found 'Test Strain 1' (strain)")
        else:
            print("   ❌ Missing 'Test Strain 1' (strain)")
        
        print("\n7. Analyzing content structure...")
        # Look for the bullet point and lineage
        if '•' in cell_text:
            print("   ✓ Found bullet point (•)")
            # Find the lineage part
            parts = cell_text.split('\n')
            if len(parts) >= 1 and '•' in parts[0]:
                lineage_part = parts[0]
                print(f"   Lineage part: '{lineage_part}'")
        
        # Look for brand part
        if len(lines) >= 2:
            brand_part = lines[1]
            print(f"   Brand part: '{brand_part}'")
            if brand_part.strip() == 'Test Brand 1':
                print("   ✓ Brand content is correct")
            else:
                print(f"   ❌ Brand content is wrong: '{brand_part}'")
        
        # Look for strain part
        if len(lines) >= 3:
            strain_part = lines[2]
            print(f"   Strain part: '{strain_part}'")
            if strain_part.strip() == 'Test Strain 1':
                print("   ✓ Strain content is correct")
            else:
                print(f"   ❌ Strain content is wrong: '{strain_part}'")
        
        print("\n8. Summary...")
        if 'Test Brand 1' in cell_text:
            print("   ✓ Product brand is present in the output")
        else:
            print("   ❌ Product brand is missing from the output")
        
        return True
        
    except Exception as e:
        print(f"\n❌ DEBUG FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_product_brand_debug()
    sys.exit(0 if success else 1) 