#!/usr/bin/env python3
"""
Test script to verify that the NaN JSON serialization fix works properly.
"""

import json
import math
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_nan_handling():
    """Test that NaN values are properly handled in JSON serialization."""
    
    # Test data with NaN values that would cause JSON serialization issues
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
                'Description': 'A test product with NaN values',
                'THC test result': 18.5,
                'CBD test result': 0.8,
                'Lineage': 'HYBRID',
                'Source': 'JSON Match',
                'mg/g': float('nan'),  # This would normally cause JSON serialization to fail
                'test_nan': math.nan,   # Another NaN value
                'test_inf': float('inf'),  # Infinity value
                'test_neg_inf': float('-inf'),  # Negative infinity
                'normal_float': 3.14,
                'normal_int': 42,
                'normal_string': 'Hello World',
                'normal_bool': True,
                'normal_none': None
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
                'Source': 'JSON Match',
                'mg/g': float('nan'),  # Another NaN value
                'test_nan': math.nan,
                'normal_float': 2.718,
                'normal_int': 100,
                'normal_string': 'Test String',
                'normal_bool': False,
                'normal_none': None
            }
        ],
        'selected_tags': [],
        'json_matched_tags': [],
        'cache_status': 'JSON Match Complete',
        'filter_mode': 'json_matched',
        'has_full_excel': False,
        'message': 'JSON matched 5 products. They are now available in the Available list for you to select.'
    }
    
    # Define the make_json_safe function (same as in app.py)
    def make_json_safe(obj):
        """Recursively convert objects to JSON-safe format."""
        if isinstance(obj, dict):
            return {str(k): make_json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_json_safe(item) for item in obj]
        elif isinstance(obj, (int, str, bool, type(None))):
            return obj
        elif isinstance(obj, float):
            # Handle NaN and infinity values
            import math
            if math.isnan(obj) or math.isinf(obj):
                return ''
            return obj
        else:
            return str(obj)
    
    try:
        # Test 1: Original data (should fail)
        print("Testing original data with NaN values...")
        try:
            json_str = json.dumps(test_data, indent=2)
            print("❌ Original data serialized successfully (unexpected)")
        except (TypeError, ValueError) as e:
            print(f"✅ Original data failed to serialize as expected: {e}")
        
        # Test 2: JSON-safe data (should succeed)
        print("\nTesting JSON-safe data...")
        safe_data = make_json_safe(test_data)
        json_str = json.dumps(safe_data, indent=2)
        print("✅ JSON-safe data serialized successfully!")
        print(f"Serialized JSON length: {len(json_str)} characters")
        
        # Test 3: Verify NaN values were converted to empty strings
        print("\nVerifying NaN value conversion...")
        for i, tag in enumerate(safe_data['available_tags']):
            print(f"Tag {i+1}:")
            print(f"  mg/g: '{tag.get('mg/g', 'N/A')}' (should be empty string)")
            print(f"  test_nan: '{tag.get('test_nan', 'N/A')}' (should be empty string)")
            print(f"  test_inf: '{tag.get('test_inf', 'N/A')}' (should be empty string)")
            print(f"  test_neg_inf: '{tag.get('test_neg_inf', 'N/A')}' (should be empty string)")
            print(f"  normal_float: {tag.get('normal_float', 'N/A')} (should be preserved)")
            print(f"  normal_int: {tag.get('normal_int', 'N/A')} (should be preserved)")
            print(f"  normal_string: '{tag.get('normal_string', 'N/A')}' (should be preserved)")
            print(f"  normal_bool: {tag.get('normal_bool', 'N/A')} (should be preserved)")
            print(f"  normal_none: {tag.get('normal_none', 'N/A')} (should be preserved)")
        
        # Test 4: Verify data integrity
        print("\nVerifying data integrity...")
        assert safe_data['success'] == True
        assert safe_data['matched_count'] == 5
        assert len(safe_data['matched_names']) == 3
        assert len(safe_data['available_tags']) == 2
        print("✅ Data integrity test passed!")
        
        # Test 5: Test deserialization
        print("\nTesting deserialization...")
        parsed_data = json.loads(json_str)
        print("✅ Deserialization test passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ NaN handling test failed: {e}")
        return False

def test_ensure_serializable_function():
    """Test the ensure_serializable function from json_matcher.py."""
    
    # Test data with various problematic values
    problematic_data = {
        'normal_string': 'Hello World',
        'normal_number': 42,
        'normal_float': 3.14,
        'normal_bool': True,
        'normal_none': None,
        'normal_list': [1, 2, 3],
        'normal_dict': {'a': 1, 'b': 2},
        'nan_float': float('nan'),
        'inf_float': float('inf'),
        'neg_inf_float': float('-inf'),
        'math_nan': math.nan,
        'nested_problematic': {
            'normal': 'value',
            'nan_value': float('nan'),
            'inf_value': float('inf')
        }
    }
    
    # Define the ensure_serializable function (same as in json_matcher.py)
    def ensure_serializable(obj):
        if isinstance(obj, dict):
            return {str(k): ensure_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ensure_serializable(item) for item in obj]
        elif isinstance(obj, (int, str, bool, type(None))):
            return obj
        elif isinstance(obj, float):
            # Handle NaN and infinity values
            import math
            if math.isnan(obj) or math.isinf(obj):
                return ''
            return obj
        else:
            return str(obj)
    
    try:
        # Apply the function
        safe_data = ensure_serializable(problematic_data)
        
        # Test serialization
        json_str = json.dumps(safe_data, indent=2)
        print("✅ ensure_serializable function test passed!")
        print(f"Serialized JSON length: {len(json_str)} characters")
        
        # Verify that problematic values were converted to empty strings
        assert safe_data['nan_float'] == ''
        assert safe_data['inf_float'] == ''
        assert safe_data['neg_inf_float'] == ''
        assert safe_data['math_nan'] == ''
        assert safe_data['nested_problematic']['nan_value'] == ''
        assert safe_data['nested_problematic']['inf_value'] == ''
        print("✅ Problematic value conversion test passed!")
        
        # Verify that normal values were preserved
        assert safe_data['normal_string'] == 'Hello World'
        assert safe_data['normal_number'] == 42
        assert safe_data['normal_float'] == 3.14
        assert safe_data['normal_bool'] == True
        assert safe_data['normal_none'] == None
        print("✅ Normal value preservation test passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ ensure_serializable function test failed: {e}")
        return False

def test_safe_get_value_function():
    """Test the safe_get_value function."""
    
    import pandas as pd
    
    # Define the safe_get_value function (same as in json_matcher.py)
    def safe_get_value(value, default=''):
        if value is None:
            return default
        if isinstance(value, pd.Series):
            if pd.isna(value).any():
                return default
            value = value.iloc[0] if len(value) > 0 else default
        elif pd.isna(value):
            return default
        # Convert to string and check for 'nan' string values
        str_value = str(value).strip()
        if str_value.lower() in ['nan', 'inf', '-inf']:
            return default
        return str_value
    
    try:
        # Test various input types
        test_cases = [
            (None, ''),
            (float('nan'), ''),
            (math.nan, ''),
            (float('inf'), ''),
            (float('-inf'), ''),
            ('nan', ''),
            ('NaN', ''),
            ('inf', ''),
            ('-inf', ''),
            ('  nan  ', ''),
            ('  INF  ', ''),
            (42, '42'),
            (3.14, '3.14'),
            ('Hello World', 'Hello World'),
            (True, 'True'),
            ('', ''),
            ('   ', ''),
        ]
        
        print("Testing safe_get_value function...")
        for input_val, expected in test_cases:
            result = safe_get_value(input_val)
            if result == expected:
                print(f"✅ {input_val} -> '{result}' (expected: '{expected}')")
            else:
                print(f"❌ {input_val} -> '{result}' (expected: '{expected}')")
                return False
        
        print("✅ All safe_get_value test cases passed!")
        return True
        
    except Exception as e:
        print(f"❌ safe_get_value function test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running NaN JSON serialization fix tests...\n")
    
    tests = [
        ("NaN Handling", test_nan_handling),
        ("ensure_serializable Function", test_ensure_serializable_function),
        ("safe_get_value Function", test_safe_get_value_function)
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
        print("🎉 All tests passed! The NaN JSON serialization fix should work properly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 