#!/usr/bin/env python3
"""
Debug script to diagnose lineage editor loading issues.
"""

import requests
import time
import json
import sys
import os

def test_server_health():
    """Test if the server is running and responsive."""
    print("🔍 Testing server health...")
    
    try:
        response = requests.get("http://127.0.0.1:9090/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responsive")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False

def test_main_page():
    """Test if the main page loads with lineage editor components."""
    print("\n🔍 Testing main page...")
    
    try:
        response = requests.get("http://127.0.0.1:9090/", timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # Check for lineage editor components
            checks = [
                ('lineageEditorModal', 'Lineage editor modal HTML'),
                ('strainLineageEditorModal', 'Strain lineage editor modal HTML'),
                ('lineage-editor.js', 'Lineage editor JavaScript'),
                ('bootstrap', 'Bootstrap framework'),
                ('jquery', 'jQuery library')
            ]
            
            all_found = True
            for check, description in checks:
                if check in html_content:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
                    all_found = False
            
            return all_found
        else:
            print(f"❌ Main page returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Main page test failed: {e}")
        return False

def test_lineage_api_endpoints():
    """Test lineage API endpoints."""
    print("\n🔍 Testing lineage API endpoints...")
    
    endpoints = [
        ("/api/update-lineage", {
            "tag_name": "Test Product",
            "Product Name*": "Test Product", 
            "lineage": "HYBRID"
        }),
        ("/api/update-strain-lineage", {
            "strain_name": "Test Strain",
            "lineage": "HYBRID"
        })
    ]
    
    all_working = True
    for endpoint, data in endpoints:
        try:
            response = requests.post(f"http://127.0.0.1:9090{endpoint}", 
                                   json=data, timeout=10)
            
            # Accept 200 (success) or 404 (not found) as valid responses
            if response.status_code in [200, 404]:
                print(f"✅ {endpoint} responds properly (status: {response.status_code})")
            else:
                print(f"❌ {endpoint} returned unexpected status: {response.status_code}")
                all_working = False
                
        except requests.exceptions.Timeout:
            print(f"❌ {endpoint} timed out")
            all_working = False
        except Exception as e:
            print(f"❌ {endpoint} failed: {e}")
            all_working = False
    
    return all_working

def check_javascript_files():
    """Check if required JavaScript files exist and are valid."""
    print("\n🔍 Checking JavaScript files...")
    
    js_files = [
        ('static/js/lineage-editor.js', [
            ('class LineageEditor', 'LineageEditor class'),
            ('class StrainLineageEditor', 'StrainLineageEditor class'),
            ('openEditor', 'openEditor method'),
            ('saveChanges', 'saveChanges method'),
            ('init()', 'initialization method')
        ]),
        ('static/js/main.js', [
            ('openEditor', 'openEditor method'),
            ('lineageEditor', 'lineageEditor reference'),
            ('strainLineageEditor', 'strainLineageEditor reference')
        ]),
        ('static/js/tags_table.js', [
            ('openEditor', 'openEditor method'),
            ('lineageEditor', 'lineageEditor reference')
        ])
    ]
    
    all_valid = True
    for js_file, checks in js_files:
        if os.path.exists(js_file):
            try:
                with open(js_file, 'r') as f:
                    content = f.read()
                
                file_valid = True
                for check, description in checks:
                    if check in content:
                        print(f"  ✅ {description} in {js_file}")
                    else:
                        print(f"  ❌ {description} missing in {js_file}")
                        file_valid = False
                
                if file_valid:
                    print(f"✅ {js_file} is valid")
                else:
                    print(f"❌ {js_file} has issues")
                    all_valid = False
                    
            except Exception as e:
                print(f"❌ Error reading {js_file}: {e}")
                all_valid = False
        else:
            print(f"❌ {js_file} not found")
            all_valid = False
    
    return all_valid

def check_html_templates():
    """Check if HTML templates are properly structured."""
    print("\n🔍 Checking HTML templates...")
    
    template_files = [
        'templates/lineage_editor.html',
        'templates/base.html'
    ]
    
    all_valid = True
    for template_file in template_files:
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r') as f:
                    content = f.read()
                
                if template_file == 'templates/lineage_editor.html':
                    checks = [
                        ('lineageEditorModal', 'Lineage editor modal'),
                        ('strainLineageEditorModal', 'Strain lineage editor modal'),
                        ('modal fade', 'Bootstrap modal class'),
                        ('data-bs-dismiss', 'Bootstrap dismiss attribute')
                    ]
                else:
                    checks = [
                        ('lineage_editor.html', 'Lineage editor include'),
                        ('bootstrap', 'Bootstrap CSS/JS'),
                        ('jquery', 'jQuery library')
                    ]
                
                file_valid = True
                for check, description in checks:
                    if check in content:
                        print(f"  ✅ {description} in {template_file}")
                    else:
                        print(f"  ❌ {description} missing in {template_file}")
                        file_valid = False
                
                if file_valid:
                    print(f"✅ {template_file} is valid")
                else:
                    print(f"❌ {template_file} has issues")
                    all_valid = False
                    
            except Exception as e:
                print(f"❌ Error reading {template_file}: {e}")
                all_valid = False
        else:
            print(f"❌ {template_file} not found")
            all_valid = False
    
    return all_valid

def main():
    """Run all diagnostic tests."""
    print("="*60)
    print("LINEAGE EDITOR DIAGNOSTIC TOOL")
    print("="*60)
    
    # Check if server is running first
    if not test_server_health():
        print("\n❌ Server is not running. Please start the server first:")
        print("   python app.py")
        return False
    
    # Run all tests
    tests = [
        ("Main Page", test_main_page),
        ("API Endpoints", test_lineage_api_endpoints),
        ("JavaScript Files", check_javascript_files),
        ("HTML Templates", check_html_templates)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if passed == total:
        print("\n🎉 All tests passed! The lineage editor should be working properly.")
        print("\nIf you're still experiencing issues, try:")
        print("1. Clear your browser cache and refresh the page")
        print("2. Check the browser console for JavaScript errors")
        print("3. Try opening the lineage editor in an incognito/private window")
        return True
    else:
        print("\n❌ Some tests failed. Issues identified:")
        print("1. Check the specific failures above")
        print("2. Ensure all required files are present")
        print("3. Verify the server is running correctly")
        print("4. Check browser console for JavaScript errors")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 