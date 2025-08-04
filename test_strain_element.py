#!/usr/bin/env python3
"""
Test to check if strain filter element exists
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_strain_element():
    """Test if strain filter element exists"""
    print("=== Testing Strain Filter Element ===")
    
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
        
        print("\n2. Checking if strain filter element exists...")
        strain_filter = driver.find_element(By.ID, "strainFilter")
        if strain_filter:
            print("   ✓ Strain filter element found")
            print(f"   Element tag: {strain_filter.tag_name}")
            print(f"   Element HTML: {strain_filter.get_attribute('outerHTML')[:200]}...")
        else:
            print("   ✗ Strain filter element not found")
            return False
        
        print("\n3. Uploading test file...")
        # Find and upload the test file
        file_input = driver.find_element(By.ID, "fileInput")
        file_path = "/Users/adamcordova/Desktop/labelMaker_ newgui BACKUP 6.24/data/default_inventory.xlsx"
        file_input.send_keys(file_path)
        
        # Wait for upload to complete
        wait.until(EC.invisibility_of_element_located((By.ID, "uploadProgress")))
        print("   File uploaded successfully")
        
        # Wait a bit for filters to populate
        import time
        time.sleep(3)
        
        print("\n4. Checking strain filter after upload...")
        strain_filter = driver.find_element(By.ID, "strainFilter")
        options = [option.text for option in strain_filter.find_elements(By.TAG_NAME, "option")]
        print(f"   Options after upload: {options}")
        
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
    test_strain_element() 