#!/usr/bin/env python3
"""
API Debug Script for AGTDesigner2
This script helps debug the API endpoint issues causing 400 errors
"""

import sys
import os
import traceback

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("=== AGTDesigner2 API Debug Script ===")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

# Test imports
try:
    from src.core.data.excel_processor import ExcelProcessor
    print("✅ ExcelProcessor imported successfully")
except ImportError as e:
    print(f"❌ Failed to import ExcelProcessor: {e}")

try:
    from src.core.data.json_matcher import JSONMatcher
    print("✅ JSONMatcher imported successfully")  
except ImportError as e:
    print(f"❌ Failed to import JSONMatcher: {e}")

# Test ExcelProcessor initialization
try:
    processor = ExcelProcessor()
    print("✅ ExcelProcessor initialized successfully")
    
    # Test get_default_upload_file
    try:
        default_file = processor.get_default_upload_file()
        print(f"✅ Default upload file: {default_file}")
        
        # Check if file exists
        if default_file and os.path.exists(default_file):
            print(f"✅ Default file exists: {os.path.getsize(default_file)} bytes")
        else:
            print(f"❌ Default file does not exist: {default_file}")
            
    except Exception as e:
        print(f"❌ Error getting default upload file: {e}")
        traceback.print_exc()
        
    # Test loading data
    try:
        data = processor.load_data()
        print(f"✅ Data loaded successfully: {len(data)} records")
        
        # Show sample data
        if data:
            print(f"Sample record keys: {list(data[0].keys())[:5]}")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Error initializing ExcelProcessor: {e}")
    traceback.print_exc()

# Test file system
print("\n=== File System Check ===")
required_dirs = ['uploads', 'output', 'cache', 'logs', 'src', 'static', 'templates']
for dir_name in required_dirs:
    if os.path.exists(dir_name):
        print(f"✅ {dir_name}/ exists")
    else:
        print(f"❌ {dir_name}/ missing")
        
# Check for Excel files
print("\n=== Excel Files Check ===")
excel_extensions = ['.xlsx', '.xls', '.csv']
for root, dirs, files in os.walk('.'):
    for file in files:
        if any(file.endswith(ext) for ext in excel_extensions):
            file_path = os.path.join(root, file)
            print(f"Found data file: {file_path}")

# Test Flask app import
print("\n=== Flask App Test ===")
try:
    from app import app
    print("✅ Flask app imported successfully")
    
    # Test app configuration
    print(f"Debug mode: {app.debug}")
    print(f"Secret key set: {'SECRET_KEY' in app.config}")
    
    # Test specific routes
    with app.test_client() as client:
        print("\n=== Testing API Endpoints ===")
        
        # Test root route
        response = client.get('/')
        print(f"GET /: Status {response.status_code}")
        
        # Test API routes
        response = client.get('/api/filter-options')
        print(f"GET /api/filter-options: Status {response.status_code}")
        
        response = client.get('/api/available-tags')
        print(f"GET /api/available-tags: Status {response.status_code}")
        if response.status_code != 200:
            print(f"Response data: {response.get_data(as_text=True)}")
            
        response = client.get('/api/selected-tags')
        print(f"GET /api/selected-tags: Status {response.status_code}")
        if response.status_code != 200:
            print(f"Response data: {response.get_data(as_text=True)}")
            
except Exception as e:
    print(f"❌ Error testing Flask app: {e}")
    traceback.print_exc()

print("\n=== Debug Complete ===")
