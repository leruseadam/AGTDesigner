#!/usr/bin/env python3
"""
Test THC/CBD processing to verify values are being extracted correctly
"""

import sqlite3
import os
from src.core.generation.template_processor import TemplateProcessor

def test_thc_cbd_processing():
    """Test THC/CBD processing with actual database records."""
    
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
        
        print(f"📊 Testing THC/CBD processing for: {record.get('Product Name*', 'Unknown')}")
        print(f"   Database THC: {record.get('THC', 'N/A')}")
        print(f"   Database CBD: {record.get('CBD', 'N/A')}")
        print(f"   Ratio_or_THC_CBD: {record.get('Ratio or THC/CBD', 'N/A')}")
        
        # Test the format_classic_ratio function
        processor = TemplateProcessor('horizontal', 'default')
        
        # Test with the placeholder format
        test_text = "THC:|BR|CBD:"
        result = processor.format_classic_ratio(test_text, record)
        
        print(f"   Input: '{test_text}'")
        print(f"   Output: '{result}'")
        
        # Test with actual ratio value
        ratio_text = record.get('Ratio or THC/CBD', '')
        if ratio_text:
            result2 = processor.format_classic_ratio(ratio_text, record)
            print(f"   Input (from DB): '{ratio_text}'")
            print(f"   Output: '{result2}'")
        
        conn.close()
        
        if "THC: 0%" in result and "CBD: 0%" in result:
            print("❌ Still showing 0% values - issue not fixed")
            return False
        else:
            print("✅ THC/CBD values are being processed correctly")
            return True
        
    except Exception as e:
        print(f"❌ Error testing THC/CBD processing: {e}")
        return False

if __name__ == "__main__":
    success = test_thc_cbd_processing()
    if success:
        print("\n🎉 THC/CBD processing test passed!")
    else:
        print("\n⚠️  THC/CBD processing test failed!")
