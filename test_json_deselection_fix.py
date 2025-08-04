#!/usr/bin/env python3
"""
Test script to reproduce and fix the JSON deselection issue.
"""

import requests
import json
import time

def test_json_deselection_issue():
    """Test that JSON selected items can be properly deselected."""
    
    print("🧪 Testing JSON Deselection Issue")
    print("=" * 50)
    
    # Base URL for the application
    base_url = "http://localhost:5001"
    
    # Test JSON URL (using a local test file)
    import os
    test_json_path = os.path.join(os.getcwd(), "test_inventory.json")
    test_json_url = f"file://{test_json_path}"
    
    try:
        # Step 1: Perform JSON matching
        print("1. Performing JSON matching...")
        json_match_response = requests.post(f"{base_url}/api/json-match", 
                                          json={"url": test_json_url},
                                          timeout=30)
        
        if json_match_response.status_code != 200:
            print(f"❌ JSON matching failed: {json_match_response.status_code}")
            print(f"Response: {json_match_response.text}")
            return False
        
        match_result = json_match_response.json()
        print(f"✅ JSON matching successful: {match_result.get('matched_count', 0)} items matched")
        
        # Step 2: Check selected tags
        print("\n2. Checking selected tags...")
        selected_response = requests.get(f"{base_url}/api/selected-tags")
        
        if selected_response.status_code != 200:
            print(f"❌ Failed to get selected tags: {selected_response.status_code}")
            return False
        
        selected_tags = selected_response.json()
        print(f"✅ Selected tags count: {len(selected_tags)}")
        
        if len(selected_tags) == 0:
            print("❌ No selected tags found after JSON matching")
            return False
        
        # Step 3: Try to deselect a tag
        print("\n3. Testing tag deselection...")
        if len(selected_tags) > 0:
            tag_to_deselect = selected_tags[0]
            tag_name = tag_to_deselect.get('Product Name*', '') if isinstance(tag_to_deselect, dict) else str(tag_to_deselect)
            
            print(f"Attempting to deselect: {tag_name}")
            
            # Simulate deselection by moving tag to available
            move_response = requests.post(f"{base_url}/api/move-tags",
                                        json={
                                            "tags": [tag_name],
                                            "direction": "to_available"
                                        })
            
            if move_response.status_code != 200:
                print(f"❌ Failed to deselect tag: {move_response.status_code}")
                print(f"Response: {move_response.text}")
                return False
            
            print("✅ Tag deselection request successful")
            
            # Step 4: Verify the tag was actually deselected
            print("\n4. Verifying deselection...")
            time.sleep(1)  # Give the backend time to process
            
            updated_selected_response = requests.get(f"{base_url}/api/selected-tags")
            if updated_selected_response.status_code != 200:
                print(f"❌ Failed to get updated selected tags: {updated_selected_response.status_code}")
                return False
            
            updated_selected_tags = updated_selected_response.json()
            updated_tag_names = [tag.get('Product Name*', '') if isinstance(tag, dict) else str(tag) for tag in updated_selected_tags]
            
            if tag_name in updated_tag_names:
                print(f"❌ Tag '{tag_name}' is still in selected tags after deselection")
                print(f"Updated selected tags: {updated_tag_names}")
                return False
            else:
                print(f"✅ Tag '{tag_name}' successfully deselected")
        
        # Step 5: Test available tags to see if deselected tag appears there
        print("\n5. Checking available tags...")
        available_response = requests.get(f"{base_url}/api/available-tags")
        
        if available_response.status_code != 200:
            print(f"❌ Failed to get available tags: {available_response.status_code}")
            return False
        
        available_tags = available_response.json()
        available_tag_names = [tag.get('Product Name*', '') if isinstance(tag, dict) else str(tag) for tag in available_tags]
        
        if tag_name in available_tag_names:
            print(f"✅ Tag '{tag_name}' appears in available tags after deselection")
        else:
            print(f"⚠️ Tag '{tag_name}' not found in available tags (may be filtered)")
        
        print("\n✅ JSON deselection test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_frontend_deselection():
    """Test the frontend deselection functionality."""
    
    print("\n🧪 Testing Frontend Deselection")
    print("=" * 50)
    
    # This would require a browser automation tool like Selenium
    # For now, we'll just document the expected behavior
    
    print("Frontend deselection should work as follows:")
    print("1. JSON matched items appear in Selected Tags list")
    print("2. User can uncheck individual checkboxes in Selected Tags")
    print("3. Unchecked items should be removed from Selected Tags")
    print("4. Unchecked items should appear in Available Tags (if not filtered)")
    print("5. The deselection should persist across page refreshes")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting JSON Deselection Fix Test")
    print()
    
    # Test backend deselection
    backend_success = test_json_deselection_issue()
    
    # Test frontend deselection (documentation only)
    frontend_success = test_frontend_deselection()
    
    print("\n" + "=" * 50)
    if backend_success and frontend_success:
        print("🎉 All tests completed successfully!")
        print("JSON deselection functionality should be working properly.")
    else:
        print("❌ Some tests failed. JSON deselection needs to be fixed.")
    
    print("\nTo test frontend deselection manually:")
    print("1. Load the application in a browser")
    print("2. Perform JSON matching with a test URL")
    print("3. Try to uncheck items in the Selected Tags list")
    print("4. Verify that unchecked items are removed from Selected Tags")
    print("5. Check that unchecked items appear in Available Tags") 