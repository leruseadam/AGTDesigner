#!/usr/bin/env python3
"""
Test Ratio product generation specifically
"""

from src.core.generation.template_processor import TemplateProcessor
import pandas as pd

def test_ratio_products():
    """Test generating labels specifically for Ratio brand products."""
    print("🧪 Testing Ratio product label generation...")
    
    # Load the uploaded Excel file with products
    excel_path = "uploads/1759567264_valid_test.xlsx"
    try:
        df = pd.read_excel(excel_path)
        print(f"📊 Loaded Excel file with {len(df)} products")
        
        # Filter to only Ratio products  
        ratio_df = df[df['Product Brand'].str.contains('Ratio', case=False, na=False)]
        print(f"🎯 Found {len(ratio_df)} Ratio products:")
        
        for idx, row in ratio_df.iterrows():
            print(f"  - {row.get('Product Name*', 'Unknown')} by {row.get('Product Brand', 'Unknown')}")
            print(f"    Type: {row.get('Product Type*', 'Unknown')}")
        
        if len(ratio_df) == 0:
            print("❌ No Ratio products found!")
            return
            
        # Convert to records for processing
        records = ratio_df.to_dict('records')
        
        # Test with 3 Ratio products
        test_records = records[:3]
        print(f"\n🔧 Testing with {len(test_records)} Ratio products...")
        
        # Create template processor
        processor = TemplateProcessor('vertical', 'default')
        
        # Process the records
        doc_buffer = processor.process_records(test_records)
        
        # Save the result
        output_path = "test_ratio_brand_labels.docx"
        
        # Check if doc_buffer is a Document object or BytesIO
        if hasattr(doc_buffer, 'save'):
            # It's a Document object
            doc_buffer.save(output_path)
        elif hasattr(doc_buffer, 'getvalue'):
            # It's a BytesIO object
            with open(output_path, 'wb') as f:
                f.write(doc_buffer.getvalue())
        else:
            print(f"❌ Unexpected doc_buffer type: {type(doc_buffer)}")
            return
        
        print(f"✅ Generated labels saved to: {output_path}")
        print(f"📄 Please open '{output_path}' to check if Ratio brand appears!")
        
    except Exception as e:
        print(f"❌ Error testing Ratio products: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ratio_products()