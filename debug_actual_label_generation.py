#!/usr/bin/env python3
"""
Debug script to generate an actual label document and examine where ProductStrain 
is incorrectly showing ProductBrand values.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.excel_processor import ExcelProcessor
from src.core.generation.template_processor import TemplateProcessor, get_font_scheme
from src.core.data.excel_processor import get_default_upload_file
import pandas as pd

def debug_actual_label_generation():
    """Generate an actual label document and examine the content."""
    
    print("🔍 Debugging Actual Label Generation")
    print("=" * 50)
    
    # Load the default Excel file
    default_file = get_default_upload_file()
    print(f"📁 Loading default file: {default_file}")
    
    # Initialize Excel processor
    excel_processor = ExcelProcessor()
    success = excel_processor.load_file(default_file)
    
    if not success:
        print("❌ Failed to load Excel file")
        return
    
    print(f"✅ Excel file loaded successfully")
    print(f"📊 Total records: {len(excel_processor.df)}")
    
    # Get a few sample records for testing
    df = excel_processor.df
    
    # Look for records where ProductStrain might be different from ProductBrand
    strain_col = 'Product Strain' if 'Product Strain' in df.columns else 'ProductStrain'
    brand_col = 'Product Brand' if 'Product Brand' in df.columns else 'ProductBrand'
    
    if strain_col not in df.columns or brand_col not in df.columns:
        print(f"❌ Missing required columns: {strain_col}, {brand_col}")
        print(f"Available columns: {list(df.columns)}")
        return
    
    # Convert to string to avoid categorical comparison issues
    strain_values = df[strain_col].astype(str)
    brand_values = df[brand_col].astype(str)
    
    # Find records where ProductStrain is different from ProductBrand
    different_records = df[strain_values != brand_values].head(3)
    
    if len(different_records) == 0:
        print("❌ No records found where ProductStrain differs from ProductBrand")
        return
    
    print(f"✅ Found {len(different_records)} records with different ProductStrain and ProductBrand")
    
    # Test with the first record that has different values
    test_record = different_records.iloc[0]
    print(f"\n🧪 Testing with record:")
    print(f"  Product Type: {test_record.get('Product Type*', 'N/A')}")
    print(f"  Product Strain: '{test_record.get(strain_col, 'N/A')}'")
    print(f"  Product Brand: '{test_record.get(brand_col, 'N/A')}'")
    print(f"  Description: '{test_record.get('Description', 'N/A')}'")
    
    # Initialize template processor
    template_processor = TemplateProcessor('vertical', get_font_scheme('vertical'))
    
    # Build label context
    print(f"\n🔧 Building label context...")
    try:
        # Create a dummy document for the _build_label_context method
        from docx import Document
        dummy_doc = Document()
        
        label_context = template_processor._build_label_context(test_record, dummy_doc)
        
        print(f"✅ Label context built successfully")
        print(f"  ProductStrain in context: '{label_context.get('ProductStrain', 'N/A')}'")
        print(f"  ProductBrand in context: '{label_context.get('ProductBrand', 'N/A')}'")
        
        # Check if ProductStrain contains ProductBrand value
        strain_context = label_context.get('ProductStrain', '')
        brand_context = label_context.get('ProductBrand', '')
        
        if brand_context and brand_context in strain_context:
            print(f"⚠️  WARNING: ProductStrain context contains ProductBrand value!")
            print(f"  This suggests the issue is in _build_label_context")
        else:
            print(f"✅ ProductStrain context does NOT contain ProductBrand value")
            print(f"  The issue must be elsewhere in the pipeline")
            
    except Exception as e:
        print(f"❌ Error building label context: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Now generate an actual document to see what happens
    print(f"\n📄 Generating actual document...")
    try:
        # Process the record to generate a document
        result_doc = template_processor.process_records([test_record])
        
        if result_doc:
            print(f"✅ Document generated successfully")
            
            # Examine the document content
            print(f"\n🔍 Examining document content...")
            
            # Look for ProductStrain and ProductBrand content in the document
            strain_found = False
            brand_found = False
            
            for table in result_doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        cell_text = cell.text.strip()
                        if cell_text:
                            print(f"  Cell content: '{cell_text}'")
                            
                            # Check if this cell contains strain or brand content
                            if 'PRODUCTSTRAIN_START' in cell_text or 'PRODUCTSTRAIN_END' in cell_text:
                                strain_found = True
                                print(f"    -> Contains ProductStrain markers")
                                
                            if 'PRODUCTBRAND' in cell_text:
                                brand_found = True
                                print(f"    -> Contains ProductBrand markers")
            
            if not strain_found:
                print(f"⚠️  No ProductStrain markers found in document")
            if not brand_found:
                print(f"⚠️  No ProductBrand markers found in document")
                
            # Save the document for inspection
            output_path = "debug_actual_label_output.docx"
            result_doc.save(output_path)
            print(f"\n💾 Document saved as: {output_path}")
            print(f"  You can open this file to manually inspect the content")
            
        else:
            print(f"❌ Document generation failed")
            
    except Exception as e:
        print(f"❌ Error generating document: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_actual_label_generation() 