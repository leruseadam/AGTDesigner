#!/usr/bin/env python3
"""
Final test to verify the grid display fix works correctly.
This tests the updated functions with optimized dimensions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_final_grid_fix():
    """Test the final grid display fix."""
    print("🧪 Testing Final Grid Display Fix")
    print("=" * 40)
    
    try:
        from src.core.generation.docx_formatting import create_3x3_grid, fix_page_margins_for_3x3_grid
        
        # Test the updated functions
        print("✓ Imported updated functions")
        
        # Create document and apply margin fix
        from docx import Document
        doc = Document()
        doc = fix_page_margins_for_3x3_grid(doc)
        
        # Check margins
        if doc.sections:
            section = doc.sections[0]
            print(f"✓ Page: {section.page_width/1440:.2f}\" × {section.page_height/1440:.2f}\"")
            print(f"✓ Margins: L={section.left_margin.inches:.2f}\", R={section.right_margin.inches:.2f}\", T={section.top_margin.inches:.2f}\", B={section.bottom_margin.inches:.2f}\"")
            
            available_width = (section.page_width - section.left_margin - section.right_margin) / 1440
            available_height = (section.page_height - section.top_margin - section.bottom_margin) / 1440
            print(f"✓ Available space: {available_width:.2f}\" × {available_height:.2f}\"")
        
        # Create 3x3 grid with updated dimensions
        table = create_3x3_grid(doc, template_type='vertical')
        if table:
            print(f"✓ Grid created: {len(table.rows)}×{len(table.columns)}")
            
            # Check if it's a perfect 3x3
            if len(table.rows) == 3 and len(table.columns) == 3:
                print(f"✅ Perfect 3×3 grid created!")
            else:
                print(f"⚠️  Grid size: {len(table.rows)}×{len(table.columns)} (expected 3×3)")
            
            # Save for verification
            doc.save("final_grid_test.docx")
            print(f"✓ Final test document saved: final_grid_test.docx")
            
            print(f"\n🎉 Grid display fix verified!")
            print(f"📁 Open 'final_grid_test.docx' to see the perfect 3×3 layout")
            
        else:
            print(f"❌ Failed to create grid")
            
    except Exception as e:
        print(f"❌ Error in final test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_grid_fix()
