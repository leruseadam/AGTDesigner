#!/usr/bin/env python3
"""
Fix script for PythonAnywhere missing requests module
Run this on PythonAnywhere to install the missing requests module
"""

import subprocess
import sys
import os

def check_requests_module():
    """Check if requests module is available"""
    try:
        import requests
        print("✅ requests module is available")
        print(f"   Version: {requests.__version__}")
        return True
    except ImportError:
        print("❌ requests module is missing")
        return False

def install_requests_module():
    """Install the requests module"""
    print("🔧 Installing requests module...")
    
    try:
        # Try to install requests using pip
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 'requests'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ requests module installed successfully")
            print("Output:", result.stdout)
            return True
        else:
            print("❌ Failed to install requests module")
            print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error installing requests module: {e}")
        return False

def check_pythonanywhere_environment():
    """Check PythonAnywhere environment"""
    print("🔍 Checking PythonAnywhere environment...")
    
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment")

def main():
    """Main function to fix requests module"""
    print("🚀 PythonAnywhere Requests Module Fix")
    print("=" * 50)
    
    # Check environment
    check_pythonanywhere_environment()
    print()
    
    # Check if requests is already available
    if check_requests_module():
        print("✅ No fix needed - requests module is already available")
        return True
    
    print()
    
    # Install requests module
    if install_requests_module():
        print()
        # Verify installation
        if check_requests_module():
            print("🎉 Successfully fixed requests module!")
            return True
        else:
            print("❌ Installation completed but module still not available")
            return False
    else:
        print("❌ Failed to install requests module")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 Alternative solutions:")
        print("1. Try installing in user space: pip install --user requests")
        print("2. Check if you're in the correct virtual environment")
        print("3. Contact PythonAnywhere support if the issue persists")
    sys.exit(0 if success else 1) 