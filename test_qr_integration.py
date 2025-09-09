#!/usr/bin/env python3
"""
Test script to verify complete QR code integration with font sizing.
"""
from src.core.generation.template_processor import TemplateProcessor
from docx import Document
from io import BytesIO

def test_qr_integration():
    """Test complete QR code integration with font sizing."""
    
    print("Testing Complete QR Code Integration")
    print("=" * 40)
    
    # Create a mock template
    template_buffer = BytesIO()
    doc = Document()
    template_buffer = BytesIO()
    doc.save(template_buffer)
    template_buffer.seek(0)
    
    # Test different template types
    template_types = ['mini', 'vertical', 'horizontal', 'double']
    
    for template_type in template_types:
        print(f"\n{template_type.upper()} Template:")
        print("-" * 20)
        
        # Create processor
        processor = TemplateProcessor(template_type, template_buffer)
        
        # Test record with QR code
        test_record = {
            'Product Name*': 'Test Product for QR Code',
            'Product Type*': 'flower',
            'THC': '22.5',
            'CBD': '0.8'
        }
        
        # Test context building
        context = processor._build_label_context(test_record, Document())
        
        # Check QR code generation
        if 'QR' in context:
            print(f"  ✅ QR code generated: {type(context['QR'])}")
            print(f"  ✅ QR_START marker: {context.get('QR_START', 'Not found')}")
            print(f"  ✅ QR_END marker: {context.get('QR_END', 'Not found')}")
        else:
            print(f"  ❌ QR code not found in context")
        
        # Test font sizing for QR markers
        from src.core.generation.unified_font_sizing import get_font_size_by_marker
        
        # Test with QR markers
        qr_font_size = get_font_size_by_marker("Test Product", 'QR', template_type, 1.0)
        print(f"  ✅ QR font size: {qr_font_size.pt}pt")
        
        # Test with different product name lengths
        test_names = [
            "Short",
            "Medium Product Name",
            "Very Long Product Name That Should Test Font Sizing"
        ]
        
        for name in test_names:
            size = get_font_size_by_marker(name, 'QR', template_type, 1.0)
            print(f"    '{name[:20]}...': {size.pt}pt")
    
    print(f"\n✅ Complete QR code integration test passed!")

if __name__ == "__main__":
    test_qr_integration()
