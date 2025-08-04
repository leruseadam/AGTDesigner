#!/usr/bin/env python3
"""
Test script to verify that RSO/CO2 Tankers now use "THC: CBD:" format instead of ratio
and have Product Brand centering like edibles.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from src.core.generation.docx_formatting import enforce_arial_bold_all_text
from docx import Document
from docx.shared import Pt
import tempfile
import os

def test_rso_co2_thc_cbd_formatting():
    """Test that RSO/CO2 Tankers get proper THC/CBD formatting and brand centering."""
    
    print("Testing RSO/CO2 Tankers THC/CBD formatting and brand centering:")
    print("=" * 60)
    
    # Create test data with RSO/CO2 Tankers
    test_data = [
        {
            'Product Name*': 'Test RSO Tanker',
            'Product Type*': 'rso/co2 tankers',
            'Product Brand': 'Test Brand',
            'Product Strain': 'Test Strain',
            'Price': '$25.99',
            'Weight*': '1',
            'Units': 'g',
            'Ratio': '25% THC, 2% CBD',
            'Lineage': 'HYBRID',
            'DOH': 'YES'
        }
    ]
    
    # Test different template types
    template_types = ['vertical', 'horizontal', 'mini']
    
    for template_type in template_types:
        print(f"\n--- Testing {template_type.upper()} template ---")
        
        try:
            # Create template processor
            processor = TemplateProcessor(template_type, {}, scale_factor=1.0)
            
            # Process the test data
            doc = processor.process_records(test_data)
            
            if doc:
                
                # Save the document for inspection
                output_file = f"test_rso_co2_{template_type}_thc_cbd.docx"
                doc.save(output_file)
                print(f"    ✅ Generated: {output_file}")
                
                # Check the content for proper formatting
                found_thc_cbd = False
                found_brand_center = False
                
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            cell_text = cell.text
                            
                            # Check for THC/CBD format
                            if 'THC:' in cell_text and 'CBD:' in cell_text:
                                found_thc_cbd = True
                                print(f"    ✅ Found THC/CBD format: {cell_text.strip()}")
                            
                            # Check for brand centering markers
                            if 'PRODUCTBRAND_CENTER_START' in cell_text:
                                found_brand_center = True
                                print(f"    ✅ Found Product Brand centering markers")
                            
                            # Check for ratio markers (should NOT be present for RSO/CO2 Tankers)
                            if 'RATIO_START' in cell_text and 'THC:' in cell_text:
                                print(f"    ❌ Found RATIO markers with THC/CBD content (should use THC_CBD markers)")
                
                if not found_thc_cbd:
                    print(f"    ❌ No THC/CBD format found in {template_type} template")
                
                if not found_brand_center:
                    print(f"    ❌ No Product Brand centering markers found in {template_type} template")
                
            else:
                print(f"    ❌ No documents generated for {template_type} template")
                
        except Exception as e:
            print(f"    ❌ Error processing {template_type} template: {e}")
    
    print(f"\n✅ RSO/CO2 Tankers formatting test completed!")
    print(f"Check the generated files to verify the formatting is correct.")

if __name__ == "__main__":
    test_rso_co2_thc_cbd_formatting() 