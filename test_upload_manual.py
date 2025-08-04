#!/usr/bin/env python3
"""
Manual Upload Test Script
This script helps test upload functionality step by step.
"""

import os
import sys
import pandas as pd
from datetime import datetime

def create_simple_test_file():
    """Create a simple test Excel file."""
    try:
        # Create simple test data
        data = {
            'Product Name*': ['Test Product'],
            'Vendor': ['Test Vendor'],
            'Product Type*': ['Concentrate'],
            'Price': [25.00]
        }
        
        df = pd.DataFrame(data)
        
        # Create test file
        test_file = 'simple_test.xlsx'
        df.to_excel(test_file, index=False)
        
        print(f"✅ Created simple test file: {test_file}")
        print(f"✅ File size: {os.path.getsize(test_file)} bytes")
        print(f"✅ File exists: {os.path.exists(test_file)}")
        
        return test_file
    except Exception as e:
        print(f"❌ Error creating test file: {e}")
        return None

def test_app_import():
    """Test if the Flask app can be imported."""
    try:
        from app import app
        print("✅ Flask app imported successfully")
        return app
    except Exception as e:
        print(f"❌ Error importing Flask app: {e}")
        return None

def test_status_endpoint(app):
    """Test the status endpoint."""
    try:
        with app.test_client() as client:
            response = client.get('/api/status')
            print(f"📊 Status endpoint: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"📊 Status data: {data}")
                return True
            else:
                print(f"❌ Status endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error testing status endpoint: {e}")
        return False

def test_upload_endpoint(app, test_file):
    """Test the upload endpoint."""
    try:
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            return False
        
        with app.test_client() as client:
            with open(test_file, 'rb') as f:
                # Use just the filename, not the full path
                filename = os.path.basename(test_file)
                print(f"📤 Testing upload with: {filename}")
                
                response = client.post('/upload', 
                                     data={'file': (f, filename, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')})
                
                print(f"📤 Upload response status: {response.status_code}")
                
                try:
                    data = response.get_json()
                    print(f"📤 Upload response: {data}")
                except:
                    print(f"📤 Upload response (raw): {response.data}")
                
                if response.status_code == 200:
                    print("✅ Upload test successful!")
                    return True
                else:
                    print("❌ Upload test failed")
                    return False
    except Exception as e:
        print(f"❌ Error testing upload: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🧪 Manual Upload Test Script")
    print("=" * 40)
    
    # Step 1: Test app import
    print("\n1️⃣ Testing Flask app import...")
    app = test_app_import()
    if not app:
        print("❌ Cannot continue without Flask app")
        return
    
    # Step 2: Test status endpoint
    print("\n2️⃣ Testing status endpoint...")
    status_ok = test_status_endpoint(app)
    if not status_ok:
        print("⚠️  Status endpoint not working, but continuing...")
    
    # Step 3: Create test file
    print("\n3️⃣ Creating test file...")
    test_file = create_simple_test_file()
    if not test_file:
        print("❌ Cannot continue without test file")
        return
    
    # Step 4: Test upload
    print("\n4️⃣ Testing upload endpoint...")
    upload_ok = test_upload_endpoint(app, test_file)
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 TEST SUMMARY")
    print("=" * 40)
    
    print(f"Flask app import: {'✅' if app else '❌'}")
    print(f"Status endpoint: {'✅' if status_ok else '❌'}")
    print(f"Test file creation: {'✅' if test_file else '❌'}")
    print(f"Upload endpoint: {'✅' if upload_ok else '❌'}")
    
    if upload_ok:
        print("\n🎉 Upload functionality is working!")
    else:
        print("\n🔧 Upload needs attention. Check:")
        print("1. PythonAnywhere error logs")
        print("2. Virtual environment")
        print("3. Dependencies")
        print("4. Web app configuration")

if __name__ == "__main__":
    main() 