#!/usr/bin/env python3
"""
Simple Requirements Checker for PythonAnywhere
Quick check for essential packages needed by the AGT Designer app.
"""

import sys
import importlib

def check_package(package_name, import_name=None):
    """Check if a package is installed and can be imported."""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name}: {version}")
        return True
    except ImportError:
        print(f"❌ {package_name}: NOT INSTALLED")
        return False
    except Exception as e:
        print(f"⚠️  {package_name}: {e}")
        return False

def main():
    print("🔍 PythonAnywhere Requirements Check")
    print("=" * 50)
    
    # Essential packages for the app
    packages = [
        ('Flask', 'flask'),
        ('Pandas', 'pandas'),
        ('OpenPyXL', 'openpyxl'),
        ('NumPy', 'numpy'),
        ('Requests', 'requests'),
        ('python-docx', 'docx'),
        ('ReportLab', 'reportlab'),
        ('Pillow', 'PIL'),
        ('SQLite3', 'sqlite3'),  # Built-in
    ]
    
    missing_packages = []
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            missing_packages.append(package_name)
    
    print("\n" + "=" * 50)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("\n📦 Install missing packages with:")
        for package in missing_packages:
            if package == 'SQLite3':
                print("   # SQLite3 is built-in, no installation needed")
            else:
                print(f"   pip install {package.lower()}")
    else:
        print("✅ All essential packages are installed!")
    
    print("\n🚀 To install all requirements:")
    print("   pip install -r requirements.txt")
    
    print("\n🌐 Test your app:")
    print("   python app.py")

if __name__ == "__main__":
    main() 