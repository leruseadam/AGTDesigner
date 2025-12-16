#!/usr/bin/env python3
"""
DEBUG TAG GENERATION ISSUE
Diagnose why only 18 tags are output when 49 matched
"""

import logging
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging to see all debug info
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('tag_generation_debug.log')
    ]
)

def analyze_tag_generation_issue():
    """Analyze the tag generation issue step by step."""
    print("=" * 60)
    print("TAG GENERATION ISSUE ANALYSIS")
    print("=" * 60)
    
    try:
        # Check if we can import the necessary modules
        from src.core.generation.template_processor import TemplateProcessor, CHUNK_SIZE_LIMIT
        from src.core.data.excel_processor import ExcelProcessor
        
        print(f"✅ Successfully imported modules")
        print(f"📊 CHUNK_SIZE_LIMIT: {CHUNK_SIZE_LIMIT}")
        
        # Test different template types and their chunk sizes
        template_types = ['horizontal', 'vertical', 'mini', 'double', 'inventory']
        
        for template_type in template_types:
            try:
                processor = TemplateProcessor(template_type, 'arial', 1.0)
                print(f"📋 {template_type.upper()} template:")
                print(f"   - Chunk size: {processor.chunk_size}")
                print(f"   - Should handle 49 products in: {(49 + processor.chunk_size - 1) // processor.chunk_size} chunks")
            except Exception as e:
                print(f"❌ Error creating {template_type} processor: {e}")
        
        print("\n" + "=" * 60)
        print("CHUNK ANALYSIS FOR 49 PRODUCTS")
        print("=" * 60)
        
        # Simulate chunking for 49 products
        test_records = [{'ProductName': f'Product_{i}', 'Product Name*': f'Product_{i}'} for i in range(1, 50)]
        
        for template_type in ['horizontal', 'vertical']:
            try:
                processor = TemplateProcessor(template_type, 'arial', 1.0)
                chunk_size = processor.chunk_size
                
                print(f"\n📋 {template_type.upper()} template analysis:")
                print(f"   - Records: {len(test_records)}")
                print(f"   - Chunk size: {chunk_size}")
                
                # Simulate chunking
                chunks = []
                for i in range(0, len(test_records), chunk_size):
                    chunk = test_records[i:i + chunk_size]
                    chunks.append(chunk)
                
                print(f"   - Number of chunks: {len(chunks)}")
                for i, chunk in enumerate(chunks):
                    print(f"   - Chunk {i+1}: {len(chunk)} records")
                
                # Check if 18 might be from the first chunk
                if len(chunks) > 0 and len(chunks[0]) >= 18:
                    print(f"   ⚠️  POTENTIAL ISSUE: First chunk has {len(chunks[0])} records")
                    print(f"       If only first chunk processed partially, could explain 18 output")
                
            except Exception as e:
                print(f"❌ Error analyzing {template_type}: {e}")
        
        print("\n" + "=" * 60)
        print("TEMPLATE EXPANSION ANALYSIS")
        print("=" * 60)
        
        # Test template expansion
        try:
            processor = TemplateProcessor('horizontal', 'arial', 1.0)
            
            # Test expansion for different product counts
            test_counts = [9, 18, 49]
            for count in test_counts:
                try:
                    buffer = processor._expand_template_to_3x3_fixed(count)
                    print(f"✅ Template expansion for {count} products: SUCCESS")
                except Exception as e:
                    print(f"❌ Template expansion for {count} products: {e}")
                    
        except Exception as e:
            print(f"❌ Error testing template expansion: {e}")
            
        print("\n" + "=" * 60)
        print("RECOMMENDATIONS")
        print("=" * 60)
        
        print("""
🔍 DEBUGGING STEPS:

1. CHECK CHUNK PROCESSING:
   - Look for early termination in process_records()
   - Check for timeout errors in logs
   - Verify all chunks are being processed

2. CHECK TEMPLATE EXPANSION:
   - Verify _expand_template_to_3x3_fixed() creates correct grid size
   - Check if template has space for all 49 products

3. CHECK ERROR HANDLING:
   - Look for exceptions that might stop processing
   - Check memory or performance limits

4. IMMEDIATE FIX:
   - Try reducing chunk size to force more frequent processing
   - Add debug logging to see which chunk stops processing
   
🚀 QUICK TEST:
   - Generate with 9 products (should work fine)
   - Generate with 20 products (test if issue is > 18)
   - Generate with 49 products (current issue)
        """)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the correct directory")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_tag_generation_issue()