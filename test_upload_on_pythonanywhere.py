#!/usr/bin/env python3
"""
Simple test script to verify upload functionality on PythonAnywhere
Run this after uploading a file to check if it was processed correctly
"""

import os
import sys
import time

def test_upload_processing():
    """Test if uploaded files are being processed correctly"""
    print("🔍 Testing Upload Processing on PythonAnywhere")
    print("=" * 50)
    
    # Change to project directory
    os.chdir('/home/adamcordova/AGTDesigner')
    
    # Check upload folder
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        print(f"❌ Upload folder not found: {upload_folder}")
        return False
    
    files = [f for f in os.listdir(upload_folder) if f.endswith('.xlsx')]
    if not files:
        print("❌ No Excel files found in upload folder")
        return False
    
    print(f"✅ Found {len(files)} Excel files in upload folder")
    
    # Check the most recent file
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(upload_folder, f)))
    latest_path = os.path.join(upload_folder, latest_file)
    latest_time = os.path.getmtime(latest_path)
    
    print(f"📁 Most recent file: {latest_file}")
    print(f"⏰ Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(latest_time))}")
    
    # Check if this file is being processed
    try:
        from app import processing_status, processing_timestamps
        
        if latest_file in processing_status:
            status = processing_status[latest_file]
            timestamp = processing_timestamps.get(latest_file, 0)
            age = time.time() - timestamp if timestamp > 0 else 0
            
            print(f"📊 Processing status: {status}")
            print(f"⏱️  Age: {age:.1f} seconds")
            
            if status == 'ready':
                print("✅ File processing completed successfully!")
                return True
            elif status == 'processing':
                print("⏳ File is still being processed...")
                return False
            elif status.startswith('error'):
                print(f"❌ Processing error: {status}")
                return False
        else:
            print("⚠️  File not found in processing status")
            return False
            
    except Exception as e:
        print(f"❌ Error checking processing status: {e}")
        return False

def test_excel_processor():
    """Test if the Excel processor has the uploaded data"""
    print("\n🔍 Testing Excel Processor")
    print("=" * 30)
    
    try:
        from app import get_excel_processor
        
        processor = get_excel_processor()
        if processor is None:
            print("❌ Excel processor is None")
            return False
        
        if not hasattr(processor, 'df') or processor.df is None:
            print("❌ No DataFrame in processor")
            return False
        
        if processor.df.empty:
            print("❌ DataFrame is empty")
            return False
        
        print(f"✅ DataFrame has {len(processor.df)} rows, {len(processor.df.columns)} columns")
        
        # Check if this looks like the uploaded data
        if len(processor.df) > 0:
            print("📋 Sample data:")
            print(processor.df.head(2))
            
            # Check for expected columns
            expected_cols = ['ProductName', 'Product Type*', 'Product Brand', 'Product Strain']
            found_cols = [col for col in expected_cols if col in processor.df.columns]
            print(f"✅ Found {len(found_cols)}/{len(expected_cols)} expected columns: {found_cols}")
            
            return True
        else:
            print("❌ DataFrame has no rows")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Excel processor: {e}")
        return False

def test_available_tags():
    """Test if available tags are updated"""
    print("\n🔍 Testing Available Tags")
    print("=" * 30)
    
    try:
        from app import get_excel_processor
        
        processor = get_excel_processor()
        if processor is None:
            print("❌ Excel processor is None")
            return False
        
        # Get available tags
        if hasattr(processor, 'get_available_tags'):
            tags = processor.get_available_tags()
            if tags:
                print(f"✅ Found {len(tags)} available tags")
                print(f"📋 Sample tags: {tags[:5]}")
                return True
            else:
                print("❌ No available tags found")
                return False
        else:
            print("❌ No get_available_tags method")
            return False
            
    except Exception as e:
        print(f"❌ Error testing available tags: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 PythonAnywhere Upload Test")
    print("=" * 50)
    
    tests = [
        test_upload_processing,
        test_excel_processor,
        test_available_tags
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Upload is working correctly.")
    else:
        print("⚠️  Some tests failed. Upload may not be working properly.")
        print("\n💡 Troubleshooting steps:")
        print("1. Check PythonAnywhere error logs")
        print("2. Try reloading the web app")
        print("3. Upload a new file and test again")

if __name__ == "__main__":
    main() 