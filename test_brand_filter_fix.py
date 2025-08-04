#!/usr/bin/env python3
"""
Test script to verify brand filter fix - ensures filters don't revert after selection
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

def test_brand_filter_fix():
    """Test that brand filter doesn't revert after selection"""
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)
        
        print("1. Loading the application...")
        driver.get("http://localhost:9090")
        
        # Wait for the page to load
        wait.until(EC.presence_of_element_located((By.ID, "fileInput")))
        print("   Application loaded successfully")
        
        print("2. Uploading test file...")
        # Find and upload the test file
        file_input = driver.find_element(By.ID, "fileInput")
        file_path = "/Users/adamcordova/Desktop/labelMaker_ newgui BACKUP 6.24/data/default_inventory.xlsx"
        file_input.send_keys(file_path)
        
        # Wait for upload to complete
        wait.until(EC.invisibility_of_element_located((By.ID, "uploadProgress")))
        print("   File uploaded successfully")
        
        # Wait for filters to populate
        print("3. Waiting for filters to populate...")
        time.sleep(3)
        
        # Check if brand filter is populated
        brand_filter = Select(driver.find_element(By.ID, "brandFilter"))
        brand_options = [option.text for option in brand_filter.options]
        print(f"   Brand filter options: {brand_options}")
        
        if len(brand_options) <= 1:
            print("   ERROR: Brand filter not populated properly")
            return False
        
        # Select a specific brand
        print("4. Selecting a brand filter...")
        test_brand = brand_options[1] if len(brand_options) > 1 else brand_options[0]  # Select first non-"All" option
        brand_filter.select_by_visible_text(test_brand)
        print(f"   Selected brand: {test_brand}")
        
        # Wait for filter to apply
        time.sleep(2)
        
        # Check if the filter value is still selected
        current_brand_value = brand_filter.first_selected_option.text
        print(f"   Current brand filter value: {current_brand_value}")
        
        if current_brand_value != test_brand:
            print("   ERROR: Brand filter reverted after selection")
            return False
        
        # Wait a bit longer to see if it reverts
        print("5. Waiting to check for filter reversion...")
        time.sleep(3)
        
        # Check again
        current_brand_value_after_wait = brand_filter.first_selected_option.text
        print(f"   Brand filter value after wait: {current_brand_value_after_wait}")
        
        if current_brand_value_after_wait != test_brand:
            print("   ERROR: Brand filter reverted after waiting")
            return False
        
        # Check available tags to see if filtering worked
        print("6. Checking available tags...")
        available_tags_container = driver.find_element(By.ID, "availableTags")
        tag_elements = available_tags_container.find_elements(By.CLASS_NAME, "tag-checkbox")
        print(f"   Available tags count: {len(tag_elements)}")
        
        if len(tag_elements) == 0:
            print("   WARNING: No tags visible after filtering")
        else:
            print("   Tags are visible after filtering")
        
        print("7. Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ERROR: Test failed with exception: {e}")
        return False
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    print("Testing Brand Filter Fix")
    print("=" * 50)
    
    success = test_brand_filter_fix()
    
    if success:
        print("\n✅ Brand filter fix test PASSED")
        print("The brand filter no longer reverts after selection")
    else:
        print("\n❌ Brand filter fix test FAILED")
        print("The brand filter still reverts after selection")
    
    print("\nTest completed.") 