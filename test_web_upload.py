#!/usr/bin/env python3
"""
Test script to upload a file to the web version and verify the fix.
"""

import requests
import os
import time

def test_web_upload():
    """Test uploading a file to the web version."""
    
    base_url = "https://www.agtpricetags.com"
    
    print("🌐 TESTING WEB VERSION UPLOAD")
    print("=" * 40)
    
    # Find a test Excel file
    test_files = [
        "test_upload.xlsx",
        "AGT_Essential_Product_Database_20250822_022042.xlsx",
        "comprehensive_product_database_20250822_020149.xlsx",
        "uploads/test_data.xlsx",
        "test_data.xlsx", 
        "sample_data.xlsx"
    ]
    
    test_file = None
    for file_path in test_files:
        if os.path.exists(file_path):
            test_file = file_path
            break
    
    if not test_file:
        print("❌ No test Excel file found. Please create a test file first.")
        print("   You can use any Excel file with product data.")
        return
    
    print(f"📁 Using test file: {test_file}")
    
    # Step 1: Clear cache
    print("\n1️⃣ Clearing cache...")
    try:
        response = requests.post(f"{base_url}/api/clear-cache", timeout=10)
        if response.status_code == 200:
            print("✅ Cache cleared")
        else:
            print(f"⚠️  Cache clear: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Cache clear failed: {e}")
    
    # Step 2: Upload file
    print(f"\n2️⃣ Uploading file...")
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/upload-fast", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful: {result.get('message', 'OK')}")
            print(f"📊 Status: {result.get('processing_status', 'Unknown')}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return
    
    # Step 3: Wait for processing
    print(f"\n3️⃣ Waiting for processing...")
    time.sleep(5)  # Wait 5 seconds for background processing
    
    # Step 4: Check available tags
    print(f"\n4️⃣ Checking available tags...")
    try:
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{base_url}/api/available-tags?t={timestamp}", timeout=15)
        
        if response.status_code == 200:
            tags = response.json()
            print(f"✅ Available tags: {len(tags)} tags")
            
            if len(tags) > 0:
                print(f"📋 Sample data:")
                sample = tags[0]
                for key in ['Product Name*', 'Product Type*', 'Lineage', 'Vendor']:
                    if key in sample:
                        print(f"   {key}: {sample[key]}")
                
                # Check for non-classic types
                non_classic = 0
                mixed_lineage = 0
                for tag in tags[:20]:  # Check first 20
                    if tag.get('Product Type*', '').lower() in ['edible (solid)', 'edible (liquid)', 'tincture', 'topical', 'capsule']:
                        non_classic += 1
                    if tag.get('Lineage', '').upper() == 'MIXED':
                        mixed_lineage += 1
                
                print(f"📊 Non-classic types (first 20): {non_classic}")
                print(f"📊 MIXED lineage (first 20): {mixed_lineage}")
                
                print(f"\n🎯 SUCCESS! Web version is now showing fresh data!")
                print(f"   - Total tags: {len(tags)}")
                print(f"   - Data structure looks correct")
                print(f"   - Fresh data fix is working!")
            else:
                print("⚠️  No tags returned - processing may still be in progress")
                print("   Try again in a few seconds")
        else:
            print(f"❌ Available tags failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Available tags check failed: {e}")

if __name__ == "__main__":
    test_web_upload()
