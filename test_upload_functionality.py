#!/usr/bin/env python3
"""
Test the actual upload functionality to see what's happening.
"""

import os
import sys
import pandas as pd
import requests
import time

def create_test_excel():
    """Create a test Excel file for upload."""
    test_data = {
        'Product Name*': ['Test Upload Product 1', 'Test Upload Product 2'],
        'Vendor': ['Test Vendor 1', 'Test Vendor 2'],
        'Product Type*': ['edibles', 'flower'],
        'Weight*': ['10', '3.5'],
        'Units': ['mg', 'g'],
        'Price* (Tier Name for Bulk)': ['25.00', '45.00'],
        'Lineage': ['SATIVA', 'INDICA'],
        'Product Strain': ['Test Strain 1', 'Test Strain 2'],
        'Description': ['Test Description 1', 'Test Description 2'],
        'Ratio': ['10mg THC', '20% THC']
    }
    
    df = pd.DataFrame(test_data)
    test_file = 'test_upload.xlsx'
    df.to_excel(test_file, index=False)
    print(f"✅ Created test Excel file: {test_file}")
    return test_file

def test_upload_via_api():
    """Test upload via the Flask API."""
    test_file = create_test_excel()
    
    try:
        # Get current product count
        from app import get_product_database
        db = get_product_database()
        initial_count = len(db.get_all_products())
        print(f"📊 Initial product count: {initial_count}")
        
        # Test upload via requests
        url = 'http://localhost:5001/upload'
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(url, files=files)
        
        print(f"📤 Upload response status: {response.status_code}")
        print(f"📤 Upload response: {response.json()}")
        
        if response.status_code == 200:
            print("⏳ Waiting for background processing...")
            time.sleep(5)  # Wait for background processing
            
            # Check if products were added
            final_count = len(db.get_all_products())
            added_count = final_count - initial_count
            
            print(f"📊 Final product count: {final_count}")
            print(f"📊 Products added: {added_count}")
            
            if added_count > 0:
                print("✅ Upload successful - products added to database!")
                return True
            else:
                print("❌ Upload failed - no products added to database")
                return False
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during upload test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"🧹 Cleaned up test file: {test_file}")

def test_direct_database_storage():
    """Test direct database storage without upload."""
    print("\n🔬 Testing direct database storage...")
    
    try:
        from app import get_product_database
        from src.core.data.excel_processor import ExcelProcessor
        
        # Create test data
        test_data = {
            'Product Name*': ['Direct Test Product'],
            'Vendor': ['Direct Test Vendor'],
            'Product Type*': ['edibles'],
            'Weight*': ['5'],
            'Units': ['mg'],
            'Price* (Tier Name for Bulk)': ['15.00'],
            'Lineage': ['HYBRID'],
            'Product Strain': ['Direct Test Strain'],
            'Description': ['Direct Test Description'],
            'Ratio': ['5mg THC']
        }
        
        df = pd.DataFrame(test_data)
        
        # Test direct storage
        db = get_product_database()
        initial_count = len(db.get_all_products())
        
        storage_result = db.store_excel_data(df, 'direct_test.xlsx')
        print(f"📊 Direct storage result: {storage_result}")
        
        final_count = len(db.get_all_products())
        added_count = final_count - initial_count
        
        print(f"📊 Products added via direct storage: {added_count}")
        
        if added_count > 0:
            print("✅ Direct database storage works!")
            return True
        else:
            print("❌ Direct database storage failed")
            return False
            
    except Exception as e:
        print(f"❌ Direct storage error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Upload Functionality")
    print("=" * 50)
    
    # Test 1: Direct database storage
    direct_success = test_direct_database_storage()
    
    # Test 2: Upload via API (only if Flask is running)
    print("\n🌐 Testing upload via API...")
    try:
        # Check if Flask is running
        response = requests.get('http://localhost:5001/test', timeout=2)
        if response.status_code == 200:
            api_success = test_upload_via_api()
        else:
            print("❌ Flask app not running on localhost:5001")
            api_success = False
    except requests.exceptions.RequestException:
        print("❌ Flask app not running on localhost:5001")
        api_success = False
    
    print("\n📋 Test Results:")
    print(f"  Direct database storage: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"  API upload: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if not direct_success:
        print("\n❌ The issue is with database storage itself")
    elif not api_success:
        print("\n❌ The issue is with the upload API/background processing")
    else:
        print("\n✅ Both tests passed - upload should be working!")
