#!/usr/bin/env python3
"""
Test script to verify that weight values include units in JSON responses
and that units are available as URL parameters.
"""

import requests
import json
import sys

def test_json_matching_with_units():
    """Test JSON matching with units parameter."""
    
    # Test URL (you can replace this with a real JSON URL)
    test_url = "https://example.com/test.json"
    
    # Test cases with different units
    test_cases = [
        {'units': 'g', 'description': 'Grams'},
        {'units': 'oz', 'description': 'Ounces'},
        {'units': 'mg', 'description': 'Milligrams'},
        {'units': 'lb', 'description': 'Pounds'}
    ]
    
    print("Testing JSON matching with units parameter...")
    print("=" * 50)
    
    for test_case in test_cases:
        units = test_case['units']
        description = test_case['description']
        
        print(f"\nTesting with {description} ({units}):")
        
        # Test POST method with units in JSON body
        try:
            response = requests.post(
                'http://localhost:5002/api/json-match',
                json={'url': test_url, 'units': units},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ POST request successful")
                print(f"  📊 Response includes units_available: {data.get('units_available', False)}")
                print(f"  📊 Default units: {data.get('default_units', 'Not found')}")
                print(f"  📊 Message: {data.get('message', 'No message')}")
                
                # Check if weight values include units
                available_tags = data.get('available_tags', [])
                if available_tags:
                    print(f"  📊 Found {len(available_tags)} available tags")
                    for i, tag in enumerate(available_tags[:3]):  # Show first 3 tags
                        weight = tag.get('Weight*', tag.get('Weight', ''))
                        print(f"    Tag {i+1}: Weight = '{weight}'")
                else:
                    print(f"  📊 No available tags found (expected for test URL)")
            else:
                print(f"  ❌ POST request failed: {response.status_code}")
                print(f"  📊 Response: {response.text}")
                
        except Exception as e:
            print(f"  ❌ POST request error: {e}")
        
        # Test GET method with units as URL parameter
        try:
            response = requests.get(
                f'http://localhost:5002/api/json-match?url={test_url}&units={units}',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ GET request successful")
                print(f"  📊 Response includes units_available: {data.get('units_available', False)}")
                print(f"  📊 Default units: {data.get('default_units', 'Not found')}")
            else:
                print(f"  ❌ GET request failed: {response.status_code}")
                print(f"  📊 Response: {response.text}")
                
        except Exception as e:
            print(f"  ❌ GET request error: {e}")

def test_weight_formatting():
    """Test weight formatting in the Excel processor."""
    
    print("\n\nTesting weight formatting in Excel processor...")
    print("=" * 50)
    
    try:
        # Import the Excel processor
        sys.path.append('.')
        from src.core.data.excel_processor import ExcelProcessor
        
        # Create a test processor
        processor = ExcelProcessor()
        
        # Test cases
        test_records = [
            {
                'Weight*': '3.5',
                'Units': 'g',
                'Product Type*': 'flower'
            },
            {
                'Weight*': '1',
                'Units': 'oz',
                'Product Type*': 'flower'
            },
            {
                'Weight*': '100',
                'Units': 'mg',
                'Product Type*': 'edible'
            }
        ]
        
        for i, record in enumerate(test_records):
            formatted_weight = processor._format_weight_units(record)
            print(f"  Test {i+1}: Weight={record['Weight*']}, Units={record['Units']} -> Formatted: '{formatted_weight}'")
            
            # Check if units are included
            if record['Units'] in formatted_weight:
                print(f"    ✅ Units included correctly")
            else:
                print(f"    ❌ Units not included")
                
    except Exception as e:
        print(f"  ❌ Error testing weight formatting: {e}")

if __name__ == "__main__":
    print("Weight Units JSON Test")
    print("=" * 50)
    
    # Test JSON matching with units
    test_json_matching_with_units()
    
    # Test weight formatting
    test_weight_formatting()
    
    print("\n\nTest completed!")
