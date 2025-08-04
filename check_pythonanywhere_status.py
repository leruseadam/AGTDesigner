#!/usr/bin/env python3
"""
Python Anywhere Status Check Script
This script helps diagnose deployment issues on Python Anywhere.
"""

import requests
import sys
import os

def check_website_status():
    """Check the status of the website"""
    print("🔍 Checking website status...")
    
    try:
        # Check main domain
        response = requests.get('https://www.agtpricetags.com/', timeout=10)
        print(f"✅ Main domain status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Website is working!")
            return True
        else:
            print(f"❌ Website returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def check_wsgi_file():
    """Check if WSGI file exists and is valid"""
    print("\n🔍 Checking WSGI file...")
    
    wsgi_files = [
        'wsgi.py',
        'wsgi_pythonanywhere.py',
        'pythonanywhere_wsgi.py'
    ]
    
    for wsgi_file in wsgi_files:
        if os.path.exists(wsgi_file):
            print(f"✅ Found WSGI file: {wsgi_file}")
            try:
                with open(wsgi_file, 'r') as f:
                    content = f.read()
                    if 'application' in content:
                        print(f"✅ {wsgi_file} contains 'application' variable")
                    else:
                        print(f"⚠️  {wsgi_file} missing 'application' variable")
            except Exception as e:
                print(f"❌ Error reading {wsgi_file}: {e}")
        else:
            print(f"❌ WSGI file not found: {wsgi_file}")

def check_app_file():
    """Check if app.py exists and can be imported"""
    print("\n🔍 Checking app.py...")
    
    if os.path.exists('app.py'):
        print("✅ app.py exists")
        try:
            # Try to import the app
            sys.path.insert(0, os.getcwd())
            from app import create_app
            app = create_app()
            print("✅ app.py imports successfully")
            return True
        except Exception as e:
            print(f"❌ Error importing app.py: {e}")
            return False
    else:
        print("❌ app.py not found")
        return False

def main():
    print("🚀 Python Anywhere Status Check")
    print("=" * 40)
    
    # Check website status
    website_ok = check_website_status()
    
    # Check local files
    check_wsgi_file()
    app_ok = check_app_file()
    
    print("\n📋 Summary:")
    print(f"Website accessible: {'✅ Yes' if website_ok else '❌ No'}")
    print(f"App.py valid: {'✅ Yes' if app_ok else '❌ No'}")
    
    if not website_ok:
        print("\n🔧 Recommended Actions:")
        print("1. Log into Python Anywhere dashboard")
        print("2. Go to 'Web' tab")
        print("3. Find your web app (agtpricetags.com)")
        print("4. Click 'Reload' or 'Restart'")
        print("5. Check error logs for specific issues")
        print("\nIf the issue persists:")
        print("- Verify WSGI file points to correct application")
        print("- Check Python Anywhere web app configuration")
        print("- Ensure all dependencies are installed")

if __name__ == "__main__":
    main() 