#!/usr/bin/env python3
"""
Test the THC/CBD fix by processing a sample record
"""

from src.core.data.excel_processor import ExcelProcessor
from src.core.generation.template_processor import TemplateProcessor

def test_thc_cbd_fix():
    """Test that THC/CBD values are processed correctly."""
    
    print("🧪 Testing THC/CBD fix...")
    
    try:
        # Load Excel data
        processor = ExcelProcessor()
        processor.load_file('uploads/A Greener Today - Bothell_inventory_08-29-2025  8_38 PM.xlsx')
        
        if processor.df is None or processor.df.empty:
            print("❌ No Excel data loaded")
            return
        
        # Find a Carbon Fiber product
        carbon_fiber_products = processor.df[processor.df['ProductName'].str.contains('Carbon Fiber Infused Pre-Roll', case=False, na=False)]
        
        if len(carbon_fiber_products) == 0:
            print("❌ No Carbon Fiber products found")
            return
        
        print(f"✅ Found {len(carbon_fiber_products)} Carbon Fiber products")
        
        # Get the first product
        product = carbon_fiber_products.iloc[0]
        print(f"📋 Testing product: {product['ProductName']}")
        print(f"   THC test result: {product.get('THC test result', 'N/A')}")
        print(f"   CBD test result: {product.get('CBD test result', 'N/A')}")
        print(f"   Total THC: {product.get('Total THC', 'N/A')}")
        print(f"   THCA: {product.get('THCA', 'N/A')}")
        print(f"   CBDA: {product.get('CBDA', 'N/A')}")
        
        # Set selected tags to include this product
        processor.selected_tags = [product['ProductName']]
        
        # Get selected records
        records = processor.get_selected_records('vertical')
        
        if not records:
            print("❌ No records returned from get_selected_records")
            return
        
        print(f"✅ Got {len(records)} records from Excel processor")
        
        # Check the first record
        record = records[0]
        print(f"📋 Record THC/CBD values:")
        print(f"   THC: '{record.get('THC', 'NOT_FOUND')}'")
        print(f"   CBD: '{record.get('CBD', 'NOT_FOUND')}'")
        print(f"   AI: '{record.get('AI', 'NOT_FOUND')}'")
        print(f"   AK: '{record.get('AK', 'NOT_FOUND')}'")
        print(f"   THC_CBD: '{record.get('THC_CBD', 'NOT_FOUND')}'")
        
        # Test template processor
        from src.core.generation.template_processor import get_font_scheme
        font_scheme = get_font_scheme('vertical')
        template_processor = TemplateProcessor('vertical', font_scheme)
        
        # Create a simple document for testing
        from docx import Document
        doc = Document()
        
        # Process the record
        label_context = template_processor._build_label_context(record, doc)
        
        print(f"📋 Label context THC/CBD values:")
        print(f"   THC: '{label_context.get('THC', 'NOT_FOUND')}'")
        print(f"   CBD: '{label_context.get('CBD', 'NOT_FOUND')}'")
        print(f"   Ratio_or_THC_CBD: '{label_context.get('Ratio_or_THC_CBD', 'NOT_FOUND')}'")
        
        # Check if values are non-zero
        thc_val = label_context.get('THC', '')
        cbd_val = label_context.get('CBD', '')
        
        if thc_val and thc_val != '0' and thc_val != '0.0':
            print(f"✅ THC value is non-zero: {thc_val}")
        else:
            print(f"❌ THC value is zero or empty: {thc_val}")
        
        if cbd_val and cbd_val != '0' and cbd_val != '0.0':
            print(f"✅ CBD value is non-zero: {cbd_val}")
        else:
            print(f"❌ CBD value is zero or empty: {cbd_val}")
        
        print("🎉 Test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_thc_cbd_fix()
