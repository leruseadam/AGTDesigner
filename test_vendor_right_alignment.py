#!/usr/bin/env python3
"""
Test script to verify that vendor placeholders are right-aligned.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.generation.template_processor import TemplateProcessor
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
import tempfile
import os

def test_vendor_right_alignment():
    """Test that vendor placeholders are right-aligned."""
    print("Testing Vendor Right Alignment")
    
    # Test with a record that has vendor information
    test_record = {
        'ProductName': 'Test Product',
        'ProductBrand': 'Test Brand',
        'ProductStrain': 'Test Strain',
        'ProductType': 'concentrate',
        'ProductVendor': 'Test Vendor',
        'Price': '$12',
        'THC': '71.66%',
        'CBD': '',
        'Description': 'Test Description',
        'WeightUnits': '1g'
    }
    
    print("1. Testing vendor-only paragraph right alignment:")
    
    # Test with horizontal template (which has ProductVendor placeholder)
    tp = TemplateProcessor('horizontal', {})
    
    # Check if vendor is being added to label context
    print("\n1.5. Checking label context:")
    label_context = tp._build_label_context(test_record, None)
    print(f"  ProductVendor in context: '{label_context.get('ProductVendor', 'NOT_FOUND')}'")
    print(f"  All context keys: {list(label_context.keys())}")
    
    # Process the test record
    documents = tp.process_records([test_record])
    
    if not documents:
        print("✗ No documents generated")
        return False
    
    # Save the first document to a temporary file
    doc = documents[0] if isinstance(documents, list) else documents
    
    # Check if vendor placeholders are right-aligned
    vendor_alignment_found = False
    print("\n2. Checking vendor alignment in document:")
    
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    # Check if this paragraph contains vendor content
                    paragraph_text = paragraph.text.strip()
                    print(f"  Paragraph text: '{paragraph_text}'")
                    print(f"  Paragraph alignment: {paragraph.alignment}")
                    
                    if 'Test Vendor' in paragraph_text:
                        print(f"  ✅ Found vendor text: '{paragraph_text}'")
                        print(f"  Paragraph alignment: {paragraph.alignment}")
                        
                        if paragraph.alignment == WD_ALIGN_PARAGRAPH.RIGHT:
                            print("  ✅ SUCCESS: Vendor paragraph is right-aligned")
                            vendor_alignment_found = True
                        else:
                            print(f"  ❌ ERROR: Vendor paragraph is not right-aligned (alignment: {paragraph.alignment})")
                        
                        # Check if vendor text is italic and gray
                        for run in paragraph.runs:
                            if 'Test Vendor' in run.text:
                                print(f"  Run text: '{run.text}'")
                                print(f"  Run italic: {run.font.italic}")
                                if hasattr(run.font, 'color') and run.font.color.rgb:
                                    print(f"  Run color: {run.font.color.rgb}")
                                else:
                                    print("  Run color: Not set")
                    elif 'PRODUCTVENDOR' in paragraph_text:
                        print(f"  ⚠️  Found PRODUCTVENDOR placeholder: '{paragraph_text}'")
                    elif 'Test' in paragraph_text:
                        print(f"  ℹ️  Found other text with 'Test': '{paragraph_text}'")
    
    if vendor_alignment_found:
        print("\n✅ SUCCESS: Vendor right alignment is working correctly")
        return True
    else:
        print("\n❌ ERROR: No vendor alignment found or vendor not right-aligned")
        return False

if __name__ == "__main__":
    success = test_vendor_right_alignment()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")
        sys.exit(1) 