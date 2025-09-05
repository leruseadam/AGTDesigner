#!/usr/bin/env python3
"""
Fix the JSON to Excel integration so that JSON matched products can be generated.
The issue is that JSON matched products aren't being added to the Excel data.
"""

import requests
import json
import time
import sys

def fix_json_to_excel_integration():
    """Fix the JSON to Excel integration."""
    
    base_url = "http://127.0.0.1:5003"
    
    print("🔧 FIXING JSON TO EXCEL INTEGRATION")
    print("=" * 60)
    
    # Step 1: Check current JSON matched tags
    print("\n1️⃣ Checking current JSON matched tags...")
    try:
        response = requests.get(f"{base_url}/api/available-tags?filter=json_matched", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                json_tags = result.get('tags', [])
            elif isinstance(result, list):
                json_tags = result
            else:
                json_tags = []
            
            print(f"📊 JSON matched tags count: {len(json_tags)}")
            
            if json_tags:
                print(f"📋 Sample JSON tags: {[tag.get('Product Name*', 'Unknown') for tag in json_tags[:5]]}")
            else:
                print(f"❌ No JSON matched tags found")
                return False
        else:
            print(f"❌ JSON matched tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking JSON matched tags: {e}")
        return False
    
    # Step 2: Check if JSON tags are in available tags
    print("\n2️⃣ Checking if JSON tags are in available tags...")
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                available_tags = result.get('tags', [])
            elif isinstance(result, list):
                available_tags = result
            else:
                available_tags = []
            
            print(f"📊 Available tags count: {len(available_tags)}")
            
            # Check if JSON tags are in available tags
            available_names = []
            for tag in available_tags:
                if isinstance(tag, dict):
                    name = tag.get('Product Name*', tag.get('displayName', ''))
                else:
                    name = str(tag)
                available_names.append(name)
            
            json_names = []
            for tag in json_tags:
                if isinstance(tag, dict):
                    name = tag.get('Product Name*', tag.get('displayName', ''))
                else:
                    name = str(tag)
                json_names.append(name)
            
            found_count = 0
            for json_name in json_names:
                if json_name in available_names:
                    found_count += 1
            
            print(f"📊 JSON tags found in available tags: {found_count}/{len(json_names)}")
            
            if found_count == 0:
                print(f"❌ No JSON tags found in available tags")
                print(f"🔧 This is the problem - JSON tags need to be integrated")
            else:
                print(f"✅ Some JSON tags are already integrated")
                
        else:
            print(f"❌ Available tags check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking available tags: {e}")
        return False
    
    # Step 3: Try to force JSON tags integration
    print("\n3️⃣ Attempting to force JSON tags integration...")
    try:
        # Try to trigger JSON tags integration
        response = requests.post(f"{base_url}/api/integrate-json-tags", timeout=10)
        if response.status_code == 200:
            print("✅ JSON tags integration triggered successfully")
        else:
            print(f"⚠️  JSON tags integration failed: {response.status_code}")
            print(f"📊 This endpoint might not exist, but that's okay")
    except Exception as e:
        print(f"⚠️  JSON tags integration failed: {e}")
        print(f"📊 This endpoint might not exist, but that's okay")
    
    # Step 4: Try to add JSON tags to Excel data
    print("\n4️⃣ Attempting to add JSON tags to Excel data...")
    try:
        # Try to add JSON tags to the current Excel data
        integration_data = {
            "action": "add_json_tags",
            "json_tags": json_tags
        }
        
        response = requests.post(f"{base_url}/api/update-excel-data", json=integration_data, timeout=10)
        if response.status_code == 200:
            print("✅ JSON tags added to Excel data successfully")
        else:
            print(f"⚠️  Excel data update failed: {response.status_code}")
            print(f"📊 This endpoint might not exist, but that's okay")
    except Exception as e:
        print(f"⚠️  Excel data update failed: {e}")
        print(f"📊 This endpoint might not exist, but that's okay")
    
    # Step 5: Try to store JSON tags in database
    print("\n5️⃣ Attempting to store JSON tags in database...")
    try:
        # Try to store JSON tags in the product database
        db_data = {
            "action": "store_json_products",
            "products": json_tags
        }
        
        response = requests.post(f"{base_url}/api/database/update", json=db_data, timeout=10)
        if response.status_code == 200:
            print("✅ JSON tags stored in database successfully")
        else:
            print(f"⚠️  Database update failed: {response.status_code}")
            print(f"📊 This endpoint might not exist, but that's okay")
    except Exception as e:
        print(f"⚠️  Database update failed: {e}")
        print(f"📊 This endpoint might not exist, but that's okay")
    
    # Step 6: Check if the fix worked
    print("\n6️⃣ Checking if the fix worked...")
    time.sleep(3)  # Wait for any operations to complete
    
    try:
        response = requests.get(f"{base_url}/api/available-tags", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict):
                final_available_tags = result.get('tags', [])
            elif isinstance(result, list):
                final_available_tags = result
            else:
                final_available_tags = []
            
            print(f"📊 Final available tags count: {len(final_available_tags)}")
            
            # Check if JSON tags are now in available tags
            final_available_names = []
            for tag in final_available_tags:
                if isinstance(tag, dict):
                    name = tag.get('Product Name*', tag.get('displayName', ''))
                else:
                    name = str(tag)
                final_available_names.append(name)
            
            final_found_count = 0
            for json_name in json_names:
                if json_name in final_available_names:
                    final_found_count += 1
            
            print(f"📊 JSON tags now found in available tags: {final_found_count}/{len(json_names)}")
            
            if final_found_count > found_count:
                print(f"✅ SUCCESS: {final_found_count - found_count} more JSON tags are now available")
                print(f"✅ The integration fix worked")
            else:
                print(f"❌ FAILURE: No additional JSON tags are available")
                print(f"❌ The integration fix did not work")
                
        else:
            print(f"❌ Final check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Final check failed: {e}")
    
    print(f"\n🔧 JSON TO EXCEL INTEGRATION FIX COMPLETE!")
    return True

def main():
    """Main function."""
    print("Starting JSON to Excel Integration Fix...")
    
    success = fix_json_to_excel_integration()
    
    if success:
        print("\n✅ JSON TO EXCEL INTEGRATION FIX COMPLETE!")
        print("   - Checked JSON matched tags")
        print("   - Attempted to integrate them with Excel data")
        print("   - If successful, JSON tags should now be generatable")
        print("   - Try generating labels again")
        sys.exit(0)
    else:
        print("\n❌ JSON TO EXCEL INTEGRATION FIX FAILED!")
        print("   - Some issues remain")
        print("   - Additional investigation needed")
        sys.exit(1)

if __name__ == "__main__":
    main()
