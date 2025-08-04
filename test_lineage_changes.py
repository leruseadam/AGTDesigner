#!/usr/bin/env python3
"""
Test script to verify lineage changes are being saved and persisted
"""

import requests
import json
import time

def test_lineage_update():
    """Test lineage update functionality"""
    
    print("Testing Lineage Update Functionality")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get("http://127.0.0.1:9090/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server responded with error:", response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        print("❌ Server is not running:", e)
        return False
    
    # Test 2: Get available tags to find a test tag
    try:
        response = requests.get("http://127.0.0.1:9090/api/available-tags", timeout=10)
        if response.status_code == 200:
            available_tags = response.json()
            if available_tags:
                test_tag = available_tags[0]
                tag_name = test_tag.get('Product Name*', '')
                current_lineage = test_tag.get('Lineage', 'MIXED')
                print(f"✅ Found test tag: '{tag_name}' with current lineage: '{current_lineage}'")
            else:
                print("❌ No available tags found")
                return False
        else:
            print("❌ Failed to get available tags:", response.status_code)
            return False
    except Exception as e:
        print("❌ Error getting available tags:", e)
        return False
    
    # Test 3: Update lineage
    try:
        # Choose a different lineage for testing
        new_lineage = "SATIVA" if current_lineage != "SATIVA" else "INDICA"
        
        print(f"🔄 Updating lineage for '{tag_name}' from '{current_lineage}' to '{new_lineage}'")
        
        response = requests.post(
            "http://127.0.0.1:9090/api/update-lineage",
            json={
                "tag_name": tag_name,
                "lineage": new_lineage
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Lineage update successful: {result.get('message', '')}")
        else:
            error_data = response.json()
            print(f"❌ Lineage update failed: {error_data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Error updating lineage: {e}")
        return False
    
    # Test 4: Verify the change was saved by getting available tags again
    try:
        print("🔄 Verifying lineage change was saved...")
        time.sleep(1)  # Give the server a moment to process
        
        response = requests.get("http://127.0.0.1:9090/api/available-tags", timeout=10)
        if response.status_code == 200:
            available_tags = response.json()
            updated_tag = None
            for tag in available_tags:
                if tag.get('Product Name*', '') == tag_name:
                    updated_tag = tag
                    break
            
            if updated_tag:
                updated_lineage = updated_tag.get('Lineage', '')
                if updated_lineage == new_lineage:
                    print(f"✅ Lineage change verified! Tag '{tag_name}' now has lineage '{updated_lineage}'")
                else:
                    print(f"❌ Lineage change not persisted! Expected '{new_lineage}', got '{updated_lineage}'")
                    return False
            else:
                print(f"❌ Could not find updated tag '{tag_name}' in available tags")
                return False
        else:
            print("❌ Failed to get available tags for verification:", response.status_code)
            return False
    except Exception as e:
        print(f"❌ Error verifying lineage change: {e}")
        return False
    
    # Test 5: Test label generation with the updated lineage
    try:
        print("🔄 Testing label generation with updated lineage...")
        
        response = requests.post(
            "http://127.0.0.1:9090/api/generate",
            json={
                "selected_tags": [tag_name],
                "template_type": "mini",
                "scale_factor": 1.0
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Label generation successful with updated lineage")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"   Content-Length: {response.headers.get('Content-Length', 'Unknown')} bytes")
        else:
            error_data = response.json()
            print(f"❌ Label generation failed: {error_data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing label generation: {e}")
        return False
    
    return True

def test_multiple_lineage_changes():
    """Test multiple lineage changes to ensure persistence"""
    
    print("\nTesting Multiple Lineage Changes")
    print("=" * 50)
    
    # Get available tags
    try:
        response = requests.get("http://127.0.0.1:9090/api/available-tags", timeout=10)
        if response.status_code == 200:
            available_tags = response.json()
            test_tags = available_tags[:3]  # Test with first 3 tags
        else:
            print("❌ Failed to get available tags")
            return False
    except Exception as e:
        print(f"❌ Error getting available tags: {e}")
        return False
    
    # Test different lineages
    test_lineages = ["SATIVA", "INDICA", "HYBRID"]
    changes_made = []
    
    for i, tag in enumerate(test_tags):
        tag_name = tag.get('Product Name*', '')
        current_lineage = tag.get('Lineage', 'MIXED')
        new_lineage = test_lineages[i % len(test_lineages)]
        
        if current_lineage != new_lineage:
            try:
                print(f"🔄 Updating '{tag_name}' from '{current_lineage}' to '{new_lineage}'")
                
                response = requests.post(
                    "http://127.0.0.1:9090/api/update-lineage",
                    json={
                        "tag_name": tag_name,
                        "lineage": new_lineage
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    changes_made.append((tag_name, current_lineage, new_lineage))
                    print(f"✅ Updated successfully")
                else:
                    print(f"❌ Update failed")
            except Exception as e:
                print(f"❌ Error updating {tag_name}: {e}")
    
    # Verify all changes
    print(f"\n🔄 Verifying {len(changes_made)} lineage changes...")
    time.sleep(1)
    
    try:
        response = requests.get("http://127.0.0.1:9090/api/available-tags", timeout=10)
        if response.status_code == 200:
            available_tags = response.json()
            verified_count = 0
            
            for tag_name, old_lineage, new_lineage in changes_made:
                for tag in available_tags:
                    if tag.get('Product Name*', '') == tag_name:
                        current_lineage = tag.get('Lineage', '')
                        if current_lineage == new_lineage:
                            print(f"✅ Verified: '{tag_name}' lineage is '{current_lineage}'")
                            verified_count += 1
                        else:
                            print(f"❌ Failed: '{tag_name}' expected '{new_lineage}', got '{current_lineage}'")
                        break
            
            print(f"📊 Verification complete: {verified_count}/{len(changes_made)} changes persisted")
            return verified_count == len(changes_made)
        else:
            print("❌ Failed to get available tags for verification")
            return False
    except Exception as e:
        print(f"❌ Error verifying changes: {e}")
        return False

if __name__ == "__main__":
    print("Testing Lineage Change Persistence")
    print("=" * 60)
    
    # Test single lineage update
    success1 = test_lineage_update()
    
    # Test multiple lineage updates
    success2 = test_multiple_lineage_changes()
    
    if success1 and success2:
        print("\n🎉 All lineage change tests passed!")
        print("✅ Lineage changes are being saved and persisted correctly")
    else:
        print("\n❌ Some lineage change tests failed")
        print("⚠️  Lineage changes may not be working correctly")
    
    print("=" * 60) 