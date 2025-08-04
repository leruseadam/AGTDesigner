#!/usr/bin/env python3
"""
Test script for the strain lineage editor functionality.
This script tests the new API endpoint for updating all lineage values for a given strain.
"""

import requests
import json
import sys
import os

def test_strain_lineage_update():
    """Test the strain lineage update functionality."""
    
    # Test data
    test_data = {
        'strain_name': 'Test Strain',
        'lineage': 'HYBRID'
    }
    
    try:
        # Make request to the new API endpoint
        response = requests.post(
            'http://localhost:5000/api/update-strain-lineage',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('message', 'Unknown success')}")
            print(f"   Affected products: {result.get('product_count', 0)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask app is running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_invalid_strain():
    """Test with an invalid strain name."""
    
    test_data = {
        'strain_name': 'NonExistentStrain',
        'lineage': 'HYBRID'
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/update-strain-lineage',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\nInvalid strain test:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 404:
            print("✅ Correctly handled non-existent strain")
            return True
        else:
            print("❌ Should have returned 404 for non-existent strain")
            return False
            
    except Exception as e:
        print(f"❌ Error testing invalid strain: {e}")
        return False

def test_missing_parameters():
    """Test with missing parameters."""
    
    test_cases = [
        {'strain_name': 'Test Strain'},  # Missing lineage
        {'lineage': 'HYBRID'},           # Missing strain_name
        {}                               # Missing both
    ]
    
    for i, test_data in enumerate(test_cases):
        try:
            response = requests.post(
                'http://localhost:5000/api/update-strain-lineage',
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"\nMissing parameters test {i+1}:")
            print(f"Test data: {test_data}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 400:
                print("✅ Correctly handled missing parameters")
            else:
                print("❌ Should have returned 400 for missing parameters")
                
        except Exception as e:
            print(f"❌ Error testing missing parameters: {e}")

if __name__ == "__main__":
    print("Testing Strain Lineage Editor Functionality")
    print("=" * 50)
    
    # Test the main functionality
    success = test_strain_lineage_update()
    
    # Test error cases
    test_invalid_strain()
    test_missing_parameters()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Strain lineage editor functionality appears to be working!")
    else:
        print("❌ Some tests failed. Check the Flask app and try again.")
    
    print("\nTo use the strain lineage editor:")
    print("1. Right-click on any product in the tags table")
    print("2. Select 'Edit Strain Lineage: [Strain Name]'")
    print("3. Choose the new lineage for all products with that strain")
    print("4. Click 'Update All Products'") 