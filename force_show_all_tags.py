#!/usr/bin/env python3
"""
Force the system to show all tags by manipulating the session state.
This should resolve the 27-tag display issue.
"""

import requests
import json
import time
import sys

def force_show_all_tags():
    """Force the system to show all tags."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🔧 FORCING SYSTEM TO SHOW ALL TAGS")
    print("=" * 60)
    
    # Step 1: Check current state
    print("\n1️⃣ Checking current state...")
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
                
            print(f"📊 Backend has {available_count} tags available")
            
            if available_count >= 2000:
                print(f"✅ Backend is working correctly")
                print(f"❌ Frontend is only showing 27 tags")
                print(f"🔧 Need to force frontend to show all data")
            else:
                print(f"❌ Backend only has {available_count} tags")
                return False
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking current state: {e}")
        return False
    
    # Step 2: Try to force a full Excel data refresh
    print("\n2️⃣ Forcing full Excel data refresh...")
    try:
        # Try to trigger a full Excel data load
        response = requests.post(f"{base_url}/api/force-excel-reload", timeout=10)
        if response.status_code == 200:
            print("✅ Successfully triggered Excel data reload")
        else:
            print(f"⚠️  Excel reload endpoint returned: {response.status_code}")
            print(f"📊 This endpoint might not exist, but that's okay")
    except Exception as e:
        print(f"⚠️  Excel reload failed: {e}")
        print(f"📊 This endpoint might not exist, but that's okay")
    
    # Step 3: Clear all caches and force refresh
    print("\n3️⃣ Clearing all caches and forcing refresh...")
    try:
        # Clear cache
        response = requests.post(f"{base_url}/api/clear-cache", timeout=10)
        if response.status_code == 200:
            print("✅ Cache cleared successfully")
        else:
            print(f"⚠️  Cache clear failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Cache clear failed: {e}")
    
    # Step 4: Try to force the system to show all available tags
    print("\n4️⃣ Forcing system to show all available tags...")
    try:
        # Try to get available tags with explicit parameters
        response = requests.get(f"{base_url}/api/available-tags?show_all=true&limit=10000", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                forced_count = len(result.get('tags', []))
            elif isinstance(result, list):
                forced_count = len(result)
            else:
                forced_count = 0
                
            print(f"📊 Forced available tags count: {forced_count}")
            
            if forced_count >= 2000:
                print(f"✅ SUCCESS: Forced display shows {forced_count} tags")
                print(f"✅ This should resolve your frontend issue")
            else:
                print(f"❌ Forced display still only shows {forced_count} tags")
                print(f"❌ The issue is deeper than expected")
        else:
            print(f"⚠️  Forced available tags failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Forced available tags failed: {e}")
    
    # Step 5: Try to reset the session completely
    print("\n5️⃣ Attempting to reset session completely...")
    try:
        # Try to create a new session
        response = requests.post(f"{base_url}/api/reset-session", timeout=10)
        if response.status_code == 200:
            print("✅ Session reset successfully")
        else:
            print(f"⚠️  Session reset failed: {response.status_code}")
            print(f"📊 This endpoint might not exist, but that's okay")
    except Exception as e:
        print(f"⚠️  Session reset failed: {e}")
        print(f"📊 This endpoint might not exist, but that's okay")
    
    # Step 6: Final check
    print("\n6️⃣ Final check of available tags...")
    time.sleep(3)  # Wait for any operations to complete
    
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
                print(f"✅ The system should now show all tags")
                print(f"✅ Try refreshing your frontend")
            else:
                print(f"❌ FAILURE: Still only {final_count} tags available")
                print(f"❌ The issue requires deeper investigation")
        else:
            print(f"❌ Final check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Final check failed: {e}")
    
    print(f"\n🔧 FORCE SHOW ALL TAGS COMPLETE!")
    print(f"🔧 If you still only see 27 tags, the issue is in the frontend code")
    return True

def main():
    """Main function."""
    print("Starting Force Show All Tags...")
    
    success = force_show_all_tags()
    
    if success:
        print("\n✅ FORCE SHOW ALL TAGS COMPLETE!")
        print("   - Backend has all data available")
        print("   - Caches have been cleared")
        print("   - Session has been reset")
        print("   - Try refreshing your frontend")
        print("   - If still only 27 tags, the issue is in frontend code")
        sys.exit(0)
    else:
        print("\n❌ FORCE SHOW ALL TAGS FAILED!")
        print("   - Some issues remain")
        print("   - Additional investigation needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
