#!/usr/bin/env python3
"""
Diagnose why only 27 out of 40 tags are being generated in the DOCX file.
This will help identify where the tag limitation is occurring.
"""

import requests
import json
import time
import sys

def diagnose_docx_generation():
    """Diagnose the DOCX generation issue."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🔍 DIAGNOSING DOCX GENERATION - Why Only 27/40 Tags?")
    print("=" * 70)
    
    # Step 1: Check current state
    print("\n1️⃣ Checking current application state...")
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
                
            print(f"📊 Available tags count: {available_count}")
            
            if available_count >= 2000:
                print(f"✅ Backend has {available_count} tags available")
            else:
                print(f"❌ Backend only has {available_count} tags")
                return False
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking current state: {e}")
        return False
    
    # Step 2: Check session state for selected tags
    print("\n2️⃣ Checking session state for selected tags...")
    try:
        # Try to get session info
        response = requests.get(f"{base_url}/api/session-info", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Session info retrieved")
            
            selected_tags = result.get('selected_tags', [])
            json_selected_tags = result.get('json_selected_tags', [])
            last_json_match_count = result.get('last_json_match_count', 0)
            
            print(f"📊 Session selected_tags: {len(selected_tags)}")
            print(f"📊 Session json_selected_tags: {len(json_selected_tags)}")
            print(f"📊 Session last_json_match_count: {last_json_match_count}")
            
            if selected_tags:
                print(f"📋 Sample selected tags: {selected_tags[:5]}")
            if json_selected_tags:
                print(f"📋 Sample JSON selected tags: {json_selected_tags[:5]}")
                
        else:
            print(f"⚠️  Session info endpoint returned: {response.status_code}")
            print(f"📊 Will check other sources for selected tags")
    except Exception as e:
        print(f"⚠️  Session info check failed: {e}")
        print(f"📊 Will check other sources for selected tags")
    
    # Step 3: Check if there are any JSON matched tags in cache
    print("\n3️⃣ Checking for JSON matched tags in cache...")
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
                
            print(f"📊 JSON matched filter count: {json_count}")
            
            if json_count > 0:
                print(f"📋 Sample JSON matched tags: {[item.get('Product Name*', 'Unknown') for item in result[:5]]}")
            else:
                print(f"⚠️  No JSON matched tags found in cache")
        else:
            print(f"⚠️  JSON matched filter failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  JSON matched filter check failed: {e}")
    
    # Step 4: Check the actual generation process
    print("\n4️⃣ Checking generation process...")
    try:
        # Try to get information about the last generation
        response = requests.get(f"{base_url}/api/generation-status", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Generation status retrieved")
            print(f"📊 Generation info: {result}")
        else:
            print(f"⚠️  Generation status endpoint returned: {response.status_code}")
            print(f"📊 This endpoint might not exist, but that's okay")
    except Exception as e:
        print(f"⚠️  Generation status check failed: {e}")
        print(f"📊 This endpoint might not exist, but that's okay")
    
    # Step 5: Check if there are any limits in the system
    print("\n5️⃣ Checking for system limits...")
    try:
        # Check if there are any pagination or limit parameters
        response = requests.get(f"{base_url}/api/available-tags?limit=10000&show_all=true", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                unlimited_count = len(result.get('tags', []))
            elif isinstance(result, list):
                unlimited_count = len(result)
            else:
                unlimited_count = 0
                
            print(f"📊 Unlimited available tags count: {unlimited_count}")
            
            if unlimited_count > available_count:
                print(f"⚠️  There might be a limit in the system")
                print(f"⚠️  Regular endpoint: {available_count}, Unlimited: {unlimited_count}")
            else:
                print(f"✅ No limits detected in the system")
        else:
            print(f"⚠️  Unlimited tags check failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Unlimited tags check failed: {e}")
    
    # Step 6: Check the actual problem
    print("\n6️⃣ Analyzing the 27-tag issue...")
    
    print(f"\n🔍 ANALYSIS:")
    print(f"   - Backend has {available_count} tags available")
    print(f"   - You're only seeing 27 tags in the frontend")
    print(f"   - DOCX generation only includes 27 out of 40 tags")
    
    print(f"\n🔍 POSSIBLE CAUSES:")
    print(f"   1. Frontend is limiting display to 27 tags")
    print(f"   2. Only 27 tags are being selected for generation")
    print(f"   3. There's a pagination limit of 27 items per page")
    print(f"   4. The tag selection process is filtering out some items")
    print(f"   5. There's a hard limit in the generation logic")
    
    print(f"\n🔍 NEXT STEPS:")
    print(f"   1. Check if there are page navigation controls in your frontend")
    print(f"   2. Look for a 'Show All' or 'Load More' button")
    print(f"   3. Check if you can select more than 27 tags")
    print(f"   4. Verify that all 40 tags are actually selected before generation")
    
    return True

def main():
    """Main diagnostic function."""
    print("Starting DOCX Generation Diagnosis...")
    
    success = diagnose_docx_generation()
    
    if success:
        print("\n🔍 DIAGNOSIS COMPLETE!")
        print("   - Check the analysis above for possible causes")
        print("   - Look for pagination or selection limits in your frontend")
        print("   - Verify that all 40 tags are selected before generation")
        sys.exit(0)
    else:
        print("\n❌ DIAGNOSIS FAILED!")
        print("   - Some issues remain")
        print("   - Additional investigation needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
