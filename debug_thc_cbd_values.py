#!/usr/bin/env python3
"""
Debug THC/CBD values in Excel processor
"""

import pandas as pd
from src.core.data.excel_processor import ExcelProcessor

def debug_thc_cbd_values():
    """Debug why THC/CBD values are empty in the record."""
    
    print("🔍 Debugging THC/CBD values...")
    
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
        
        # Check the raw Excel data
        print(f"\n📊 Raw Excel data:")
        print(f"   THC test result: '{product.get('THC test result', 'N/A')}'")
        print(f"   CBD test result: '{product.get('CBD test result', 'N/A')}'")
        print(f"   Total THC: '{product.get('Total THC', 'N/A')}'")
        print(f"   THCA: '{product.get('THCA', 'N/A')}'")
        print(f"   CBDA: '{product.get('CBDA', 'N/A')}'")
        
        # Simulate the THC/CBD calculation logic
        def safe_float(value):
            try:
                if pd.isna(value) or value == '' or str(value).lower() in ['nan', 'none']:
                    return 0.0
                return float(str(value).replace('%', '').strip())
            except (ValueError, TypeError):
                return 0.0
        
        # Get the values
        thc_test_result = str(product.get('THC test result', '')).strip()
        cbd_test_result = str(product.get('CBD test result', '')).strip()
        total_thc_value = str(product.get('Total THC', '')).strip()
        thc_content_value = str(product.get('THCA', '')).strip()
        total_cbd_value = str(product.get('Total CBD', '')).strip()
        cbd_content_value = str(product.get('CBDA', '')).strip()
        
        print(f"\n🧮 Calculated values:")
        print(f"   thc_test_result: '{thc_test_result}'")
        print(f"   cbd_test_result: '{cbd_test_result}'")
        print(f"   total_thc_value: '{total_thc_value}'")
        print(f"   thc_content_value: '{thc_content_value}'")
        print(f"   total_cbd_value: '{total_cbd_value}'")
        print(f"   cbd_content_value: '{cbd_content_value}'")
        
        # Convert to float
        thc_test_float = safe_float(thc_test_result)
        cbd_test_float = safe_float(cbd_test_result)
        total_thc_float = safe_float(total_thc_value)
        thc_content_float = safe_float(thc_content_value)
        total_cbd_float = safe_float(total_cbd_value)
        cbd_content_float = safe_float(cbd_content_value)
        
        print(f"\n🔢 Float values:")
        print(f"   thc_test_float: {thc_test_float}")
        print(f"   cbd_test_float: {cbd_test_float}")
        print(f"   total_thc_float: {total_thc_float}")
        print(f"   thc_content_float: {thc_content_float}")
        print(f"   total_cbd_float: {total_cbd_float}")
        print(f"   cbd_content_float: {cbd_content_float}")
        
        # Calculate ai_value (THC)
        if total_thc_float > 0:
            if thc_test_float > total_thc_float:
                ai_value = thc_test_result
                print(f"   Using THC test result ({thc_test_result}) over Total THC ({total_thc_value})")
            else:
                ai_value = total_thc_value
                print(f"   Using Total THC ({total_thc_value}) over THC test result ({thc_test_result})")
        else:
            # Total THC is 0 or empty, compare THCA vs THC test result
            if thc_content_float > 0 and thc_content_float >= thc_test_float:
                ai_value = thc_content_value
                print(f"   Using THCA ({thc_content_value}) over THC test result ({thc_test_result})")
            elif thc_test_float > 0:
                ai_value = thc_test_result
                print(f"   Using THC test result ({thc_test_result})")
            else:
                ai_value = ''
                print(f"   No valid THC value found")
        
        # Calculate ak_value (CBD)
        if cbd_content_float > total_cbd_float:
            ak_value = cbd_content_value
            print(f"   Using CBDA ({cbd_content_value}) over Total CBD ({total_cbd_value})")
        else:
            ak_value = total_cbd_value
            print(f"   Using Total CBD ({total_cbd_value}) over CBDA ({cbd_content_value})")
        
        # Clean up the values
        if ai_value in ['nan', 'NaN', '']:
            ai_value = ''
        if ak_value in ['nan', 'NaN', '']:
            ak_value = ''
        
        print(f"\n✅ Final values:")
        print(f"   ai_value (THC): '{ai_value}'")
        print(f"   ak_value (CBD): '{ak_value}'")
        
        # Test the actual Excel processor
        print(f"\n🧪 Testing actual Excel processor:")
        processor.selected_tags = [product['ProductName']]
        records = processor.get_selected_records('vertical')
        
        if records:
            record = records[0]
            print(f"   Record THC: '{record.get('THC', 'NOT_FOUND')}'")
            print(f"   Record CBD: '{record.get('CBD', 'NOT_FOUND')}'")
            print(f"   Record AI: '{record.get('AI', 'NOT_FOUND')}'")
            print(f"   Record AK: '{record.get('AK', 'NOT_FOUND')}'")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_thc_cbd_values()
