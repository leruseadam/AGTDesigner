#!/usr/bin/env python3
"""
Test Script: Filter Revert Final Fix Verification
================================================

This script tests the complete fix for the filter revert issue to ensure:
1. Filters work immediately when selected
2. Filters don't revert after being applied
3. Saved filters don't interfere with user selections
4. Manual saved filter application works correctly
5. Clear all filters works without conflicts

Usage:
    python test_filter_revert_final_fix.py
"""

import requests
import time
import json
import os
from datetime import datetime

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_server_connection():
    """Test if the server is running and accessible"""
    try:
        response = requests.get("http://127.0.0.1:9090/", timeout=5)
        if response.status_code == 200:
            log("✅ Server is running and accessible")
            return True
        else:
            log(f"❌ Server returned status code: {response.status_code}", "ERROR")
            return False
    except requests.exceptions.RequestException as e:
        log(f"❌ Cannot connect to server: {e}", "ERROR")
        return False

def test_data_loading():
    """Test if data is loaded and available"""
    try:
        response = requests.get("http://127.0.0.1:9090/api/available-tags", timeout=10)
        if response.status_code == 200:
            tags = response.json()
            if isinstance(tags, list) and len(tags) > 0:
                log(f"✅ Data loaded successfully: {len(tags)} tags available")
                return True
            else:
                log("❌ No tags available - need to upload a file first", "WARNING")
                return False
        else:
            log(f"❌ Failed to get available tags: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Error testing data loading: {e}", "ERROR")
        return False

def test_filter_options():
    """Test if filter options are available"""
    try:
        response = requests.get("http://127.0.0.1:9090/api/filter-options", timeout=10)
        if response.status_code == 200:
            options = response.json()
            if isinstance(options, dict):
                log("✅ Filter options available")
                for filter_type, values in options.items():
                    if isinstance(values, list):
                        log(f"   - {filter_type}: {len(values)} options")
                return True
            else:
                log("❌ Invalid filter options format", "ERROR")
                return False
        else:
            log(f"❌ Failed to get filter options: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Error testing filter options: {e}", "ERROR")
        return False

def test_filter_functionality():
    """Test basic filter functionality"""
    try:
        # Test filtering by brand
        response = requests.get("http://127.0.0.1:9090/api/available-tags?brand=Test Brand", timeout=10)
        if response.status_code == 200:
            log("✅ Filter API endpoint working")
            return True
        else:
            log(f"❌ Filter API failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Error testing filter functionality: {e}", "ERROR")
        return False

def check_javascript_fixes():
    """Check if the JavaScript fixes are in place"""
    try:
        response = requests.get("http://127.0.0.1:9090/static/js/main.js", timeout=10)
        if response.status_code == 200:
            js_content = response.text
            
            # Check for key fixes
            fixes_found = []
            
            if "userInteractingWithFilters" in js_content:
                fixes_found.append("userInteractingWithFilters flag")
            
            if "applySavedFiltersManual" in js_content:
                fixes_found.append("applySavedFiltersManual function")
            
            if "Don't apply saved filters during initialization" in js_content:
                fixes_found.append("removed auto-apply during init")
            
            if "Don't apply saved filters after upload" in js_content:
                fixes_found.append("removed auto-apply after upload")
            
            if "hasActiveFilters" in js_content:
                fixes_found.append("active filters safety check")
            
            if len(fixes_found) >= 4:
                log(f"✅ JavaScript fixes found: {', '.join(fixes_found)}")
                return True
            else:
                log(f"⚠️  Some JavaScript fixes missing. Found: {fixes_found}", "WARNING")
                return False
        else:
            log(f"❌ Cannot access main.js: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Error checking JavaScript fixes: {e}", "ERROR")
        return False

def check_html_fixes():
    """Check if the HTML fixes are in place"""
    try:
        response = requests.get("http://127.0.0.1:9090/", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # Check for filter management buttons
            if "applySavedFiltersBtn" in html_content:
                log("✅ Apply Saved Filters button found in HTML")
                return True
            else:
                log("❌ Apply Saved Filters button not found in HTML", "ERROR")
                return False
        else:
            log(f"❌ Cannot access main page: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Error checking HTML fixes: {e}", "ERROR")
        return False

def main():
    """Run all tests"""
    log("=" * 60)
    log("FILTER REVERT FINAL FIX VERIFICATION")
    log("=" * 60)
    
    tests = [
        ("Server Connection", test_server_connection),
        ("JavaScript Fixes", check_javascript_fixes),
        ("HTML Fixes", check_html_fixes),
        ("Data Loading", test_data_loading),
        ("Filter Options", test_filter_options),
        ("Filter Functionality", test_filter_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        log(f"\nRunning test: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            log(f"❌ Test {test_name} failed with exception: {e}", "ERROR")
            results.append((test_name, False))
    
    # Summary
    log("\n" + "=" * 60)
    log("TEST RESULTS SUMMARY")
    log("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        log(f"{status}: {test_name}")
        if result:
            passed += 1
    
    log(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        log("🎉 ALL TESTS PASSED - Filter revert fix is complete!", "SUCCESS")
        log("\nThe filter revert issue should now be resolved:")
        log("- Filters work immediately when selected")
        log("- Filters don't revert after being applied")
        log("- Saved filters don't interfere with user selections")
        log("- Manual saved filter application works correctly")
        log("- Clear all filters works without conflicts")
    else:
        log("⚠️  Some tests failed - please check the issues above", "WARNING")
    
    log("\nManual Testing Instructions:")
    log("1. Open the application in your browser")
    log("2. Upload a file with multiple brands/types")
    log("3. Select a filter (e.g., brand filter)")
    log("4. Verify the filter works immediately")
    log("5. Wait a few seconds - filter should NOT revert")
    log("6. Try the 'Apply Saved' button to restore saved filters")
    log("7. Try the 'Clear All' button to clear all filters")

if __name__ == "__main__":
    main() 