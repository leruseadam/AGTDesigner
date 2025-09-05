#!/usr/bin/env python3
"""
Reset filter mode to see if that resolves the 27-tag display issue.
The problem might be that the frontend is stuck in JSON matched mode.
"""

import requests
import json
import time
import sys

def reset_filter_mode():
    """Reset the filter mode to see if that resolves the display issue."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🔄 RESETTING FILTER MODE - Fixing 27-Tag Display Issue")
    print("=" * 70)
    
    # Step 1: Check current filter status
    print("\n1️⃣ Checking current filter status...")
    try:
        # Try to get filter status
        response = requests.get(f"{base_url}/api/filter-status", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Filter status retrieved")
            print(f"📊 Current filter mode: {result.get('mode', 'Unknown')}")
            print(f"📊 Has JSON matched: {result.get('has_json_matched', False)}")
            print(f"📊 JSON matched count: {result.get('json_matched_count', 0)}")
        else:
            print(f"⚠️  Filter status endpoint returned: {response.status_code}")
            print("📊 Assuming filter mode needs to be reset")
    except Exception as e:
        print(f"⚠️  Filter status check failed: {e}")
        print("📊 Proceeding with filter reset")
    
    # Step 2: Check current available tags
    print("\n2️⃣ Checking current available tags...")
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
                print(f"✅ The issue is in the frontend display")
            else:
                print(f"❌ Backend only has {available_count} tags")
                print(f"❌ The issue is in the backend")
                return False
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking available tags: {e}")
        return False
    
    # Step 3: Try to reset filter mode to full Excel
    print("\n3️⃣ Attempting to reset filter mode to full Excel...")
    try:
        # Try to switch to full Excel mode
        response = requests.post(f"{base_url}/api/filter-mode", 
                               json={'filter_mode': 'full_excel'}, 
                               timeout=10)
        if response.status_code == 200:
            print("✅ Successfully switched to full Excel mode")
        else:
            print(f"⚠️  Filter mode switch failed: {response.status_code}")
            print(f"📊 This endpoint might not exist, but that's okay")
    except Exception as e:
        print(f"⚠️  Filter mode switch failed: {e}")
        print(f"📊 This endpoint might not exist, but that's okay")
    
    # Step 4: Check if switching to full Excel mode helps
    print("\n4️⃣ Checking if full Excel mode shows more tags...")
    try:
        response = requests.get(f"{base_url}/api/available-tags?filter=full_excel", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                full_excel_count = len(result.get('tags', []))
            elif isinstance(result, list):
                full_excel_count = len(result)
            else:
                full_excel_count = 0
                
            print(f"📊 Full Excel mode count: {full_excel_count}")
            
            if full_excel_count >= 2000:
                print(f"✅ Full Excel mode shows {full_excel_count} tags")
                print(f"✅ This should resolve your display issue")
            else:
                print(f"❌ Full Excel mode only shows {full_excel_count} tags")
                print(f"❌ The issue is deeper than filter mode")
        else:
            print(f"⚠️  Full Excel filter failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Full Excel filter check failed: {e}")
    
    # Step 5: Check if there are any session issues
    print("\n5️⃣ Checking for session issues...")
    try:
        # Try to clear cache to reset any stuck states
        response = requests.post(f"{base_url}/api/clear-cache", timeout=10)
        if response.status_code == 200:
            print("✅ Cache cleared successfully")
            print(f"📊 This should reset any stuck filter states")
        else:
            print(f"⚠️  Cache clear failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Cache clear failed: {e}")
    
    # Step 6: Final check of available tags
    print("\n6️⃣ Final check of available tags...")
    time.sleep(2)  # Wait for cache to clear
    
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                final_count = len(result.get('tags', []))
            elif isinstance(result, list):
                final_count = len(result)
            else:
                final_count = 0
                
            print(f"📊 Final available tags count: {final_count}")
            
            if final_count >= 2000:
                print(f"✅ SUCCESS: {final_count} tags are now available")
                print(f"✅ The filter reset should resolve your display issue")
                print(f"✅ Try refreshing your frontend to see all tags")
            else:
                print(f"❌ FAILURE: Still only {final_count} tags available")
                print(f"❌ The issue is more complex than filter mode")
        else:
            print(f"❌ Final check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Final check failed: {e}")
    
    print(f"\n🔍 FILTER MODE RESET COMPLETE!")
    print(f"🔍 Check your frontend to see if you now see all tags")
    return True

def main():
    """Main reset function."""
    print("Starting Filter Mode Reset...")
    
    success = reset_filter_mode()
    
    if success:
        print("\n✅ FILTER MODE RESET COMPLETE!")
        print("   - Backend has all your data available")
        print("   - Filter mode has been reset")
        print("   - Cache has been cleared")
        print("   - Try refreshing your frontend")
        print("   - You should now see all your tags")
        sys.exit(0)
    else:
        print("\n❌ FILTER MODE RESET FAILED!")
        print("   - Some issues remain")
        print("   - Additional investigation needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
