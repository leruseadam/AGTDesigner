#!/usr/bin/env python3
"""
PythonAnywhere Dependency Installation Script
This script checks and installs all necessary dependencies for the AGT Designer application.
"""

import os
import sys
import subprocess
import importlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Core dependencies required for the application
REQUIRED_PACKAGES = [
    # Flask and web framework
    'flask',
    'flask-cors',
    'flask-caching',
    'werkzeug',
    
    # Data processing
    'pandas',
    'numpy',
    'openpyxl',
    'xlrd',
    
    # File handling
    'python-docx',
    'Pillow',
    
    # Database
    'sqlite3',  # Built-in, but we'll check
    
    # HTTP requests
    'requests',
    
    # Utilities
    'python-dateutil',
    'pytz',
    
    # Optional but recommended
    'psutil',  # For system monitoring
    'chardet',  # For file encoding detection
]

# PythonAnywhere-specific packages
PYTHONANYWHERE_PACKAGES = [
    'requests',
    'psutil',
    'chardet',
]

def check_python_version():
    """Check if Python version is compatible."""
    print("=== Python Version Check ===")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_package_installed(package_name):
    """Check if a package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip."""
    try:
        print(f"Installing {package_name}...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', package_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {package_name} installed successfully")
            return True
        else:
            print(f"❌ Failed to install {package_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing {package_name}: {e}")
        return False

def check_and_install_packages():
    """Check and install required packages."""
    print("\n=== Package Installation Check ===")
    
    missing_packages = []
    installed_packages = []
    
    for package in REQUIRED_PACKAGES:
        if check_package_installed(package):
            print(f"✅ {package} is installed")
            installed_packages.append(package)
        else:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstalling {len(missing_packages)} missing packages...")
        failed_installations = []
        
        for package in missing_packages:
            if not install_package(package):
                failed_installations.append(package)
        
        if failed_installations:
            print(f"\n❌ Failed to install: {', '.join(failed_installations)}")
            return False
        else:
            print("\n✅ All packages installed successfully")
            return True
    else:
        print("\n✅ All required packages are already installed")
        return True

def check_pythonanywhere_specific():
    """Check PythonAnywhere-specific requirements."""
    print("\n=== PythonAnywhere Specific Checks ===")
    
    # Check if we're on PythonAnywhere
    is_pythonanywhere = any([
        'PYTHONANYWHERE_SITE' in os.environ,
        'PYTHONANYWHERE_DOMAIN' in os.environ,
        os.path.exists('/var/log/pythonanywhere'),
        'pythonanywhere.com' in os.environ.get('HTTP_HOST', '')
    ])
    
    if is_pythonanywhere:
        print("✅ Running on PythonAnywhere")
        
        # Check PythonAnywhere-specific packages
        for package in PYTHONANYWHERE_PACKAGES:
            if check_package_installed(package):
                print(f"✅ {package} is installed")
            else:
                print(f"⚠️  {package} is recommended for PythonAnywhere")
                install_package(package)
    else:
        print("ℹ️  Not running on PythonAnywhere")
    
    return True

def check_file_permissions():
    """Check file permissions and accessibility."""
    print("\n=== File Permission Check ===")
    
    # Check if we can write to the current directory
    try:
        test_file = 'test_write_permission.tmp'
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ Write permission to current directory")
    except Exception as e:
        print(f"❌ Write permission issue: {e}")
        return False
    
    # Check uploads directory
    uploads_dir = 'uploads'
    if os.path.exists(uploads_dir):
        try:
            test_file = os.path.join(uploads_dir, 'test_write_permission.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("✅ Write permission to uploads directory")
        except Exception as e:
            print(f"❌ Uploads directory write permission issue: {e}")
            return False
    else:
        print("ℹ️  Uploads directory doesn't exist (will be created when needed)")
    
    return True

def check_database_access():
    """Check database access and permissions."""
    print("\n=== Database Access Check ===")
    
    try:
        import sqlite3
        print("✅ SQLite3 is available")
        
        # Test database creation
        test_db = 'test_db.sqlite'
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)')
        cursor.execute('INSERT INTO test (name) VALUES (?)', ('test',))
        cursor.execute('SELECT * FROM test')
        result = cursor.fetchone()
        conn.close()
        os.remove(test_db)
        
        print("✅ Database read/write access is working")
        return True
    except Exception as e:
        print(f"❌ Database access issue: {e}")
        return False

def check_excel_libraries():
    """Check Excel processing libraries."""
    print("\n=== Excel Library Check ===")
    
    excel_libs = ['openpyxl', 'xlrd', 'pandas']
    for lib in excel_libs:
        if check_package_installed(lib):
            print(f"✅ {lib} is available")
        else:
            print(f"❌ {lib} is missing")
            install_package(lib)
    
    return True

def check_web_framework():
    """Check Flask and web framework components."""
    print("\n=== Web Framework Check ===")
    
    flask_components = ['flask', 'flask_cors', 'flask_caching']
    for component in flask_components:
        if check_package_installed(component):
            print(f"✅ {component} is available")
        else:
            print(f"❌ {component} is missing")
            install_package(component)
    
    return True

def create_requirements_file():
    """Create a requirements.txt file with all necessary dependencies."""
    print("\n=== Creating Requirements File ===")
    
    try:
        # Get installed package versions
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'freeze'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            with open('requirements_pythonanywhere.txt', 'w') as f:
                f.write("# PythonAnywhere Requirements\n")
                f.write("# Generated automatically\n\n")
                f.write(result.stdout)
            
            print("✅ Created requirements_pythonanywhere.txt")
            return True
        else:
            print("❌ Failed to create requirements file")
            return False
    except Exception as e:
        print(f"❌ Error creating requirements file: {e}")
        return False

def main():
    """Run all dependency checks and installations."""
    print("=== PythonAnywhere Dependency Installation ===")
    print("This script will check and install all necessary dependencies.")
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Package Installation", check_and_install_packages),
        ("PythonAnywhere Specific", check_pythonanywhere_specific),
        ("File Permissions", check_file_permissions),
        ("Database Access", check_database_access),
        ("Excel Libraries", check_excel_libraries),
        ("Web Framework", check_web_framework),
        ("Requirements File", create_requirements_file),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            print(f"\n{'='*50}")
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results[check_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("=== INSTALLATION SUMMARY ===")
    print("="*50)
    
    all_passed = True
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All dependencies are properly installed!")
        print("Your PythonAnywhere environment is ready to run the application.")
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")
        print("You may need to manually install some packages or fix permissions.")
    
    print("\n=== NEXT STEPS ===")
    print("1. If all checks passed, your environment is ready")
    print("2. If some checks failed, review the errors and try again")
    print("3. Run the application with: python3 app.py")
    print("4. Or reload your web app in the PythonAnywhere dashboard")

if __name__ == "__main__":
    main() 