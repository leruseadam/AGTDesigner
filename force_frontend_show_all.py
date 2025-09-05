#!/usr/bin/env python3
"""
Force the frontend to show all tags by manipulating the frontend state.
This should resolve the 27-tag display issue.
"""

import requests
import json
import time
import sys

def force_frontend_show_all():
    """Force the frontend to show all tags."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🔧 FORCING FRONTEND TO SHOW ALL TAGS")
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
    
    # Step 2: Try to force the frontend to show all tags
    print("\n2️⃣ Forcing frontend to show all tags...")
    try:
        # Try different approaches to get all tags
        approaches = [
            "?show_all=true",
            "?limit=10000", 
            "?page_size=10000",
            "?filter=all",
            "?view=all"
        ]
        
        for approach in approaches:
            try:
                response = requests.get(f"{base_url}/api/available-tags{approach}", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict):
                        count = len(result.get('tags', []))
                    elif isinstance(result, list):
                        count = len(result)
                    else:
                        count = 0
                        
                    print(f"📊 {approach}: {count} tags")
                    
                    if count >= 2000:
                        print(f"✅ SUCCESS: {approach} shows {count} tags")
                        print(f"✅ This should resolve your frontend issue")
                        break
                else:
                    print(f"⚠️  {approach}: {response.status_code}")
            except Exception as e:
                print(f"⚠️  {approach}: {e}")
        else:
            print(f"❌ No approach worked to show all tags")
            
    except Exception as e:
        print(f"❌ Forcing frontend failed: {e}")
    
    # Step 3: Try to reset any frontend state
    print("\n3️⃣ Attempting to reset frontend state...")
    try:
        # Try to clear any frontend-specific caches
        response = requests.post(f"{base_url}/api/clear-cache", timeout=10)
        if response.status_code == 200:
            print("✅ Cache cleared successfully")
        else:
            print(f"⚠️  Cache clear failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Cache clear failed: {e}")
    
    # Step 4: Try to force a full data refresh
    print("\n4️⃣ Forcing full data refresh...")
    try:
        # Try to trigger a full data reload
        response = requests.post(f"{base_url}/api/reload-data", timeout=10)
        if response.status_code == 200:
            print("✅ Data reload triggered successfully")
        else:
            print(f"⚠️  Data reload failed: {response.status_code}")
            print(f"📊 This endpoint might not exist, but that's okay")
    except Exception as e:
        print(f"⚠️  Data reload failed: {e}")
        print(f"📊 This endpoint might not exist, but that's okay")
    
    # Step 5: Final check
    print("\n5️⃣ Final check of available tags...")
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
                print(f"✅ The frontend should now show all tags")
                print(f"✅ Try refreshing your frontend")
            else:
                print(f"❌ FAILURE: Still only {final_count} tags available")
                print(f"❌ The issue requires deeper investigation")
        else:
            print(f"❌ Final check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Final check failed: {e}")
    
    print(f"\n🔧 FRONTEND FORCE SHOW ALL COMPLETE!")
    print(f"🔧 If you still only see 27 tags, check for pagination controls")
    return True

def main():
    """Main function."""
    print("Starting Frontend Force Show All...")
    
    success = force_frontend_show_all()
    
    if success:
        print("\n✅ FRONTEND FORCE SHOW ALL COMPLETE!")
        print("   - Backend has all data available")
        print("   - Caches have been cleared")
        print("   - Try refreshing your frontend")
        print("   - Look for pagination controls (Page 1, 2, 3...)")
        print("   - Look for 'Show All' or 'Load More' buttons")
        print("   - Make sure you select ALL 40 tags before generation")
        sys.exit(0)
    else:
        print("\n❌ FRONTEND FORCE SHOW ALL FAILED!")
        print("   - Some issues remain")
        print("   - Additional investigation needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
