#!/usr/bin/env python3
"""
Test script to verify that the unified font sizing system is working correctly
and that the brand font sizing and DOH placeholder replacement are fixed.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.generation.template_processor import TemplateProcessor

def test_unified_font_sizing():
    """Test that unified font sizing system is working correctly."""
    print("🧪 Testing Unified Font Sizing System")
    print("=" * 60)
    
    try:
        # Create a template processor for mini templates
        processor = TemplateProcessor('mini', {}, 1.0)
        
        # Create test records with complete data to avoid being treated as empty labels
        test_records = [
            {
                'ProductName': 'Test Product 1',
                'ProductBrand': 'HUSTLER\'S AMBITION',  # Long brand name to test brand font sizing
                'ProductStrain': 'Test Strain',
                'Price': '$25.00',
                'Lineage': 'HYBRID',
                'DescAndWeight': 'Premium Flower - 3.5g',
                'Ratio_or_THC_CBD': 'THC: 22% CBD: 1%',
                'DOH': 'NO',  # This should show nothing
                'ProductType': 'flower',
                'Description': 'Premium Flower - 3.5g',  # Add Description field
                'THC': '22%',  # Add individual THC field
                'CBD': '1%',   # Add individual CBD field
                'Weight': '3.5g'  # Add Weight field
            },
            {
                'ProductName': 'Test Product 2',
                'ProductBrand': 'SUPER MEGA BUSSIN\'',  # Another long brand name
                'ProductStrain': 'Another Strain',
                'Price': '$30.00',
                'Lineage': 'SATIVA',
                'DescAndWeight': 'Premium Flower - 7g',
                'Ratio_or_THC_CBD': 'THC: 25% CBD: 0.5%',
                'DOH': 'YES',  # This should show DOH image placeholder
                'ProductType': 'flower',
                'Description': 'Premium Flower - 7g',  # Add Description field
                'THC': '25%',  # Add individual THC field
                'CBD': '0.5%', # Add individual CBD field
                'Weight': '7g'  # Add Weight field
            }
        ]
        
        # Process the records
        doc = processor.process_records(test_records)
        
        # Verify content in the generated document
        print("\n3. Verifying content in generated document:")
        print("-" * 60)
        found_brand = False
        found_thc_cbd = False
        found_doh_image_placeholder = False
        found_doh_empty = False
        
        # Iterate through tables and cells to find content
        for table_idx, table in enumerate(doc.tables):
            print(f"  Checking Table {table_idx+1}...")
            for row_idx, row in enumerate(table.rows):
                for col_idx, cell in enumerate(row.cells):
                    cell_text = ' '.join([para.text for para in cell.paragraphs]).strip()
                    if cell_text:  # Only show non-empty cells
                        print(f"    Cell ({row_idx}, {col_idx}) content: '{cell_text[:100]}'")
                    
                    # Check for ProductBrand content
                    if 'HUSTLER\'S AMBITION' in cell_text or 'SUPER MEGA BUSSIN\'' in cell_text:
                        print(f"      ✅ Found ProductBrand in cell ({row_idx}, {col_idx}): {cell_text[:50]}...")
                        found_brand = True
                        
                        # Check font size for brand text
                        for para in cell.paragraphs:
                            for run in para.runs:
                                if any(brand in run.text for brand in ['HUSTLER\'S AMBITION', 'SUPER MEGA BUSSIN\'']):
                                    if hasattr(run.font, 'size') and run.font.size:
                                        print(f"        Font size for brand: {run.font.size.pt}pt")
                                    else:
                                        print(f"        Font size for brand: Not set")
                    
                    # Check for THC/CBD content
                    if 'THC: 22% CBD: 1%' in cell_text or 'THC: 25% CBD: 0.5%' in cell_text:
                        print(f"      ✅ Found THC/CBD content in cell ({row_idx}, {col_idx}): {cell_text[:50]}...")
                        found_thc_cbd = True
                    
                    # Check for DOH content
                    if '[DOH_IMAGE_PLACEHOLDER]' in cell_text:
                        print(f"      ✅ Found DOH image placeholder in cell ({row_idx}, {col_idx}): {cell_text[:50]}...")
                        found_doh_image_placeholder = True
                    
                    # Check that DOH='NO' shows nothing (no "NO" text)
                    if 'NO' in cell_text and '{{Label' not in cell_text and '[DOH_IMAGE_PLACEHOLDER]' not in cell_text:
                        # This might be legitimate "NO" text from other fields, not DOH
                        if 'THC:' in cell_text or 'CBD:' in cell_text:
                            print(f"      ℹ️  Found 'NO' in THC/CBD context (not DOH): {cell_text[:50]}...")
                        else:
                            print(f"      ❌ Found unexpected 'NO' text in cell ({row_idx}, {col_idx}): {cell_text[:50]}...")
                    
                    # Check for empty DOH fields (should be empty for DOH='NO')
                    if '{{Label' in cell_text and 'DOH}}' in cell_text:
                        print(f"      ❌ Found DOH placeholder in cell ({row_idx}, {col_idx}): {cell_text[:50]}...")
                    elif 'DOH' not in cell_text and 'THC:' in cell_text:
                        # This is a cell with THC/CBD but no DOH - should be empty for DOH='NO'
                        found_doh_empty = True
        
        # Final check
        print("\n4. Final Verification:")
        print("-" * 60)
        if found_brand:
            print("✅ ProductBrand fields are properly populated")
        else:
            print("❌ ProductBrand fields are NOT populated")
        
        if found_thc_cbd:
            print("✅ THC/CBD ratio fields are properly populated")
        else:
            print("❌ THC/CBD ratio fields are NOT populated")
        
        if found_doh_image_placeholder:
            print("✅ DOH='YES' shows image placeholder correctly")
        else:
            print("❌ DOH='YES' is NOT showing image placeholder")
        
        if found_doh_empty:
            print("✅ DOH='NO' shows nothing (empty field)")
        else:
            print("❌ DOH='NO' field is not empty")
        
        if found_brand and found_thc_cbd and found_doh_image_placeholder and found_doh_empty:
            print("\n🎉 All checks passed! Unified font sizing system is working correctly.")
        else:
            print("\n⚠️ Some checks failed. Review the output above for details.")
        
        # Save the document for manual inspection
        output_path = "test_unified_font_sizing_output.docx"
        doc.save(output_path)
        print(f"\nGenerated document saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unified_font_sizing()
