#!/usr/bin/env python3
"""
Diagnostic script to check PythonAnywhere deployment status
Run this on PythonAnywhere to verify the fixes are deployed
"""

import os
import sys
import subprocess

def check_git_status():
    """Check if the latest changes are deployed"""
    print("=== Git Status Check ===")
    try:
        result = subprocess.run(['git', 'log', '--oneline', '-3'], 
                              capture_output=True, text=True, cwd='/home/adamcordova/AGTDesigner')
        print("Latest commits:")
        print(result.stdout)
        
        # Check if the Flask context fix is in the latest commit
        if 'Flask context errors' in result.stdout:
            print("✅ Flask context fixes are deployed")
        else:
            print("❌ Flask context fixes may not be deployed")
            
    except Exception as e:
        print(f"Error checking git status: {e}")

def check_app_py_fixes():
    """Check if the Flask context fixes are in app.py"""
    print("\n=== App.py Fixes Check ===")
    app_py_path = '/home/adamcordova/AGTDesigner/app.py'
    
    if not os.path.exists(app_py_path):
        print(f"❌ app.py not found at {app_py_path}")
        return
    
    try:
        with open(app_py_path, 'r') as f:
            content = f.read()
        
        # Check for key fixes
        fixes_found = []
        
        if 'has_request_context' in content:
            fixes_found.append("✅ has_request_context check")
        else:
            fixes_found.append("❌ has_request_context check missing")
            
        if 'sid = \'background\'' in content:
            fixes_found.append("✅ background session handling")
        else:
            fixes_found.append("❌ background session handling missing")
            
        if 'Working outside of request context' in content:
            fixes_found.append("❌ Old error handling still present")
        else:
            fixes_found.append("✅ Old error handling removed")
        
        for fix in fixes_found:
            print(fix)
            
    except Exception as e:
        print(f"Error checking app.py: {e}")

def check_web_app_status():
    """Check web app status"""
    print("\n=== Web App Status ===")
    print("Please check the following in your PythonAnywhere dashboard:")
    print("1. Go to the Web tab")
    print("2. Check if your web app is running (green status)")
    print("3. Check the error logs for any issues")
    print("4. Try reloading the web app if needed")

def main():
    print("PythonAnywhere Deployment Diagnostic")
    print("=" * 40)
    
    check_git_status()
    check_app_py_fixes()
    check_web_app_status()
    
    print("\n=== Next Steps ===")
    print("If fixes are not deployed:")
    print("1. Run: cd /home/adamcordova/AGTDesigner")
    print("2. Run: git pull origin main")
    print("3. Go to Web tab and click 'Reload'")
    print("4. Test file upload functionality")

if __name__ == "__main__":
    main() 