#!/usr/bin/env python3
"""
Find Virtual Environment on PythonAnywhere
"""

import os
import sys
import subprocess
from pathlib import Path

def find_virtual_environment():
    """Find the virtual environment more comprehensively."""
    print("🔍 Searching for virtual environment...")
    
    # Check if we're currently in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"✅ Currently in virtual environment: {sys.prefix}")
        return sys.prefix
    
    # Common virtual environment names and locations
    search_paths = [
        # Current directory and subdirectories
        Path.cwd(),
        Path.cwd() / 'venv_pythonanywhere',
        Path.cwd() / 'venv',
        Path.cwd() / '.venv',
        Path.cwd() / 'env',
        
        # Home directory
        Path.home(),
        Path.home() / 'venv_pythonanywhere',
        Path.home() / 'venv',
        Path.home() / '.venv',
        Path.home() / 'env',
        
        # Project-specific paths
        Path.home() / 'AGTDesigner' / 'venv_pythonanywhere',
        Path.home() / 'AGTDesigner' / 'venv',
        Path.home() / 'AGTDesigner' / '.venv',
        Path.home() / 'AGTDesigner' / 'env',
    ]
    
    for path in search_paths:
        if path.exists():
            # Check for site-packages directory
            site_packages = path / 'lib' / 'python3.11' / 'site-packages'
            if site_packages.exists():
                print(f"✅ Found virtual environment: {path}")
                return str(path)
            
            # Check for Scripts/activate_this.py (Windows-style)
            activate_script_win = path / 'Scripts' / 'activate_this.py'
            if activate_script_win.exists():
                print(f"✅ Found virtual environment: {path}")
                return str(path)
    
    # Try to find by checking which python is being used
    try:
        result = subprocess.run(['which', 'python'], capture_output=True, text=True)
        if result.returncode == 0:
            python_path = result.stdout.strip()
            print(f"🔍 Python path: {python_path}")
            
            # Extract virtual environment path from python path
            if 'venv' in python_path or 'env' in python_path:
                venv_path = Path(python_path).parent.parent
                if (venv_path / 'lib' / 'python3.11' / 'site-packages').exists():
                    print(f"✅ Found virtual environment from Python path: {venv_path}")
                    return str(venv_path)
    except Exception as e:
        print(f"⚠️  Could not determine Python path: {e}")
    
    print("❌ No virtual environment found")
    return None

def check_current_venv():
    """Check current virtual environment status."""
    print("\n🔍 Current Environment Status:")
    print(f"   Python executable: {sys.executable}")
    print(f"   Python version: {sys.version}")
    print(f"   sys.prefix: {sys.prefix}")
    print(f"   sys.base_prefix: {sys.base_prefix}")
    
    if hasattr(sys, 'real_prefix'):
        print(f"   sys.real_prefix: {sys.real_prefix}")
        print("   ✅ Virtual environment is active")
        return True
    elif hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        print("   ✅ Virtual environment is active")
        return True
    else:
        print("   ❌ No virtual environment active")
        return False

def main():
    """Main function."""
    print("🚀 Virtual Environment Detection")
    print("=" * 40)
    
    # Check current environment
    is_venv_active = check_current_venv()
    
    # Find virtual environment
    venv_path = find_virtual_environment()
    
    print(f"\n📋 Results:")
    if venv_path:
        print(f"   Virtual environment found: {venv_path}")
        print(f"   Activate script: {Path(venv_path) / 'bin' / 'activate_this.py'}")
    else:
        print("   No virtual environment found")
    
    if is_venv_active:
        print("   ✅ Virtual environment is currently active")
    else:
        print("   ❌ Virtual environment is not active")
    
    # Provide recommendations
    print(f"\n💡 Recommendations:")
    if venv_path and not is_venv_active:
        print(f"   Activate your virtual environment:")
        print(f"   source {venv_path}/bin/activate")
    elif venv_path and is_venv_active:
        print(f"   ✅ Virtual environment is ready for WSGI configuration")
    else:
        print(f"   Consider creating a virtual environment:")
        print(f"   python3.11 -m venv venv_pythonanywhere")

if __name__ == "__main__":
    main() 