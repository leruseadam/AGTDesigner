#!/usr/bin/env python3
"""
Diagnostic script to test the actual label generation process and see why it's showing 2x3 instead of 3x3.
This will simulate the actual label generation flow.
"""

import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def debug_label_generation_issue():
    """Debug the label generation issue."""
    print("Debugging Label Generation Issue (2x3 vs 3x3)")
    print("=" * 50)
    
    try:
        # Import required modules
        from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
        from src.core.data.excel_processor import ExcelProcessor
        
        # Test different template types
        template_types = ['vertical', 'horizontal', 'mini', 'double', 'inventory']
        
        for template_type in template_types:
            print(f"\n--- Testing Label Generation for Template Type: {template_type} ---")
            
            try:
                # Get font scheme
                font_scheme = get_font_scheme(template_type)
                print(f"  Font scheme: {font_scheme}")
                
                # Create template processor
                processor = TemplateProcessor(template_type, font_scheme)
                print(f"  Template processor created successfully")
                print(f"  Template type: {processor.template_type}")
                print(f"  Chunk size: {processor.chunk_size}")
                
                # Create sample records (simulate the actual data flow)
                sample_records = [
                    {
                        'Product Name*': f'Test Product {i+1}',
                        'ProductName': f'Test Product {i+1}',
                        'Description': f'Test Description {i+1}',
                        'Product Type*': 'Flower',
                        'Product Brand': f'Test Brand {i+1}',
                        'Product Strain': f'Test Strain {i+1}',
                        'Lineage': 'HYBRID',
                        'Vendor': f'Test Vendor {i+1}',
                        'Price': f'${(i+1)*10}.00',
                        'Weight*': f'{i+1}g',
                        'Units': 'g',
                        'THC test result': 15.0 + i,
                        'CBD test result': 0.5 + i*0.1,
                        'Ratio': f'{15+i}:{0.5+i*0.1}'
                    }
                    for i in range(9)  # Create 9 records to test 3x3 grid
                ]
                
                print(f"  Created {len(sample_records)} sample records")
                
                # Process records (this is what happens in the actual generation)
                print(f"  Processing records with TemplateProcessor...")
                final_doc = processor.process_records(sample_records)
                
                if final_doc:
                    print(f"  ✓ Document generated successfully")
                    
                    # Check the final document structure
                    if final_doc.tables:
                        table = final_doc.tables[0]
                        print(f"  Final document table: {len(table.rows)} rows x {len(table.columns)} columns")
                        
                        # Check if it's actually 3x3
                        if len(table.rows) == 3 and len(table.columns) == 3:
                            print(f"  ✓ Final grid is 3x3 as expected")
                        else:
                            print(f"  ❌ Final grid is {len(table.rows)}x{len(table.columns)}, expected 3x3")
                            
                        # Check for actual content in cells
                        content_cells = 0
                        empty_cells = 0
                        for row in table.rows:
                            for cell in row.cells:
                                if cell.text.strip():
                                    content_cells += 1
                                else:
                                    empty_cells += 1
                        
                        print(f"  Content cells: {content_cells}")
                        print(f"  Empty cells: {empty_cells}")
                        
                        # Check if we have 9 content cells (one for each record)
                        if content_cells == 9:
                            print(f"  ✓ All 9 records have content cells")
                        else:
                            print(f"  ❌ Expected 9 content cells, found {content_cells}")
                            
                    else:
                        print(f"  ❌ No tables found in final document")
                        
                else:
                    print(f"  ❌ Document generation failed")
                    
            except Exception as e:
                print(f"  ❌ Error testing {template_type}: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"❌ Error in main debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_label_generation_issue()
