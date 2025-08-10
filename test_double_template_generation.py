#!/usr/bin/env python3
"""
Test script to verify that the double template can generate a document with real data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from pathlib import Path
import tempfile

def test_double_template_generation():
    """Test that the double template can generate a document with real data."""
    print("Testing Double Template Generation")
    print("=" * 50)
    
    try:
        # Create template processor
        processor = TemplateProcessor('double', {}, 1.0)
        
        # Create test records
        test_records = [
            {
                'ProductName': 'Test Product 1',
                'Description': 'Test Product 1',
                'ProductBrand': 'Test Brand 1',
                'Price': '$25.00',
                'Lineage': 'SATIVA',
                'Ratio_or_THC_CBD': 'THC: 22% CBD: 1%',
                'ProductStrain': 'Test Strain 1',
                'DOH': 'YES',
                'ProductType': 'flower'
            },
            {
                'ProductName': 'Test Product 2',
                'Description': 'Test Product 2',
                'ProductBrand': 'Test Brand 2',
                'Price': '$30.00',
                'Lineage': 'INDICA',
                'Ratio_or_THC_CBD': 'THC: 18% CBD: 2%',
                'ProductStrain': 'Test Strain 2',
                'DOH': 'NO',
                'ProductType': 'concentrate'
            },
            {
                'ProductName': 'Test Product 3',
                'Description': 'Test Product 3',
                'ProductBrand': 'Test Brand 3',
                'Price': '$15.00',
                'Lineage': 'HYBRID',
                'Ratio_or_THC_CBD': 'THC: 20% CBD: 3%',
                'ProductStrain': 'Test Strain 3',
                'DOH': 'YES',
                'ProductType': 'pre-roll'
            }
        ]
        
        print(f"Created {len(test_records)} test records")
        
        # Process the records
        print("Processing records with double template...")
        result_doc = processor.process_records(test_records)
        
        if result_doc:
            print("✓ Document generated successfully")
            
            # Check the generated document
            print(f"Generated document has {len(result_doc.tables)} tables")
            
            if result_doc.tables:
                table = result_doc.tables[0]
                print(f"Main table: {len(table.rows)} rows × {len(table.columns)} columns")
                
                # Check a few cells to see if placeholders were replaced
                if len(table.rows) > 0 and len(table.columns) > 0:
                    first_cell = table.cell(0, 0)
                    print(f"First cell content: '{first_cell.text.strip()}'")
                    
                    # Check if placeholders were replaced
                    if '{{Label1.' in first_cell.text:
                        print("⚠️  Placeholders not replaced - template rendering issue")
                    else:
                        print("✓ Placeholders replaced with actual data")
            
            # Save the document to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
                result_doc.save(tmp_file.name)
                print(f"✓ Document saved to: {tmp_file.name}")
                
                # Check file size
                file_size = Path(tmp_file.name).stat().st_size
                print(f"Generated file size: {file_size} bytes")
                
                # Clean up
                os.unlink(tmp_file.name)
            
            return True
        else:
            print("✗ Failed to generate document")
            return False
            
    except Exception as e:
        print(f"✗ Error during template generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_double_template_generation()
    
    if success:
        print("\n✅ Double template generation successful!")
    else:
        print("\n❌ Double template generation failed!") 