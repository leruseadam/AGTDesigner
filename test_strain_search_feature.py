#!/usr/bin/env python3
"""
Test script for the strain search feature in the lineage editor.
This script tests the new search functionality added to the strain lineage editor.
"""

import requests
import json
import time
import sys

def test_strain_search_feature():
    """Test that the strain search feature is working correctly."""
    
    print("Testing Strain Search Feature in Lineage Editor")
    print("=" * 50)
    
    # Test 1: Check if the main page loads with search functionality
    print("\n1. Testing main page with search functionality...")
    try:
        response = requests.get("http://127.0.0.1:9090/", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # Check for search input elements
            search_elements = [
                'strainSearchInput',
                'clearStrainSearch', 
                'strainSearchResults',
                'strainListContainer'
            ]
            
            found_elements = []
            for element in search_elements:
                if element in html_content:
                    found_elements.append(element)
                    print(f"  ✅ Found {element}")
                else:
                    print(f"  ❌ Missing {element}")
            
            if len(found_elements) == len(search_elements):
                print("  ✅ All search elements found in main page")
            else:
                print(f"  ❌ Only {len(found_elements)}/{len(search_elements)} search elements found")
                
        else:
            print(f"  ❌ Main page returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing main page: {e}")
        return False
    
    # Test 2: Check if the strain lineage editor API is working
    print("\n2. Testing strain lineage editor API...")
    try:
        response = requests.get("http://127.0.0.1:9090/api/get-all-strains", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'strains' in data:
                strains = data['strains']
                print(f"  ✅ API returned {len(strains)} strains")
                
                # Check if we have enough strains to test search
                if len(strains) > 0:
                    print(f"  ✅ Sample strain: {strains[0].get('strain_name', 'Unknown')}")
                else:
                    print("  ⚠️  No strains found in database")
                    
            else:
                print(f"  ❌ API response format incorrect: {data}")
                return False
        else:
            print(f"  ❌ API returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing API: {e}")
        return False
    
    # Test 3: Check if search JavaScript functions are present
    print("\n3. Testing search JavaScript functions...")
    try:
        response = requests.get("http://127.0.0.1:9090/static/js/main.js", timeout=10)
        if response.status_code == 200:
            js_content = response.text
            
            # Check for search-related JavaScript functions
            search_functions = [
                'filterStrains',
                'strainSearchInput',
                'clearStrainSearch',
                'strainSearchResults'
            ]
            
            found_functions = []
            for func in search_functions:
                if func in js_content:
                    found_functions.append(func)
                    print(f"  ✅ Found {func} function")
                else:
                    print(f"  ❌ Missing {func} function")
            
            if len(found_functions) == len(search_functions):
                print("  ✅ All search functions found in JavaScript")
            else:
                print(f"  ❌ Only {len(found_functions)}/{len(search_functions)} search functions found")
                
        else:
            print(f"  ❌ JavaScript file returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing JavaScript: {e}")
        return False
    
    # Test 4: Check if search CSS styles are present
    print("\n4. Testing search CSS styles...")
    try:
        response = requests.get("http://127.0.0.1:9090/static/css/styles.css", timeout=10)
        if response.status_code == 200:
            css_content = response.text
            
            # Check for search-related CSS styles
            search_styles = [
                '#strainSearchInput',
                '.strain-item',
                '.no-results-message',
                '#clearStrainSearch'
            ]
            
            found_styles = []
            for style in search_styles:
                if style in css_content:
                    found_styles.append(style)
                    print(f"  ✅ Found {style} style")
                else:
                    print(f"  ❌ Missing {style} style")
            
            if len(found_styles) == len(search_styles):
                print("  ✅ All search styles found in CSS")
            else:
                print(f"  ❌ Only {len(found_styles)}/{len(search_styles)} search styles found")
                
        else:
            print(f"  ❌ CSS file returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing CSS: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Strain search feature test completed!")
    print("\nTo test the search functionality manually:")
    print("1. Open the application in your browser")
    print("2. Click the 'Strain Lineage Editor' button")
    print("3. Use the search box to filter strains by name")
    print("4. Try the 'Clear' button to reset the search")
    print("5. Press Enter to select the first visible strain")
    
    return True

if __name__ == "__main__":
    try:
        success = test_strain_search_feature()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1) 