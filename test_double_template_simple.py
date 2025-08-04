#!/usr/bin/env python3
"""
Simple test to verify double template fix is working.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor

def test_double_template():
    """Test double template with simple data."""
    print("Testing Double Template Fix")
    print("=" * 30)
    
    # Create test records
    test_records = [
        {
            'ProductName': 'HUSTLER\'S AMBITION Lemon Jealousy Wax',
            'Description': 'HUSTLER\'S AMBITION Lemon Jealousy Wax - 1g',
            'ProductBrand': 'HUSTLER\'S AMBITION',
            'Price': '$12',
            'Lineage': 'SATIVA',
            'Ratio_or_THC_CBD': 'THC: 75.52% CBD: 0.11%',
            'ProductStrain': 'Lemon Jealousy',
            'DOH': 'DOH'
        }
    ]
    
    try:
        # Create processor
        processor = TemplateProcessor('double', {}, 1.0)
        
        # Process records
        print("Processing test record...")
        result_doc = processor.process_records(test_records)
        
        if result_doc:
            print("✓ Document generated successfully")
            print(f"  Tables: {len(result_doc.tables)}")
            
            # Save document
            filename = "test_double_template_simple.docx"
            result_doc.save(filename)
            print(f"✓ Document saved as: {filename}")
            
            # Basic analysis
            if result_doc.tables:
                print("✓ Document contains tables")
                
                # Check first few tables
                for i in range(min(3, len(result_doc.tables))):
                    table = result_doc.tables[i]
                    try:
                        print(f"  Table {i}: {len(table.rows)} rows")
                        for row_idx, row in enumerate(table.rows):
                            print(f"    Row {row_idx}: {len(row.cells)} cells")
                            for col_idx, cell in enumerate(row.cells):
                                cell_text = cell.text.strip()
                                if cell_text:
                                    print(f"      Cell ({row_idx},{col_idx}): '{cell_text[:50]}...'")
                                else:
                                    print(f"      Cell ({row_idx},{col_idx}): Empty")
                    except Exception as table_error:
                        print(f"    Error analyzing table {i}: {table_error}")
            else:
                print("❌ No tables found in document")
                return False
                
        else:
            print("❌ Document generation failed")
            return False
            
        print("\n✅ Double template test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_double_template() 