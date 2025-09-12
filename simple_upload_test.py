#!/usr/bin/env python3
"""
Simple test to verify upload functionality works.
"""

import os
import sys
import pandas as pd
import time

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_upload_functionality():
    """Test if upload functionality works by simulating the upload process."""
    
    print("🧪 Testing Upload Functionality")
    print("=" * 50)
    
    try:
        from app import get_product_database
        from src.core.data.excel_processor import ExcelProcessor
        
        # Get initial product count
        db = get_product_database()
        initial_count = len(db.get_all_products())
        print(f"📊 Initial product count: {initial_count}")
        
        # Create test data with unique product names
        timestamp = int(time.time())
        test_data = {
            'Product Name*': [f'Upload Test Product {timestamp}'],
            'Vendor': ['Upload Test Vendor'],
            'Product Type*': ['edibles'],
            'Weight*': ['10'],
            'Units': ['mg'],
            'Price* (Tier Name for Bulk)': ['25.00'],
            'Lineage': ['SATIVA'],
            'Product Strain': ['Upload Test Strain'],
            'Description': ['Upload Test Description'],
            'Ratio': ['10mg THC']
        }
        
        df = pd.DataFrame(test_data)
        print(f"📝 Created test data with unique product: {test_data['Product Name*'][0]}")
        
        # Test database storage (this is what happens during upload)
        print("\n💾 Testing database storage...")
        storage_result = db.store_excel_data(df, f'upload_test_{timestamp}.xlsx')
        print(f"📊 Storage result: {storage_result}")
        
        # Check if products were added
        final_count = len(db.get_all_products())
        added_count = final_count - initial_count
        
        print(f"📊 Final product count: {final_count}")
        print(f"📊 Products added: {added_count}")
        
        if added_count > 0:
            print("✅ Upload functionality works! Products are being stored in database.")
            
            # Verify the product was stored correctly
            products = db.get_all_products()
            last_product = products[-1]
            print(f"\n🔍 Last product stored:")
            print(f"  Name: {last_product.get('Product Name*', 'Unknown')}")
            print(f"  Type: {last_product.get('Product Type*', 'Unknown')}")
            print(f"  Ratio: \"{last_product.get('Ratio', '')}\"")
            print(f"  Vendor: {last_product.get('Vendor', 'Unknown')}")
            
            return True
        else:
            print("❌ Upload functionality failed - no products were stored")
            print(f"Storage result details: {storage_result}")
            return False
            
    except Exception as e:
        print(f"❌ Error during upload test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_upload_functionality()
    
    if success:
        print("\n✅ Upload functionality is working correctly!")
        print("The issue might be with the Flask app not running or the web interface.")
    else:
        print("\n❌ Upload functionality has issues that need to be fixed.")
        sys.exit(1)
