#!/usr/bin/env python3
"""
Simple test to verify JSON deselection functionality works.
"""

import requests
import json
import time

def test_json_deselection_simple():
    """Test that JSON selected items can be properly deselected using the move-tags API."""
    
    print("🧪 Testing JSON Deselection - Simple Test")
    print("=" * 50)
    
    # Base URL for the application
    base_url = "http://localhost:5001"
    
    try:
        # Step 1: Check current selected tags
        print("1. Checking current selected tags...")
        selected_response = requests.get(f"{base_url}/api/selected-tags")
        
        if selected_response.status_code != 200:
            print(f"❌ Failed to get selected tags: {selected_response.status_code}")
            return False
        
        selected_tags = selected_response.json()
        print(f"✅ Current selected tags count: {len(selected_tags)}")
        
        # Step 2: Check available tags
        print("\n2. Checking available tags...")
        available_response = requests.get(f"{base_url}/api/available-tags")
        
        if available_response.status_code != 200:
            print(f"❌ Failed to get available tags: {available_response.status_code}")
            return False
        
        available_tags = available_response.json()
        print(f"✅ Available tags count: {len(available_tags)}")
        
        if len(available_tags) == 0:
            print("❌ No available tags to test with")
            return False
        
        # Step 3: Select a tag to test deselection
        print("\n3. Testing tag selection and deselection...")
        test_tag = available_tags[0]
        tag_name = test_tag.get('Product Name*', '') if isinstance(test_tag, dict) else str(test_tag)
        
        print(f"Testing with tag: {tag_name}")
        
        # First, move the tag to selected
        select_response = requests.post(f"{base_url}/api/move-tags",
                                      json={
                                          "tags": [tag_name],
                                          "direction": "to_selected"
                                      })
        
        if select_response.status_code != 200:
            print(f"❌ Failed to select tag: {select_response.status_code}")
            print(f"Response: {select_response.text}")
            return False
        
        print("✅ Tag selection successful")
        
        # Step 4: Verify the tag is now selected
        print("\n4. Verifying tag selection...")
        time.sleep(1)  # Give the backend time to process
        
        updated_selected_response = requests.get(f"{base_url}/api/selected-tags")
        if updated_selected_response.status_code != 200:
            print(f"❌ Failed to get updated selected tags: {updated_selected_response.status_code}")
            return False
        
        updated_selected_tags = updated_selected_response.json()
        updated_tag_names = [tag.get('Product Name*', '') if isinstance(tag, dict) else str(tag) for tag in updated_selected_tags]
        
        if tag_name not in updated_tag_names:
            print(f"❌ Tag '{tag_name}' was not properly selected")
            return False
        
        print(f"✅ Tag '{tag_name}' successfully selected")
        
        # Step 5: Now test deselection
        print("\n5. Testing tag deselection...")
        deselect_response = requests.post(f"{base_url}/api/move-tags",
                                        json={
                                            "tags": [tag_name],
                                            "direction": "to_available"
                                        })
        
        if deselect_response.status_code != 200:
            print(f"❌ Failed to deselect tag: {deselect_response.status_code}")
            print(f"Response: {deselect_response.text}")
            return False
        
        print("✅ Tag deselection request successful")
        
        # Step 6: Verify the tag was actually deselected
        print("\n6. Verifying deselection...")
        time.sleep(1)  # Give the backend time to process
        
        final_selected_response = requests.get(f"{base_url}/api/selected-tags")
        if final_selected_response.status_code != 200:
            print(f"❌ Failed to get final selected tags: {final_selected_response.status_code}")
            return False
        
        final_selected_tags = final_selected_response.json()
        final_tag_names = [tag.get('Product Name*', '') if isinstance(tag, dict) else str(tag) for tag in final_selected_tags]
        
        if tag_name in final_tag_names:
            print(f"❌ Tag '{tag_name}' is still in selected tags after deselection")
            return False
        else:
            print(f"✅ Tag '{tag_name}' successfully deselected")
        
        # Step 7: Verify the tag appears in available tags
        print("\n7. Verifying tag appears in available tags...")
        final_available_response = requests.get(f"{base_url}/api/available-tags")
        if final_available_response.status_code != 200:
            print(f"❌ Failed to get final available tags: {final_available_response.status_code}")
            return False
        
        final_available_tags = final_available_response.json()
        final_available_names = [tag.get('Product Name*', '') if isinstance(tag, dict) else str(tag) for tag in final_available_tags]
        
        if tag_name in final_available_names:
            print(f"✅ Tag '{tag_name}' appears in available tags after deselection")
        else:
            print(f"⚠️ Tag '{tag_name}' not found in available tags (may be filtered)")
        
        print("\n✅ JSON deselection test completed successfully!")
        print("The move-tags API is working correctly for both selection and deselection.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Simple JSON Deselection Test\n")
    success = test_json_deselection_simple()
    
    if success:
        print("\n🎉 All tests passed! JSON deselection functionality is working correctly.")
    else:
        print("\n❌ Some tests failed. JSON deselection needs to be fixed.") 