#!/usr/bin/env python3
"""
Test that Excel THC/CBD values take priority over database values
"""

import sqlite3
import os
from src.core.generation.template_processor import TemplateProcessor

def test_excel_thc_cbd_priority():
    """Test that Excel THC/CBD values take priority over database values."""
    
    db_path = "product_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get a sample product with THC/CBD data
        cursor.execute("""
            SELECT * FROM products 
            WHERE \"THC\" IS NOT NULL AND \"THC\" != '' 
            AND \"CBD\" IS NOT NULL AND \"CBD\" != ''
            LIMIT 1
        """)
        
        product = cursor.fetchone()
        if not product:
            print("❌ No products with THC/CBD data found")
            return
        
        # Get column names
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Create record dictionary with Excel THC/CBD values
        record = dict(zip(columns, product))
        
        print(f"📊 Testing Excel THC/CBD priority for: {record.get('Product Name*', 'Unknown')}")
        print(f"   Excel THC: {record.get('THC', 'N/A')}")
        print(f"   Excel CBD: {record.get('CBD', 'N/A')}")
        print(f"   Database Total THC: {record.get('Total THC', 'N/A')}")
        print(f"   Database Total CBD: {record.get('Total CBD', 'N/A')}")
        
        # Test the _build_label_context method
        processor = TemplateProcessor('horizontal', 'default')
        
        # Create a mock document
        class MockDoc:
            pass
        
        mock_doc = MockDoc()
        
        # Test _build_label_context
        label_context = processor._build_label_context(record, mock_doc)
        
        print(f"\n📋 Label context results:")
        print(f"   Ratio_or_THC_CBD: '{label_context.get('Ratio_or_THC_CBD', 'N/A')}'")
        print(f"   THC_CBD: '{label_context.get('THC_CBD', 'N/A')}'")
        
        # Check if the Excel values are being used
        ratio_thc_cbd = label_context.get('Ratio_or_THC_CBD', '')
        excel_thc = record.get('THC', '')
        excel_cbd = record.get('CBD', '')
        
        if excel_thc and excel_cbd:
            expected_thc = f"THC: {excel_thc}%"
            expected_cbd = f"CBD: {excel_cbd}%"
            
            if expected_thc in ratio_thc_cbd and expected_cbd in ratio_thc_cbd:
                print("✅ Excel THC/CBD values are being used correctly")
                return True
            else:
                print(f"❌ Expected Excel values not found in output")
                print(f"   Expected THC: {expected_thc}")
                print(f"   Expected CBD: {expected_cbd}")
                print(f"   Actual output: {ratio_thc_cbd}")
                return False
        else:
            print("⚠️  No Excel THC/CBD values to test")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing Excel THC/CBD priority: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_excel_thc_cbd_priority()
    if success:
        print("\n🎉 Excel THC/CBD priority test passed!")
    else:
        print("\n⚠️  Excel THC/CBD priority test failed!")
