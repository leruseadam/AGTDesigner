#!/usr/bin/env python3
"""
Debug script to analyze real JSON data and see exactly why only 27 items are being processed.
This will help identify the root cause of the issue.
"""

import requests
import json
import time
import sys

def debug_real_json_data():
    """Debug the user's real JSON data to see why only 27 items are processed."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🔍 DEBUGGING REAL JSON DATA - Why Only 27 Tags?")
    print("=" * 60)
    
    # Test 1: Check if server is running
    print("\n1️⃣ Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Check the diagnostic endpoint
    print("\n2️⃣ Checking JSON matching diagnostic endpoint...")
    try:
        # First, let's see what the diagnostic endpoint shows
        response = requests.post(f"{base_url}/api/json-match/diagnose", 
                               json={'url': 'test'}, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Diagnostic endpoint working")
            print(f"📊 Diagnostic info: {result}")
        else:
            print(f"❌ Diagnostic endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error with diagnostic endpoint: {e}")
    
    # Test 3: Check available tags to see current state
    print("\n3️⃣ Checking current available tags...")
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                available_count = len(result.get('tags', []))
            elif isinstance(result, list):
                available_count = len(result)
            else:
                available_count = 0
                
            print(f"📊 Current available tags: {available_count}")
            
            # Show some sample tags
            if available_count > 0:
                print(f"📋 Sample available tags:")
                tags_to_show = result.get('tags', []) if isinstance(result, dict) else result
                for i, tag in enumerate(tags_to_show[:5]):
                    if isinstance(tag, dict):
                        name = tag.get('Product Name*', tag.get('ProductName', 'Unknown'))
                        source = tag.get('Source', 'Unknown')
                        print(f"   {i+1}. {name} (Source: {source})")
        else:
            print(f"❌ Available tags endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking available tags: {e}")
    
    # Test 4: Check if there are any JSON matched tags in cache
    print("\n4️⃣ Checking for cached JSON matched tags...")
    try:
        # Try to get JSON matched tags from cache
        response = requests.get(f"{base_url}/api/available-tags?filter=json_matched", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                json_count = len(result.get('tags', []))
            elif isinstance(result, list):
                json_count = len(result)
            else:
                json_count = 0
                
            print(f"📊 JSON matched tags in cache: {json_count}")
        else:
            print(f"❌ JSON matched tags query failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking JSON matched tags: {e}")
    
    # Test 5: Check session info
    print("\n5️⃣ Checking session information...")
    try:
        response = requests.get(f"{base_url}/api/session-info", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Session info retrieved")
            print(f"📊 Session data: {result}")
        else:
            print(f"❌ Session info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting session info: {e}")
    
    print("\n🔍 DEBUG SUMMARY:")
    print("   - Check the logs for 'CRITICAL FIX' messages")
    print("   - Look for any error messages during JSON processing")
    print("   - Verify that your JSON data has the expected structure")
    print("   - Check if there are any validation errors")
    
    return True

def main():
    """Main debug function."""
    print("Starting JSON Data Debug...")
    
    success = debug_real_json_data()
    
    if success:
        print("\n🔍 DEBUG COMPLETE!")
        print("   - Check the server logs for detailed information")
        print("   - Look for any 'CRITICAL FIX' messages")
        print("   - Verify your JSON data structure")
    else:
        print("\n❌ DEBUG FAILED!")
        print("   - Server may not be running")
        print("   - Check server status")

if __name__ == "__main__":
    main()
