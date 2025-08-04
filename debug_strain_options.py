#!/usr/bin/env python3
"""
Debug script to check strain filter options
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

def debug_strain_options():
    """Debug strain filter options"""
    print("=== Debugging Strain Filter Options ===")
    
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
        
        print("\n3. Checking strain filter options...")
        # Find the strain filter dropdown
        strain_filter = Select(driver.find_element(By.ID, "strainFilter"))
        
        # Get all options
        all_options = [option.text for option in strain_filter.options]
        print(f"   Total options: {len(all_options)}")
        print(f"   All options: {all_options[:20]}...")  # Show first 20
        
        # Get non-empty options
        valid_options = [option.text for option in strain_filter.options if option.text and option.text.strip()]
        print(f"   Valid options: {len(valid_options)}")
        print(f"   Valid options: {valid_options[:20]}...")  # Show first 20
        
        # Get options that are not "All Strains"
        non_all_options = [option.text for option in strain_filter.options if option.text and option.text != "All Strains"]
        print(f"   Non-'All Strains' options: {len(non_all_options)}")
        print(f"   Non-'All Strains' options: {non_all_options[:20]}...")  # Show first 20
        
        # Get current selection
        current_selection = strain_filter.first_selected_option.text
        print(f"   Current selection: '{current_selection}'")
        
        # Try to select a specific strain
        if non_all_options:
            test_strain = non_all_options[0]
            print(f"   Trying to select: '{test_strain}'")
            strain_filter.select_by_visible_text(test_strain)
            
            # Check if selection worked
            time.sleep(1)
            new_selection = strain_filter.first_selected_option.text
            print(f"   New selection: '{new_selection}'")
            
            if new_selection == test_strain:
                print("   ✓ Selection successful")
            else:
                print(f"   ✗ Selection failed. Expected: '{test_strain}', Got: '{new_selection}'")
        
        print("\n4. Checking localStorage...")
        localStorage_value = driver.execute_script("return localStorage.getItem('labelMaker_filters');")
        if localStorage_value:
            filters = json.loads(localStorage_value)
            print(f"   localStorage filters: {filters}")
        else:
            print("   No filters in localStorage")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Debug failed with error: {e}")
        return False
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    debug_strain_options() 