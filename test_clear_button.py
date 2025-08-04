#!/usr/bin/env python3
"""
Test script to check if clear button functionality is working.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_clear_button_functionality():
    """Test the clear button functionality."""
    
    print("=== TESTING CLEAR BUTTON FUNCTIONALITY ===")
    
    base_url = "http://127.0.0.1:9090"
    
    try:
        # Test 1: Check if server is running
        print("\n1. Testing server connectivity...")
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding properly")
            return False
        
        # Test 2: Test clear-filters API endpoint
        print("\n2. Testing clear-filters API endpoint...")
        response = requests.post(f"{base_url}/api/clear-filters", 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Clear-filters API endpoint is working")
                print(f"   - Available tags: {len(data.get('available_tags', []))}")
                print(f"   - Selected tags: {len(data.get('selected_tags', []))}")
            else:
                print("❌ Clear-filters API returned success=false")
                return False
        else:
            print(f"❌ Clear-filters API failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test 3: Test clear-selected functionality
        print("\n3. Testing clear-selected functionality...")
        
        # First, get current selected tags
        response = requests.get(f"{base_url}/api/selected-tags", timeout=10)
        if response.status_code == 200:
            selected_data = response.json()
            # Handle both list and dict responses
            if isinstance(selected_data, list):
                initial_selected_count = len(selected_data)
            else:
                initial_selected_count = len(selected_data.get('selected_tags', []))
            print(f"   - Initial selected tags: {initial_selected_count}")
        else:
            print("❌ Could not get initial selected tags")
            return False
        
        # Clear selected tags
        response = requests.post(f"{base_url}/api/clear-filters", 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                cleared_selected_count = len(data.get('selected_tags', []))
                print(f"   - After clearing: {cleared_selected_count} selected tags")
                
                if cleared_selected_count == 0:
                    print("✅ Clear selected functionality is working")
                else:
                    print("❌ Clear selected did not clear all tags")
                    return False
            else:
                print("❌ Clear operation failed")
                return False
        else:
            print(f"❌ Clear operation failed with status {response.status_code}")
            return False
        
        # Test 4: Test filter clearing functionality
        print("\n4. Testing filter clearing functionality...")
        
        # Get filter options
        response = requests.get(f"{base_url}/api/filter-options", timeout=10)
        if response.status_code == 200:
            filter_data = response.json()
            print("   - Filter options available")
            
            # Test clearing filters
            response = requests.post(f"{base_url}/api/clear-filters", 
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Filter clearing is working")
                else:
                    print("❌ Filter clearing failed")
                    return False
            else:
                print(f"❌ Filter clearing failed with status {response.status_code}")
                return False
        else:
            print("❌ Could not get filter options")
            return False
        
        print("\n=== ALL TESTS PASSED ===")
        print("✅ Clear button functionality is working correctly!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the application is running on port 9090.")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Server might be overloaded.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_clear_button_ui():
    """Test the clear button UI elements."""
    
    print("\n=== TESTING CLEAR BUTTON UI ELEMENTS ===")
    
    base_url = "http://127.0.0.1:9090"
    
    try:
        # Get the main page HTML
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # Check for clear filters button
            if 'clearFiltersBtn' in html_content:
                print("✅ Clear Filters button found in HTML")
            else:
                print("❌ Clear Filters button not found in HTML")
                return False
            
            # Check for clear-filters-btn (selected tags clear button)
            if 'clear-filters-btn' in html_content:
                print("✅ Clear Selected Tags button found in HTML")
            else:
                print("❌ Clear Selected Tags button not found in HTML")
                return False
            
            # Check for onclick handlers
            if 'TagManager.clearAllFilters()' in html_content:
                print("✅ Clear All Filters onclick handler found")
            else:
                print("❌ Clear All Filters onclick handler not found")
                return False
            
            print("✅ All UI elements are present")
            return True
        else:
            print(f"❌ Could not load main page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing UI elements: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Clear Button Tests...")
    
    # Test UI elements first
    ui_success = test_clear_button_ui()
    
    # Test functionality
    func_success = test_clear_button_functionality()
    
    if ui_success and func_success:
        print("\n🎉 ALL CLEAR BUTTON TESTS PASSED!")
        print("The clear button should be working correctly.")
    else:
        print("\n❌ SOME CLEAR BUTTON TESTS FAILED!")
        print("There may be issues with the clear button functionality.")
        
        if not ui_success:
            print("- UI elements may be missing or incorrectly configured")
        if not func_success:
            print("- Backend API endpoints may not be working properly") 