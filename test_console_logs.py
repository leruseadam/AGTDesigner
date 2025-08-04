#!/usr/bin/env python3
"""
Test to capture console logs and debug the issue
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_console_logs():
    """Test to capture console logs"""
    print("=== Testing Console Logs ===")
    
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
        
        # Wait a bit for filters to populate
        import time
        time.sleep(5)
        
        print("\n3. Checking console logs...")
        logs = driver.get_log('browser')
        for log in logs:
            if 'strain' in log['message'].lower() or 'filter' in log['message'].lower():
                print(f"   {log['level']}: {log['message']}")
        
        print("\n4. Checking network requests...")
        # Execute JavaScript to check if the filter options API was called
        network_logs = driver.execute_script("""
            return window.performance.getEntries().filter(entry => 
                entry.name.includes('/api/filter-options')
            ).map(entry => ({
                name: entry.name,
                duration: entry.duration,
                startTime: entry.startTime
            }));
        """)
        
        if network_logs:
            print(f"   Filter options API calls: {len(network_logs)}")
            for log in network_logs:
                print(f"   - {log['name']} (duration: {log['duration']}ms)")
        else:
            print("   No filter options API calls found")
        
        print("\n5. Checking filter options directly...")
        # Execute JavaScript to check the filter options
        filter_options = driver.execute_script("""
            const response = await fetch('/api/filter-options');
            const data = await response.json();
            return data;
        """)
        
        if filter_options:
            print(f"   Filter options: {filter_options}")
        else:
            print("   No filter options returned")
        
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
    test_console_logs() 