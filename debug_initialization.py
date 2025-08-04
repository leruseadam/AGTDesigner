#!/usr/bin/env python3
"""
Initialization Debug Script for PythonAnywhere
"""

import os
import requests
import time

def test_initialization_endpoints():
    """Test all initialization-related endpoints."""
    print("🔍 Testing initialization endpoints...")
    
    endpoints = [
        '/api/initial-data',
        '/api/status',
        '/api/health',
        '/upload-test',
        '/initialization-test'
    ]
    
    for endpoint in endpoints:
        try:
            print(f"Testing {endpoint}...")
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=10)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  Success: {endpoint} is working")
            elif response.status_code == 405:  # Method Not Allowed
                print(f"  Note: {endpoint} exists but doesn't accept GET requests")
            else:
                print(f"  Error: {response.status_code}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print()

def test_initialization_performance():
    """Test initialization performance."""
    print("⚡ Testing initialization performance...")
    
    endpoints = [
        '/api/initial-data',
        '/api/status',
        '/api/health'
    ]
    
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=10)
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"{endpoint}: {duration:.2f}s ({response.status_code})")
        except Exception as e:
            print(f"{endpoint}: ERROR ({e})")
    
    print()

def check_initialization_configuration():
    """Check initialization configuration."""
    print("⚙️  Checking initialization configuration...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        checks = [
            ('initialize_excel_processor', 'Excel processor initialization'),
            ('get_default_upload_file', 'Default file loading'),
            ('/api/initial-data', 'Initial data endpoint'),
            ('AppLoadingSplash', 'Loading splash screen')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description}: Found")
            else:
                print(f"❌ {description}: Not found")
                
    except Exception as e:
        print(f"Configuration check error: {e}")

def main():
    """Run all tests."""
    print("🧪 PythonAnywhere Initialization Debug")
    print("=" * 40)
    
    check_initialization_configuration()
    print()
    test_initialization_endpoints()
    test_initialization_performance()
    
    print("=" * 40)
    print("📋 Next steps:")
    print("1. Visit: https://yourusername.pythonanywhere.com/initialization-test")
    print("2. Test the main application")
    print("3. Check the PythonAnywhere error logs if issues persist")

if __name__ == "__main__":
    main()
