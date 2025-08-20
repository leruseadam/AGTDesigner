#!/usr/bin/env python3
"""
Test script to debug mini template expansion issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.generation.template_processor import TemplateProcessor

def test_mini_expansion():
    """Test mini template expansion"""
    
    print("🔍 Testing Mini Template Expansion")
    print("=" * 50)
    
    try:
        # Create template processor for mini template
        processor = TemplateProcessor('mini', 'default')
        print(f"✅ Template processor created for type: {processor.template_type}")
        print(f"✅ Chunk size: {processor.chunk_size}")
        
        # Check if template path exists
        template_path = processor._get_template_path()
        print(f"✅ Template path: {template_path}")
        print(f"✅ Template exists: {os.path.exists(template_path)}")
        
        # Test template expansion
        print("\n🔍 Testing template expansion...")
        expanded_buffer = processor._expand_template_if_needed()
        print(f"✅ Template expansion successful")
        print(f"✅ Expanded buffer size: {len(expanded_buffer.getvalue())} bytes")
        
        # Test processing a simple record
        print("\n🔍 Testing with sample record...")
        sample_record = {
            'Product Strain': 'Test Strain',
            'Product Brand': 'Test Brand',
            'Price': '$25',
            'Ratio_or_THC_CBD': 'THC: 20%',
            'Lineage': 'HYBRID',
            'Vendor': 'Test Vendor'
        }
        
        # Build label context
        label_context = processor._build_label_context(sample_record, 1)
        print(f"✅ Label context built successfully")
        print(f"✅ VendorInfo: {label_context.get('VendorInfo', 'NOT SET')}")
        
        print("\n🎉 Mini template expansion test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Mini template expansion test FAILED!")
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing mini template expansion...")
    success = test_mini_expansion()
    
    if success:
        print("\n🎉 Success! Your mini template expansion is working!")
    else:
        print("\n❌ Failed! There's an issue with mini template expansion.")
