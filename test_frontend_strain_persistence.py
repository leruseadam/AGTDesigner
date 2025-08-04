#!/usr/bin/env python3
"""
Frontend test for strain filter persistence
Simulates browser behavior to test localStorage persistence
"""

import requests
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

def test_frontend_strain_persistence():
    """Test strain filter persistence in the frontend"""
    print("=== Testing Frontend Strain Filter Persistence ===")
    
    # Setup Chrome options for headless testing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        print("\n1. Loading the application...")
        driver.get("http://localhost:9090")
        
        # Wait for the page to load
        wait.until(EC.presence_of_element_located((By.ID, "fileInput")))
        print("   Application loaded successfully")
        
        print("\n2. Uploading test file...")
        # Find and upload the test file
        file_input = driver.find_element(By.ID, "fileInput")
        file_path = os.path.abspath("data/default_inventory.xlsx")
        file_input.send_keys(file_path)
        
        # Wait for upload to complete
        wait.until(EC.invisibility_of_element_located((By.ID, "uploadProgress")))
        print("   File uploaded successfully")
        
        # Wait for filters to populate
        wait.until(EC.presence_of_element_located((By.ID, "strainFilter")))
        print("   Filters populated")
        
        print("\n3. Testing strain filter selection...")
        # Find the strain filter dropdown
        strain_filter = Select(driver.find_element(By.ID, "strainFilter"))
        
        # Get available options (exclude "All Strains" and empty options)
        options = [option.text for option in strain_filter.options if option.text and option.text != "All Strains" and option.text.strip()]
        if not options:
            print("   No strain options available")
            return False
            
        # Select a specific strain (prefer a real strain name)
        test_strain = None
        for option in options:
            if option and option != "All Strains" and option != "nan" and option.strip():
                test_strain = option
                break
        
        if not test_strain:
            print("   No valid strain options found")
            return False
            
        strain_filter.select_by_visible_text(test_strain)
        print(f"   Selected strain: {test_strain}")
        
        # Wait for filter to apply
        time.sleep(2)
        
        print("\n4. Testing page reload persistence...")
        # Reload the page
        driver.refresh()
        
        # Wait for page to reload and filters to populate
        wait.until(EC.presence_of_element_located((By.ID, "strainFilter")))
        
        # Check if the strain filter still has the selected value
        strain_filter = Select(driver.find_element(By.ID, "strainFilter"))
        current_selection = strain_filter.first_selected_option.text
        
        if current_selection == test_strain:
            print(f"   ✓ Strain filter persisted after reload: {current_selection}")
        else:
            print(f"   ✗ Strain filter did not persist. Expected: {test_strain}, Got: {current_selection}")
            return False
        
        print("\n5. Testing new file upload with persisted filter...")
        # Upload a different file (use the same file for testing)
        file_input = driver.find_element(By.ID, "fileInput")
        file_input.send_keys(file_path)
        
        # Wait for upload to complete
        wait.until(EC.invisibility_of_element_located((By.ID, "uploadProgress")))
        
        # Wait for filters to repopulate
        wait.until(EC.presence_of_element_located((By.ID, "strainFilter")))
        
        # Check if the strain filter still has the selected value
        strain_filter = Select(driver.find_element(By.ID, "strainFilter"))
        current_selection = strain_filter.first_selected_option.text
        
        if current_selection == test_strain:
            print(f"   ✓ Strain filter persisted after new file upload: {current_selection}")
        else:
            print(f"   ✗ Strain filter did not persist after new file upload. Expected: {test_strain}, Got: {current_selection}")
            return False
        
        print("\n6. Testing localStorage persistence...")
        # Check localStorage directly
        localStorage_value = driver.execute_script("return localStorage.getItem('labelMaker_filters');")
        if localStorage_value:
            filters = json.loads(localStorage_value)
            if 'strain' in filters and filters['strain'] == test_strain:
                print(f"   ✓ localStorage contains correct strain filter: {filters['strain']}")
            else:
                print(f"   ✗ localStorage strain filter mismatch. Expected: {test_strain}, Got: {filters.get('strain', 'Not found')}")
                return False
        else:
            print("   ✗ No filters found in localStorage")
            return False
        
        print("\n=== All Tests Passed! ===")
        print("Strain filter persistence is working correctly.")
        return True
        
    except Exception as e:
        print(f"   ✗ Test failed with error: {e}")
        return False
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    success = test_frontend_strain_persistence()
    if not success:
        print("\n=== Test Failed ===")
        print("Please check the implementation and try again.")
    exit(0 if success else 1) 