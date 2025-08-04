#!/usr/bin/env python3
"""
Test script for the strain lineage editor button functionality.
This script tests the new button that opens the strain lineage editor.
"""

import requests
import json
import sys
import os

def test_strain_lineage_button_functionality():
    """Test that the strain lineage editor button works correctly."""
    
    print("Testing Strain Lineage Editor Button Functionality")
    print("=" * 60)
    
    try:
        # Test that the main page loads and contains the button
        response = requests.get('http://localhost:5000/')
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check if the button is present in the HTML
            if 'Strain Lineage Editor' in html_content:
                print("✅ Strain Lineage Editor button found in main page")
            else:
                print("❌ Strain Lineage Editor button not found in main page")
                return False
            
            # Check if the onclick function is present
            if 'openStrainLineageEditor()' in html_content:
                print("✅ openStrainLineageEditor() function reference found")
            else:
                print("❌ openStrainLineageEditor() function reference not found")
                return False
            
            # Check if the modal HTML is present
            if 'strainLineageEditorModal' in html_content:
                print("✅ Strain lineage editor modal HTML found")
            else:
                print("❌ Strain lineage editor modal HTML not found")
                return False
            
            print("\n✅ All HTML elements are present!")
            return True
            
        else:
            print(f"❌ Failed to load main page: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask app is running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_api_endpoint():
    """Test that the API endpoint for strain lineage updates is working."""
    
    print("\nTesting API Endpoint")
    print("-" * 30)
    
    try:
        # Test with invalid data (should return 400)
        test_data = {
            'strain_name': '',  # Missing strain name
            'lineage': 'HYBRID'
        }
        
        response = requests.post(
            'http://localhost:5000/api/update-strain-lineage',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            print("✅ API endpoint correctly handles missing strain name")
        else:
            print(f"❌ API endpoint should return 400 for missing strain name, got {response.status_code}")
            return False
        
        # Test with non-existent strain (should return 404)
        test_data = {
            'strain_name': 'NonExistentStrain',
            'lineage': 'HYBRID'
        }
        
        response = requests.post(
            'http://localhost:5000/api/update-strain-lineage',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 404:
            print("✅ API endpoint correctly handles non-existent strain")
        else:
            print(f"❌ API endpoint should return 404 for non-existent strain, got {response.status_code}")
            return False
        
        print("✅ API endpoint is working correctly!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask app is running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Strain Lineage Editor Button Implementation")
    print("=" * 60)
    
    # Test HTML elements
    html_success = test_strain_lineage_button_functionality()
    
    # Test API endpoint
    api_success = test_api_endpoint()
    
    print("\n" + "=" * 60)
    if html_success and api_success:
        print("✅ All tests passed! Strain Lineage Editor button is ready to use.")
        print("\nTo use the strain lineage editor:")
        print("1. Load a file with product data")
        print("2. Click the 'Strain Lineage Editor' button next to Product Library Browser")
        print("3. Select a strain from the dropdown")
        print("4. Choose the new lineage for all products with that strain")
        print("5. Click 'Update All Products'")
    else:
        print("❌ Some tests failed. Check the implementation.") 