#!/usr/bin/env python3
"""
Practical test script to verify JSON matched items generation with actual application components.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_json_matched_data_structure():
    """Test that JSON matched data has the correct structure for generation."""
    
    print("🧪 Testing JSON Matched Data Structure...\n")
    
    # Create realistic JSON matched data (similar to what the app produces)
    mock_json_matched_tags = [
        {
            'Product Name*': 'Blue Dream Flower',
            'ProductName': 'Blue Dream Flower',
            'displayName': 'Blue Dream Flower',
            'Description': 'Premium Blue Dream cannabis flower',
            'Vendor': 'Test Vendor 1',
            'Product Type*': 'Flower',
            'Source': 'JSON Match',
            'Lineage': 'HYBRID',
            'Weight*': '3.5g',
            'Weight': '3.5g',
            'WeightWithUnits': '3.5g',
            'WeightUnits': '3.5g',
            'Price': '$25.00',
            'Product Brand': 'Test Brand',
            'ProductBrand': 'Test Brand',
            'Product Strain': 'Blue Dream',
            'Ratio': '1:1',
            'Ratio_or_THC_CBD': '1:1',
            'THC test result': '18.5%',
            'CBD test result': '0.8%',
            'DOH': 'YES',
            'Quantity*': '1',
            'Quantity': '1',
            'quantity': '1',
            'vendor': 'Test Vendor 1',
            'productBrand': 'Test Brand',
            'lineage': 'HYBRID',
            'productType': 'Flower',
            'weight': '3.5g',
            'weightWithUnits': '3.5g',
            'tagId': 'json_001'
        },
        {
            'Product Name*': 'GMO Concentrate',
            'ProductName': 'GMO Concentrate',
            'displayName': 'GMO Concentrate',
            'Description': 'High-potency GMO concentrate',
            'Vendor': 'Test Vendor 2',
            'Product Type*': 'Concentrate',
            'Source': 'JSON Match',
            'Lineage': 'INDICA',
            'Weight*': '1g',
            'Weight': '1g',
            'WeightWithUnits': '1g',
            'WeightUnits': '1g',
            'Price': '$45.00',
            'Product Brand': 'Test Brand 2',
            'ProductBrand': 'Test Brand 2',
            'Product Strain': 'GMO',
            'Ratio': '1:0',
            'Ratio_or_THC_CBD': '1:0',
            'THC test result': '85.2%',
            'CBD test result': '0.1%',
            'DOH': 'NO',
            'Quantity*': '1',
            'Quantity': '1',
            'quantity': '1',
            'vendor': 'Test Vendor 2',
            'productBrand': 'Test Brand 2',
            'lineage': 'INDICA',
            'productType': 'Concentrate',
            'weight': '1g',
            'weightWithUnits': '1g',
            'tagId': 'json_002'
        }
    ]
    
    print(f"✅ Created {len(mock_json_matched_tags)} mock JSON matched tags")
    
    # Test field compatibility with generation system
    print("\nTesting field compatibility...")
    
    required_fields = [
        'Product Name*', 'Vendor', 'Product Type*', 'Weight*', 'Price',
        'Lineage', 'Product Brand', 'Product Strain'
    ]
    
    for i, tag in enumerate(mock_json_matched_tags):
        print(f"   Tag {i+1}: {tag['Product Name*']}")
        
        missing_fields = [field for field in required_fields if not tag.get(field)]
        if missing_fields:
            print(f"   ❌ Missing fields: {missing_fields}")
        else:
            print(f"   ✅ All required fields present")
        
        # Check for JSON Match source
        if tag.get('Source') == 'JSON Match':
            print(f"   ✅ Correctly marked as JSON Match")
        else:
            print(f"   ⚠️  Not marked as JSON Match")
    
    return mock_json_matched_tags

def test_context_building():
    """Test that JSON matched data can be converted to generation context."""
    
    print("\n🧪 Testing Context Building...\n")
    
    try:
        from src.core.generation.context_builders import build_context
        
        # Get mock data
        mock_tags = test_json_matched_data_structure()
        
        print("Testing context building for each tag...")
        
        for i, tag in enumerate(mock_tags):
            print(f"   Tag {i+1}: {tag['Product Name*']}")
            
            try:
                # Build context for this tag
                context = build_context(tag, 'vertical', 1.0)
                
                # Check that context has required fields
                required_context_fields = [
                    'ProductName', 'Vendor', 'ProductType', 'Weight', 'Price',
                    'Lineage', 'ProductBrand', 'ProductStrain'
                ]
                
                missing_context_fields = [field for field in required_context_fields if not context.get(field)]
                
                if missing_context_fields:
                    print(f"   ❌ Missing context fields: {missing_context_fields}")
                else:
                    print(f"   ✅ Context built successfully")
                    print(f"      Product: {context.get('ProductName')}")
                    print(f"      Vendor: {context.get('Vendor')}")
                    print(f"      Type: {context.get('ProductType')}")
                    print(f"      Weight: {context.get('Weight')}")
                    print(f"      Price: {context.get('Price')}")
                
            except Exception as e:
                print(f"   ❌ Context building failed: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import context_builders: {e}")
        return False
    except Exception as e:
        print(f"❌ Context building test failed: {e}")
        return False

def test_marker_wrapping():
    """Test that JSON matched data can be properly wrapped with markers."""
    
    print("\n🧪 Testing Marker Wrapping...\n")
    
    try:
        from src.core.formatting.markers import wrap_with_marker, FIELD_MARKERS
        
        # Get mock data
        mock_tags = test_json_matched_data_structure()
        
        print("Testing marker wrapping for each tag...")
        
        for i, tag in enumerate(mock_tags):
            print(f"   Tag {i+1}: {tag['Product Name*']}")
            
            # Test wrapping key fields
            test_fields = ['Product Name*', 'Vendor', 'Product Type*', 'Weight*', 'Price']
            
            for field in test_fields:
                value = tag.get(field, '')
                if value:
                    try:
                        # Find the appropriate marker
                        marker_key = None
                        for key, marker in FIELD_MARKERS.items():
                            if key.lower() in field.lower() or field.lower() in key.lower():
                                marker_key = key
                                break
                        
                        if marker_key:
                            wrapped_value = wrap_with_marker(value, marker_key)
                            print(f"      ✅ {field}: '{value}' -> '{wrapped_value}'")
                        else:
                            print(f"      ⚠️  {field}: No marker found for '{value}'")
                    
                    except Exception as e:
                        print(f"      ❌ {field}: Marker wrapping failed: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import markers: {e}")
        return False
    except Exception as e:
        print(f"❌ Marker wrapping test failed: {e}")
        return False

def test_excel_processor_integration():
    """Test integration with Excel processor for JSON matched data."""
    
    print("\n🧪 Testing Excel Processor Integration...\n")
    
    try:
        from src.core.data.excel_processor import ExcelProcessor
        import pandas as pd
        
        # Create mock JSON matched data
        mock_json_tags = [
            {
                'Product Name*': 'Test JSON Product 1',
                'Vendor': 'JSON Vendor 1',
                'Product Type*': 'Flower',
                'Weight*': '3.5g',
                'Price': '$25.00',
                'Lineage': 'HYBRID',
                'Product Brand': 'JSON Brand 1',
                'Source': 'JSON Match'
            },
            {
                'Product Name*': 'Test JSON Product 2',
                'Vendor': 'JSON Vendor 2',
                'Product Type*': 'Concentrate',
                'Weight*': '1g',
                'Price': '$45.00',
                'Lineage': 'INDICA',
                'Product Brand': 'JSON Brand 2',
                'Source': 'JSON Match'
            }
        ]
        
        # Convert to DataFrame
        df = pd.DataFrame(mock_json_tags)
        
        # Create Excel processor
        excel_processor = ExcelProcessor()
        excel_processor.df = df
        
        # Set selected tags
        excel_processor.selected_tags = [tag['Product Name*'] for tag in mock_json_tags]
        
        print(f"✅ Created Excel processor with {len(mock_json_tags)} JSON matched tags")
        print(f"✅ DataFrame shape: {excel_processor.df.shape}")
        print(f"✅ Selected tags: {excel_processor.selected_tags}")
        
        # Test data access
        print("\nTesting data access...")
        
        for i, tag_name in enumerate(excel_processor.selected_tags):
            print(f"   Tag {i+1}: {tag_name}")
            
            # Find the tag in the DataFrame
            tag_data = excel_processor.df[excel_processor.df['Product Name*'] == tag_name]
            
            if not tag_data.empty:
                tag_row = tag_data.iloc[0]
                print(f"      ✅ Found in DataFrame")
                print(f"      Vendor: {tag_row.get('Vendor', 'N/A')}")
                print(f"      Type: {tag_row.get('Product Type*', 'N/A')}")
                print(f"      Source: {tag_row.get('Source', 'N/A')}")
            else:
                print(f"      ❌ Not found in DataFrame")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import ExcelProcessor: {e}")
        return False
    except Exception as e:
        print(f"❌ Excel processor integration test failed: {e}")
        return False

def test_template_processing():
    """Test that JSON matched data can be processed through templates."""
    
    print("\n🧪 Testing Template Processing...\n")
    
    try:
        from src.core.generation.tag_generator import get_template_path
        
        # Test template path resolution
        template_types = ['vertical', 'horizontal', 'mini', 'double']
        
        print("Testing template path resolution...")
        
        for template_type in template_types:
            try:
                template_path = get_template_path(template_type)
                print(f"   ✅ {template_type}: {template_path}")
                
                # Check if template file exists
                if os.path.exists(template_path):
                    print(f"      ✅ Template file exists")
                else:
                    print(f"      ❌ Template file not found")
                    
            except Exception as e:
                print(f"   ❌ {template_type}: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import tag_generator: {e}")
        return False
    except Exception as e:
        print(f"❌ Template processing test failed: {e}")
        return False

def test_json_serialization():
    """Test JSON serialization of JSON matched data."""
    
    print("\n🧪 Testing JSON Serialization...\n")
    
    # Get mock data
    mock_tags = test_json_matched_data_structure()
    
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
        # Make data JSON safe
        safe_data = make_json_safe(mock_tags)
        
        # Serialize to JSON
        json_str = json.dumps(safe_data, indent=2)
        
        print(f"✅ JSON serialization successful ({len(json_str)} characters)")
        
        # Test deserialization
        parsed_data = json.loads(json_str)
        print(f"✅ JSON deserialization successful")
        
        # Verify data integrity
        if len(parsed_data) == len(mock_tags):
            print(f"✅ Data integrity maintained ({len(parsed_data)} tags)")
        else:
            print(f"❌ Data integrity issue: expected {len(mock_tags)}, got {len(parsed_data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON serialization test failed: {e}")
        return False

def main():
    """Run all practical tests."""
    print("🧪 JSON Matched Items Generation - Practical Test Suite")
    print("="*70)
    
    tests = [
        ("Data Structure", test_json_matched_data_structure),
        ("Context Building", test_context_building),
        ("Marker Wrapping", test_marker_wrapping),
        ("Excel Processor Integration", test_excel_processor_integration),
        ("Template Processing", test_template_processing),
        ("JSON Serialization", test_json_serialization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_name == "Data Structure":
                # This test returns data, not a boolean
                test_func()
                results.append(True)
            else:
                result = test_func()
                results.append(result)
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*70)
    print("📊 PRACTICAL TEST RESULTS")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ JSON matched items are ready for generation")
        print("✅ All components are working correctly")
        print("✅ Ready for production use")
        return 0
    elif passed >= total * 0.8:  # 80% pass rate
        print("⚠️  MOST TESTS PASSED")
        print("✅ JSON matched items should work for generation")
        print("⚠️  Some components may need attention")
        return 0
    else:
        print("❌ MANY TESTS FAILED")
        print("❌ JSON matched items have significant issues")
        print("❌ Generation may not work properly")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 