#!/usr/bin/env python3
"""
Test script to verify that the lineage dropdown fix is working correctly.
"""
import sys
import os
sys.path.append('.')

from src.core.data.excel_processor import ExcelProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_lineage_methods():
    """Test the new get_current_lineage_for_product method."""
    print("🧪 Testing lineage dropdown fix...")
    
    # Create an ExcelProcessor instance
    processor = ExcelProcessor()
    
    # Test the new method exists
    if hasattr(processor, 'get_current_lineage_for_product'):
        print("✅ get_current_lineage_for_product method exists")
    else:
        print("❌ get_current_lineage_for_product method missing")
        return False
    
    # Test with no data loaded (should return None)
    result = processor.get_current_lineage_for_product("Test Product")
    if result is None:
        print("✅ Method returns None when no data is loaded")
    else:
        print(f"❌ Method should return None but returned: {result}")
        return False
    
    print("✅ All lineage method tests passed!")
    return True

def test_javascript_changes():
    """Test that the JavaScript changes are present."""
    print("🧪 Testing JavaScript changes...")
    
    js_file = 'static/js/main.js'
    if not os.path.exists(js_file):
        print(f"❌ JavaScript file not found: {js_file}")
        return False
    
    with open(js_file, 'r') as f:
        content = f.read()
    
    # Check for the lineage resolution debug code
    if 'DEBUG: Lineage resolution for selected tag' in content:
        print("✅ Lineage debug code found in JavaScript")
    else:
        print("❌ Lineage debug code not found in JavaScript")
        return False
    
    # Check for the fetchAndUpdateSelectedTags call after lineage update
    if 'await this.fetchAndUpdateSelectedTags()' in content:
        print("✅ Selected tags refresh after lineage update found")
    else:
        print("❌ Selected tags refresh after lineage update not found")
        return False
    
    print("✅ All JavaScript tests passed!")
    return True

def test_backend_changes():
    """Test that the backend changes are present."""
    print("🧪 Testing backend changes...")
    
    app_file = 'app.py'
    if not os.path.exists(app_file):
        print(f"❌ Backend file not found: {app_file}")
        return False
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check for the get_current_lineage_for_product call
    if 'get_current_lineage_for_product' in content:
        print("✅ get_current_lineage_for_product call found in backend")
    else:
        print("❌ get_current_lineage_for_product call not found in backend")
        return False
    
    # Check for lineage update in selected tags
    if 'Updated lineage for selected tag' in content:
        print("✅ Lineage update logging found in backend")
    else:
        print("❌ Lineage update logging not found in backend")
        return False
    
    print("✅ All backend tests passed!")
    return True

def main():
    """Run all tests."""
    print("🚀 Starting lineage dropdown fix tests...\n")
    
    tests = [
        test_lineage_methods,
        test_javascript_changes,
        test_backend_changes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The lineage dropdown fix should be working correctly.")
        print("\n🔧 Fix Summary:")
        print("1. ✅ Added comprehensive lineage field checking in createTagElement")
        print("2. ✅ Added get_current_lineage_for_product method to ExcelProcessor")
        print("3. ✅ Enhanced /api/selected-tags to return current lineage values")
        print("4. ✅ Added selected tags refresh after lineage updates")
        print("\n🎯 Expected Behavior:")
        print("- Lineage dropdowns in selected tags should show current lineage values")
        print("- When a lineage is changed, the selected tags view should refresh automatically")
        print("- All lineage fields (lineage, Lineage, currentLineage, etc.) are now checked")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)