#!/usr/bin/env python3
"""
Comprehensive debug script for Product Vendor justification fix.
This will test the exact scenario from the user's screenshot and verify all aspects.
"""

import os
import sys
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import qn

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.generation.template_processor import TemplateProcessor

def debug_vendor_justification():
    """Debug the Product Vendor justification fix comprehensively."""
    print("🔍 DEBUGGING PRODUCT VENDOR JUSTIFICATION FIX")
    print("=" * 60)
    
    # Test data that matches the user's scenario
    test_records = [
        {
            'ProductName': 'Test Product 1',
            'ProductType': 'Flower',
            'Lineage': 'SATIVA',
            'ProductVendor': '1555 Industrial LLC',
            'Price': '$25.00',
            'Description': 'Test Description 1'
        },
        {
            'ProductName': 'Test Product 2', 
            'ProductType': 'Flower',
            'Lineage': 'INDICA',
            'ProductVendor': '1555 Industrial LLC',
            'Price': '$30.00',
            'Description': 'Test Description 2'
        },
        {
            'ProductName': 'Test Product 3',
            'ProductType': 'Flower', 
            'Lineage': 'HYBRID',
            'ProductVendor': '1555 Industrial LLC',
            'Price': '$35.00',
            'Description': 'Test Description 3'
        }
    ]
    
    print(f"📋 Test data: {len(test_records)} records with vendor '1555 Industrial LLC'")
    print(f"   Lineages: {[r['Lineage'] for r in test_records]}")
    print()
    
    try:
        # Initialize processor
        print("🚀 Initializing TemplateProcessor...")
        processor = TemplateProcessor('horizontal', {}, 1.0)
        print(f"   Template type: {processor.template_type}")
        print(f"   Chunk size: {processor.chunk_size}")
        print()
        
        # Process records
        print("⚙️  Processing records...")
        result_doc = processor.process_records(test_records)
        print("   ✓ Records processed successfully")
        print()
        
        # Save result
        output_file = "debug_vendor_justification_result.docx"
        result_doc.save(output_file)
        print(f"💾 Result saved as: {output_file}")
        print()
        
        # Analyze the result document
        print("🔍 ANALYZING RESULT DOCUMENT")
        print("-" * 40)
        
        # Check tables
        tables = result_doc.tables
        print(f"📊 Tables found: {len(tables)}")
        
        if tables:
            table = tables[0]
            print(f"   Table 0: {len(table.rows)} rows x {len(table.columns)} columns")
            print()
            
            # Check each cell in the first row (should contain our test data)
            for col_idx in range(min(3, len(table.columns))):
                cell = table.cell(0, col_idx)
                print(f"   📍 Cell (0,{col_idx}):")
                
                # Check paragraphs in the cell
                for para_idx, paragraph in enumerate(cell.paragraphs):
                    print(f"      Paragraph {para_idx}:")
                    print(f"        Text: '{paragraph.text}'")
                    print(f"        Alignment: {paragraph.alignment} ({get_alignment_name(paragraph.alignment)})")
                    
                    # Check for vendor text
                    if '1555 Industrial LLC' in paragraph.text:
                        print(f"        ✓ Contains vendor text: '1555 Industrial LLC'")
                        
                        # Check paragraph formatting
                        print(f"        Left indent: {paragraph.paragraph_format.left_indent}")
                        print(f"        Tab stops: {len(paragraph.paragraph_format.tab_stops)}")
                        
                        # Check tab stops in detail
                        for tab_idx, tab_stop in enumerate(paragraph.paragraph_format.tab_stops):
                            print(f"          Tab {tab_idx}: position={tab_stop.position}, alignment={tab_stop.alignment}")
                        
                        # Check runs
                        print(f"        Runs: {len(paragraph.runs)}")
                        for run_idx, run in enumerate(paragraph.runs):
                            print(f"          Run {run_idx}: '{run.text}' (font: {run.font.name}, size: {run.font.size}, bold: {run.font.bold})")
                        
                        # Verify this is the correct layout
                        if paragraph.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY:
                            print(f"        ✓ Correct alignment: JUSTIFY (allows tab stops to work)")
                        else:
                            print(f"        ❌ WRONG ALIGNMENT: {paragraph.alignment}")
                        
                        if paragraph.paragraph_format.left_indent is None or paragraph.paragraph_format.left_indent == 0:
                            print(f"        ✓ No left indent (allows tab stops to work)")
                        else:
                            print(f"        ❌ WRONG LEFT INDENT: {paragraph.paragraph_format.left_indent}")
                        
                        if len(paragraph.paragraph_format.tab_stops) > 0:
                            print(f"        ✓ Tab stops present: {len(paragraph.paragraph_format.tab_stops)}")
                        else:
                            print(f"        ❌ NO TAB STOPS")
                        
                    else:
                        print(f"        No vendor text found")
                    
                    print()
        
        # Check if the document looks correct
        print("✅ VERIFICATION SUMMARY")
        print("-" * 30)
        
        # Open the document to visually verify
        print(f"📄 Document generated: {output_file}")
        print(f"📊 Table structure: {len(tables)} tables")
        
        if tables and len(tables[0].rows) > 0:
            first_row = tables[0].rows[0]
            vendor_cells = 0
            for cell in first_row.cells:
                if '1555 Industrial LLC' in cell.text:
                    vendor_cells += 1
            
            print(f"🏷️  Vendor text found in {vendor_cells} cells")
            
            if vendor_cells == 3:
                print("   ✓ All 3 test records have vendor text")
            else:
                print(f"   ❌ Expected 3, found {vendor_cells}")
        
        print()
        print("🎯 NEXT STEPS:")
        print("   1. Open the generated document in Word")
        print("   2. Check that '1555 Industrial LLC' appears right-aligned")
        print("   3. Verify it's on the same line as the lineage (SATIVA, INDICA, HYBRID)")
        print("   4. Confirm no left indentation is applied")
        print()
        print("🔍 If issues persist, check the detailed analysis above for:")
        print("   - Wrong paragraph alignment (should be JUSTIFY)")
        print("   - Left indent conflicts (should be None or 0)")
        print("   - Missing tab stops")
        print("   - Wrong template layout (should be single-line, not two-line)")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

def get_alignment_name(alignment):
    """Convert alignment enum to readable name."""
    if alignment == WD_ALIGN_PARAGRAPH.LEFT:
        return "LEFT"
    elif alignment == WD_ALIGN_PARAGRAPH.CENTER:
        return "CENTER"
    elif alignment == WD_ALIGN_PARAGRAPH.RIGHT:
        return "RIGHT"
    elif alignment == WD_ALIGN_PARAGRAPH.JUSTIFY:
        return "JUSTIFY"
    else:
        return f"UNKNOWN ({alignment})"

if __name__ == "__main__":
    debug_vendor_justification()
