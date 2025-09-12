#!/usr/bin/env python3
"""
Test full THC/CBD processing including _build_label_context method
"""

import sqlite3
import os
from src.core.generation.template_processor import TemplateProcessor

def test_full_thc_cbd_processing():
    """Test full THC/CBD processing including _build_label_context method."""
    
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
        
        # Create record dictionary
        record = dict(zip(columns, product))
        
        print(f"📊 Testing full THC/CBD processing for: {record.get('Product Name*', 'Unknown')}")
        print(f"   Database THC: {record.get('THC', 'N/A')}")
        print(f"   Database CBD: {record.get('CBD', 'N/A')}")
        print(f"   Ratio or THC/CBD: '{record.get('Ratio or THC/CBD', 'N/A')}'")
        print(f"   Ratio: '{record.get('Ratio', 'N/A')}'")
        
        # Test the _build_label_context method
        processor = TemplateProcessor('horizontal', 'default')
        
        # Create a mock document (we don't need the actual document for this test)
        class MockDoc:
            pass
        
        mock_doc = MockDoc()
        
        # Test _build_label_context
        label_context = processor._build_label_context(record, mock_doc)
        
        print(f"\n📋 Label context results:")
        print(f"   Ratio_or_THC_CBD: '{label_context.get('Ratio_or_THC_CBD', 'N/A')}'")
        print(f"   THC_CBD: '{label_context.get('THC_CBD', 'N/A')}'")
        
        # Check if the values are properly formatted
        ratio_thc_cbd = label_context.get('Ratio_or_THC_CBD', '')
        if "THC: 0%" in ratio_thc_cbd and "CBD: 0%" in ratio_thc_cbd:
            print("❌ Still showing 0% values - issue not fixed")
            return False
        elif "THC:" in ratio_thc_cbd and "CBD:" in ratio_thc_cbd:
            print("✅ THC/CBD values are being processed correctly")
            return True
        else:
            print(f"⚠️  Unexpected format: '{ratio_thc_cbd}'")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing full THC/CBD processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_thc_cbd_processing()
    if success:
        print("\n🎉 Full THC/CBD processing test passed!")
    else:
        print("\n⚠️  Full THC/CBD processing test failed!")
