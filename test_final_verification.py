#!/usr/bin/env python3
"""
Final verification test for brand centering and font sizing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from src.core.constants import FONT_SCHEME_DOUBLE
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

def final_verification():
    """Final verification of brand centering and font sizing."""
    print("Final Verification: Brand Centering and Font Sizing")
    print("=" * 60)
    
    # Test data with actual brand names from the screenshot
    test_records = [
        {
            'Description': '2:1 CBN Blueberry Lemonade Shot -0.07oz',
            'WeightUnits': '0.07oz',
            'ProductBrand': 'JOURNEYMAN',
            'Price': '$18',
            'Lineage': '100mg THC 50mg',
            'THC_CBD': 'THC: 20% CBD: 2%',
            'ProductStrain': 'Test Strain',
            'DOH': 'DOH',
            'ProductType': 'edible (liquid)'
        },
        {
            'Description': '20:1 CBD Ratio Tincture -0.25oz',
            'WeightUnits': '0.25oz',
            'ProductBrand': 'FAIRWINDS',
            'Price': '$38',
            'Lineage': '190mg CBD 10mg',
            'THC_CBD': 'THC: 20% CBD: 2%',
            'ProductStrain': 'Test Strain',
            'DOH': 'DOH',
            'ProductType': 'tincture'
        },
        {
            'Description': '2:1:1 Agave Lime MAX Wildside Shot -2oz',
            'WeightUnits': '2oz',
            'ProductBrand': 'GREEN',
            'Price': '$18',
            'Lineage': '100mg THC 50mg',
            'THC_CBD': 'THC: 20% CBD: 2%',
            'ProductStrain': 'Test Strain',
            'DOH': 'DOH',
            'ProductType': 'edible (liquid)'
        }
    ]
    
    # Process the records
    processor = TemplateProcessor('double', FONT_SCHEME_DOUBLE)
    result_doc = processor.process_records(test_records)
    
    if not result_doc:
        print("ERROR: Failed to process test records")
        return
    
    print("✅ Document processed successfully")
    
    # Check brand centering
    print("\n" + "=" * 40)
    print("BRAND CENTERING VERIFICATION")
    print("=" * 40)
    
    centering_issues = []
    font_sizing_issues = []
    
    for table in result_doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph_text = paragraph.text.strip()
                    
                    # Check if this contains brand content
                    brand_names = ['JOURNEYMAN', 'FAIRWINDS', 'GREEN', 'CQ', 'HOT SHOTZ', 'CERES']
                    if any(brand in paragraph_text.upper() for brand in brand_names):
                        print(f"Brand content found: '{paragraph_text}'")
                        
                        # Check centering
                        if paragraph.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                            print(f"  ✅ Centering: OK (CENTER)")
                        else:
                            print(f"  ❌ Centering: FAILED ({paragraph.alignment})")
                            centering_issues.append(paragraph_text)
                        
                        # Check font sizing
                        for run in paragraph.runs:
                            if run.text.strip() and any(brand in run.text.upper() for brand in brand_names):
                                font_size_pt = run.font.size.pt if run.font.size else 0
                                print(f"  Font size: {font_size_pt}pt")
                                
                                if 8 <= font_size_pt <= 20:
                                    print(f"  ✅ Font sizing: OK ({font_size_pt}pt)")
                                else:
                                    print(f"  ❌ Font sizing: FAILED ({font_size_pt}pt)")
                                    font_sizing_issues.append(f"{paragraph_text}: {font_size_pt}pt")
    
    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    
    if not centering_issues:
        print("✅ ALL BRAND CONTENT IS PROPERLY CENTERED")
    else:
        print(f"❌ {len(centering_issues)} centering issues found:")
        for issue in centering_issues:
            print(f"  - {issue}")
    
    if not font_sizing_issues:
        print("✅ ALL FONT SIZING IS CORRECT")
    else:
        print(f"❌ {len(font_sizing_issues)} font sizing issues found:")
        for issue in font_sizing_issues:
            print(f"  - {issue}")
    
    # Save the final document
    output_path = "final_verification_output.docx"
    result_doc.save(output_path)
    print(f"\nFinal document saved to: {output_path}")
    
    if not centering_issues and not font_sizing_issues:
        print("\n🎉 SUCCESS: Both brand centering and font sizing are working correctly!")
    else:
        print("\n⚠️  Some issues remain that need attention.")

if __name__ == "__main__":
    final_verification() 