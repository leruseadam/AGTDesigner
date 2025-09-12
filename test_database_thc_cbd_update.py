#!/usr/bin/env python3
"""
Test that database is updated with Excel THC/CBD values on upload
"""

import sqlite3
import os
import pandas as pd
from src.core.data.product_database import ProductDatabase

def test_database_thc_cbd_update():
    """Test that database is updated with Excel THC/CBD values on upload."""
    
    db_path = "product_database.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        # Create a test Excel DataFrame with THC/CBD values
        test_data = {
            'Product Name*': ['Test Product 1', 'Test Product 2'],
            'Product Type*': ['flower', 'concentrate'],
            'Vendor/Supplier*': ['Test Vendor', 'Test Vendor'],
            'Product Brand': ['Test Brand', 'Test Brand'],
            'Description': ['Test Description 1', 'Test Description 2'],
            'Weight*': ['3.5g', '1g'],
            'Price': ['$25', '$30'],
            'Lineage': ['HYBRID', 'INDICA'],
            'THC': ['20.5', '25.0'],  # Direct THC values from Excel
            'CBD': ['1.2', '0.8'],    # Direct CBD values from Excel
            'Total THC': ['20.5', '25.0'],
            'Total CBD': ['1.2', '0.8'],
            'THC test result': ['20.5', '25.0'],
            'CBD test result': ['1.2', '0.8'],
            'Ratio': ['', ''],  # Empty ratio to test individual THC/CBD values
            'Ratio_or_THC_CBD': ['THC:|BR|CBD:', 'THC:|BR|CBD:']
        }
        
        test_df = pd.DataFrame(test_data)
        
        print("📊 Testing database update with Excel THC/CBD values...")
        print(f"   Test data shape: {test_df.shape}")
        print(f"   THC values: {test_df['THC'].tolist()}")
        print(f"   CBD values: {test_df['CBD'].tolist()}")
        
        # Store in database
        product_db = ProductDatabase(db_path)
        storage_result = product_db.store_excel_data(test_df, 'test_file.xlsx')
        
        print(f"\n📋 Storage result: {storage_result}")
        
        # Verify the data was stored correctly
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the test products were stored
        cursor.execute("""
            SELECT "Product Name*", "THC", "CBD", "AI", "AK" 
            FROM products 
            WHERE "Product Name*" LIKE 'Test Product%'
        """)
        
        stored_products = cursor.fetchall()
        
        print(f"\n📋 Stored products in database:")
        for product in stored_products:
            name, thc, cbd, ai, ak = product
            print(f"   {name}: THC='{thc}', CBD='{cbd}', AI='{ai}', AK='{ak}'")
        
        # Verify THC/CBD values match Excel data
        success = True
        for i, product in enumerate(stored_products):
            name, thc, cbd, ai, ak = product
            expected_thc = test_data['THC'][i]
            expected_cbd = test_data['CBD'][i]
            
            if thc != expected_thc:
                print(f"❌ THC mismatch for {name}: expected '{expected_thc}', got '{thc}'")
                success = False
            if cbd != expected_cbd:
                print(f"❌ CBD mismatch for {name}: expected '{expected_cbd}', got '{cbd}'")
                success = False
        
        if success:
            print("✅ Database THC/CBD values match Excel data")
        else:
            print("❌ Database THC/CBD values do not match Excel data")
        
        # Clean up test data
        cursor.execute("DELETE FROM products WHERE \"Product Name*\" LIKE 'Test Product%'")
        conn.commit()
        conn.close()
        
        return success
        
    except Exception as e:
        print(f"❌ Error testing database THC/CBD update: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_thc_cbd_update()
    if success:
        print("\n🎉 Database THC/CBD update test passed!")
    else:
        print("\n⚠️  Database THC/CBD update test failed!")
