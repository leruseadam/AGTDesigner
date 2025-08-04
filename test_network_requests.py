#!/usr/bin/env python3
"""
Test to check network requests made by the frontend
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_network_requests():
    """Test network requests made by the frontend"""
    print("=== Testing Network Requests ===")
    
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
        
        # Wait a bit for all API calls to complete
        import time
        time.sleep(5)
        
        print("\n3. Checking network requests...")
        # Get all network requests
        performance_entries = driver.execute_script("""
            return window.performance.getEntries().filter(entry => 
                entry.entryType === 'resource' && 
                entry.name.includes('/api/')
            ).map(entry => ({
                name: entry.name,
                duration: entry.duration,
                startTime: entry.startTime,
                transferSize: entry.transferSize || 0
            }));
        """)
        
        if performance_entries:
            print(f"   API calls found: {len(performance_entries)}")
            for entry in performance_entries:
                print(f"   - {entry['name']} (duration: {entry['duration']:.0f}ms, size: {entry['transferSize']} bytes)")
        else:
            print("   No API calls found")
        
        print("\n4. Checking if filter options API was called...")
        filter_options_calls = [entry for entry in performance_entries if '/api/filter-options' in entry['name']]
        if filter_options_calls:
            print(f"   Filter options API calls: {len(filter_options_calls)}")
            for call in filter_options_calls:
                print(f"   - {call['name']}")
        else:
            print("   No filter options API calls found")
        
        print("\n5. Manually calling filter options API...")
        # Manually call the filter options API
        filter_options = driver.execute_script("""
            return fetch('/api/filter-options')
                .then(response => response.json())
                .then(data => data);
        """)
        
        if filter_options:
            strain_options = filter_options.get('strain', [])
            print(f"   Manual API call successful")
            print(f"   Strain options: {len(strain_options)}")
            print(f"   Sample strains: {strain_options[:5]}")
        else:
            print("   Manual API call failed")
        
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
    test_network_requests() 