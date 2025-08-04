#!/usr/bin/env python3
"""
Find Virtual Environment Location on PythonAnywhere
"""

import os
import sys
import subprocess
from pathlib import Path

def find_venv_location():
    """Find where the virtual environment is located."""
    print("🔍 Searching for virtual environment location...")
    
    # Check if we're currently in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"✅ Currently in virtual environment: {sys.prefix}")
        return sys.prefix
    
    # Check which python is being used
    try:
        result = subprocess.run(['which', 'python'], capture_output=True, text=True)
        if result.returncode == 0:
            python_path = result.stdout.strip()
            print(f"🔍 Python path: {python_path}")
            
            # Extract virtual environment path from python path
            if 'venv' in python_path or 'env' in python_path:
                venv_path = Path(python_path).parent.parent
                print(f"🔍 Extracted virtual environment path: {venv_path}")
                return str(venv_path)
    except Exception as e:
        print(f"⚠️  Could not determine Python path: {e}")
    
    # Search common locations
    search_locations = [
        Path.cwd() / 'venv_pythonanywhere',
        Path.cwd() / 'venv',
        Path.cwd() / '.venv',
        Path.home() / 'AGTDesigner' / 'venv_pythonanywhere',
        Path.home() / 'venv_pythonanywhere',
        Path.home() / 'venv',
        Path.home() / '.venv',
        Path('/var/www/venv_pythonanywhere'),
        Path('/var/www/venv'),
    ]
    
    print("🔍 Searching in common locations:")
    for location in search_locations:
        print(f"   - {location}")
        if location.exists():
            site_packages = location / 'lib' / 'python3.11' / 'site-packages'
            if site_packages.exists():
                print(f"✅ Found virtual environment: {location}")
                return str(location)
    
    print("❌ No virtual environment found in common locations")
    return None

def main():
    """Main function."""
    venv_path = find_venv_location()
    
    if venv_path:
        print(f"\n🎯 Virtual environment found at: {venv_path}")
        print(f"📦 Site-packages: {venv_path}/lib/python3.11/site-packages")
        
        # Check if site-packages exists
        site_packages = Path(venv_path) / 'lib' / 'python3.11' / 'site-packages'
        if site_packages.exists():
            print("✅ Site-packages directory exists")
            
            # List some packages
            packages = list(site_packages.glob('*.dist-info'))
            if packages:
                print("📋 Some installed packages:")
                for pkg in packages[:5]:
                    print(f"   - {pkg.name}")
        else:
            print("❌ Site-packages directory not found")
    else:
        print("\n❌ No virtual environment found")
        print("💡 Try running: python3 -m venv venv_pythonanywhere")

if __name__ == "__main__":
    main() 