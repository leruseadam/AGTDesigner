#!/usr/bin/env python3
"""
Test to capture browser console errors
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_console_errors():
    """Test to capture browser console errors"""
    print("=== Testing Console Errors ===")
    
    # Setup Chrome options for headless testing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")
    
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
        file_path = "/Users/adamcordova/Desktop/labelMaker_ newgui BACKUP 6.24/data/default_inventory.xlsx"
        file_input.send_keys(file_path)
        
        # Wait for upload to complete
        wait.until(EC.invisibility_of_element_located((By.ID, "uploadProgress")))
        print("   File uploaded successfully")
        
        # Wait a bit for all operations to complete
        import time
        time.sleep(8)
        
        print("\n3. Checking console logs...")
        logs = driver.get_log('browser')
        if logs:
            print(f"   Console logs found: {len(logs)}")
            for log in logs:
                if 'error' in log['level'].lower() or 'filter' in log['message'].lower():
                    print(f"   {log['level']}: {log['message']}")
        else:
            print("   No console logs found")
        
        print("\n4. Checking for alerts...")
        # Check if there are any alerts
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"   Alert found: {alert_text}")
            alert.accept()
        except:
            print("   No alerts found")
        
        print("\n5. Handling any alerts...")
        # Handle any alerts that might be present
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"   Alert found: {alert_text}")
            alert.accept()
        except:
            print("   No alerts found")
        
        print("\n6. Manually calling fetchAndPopulateFilters...")
        # Manually call the fetchAndPopulateFilters method
        result = driver.execute_script("""
            return TagManager.fetchAndPopulateFilters()
                .then(() => 'success')
                .catch(error => 'error: ' + error.message);
        """)
        
        print(f"   Manual call result: {result}")
        
        # Wait a bit more for the manual call to complete
        time.sleep(3)
        
        print("\n7. Checking strain filter options after manual call...")
        strain_filter = driver.find_element(By.ID, "strainFilter")
        options = [option.text for option in strain_filter.find_elements(By.TAG_NAME, "option")]
        print(f"   Strain filter options: {len(options)}")
        print(f"   Options: {options[:10]}")
        
        if len(options) > 1:
            print("   ✓ Strain filter populated successfully!")
        else:
            print("   ✗ Strain filter not populated")
        
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
    test_console_errors() 