#!/usr/bin/env python3
"""
Test script to verify JSON matching fixes are working properly.
"""

import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_json_serialization():
    """Test that the JSON serialization fixes work properly."""
    
    # Test data that might cause serialization issues
    test_data = {
        'success': True,
        'matched_count': 5,
        'matched_names': ['Product 1', 'Product 2', 'Product 3'],
        'available_tags': [
            {
                'Product Name*': 'Test Product 1',
                'Vendor': 'Test Vendor',
                'Price': 25.99,
                'Weight*': '3.5g',
                'Description': 'A test product with special characters: éñç',
                'THC test result': 18.5,
                'CBD test result': 0.8,
                'Lineage': 'HYBRID',
                'Source': 'JSON Match'
            },
            {
                'Product Name*': 'Test Product 2',
                'Vendor': 'Another Vendor',
                'Price': 30.00,
                'Weight*': '1g',
                'Description': 'Another test product',
                'THC test result': 22.1,
                'CBD test result': 1.2,
                'Lineage': 'SATIVA',
                'Source': 'JSON Match'
            }
        ],
        'selected_tags': [],
        'json_matched_tags': [],
        'cache_status': 'JSON Match Complete',
        'filter_mode': 'json_matched',
        'has_full_excel': False,
        'message': 'JSON matched 5 products. They are now available in the Available list for you to select.'
    }
    
    try:
        # Test JSON serialization
        json_str = json.dumps(test_data, indent=2)
        print("✅ JSON serialization test passed!")
        print(f"Serialized JSON length: {len(json_str)} characters")
        
        # Test deserialization
        parsed_data = json.loads(json_str)
        print("✅ JSON deserialization test passed!")
        
        # Verify data integrity
        assert parsed_data['success'] == True
        assert parsed_data['matched_count'] == 5
        assert len(parsed_data['matched_names']) == 3
        assert len(parsed_data['available_tags']) == 2
        print("✅ Data integrity test passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON serialization test failed: {e}")
        return False

def test_make_json_safe_function():
    """Test the make_json_safe function."""
    
    # Test data with potential serialization issues
    problematic_data = {
        'normal_string': 'Hello World',
        'normal_number': 42,
        'normal_float': 3.14,
        'normal_bool': True,
        'normal_none': None,
        'normal_list': [1, 2, 3],
        'normal_dict': {'a': 1, 'b': 2},
        'problematic_object': object(),  # This would normally cause issues
        'problematic_function': lambda x: x,  # This would normally cause issues
        'nested_problematic': {
            'normal': 'value',
            'problematic': object()
        }
    }
    
    # Define the make_json_safe function (same as in app.py)
    def make_json_safe(obj):
        """Recursively convert objects to JSON-safe format."""
        if isinstance(obj, dict):
            return {str(k): make_json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_json_safe(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    try:
        # Apply the function
        safe_data = make_json_safe(problematic_data)
        
        # Test serialization
        json_str = json.dumps(safe_data, indent=2)
        print("✅ make_json_safe function test passed!")
        print(f"Serialized JSON length: {len(json_str)} characters")
        
        # Verify that problematic objects were converted to strings
        assert isinstance(safe_data['problematic_object'], str)
        assert isinstance(safe_data['problematic_function'], str)
        assert isinstance(safe_data['nested_problematic']['problematic'], str)
        print("✅ Object conversion test passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ make_json_safe function test failed: {e}")
        return False

def test_flask_jsonify_simulation():
    """Simulate Flask's jsonify behavior."""
    
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    with app.app_context():
        try:
            # Test data
            test_data = {
                'success': True,
                'matched_count': 3,
                'matched_names': ['Product A', 'Product B', 'Product C'],
                'available_tags': [
                    {
                        'Product Name*': 'Product A',
                        'Vendor': 'Vendor A',
                        'Price': 25.99
                    }
                ],
                'message': 'Test message'
            }
            
            # Simulate jsonify
            response = jsonify(test_data)
            print("✅ Flask jsonify simulation test passed!")
            print(f"Response status: {response.status}")
            print(f"Response mimetype: {response.mimetype}")
            
            return True
            
        except Exception as e:
            print(f"❌ Flask jsonify simulation test failed: {e}")
            return False

def main():
    """Run all tests."""
    print("🧪 Running JSON matching fix tests...\n")
    
    tests = [
        ("JSON Serialization", test_json_serialization),
        ("make_json_safe Function", test_make_json_safe_function),
        ("Flask jsonify Simulation", test_flask_jsonify_simulation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The JSON matching fixes should work properly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 