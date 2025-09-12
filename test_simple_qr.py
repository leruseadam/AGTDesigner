#!/usr/bin/env python3
"""
Simple test to verify QR code rendering with DocxTemplate.
"""
import sys
import os
sys.path.append('.')

from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import qrcode
from io import BytesIO

def test_simple_qr_rendering():
    """Test simple QR code rendering with DocxTemplate."""
    print("Testing simple QR code rendering...")
    
    # Create a simple QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data("Test QR Code")
    qr.make(fit=True)
    
    # Create QR code image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to BytesIO
    img_buffer = BytesIO()
    qr_image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Create InlineImage
    qr_inline_image = InlineImage(None, img_buffer, width=Mm(20))
    
    # Create a simple template with QR placeholder
    template_path = 'src/core/generation/templates/mini.docx'
    doc = DocxTemplate(template_path)
    
    # Create context with QR code
    context = {
        'QR': qr_inline_image,
        'Label1': {
            'ProductBrand': 'Test Brand'
        }
    }
    
    print(f"Context: {context}")
    print(f"QR type: {type(context['QR'])}")
    
    try:
        # Render the template
        doc.render(context)
        
        # Save the result
        output_file = 'test_simple_qr_output.docx'
        doc.save(output_file)
        
        print(f"✓ Template rendered successfully: {output_file}")
        
        # Check the result
        from docx import Document
        result_doc = Document(output_file)
        
        print("Result document content:")
        for i, para in enumerate(result_doc.paragraphs):
            print(f'Paragraph {i}: "{para.text}"')
        
        # Check for images
        if hasattr(result_doc, 'part') and hasattr(result_doc.part, 'related_parts'):
            image_count = len([part for part in result_doc.part.related_parts.values() 
                             if 'image' in part.content_type])
            print(f'Found {image_count} images in the result document')
        
        return True
        
    except Exception as e:
        print(f"✗ Error rendering template: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_qr_rendering()
    if success:
        print("\n✓ Simple QR code rendering test completed successfully!")
    else:
        print("\n✗ Simple QR code rendering test failed!")
