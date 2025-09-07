#!/usr/bin/env python3
"""
Test script to verify the fresh data fix for /api/available-tags endpoint.
This tests that the web version now returns fresh data from Excel processor instead of cached data.
"""

import requests
import json
import time
import sys

def test_fresh_data_fix():
    """Test that /api/available-tags returns fresh data from Excel processor."""
    
    # Test both local and web versions
    test_urls = [
        "http://127.0.0.1:5003",  # Local
        "https://www.agtpricetags.com"  # Web
    ]
    
    print("🧪 TESTING FRESH DATA FIX")
    print("=" * 50)
    
    for base_url in test_urls:
        print(f"\n🔍 Testing: {base_url}")
        print("-" * 30)
        
        try:
            # Test 1: Check if server is running
            print("1️⃣ Checking server status...")
            response = requests.get(f"{base_url}/", timeout=10)
            if response.status_code == 200:
                print("✅ Server is running")
            else:
                print(f"⚠️  Server returned status: {response.status_code}")
                continue
                
        except Exception as e:
            print(f"❌ Server not accessible: {e}")
            continue
        
        # Test 2: Clear cache first
        print("\n2️⃣ Clearing cache...")
        try:
            response = requests.post(f"{base_url}/api/clear-cache", timeout=10)
            if response.status_code == 200:
                print("✅ Cache cleared successfully")
            else:
                print(f"⚠️  Cache clear returned: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Cache clear failed: {e}")
        
        # Test 3: Check available tags
        print("\n3️⃣ Testing /api/available-tags...")
        try:
            timestamp = int(time.time() * 1000)
            response = requests.get(f"{base_url}/api/available-tags?t={timestamp}", timeout=15)
            
            if response.status_code == 200:
                tags = response.json()
                print(f"✅ Available tags endpoint working")
                print(f"📊 Returned {len(tags)} tags")
                
                if len(tags) > 0:
                    # Show sample data
                    print(f"📋 Sample tag data:")
                    sample_tag = tags[0]
                    for key, value in sample_tag.items():
                        if key in ['Product Name*', 'Product Type*', 'Lineage', 'Vendor']:
                            print(f"   {key}: {value}")
                    
                    # Check for fresh data indicators
                    print(f"\n🔍 Fresh data indicators:")
                    print(f"   - Total tags: {len(tags)}")
                    print(f"   - Has Product Name*: {'Product Name*' in sample_tag}")
                    print(f"   - Has Product Type*: {'Product Type*' in sample_tag}")
                    print(f"   - Has Lineage: {'Lineage' in sample_tag}")
                    
                    # Check for non-classic types (should have MIXED lineage)
                    non_classic_count = 0
                    mixed_lineage_count = 0
                    for tag in tags[:10]:  # Check first 10 tags
                        if tag.get('Product Type*', '').lower() in ['edible (solid)', 'edible (liquid)', 'tincture', 'topical', 'capsule']:
                            non_classic_count += 1
                        if tag.get('Lineage', '').upper() == 'MIXED':
                            mixed_lineage_count += 1
                    
                    print(f"   - Non-classic types (first 10): {non_classic_count}")
                    print(f"   - MIXED lineage (first 10): {mixed_lineage_count}")
                    
                else:
                    print("⚠️  No tags returned - may need to upload a file first")
                    
            else:
                print(f"❌ Available tags failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Available tags request failed: {e}")
        
        # Test 4: Check processing status
        print("\n4️⃣ Checking processing status...")
        try:
            response = requests.get(f"{base_url}/check-processing", timeout=10)
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Processing status: {status.get('status', 'Unknown')}")
                if 'excel_processor' in status:
                    print(f"📊 Excel processor: {status['excel_processor']}")
            else:
                print(f"⚠️  Processing status check failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Processing status check failed: {e}")
    
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 50)
    print("✅ If both local and web versions show the same number of tags")
    print("✅ And the data structure looks identical")
    print("✅ Then the fresh data fix is working!")
    print("\n💡 If you still see different values, try:")
    print("   1. Upload a fresh Excel file")
    print("   2. Clear cache again")
    print("   3. Check the PythonAnywhere logs for any errors")

if __name__ == "__main__":
    test_fresh_data_fix()
