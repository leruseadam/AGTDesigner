#!/usr/bin/env python3
"""
Test script to verify strain change persistence and frontend sync
"""

import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

def test_strain_change_persistence():
    """Test that strain changes persist after page reload"""
    
    print("Testing Strain Change Persistence")
    print("=" * 50)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://localhost:9090")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "uploadSection"))
        )
        
        print("1. Page loaded successfully")
        
        # Check if data is already loaded
        try:
            # Look for tag lists
            available_tags = driver.find_element(By.ID, "availableTags")
            if available_tags.find_elements(By.CLASS_NAME, "tag-item"):
                print("2. Data already loaded, proceeding with strain change test")
            else:
                print("2. No data loaded, need to upload file first")
                return False
        except:
            print("2. No data loaded, need to upload file first")
            return False
        
        # Find a tag with lineage dropdown
        tag_items = driver.find_elements(By.CLASS_NAME, "tag-item")
        if not tag_items:
            print("3. No tag items found")
            return False
        
        # Find first tag with lineage dropdown
        target_tag = None
        for tag in tag_items:
            try:
                lineage_select = tag.find_element(By.CLASS_NAME, "lineage-select")
                if lineage_select.is_enabled():
                    target_tag = tag
                    break
            except:
                continue
        
        if not target_tag:
            print("3. No tags with editable lineage found")
            return False
        
        # Get current lineage value
        lineage_select = target_tag.find_element(By.CLASS_NAME, "lineage-select")
        current_lineage = lineage_select.get_attribute("value")
        tag_name = target_tag.get_attribute("data-tag-name")
        
        print(f"4. Found tag: {tag_name} with current lineage: {current_lineage}")
        
        # Change lineage to a different value
        new_lineage = "SATIVA" if current_lineage != "SATIVA" else "INDICA"
        
        # Select new lineage
        select = Select(lineage_select)
        select.select_by_value(new_lineage)
        
        # Wait for save to complete
        time.sleep(3)
        
        print(f"5. Changed lineage to: {new_lineage}")
        
        # Verify change was applied (check for success message or updated value)
        updated_value = lineage_select.get_attribute("value")
        if updated_value == new_lineage:
            print("6. Lineage change confirmed in UI")
        else:
            print(f"6. Lineage change failed - expected {new_lineage}, got {updated_value}")
            return False
        
        # Now reload the page
        print("7. Reloading page...")
        driver.refresh()
        
        # Wait for page to reload
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "availableTags"))
        )
        
        print("8. Page reloaded successfully")
        
        # Find the same tag again
        tag_items = driver.find_elements(By.CLASS_NAME, "tag-item")
        reloaded_tag = None
        for tag in tag_items:
            if tag.get_attribute("data-tag-name") == tag_name:
                reloaded_tag = tag
                break
        
        if not reloaded_tag:
            print("9. Could not find the same tag after reload")
            return False
        
        # Check if lineage change persisted
        reloaded_lineage_select = reloaded_tag.find_element(By.CLASS_NAME, "lineage-select")
        reloaded_lineage = reloaded_lineage_select.get_attribute("value")
        
        if reloaded_lineage == new_lineage:
            print("10. ✓ Lineage change persisted after page reload!")
            return True
        else:
            print(f"10. ✗ Lineage change did not persist - expected {new_lineage}, got {reloaded_lineage}")
            return False
            
    except Exception as e:
        print(f"Error during test: {e}")
        return False
    finally:
        if driver:
            driver.quit()

def test_backend_api_persistence():
    """Test backend API persistence of strain changes"""
    
    print("\nTesting Backend API Persistence")
    print("=" * 50)
    
    base_url = "http://localhost:9090"
    
    try:
        # Get available tags
        response = requests.get(f"{base_url}/api/available-tags?limit=5")
        if response.status_code != 200:
            print("1. Failed to get available tags")
            return False
        
        tags = response.json()
        if not tags:
            print("1. No tags available")
            return False
        
        # Find a tag to update
        test_tag = None
        for tag in tags:
            if tag.get('Lineage') and tag.get('Product Name*'):
                test_tag = tag
                break
        
        if not test_tag:
            print("1. No suitable tag found for testing")
            return False
        
        tag_name = test_tag['Product Name*']
        current_lineage = test_tag['Lineage']
        
        print(f"2. Testing with tag: {tag_name} (current lineage: {current_lineage})")
        
        # Update lineage
        new_lineage = "SATIVA" if current_lineage != "SATIVA" else "INDICA"
        update_data = {
            'tag_name': tag_name,
            'lineage': new_lineage
        }
        
        print(f"3. Updating lineage to {new_lineage}...")
        response = requests.post(f"{base_url}/api/update-lineage", json=update_data)
        
        if response.status_code == 200:
            print("4. ✓ Lineage updated successfully via API")
        else:
            print(f"4. ✗ Failed to update lineage: {response.status_code}")
            return False
        
        # Wait a moment for changes to propagate
        time.sleep(2)
        
        # Check if change persisted by getting tags again
        response = requests.get(f"{base_url}/api/available-tags?limit=50")
        if response.status_code != 200:
            print("5. Failed to get updated tags")
            return False
        
        updated_tags = response.json()
        updated_tag = None
        for tag in updated_tags:
            if tag.get('Product Name*') == tag_name:
                updated_tag = tag
                break
        
        if not updated_tag:
            print("5. Could not find updated tag")
            return False
        
        updated_lineage = updated_tag.get('Lineage', '')
        if updated_lineage == new_lineage:
            print("6. ✓ Lineage change persisted in backend!")
            return True
        else:
            print(f"6. ✗ Lineage change did not persist - expected {new_lineage}, got {updated_lineage}")
            return False
            
    except Exception as e:
        print(f"Error during API test: {e}")
        return False

if __name__ == "__main__":
    print("Strain Change Persistence Test Suite")
    print("=" * 60)
    
    # Test backend API persistence
    api_success = test_backend_api_persistence()
    
    # Test frontend persistence (only if backend test passed)
    if api_success:
        frontend_success = test_strain_change_persistence()
    else:
        print("\nSkipping frontend test due to backend failure")
        frontend_success = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Backend API Persistence: {'✓ PASS' if api_success else '✗ FAIL'}")
    print(f"Frontend UI Persistence: {'✓ PASS' if frontend_success else '✗ FAIL'}")
    
    if api_success and frontend_success:
        print("\n🎉 ALL TESTS PASSED! Strain changes persist correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.") 