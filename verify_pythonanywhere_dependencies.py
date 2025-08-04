#!/usr/bin/env python3
"""
PythonAnywhere Dependency Verification Script
This script checks what dependencies are installed and what might be missing.
"""

import sys
import subprocess
import importlib
import pkg_resources

def check_python_version():
    """Check Python version."""
    print("🐍 Python Version Check")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")
    print()

def check_installed_packages():
    """Check currently installed packages."""
    print("📦 Installed Packages Check")
    try:
        installed_packages = [d for d in pkg_resources.working_set]
        print(f"   Total installed packages: {len(installed_packages)}")
        
        # Show key packages
        key_packages = [
            'flask', 'pandas', 'openpyxl', 'sqlite3', 'requests', 
            'numpy', 'python-docx', 'reportlab', 'pillow'
        ]
        
        for package in key_packages:
            try:
                version = pkg_resources.get_distribution(package).version
                print(f"   ✅ {package}: {version}")
            except pkg_resources.DistributionNotFound:
                print(f"   ❌ {package}: NOT INSTALLED")
        
        print()
    except Exception as e:
        print(f"   ❌ Error checking packages: {e}")
        print()

def check_imports():
    """Test importing key modules."""
    print("🔍 Import Tests")
    
    modules_to_test = [
        ('flask', 'Flask web framework'),
        ('pandas', 'Data manipulation'),
        ('openpyxl', 'Excel file handling'),
        ('sqlite3', 'SQLite database'),
        ('requests', 'HTTP requests'),
        ('numpy', 'Numerical computing'),
        ('docx', 'Word document processing'),
    
        ('PIL', 'Image processing'),
        ('pathlib', 'Path utilities'),
        ('json', 'JSON processing'),
        ('datetime', 'Date/time utilities'),
        ('threading', 'Threading support'),
        ('logging', 'Logging system'),
        ('os', 'Operating system interface'),
        ('sys', 'System-specific parameters'),
        ('time', 'Time-related functions'),
        ('gc', 'Garbage collector'),
        ('tempfile', 'Temporary file utilities'),
        ('glob', 'File pattern matching'),
        ('shutil', 'High-level file operations'),
        ('traceback', 'Print or retrieve stack traces'),
        ('functools', 'Higher-order functions'),
        ('re', 'Regular expressions'),
        ('math', 'Mathematical functions'),
        ('random', 'Random number generation'),
        ('collections', 'Specialized container datatypes'),
        ('typing', 'Support for type hints'),
        ('urllib', 'URL handling modules'),
        ('difflib', 'Helpers for computing deltas'),
        ('psutil', 'System and process utilities'),
    ]
    
    for module_name, description in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"   ✅ {module_name}: {description}")
        except ImportError as e:
            print(f"   ❌ {module_name}: {description} - {e}")
        except Exception as e:
            print(f"   ⚠️  {module_name}: {description} - {e}")
    
    print()

def check_project_specific_imports():
    """Test importing project-specific modules."""
    print("🏗️  Project-Specific Import Tests")
    
    # Add current directory to path
    import os
    sys.path.insert(0, os.getcwd())
    
    project_modules = [
        ('src.core.data.excel_processor', 'Excel processor'),
        ('src.core.data.product_database', 'Product database'),
        ('src.core.data.json_matcher', 'JSON matcher'),
        ('src.core.generation.template_processor', 'Template processor'),
    
        ('src.core.generation.font_sizing', 'Font sizing'),
        ('src.core.utils.common', 'Common utilities'),
        ('src.core.constants', 'Constants'),
    ]
    
    for module_name, description in project_modules:
        try:
            importlib.import_module(module_name)
            print(f"   ✅ {module_name}: {description}")
        except ImportError as e:
            print(f"   ❌ {module_name}: {description} - {e}")
        except Exception as e:
            print(f"   ⚠️  {module_name}: {description} - {e}")
    
    print()

def check_file_permissions():
    """Check file permissions and accessibility."""
    print("📁 File System Check")
    
    import os
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"   Current directory: {current_dir}")
    print(f"   Directory exists: {os.path.exists(current_dir)}")
    print(f"   Directory readable: {os.access(current_dir, os.R_OK)}")
    print(f"   Directory writable: {os.access(current_dir, os.W_OK)}")
    
    # Check key files
    key_files = [
        'app.py',
        'requirements.txt',
        'src/core/data/product_database.py',
        'src/core/data/excel_processor.py'
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}: exists")
            print(f"      Readable: {os.access(file_path, os.R_OK)}")
            print(f"      Writable: {os.access(file_path, os.W_OK)}")
        else:
            print(f"   ❌ {file_path}: NOT FOUND")
    
    print()

def check_database_access():
    """Check database access."""
    print("🗄️  Database Access Check")
    
    try:
        import sqlite3
        import tempfile
        
        # Test creating a temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)')
            cursor.execute('INSERT INTO test (name) VALUES (?)', ('test',))
            cursor.execute('SELECT * FROM test')
            result = cursor.fetchone()
            conn.close()
            
            print(f"   ✅ SQLite database operations: OK")
            print(f"   ✅ Test query result: {result}")
            
        except Exception as e:
            print(f"   ❌ SQLite database operations: {e}")
        finally:
            # Clean up
            try:
                os.unlink(db_path)
            except:
                pass
    
    except Exception as e:
        print(f"   ❌ Database access test failed: {e}")
    
    print()

def check_requirements_file():
    """Check requirements.txt file."""
    print("📋 Requirements File Check")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        print(f"   Requirements file found: {len(requirements)} packages listed")
        
        # Check each requirement
        for req in requirements:
            req = req.strip()
            if req and not req.startswith('#'):
                try:
                    pkg_resources.require(req)
                    print(f"   ✅ {req}")
                except Exception as e:
                    print(f"   ❌ {req}: {e}")
    
    except FileNotFoundError:
        print("   ❌ requirements.txt not found")
    except Exception as e:
        print(f"   ❌ Error reading requirements.txt: {e}")
    
    print()

def check_pythonanywhere_specific():
    """Check PythonAnywhere-specific configurations."""
    print("☁️  PythonAnywhere Environment Check")
    
    # Check if we're on PythonAnywhere
    import os
    is_pythonanywhere = (
        os.path.exists("/home/adamcordova") or 
        "pythonanywhere" in os.getcwd().lower() or
        "pythonanywhere" in os.environ.get('USER', '').lower()
    )
    
    print(f"   Running on PythonAnywhere: {is_pythonanywhere}")
    
    if is_pythonanywhere:
        print(f"   Home directory: {os.path.expanduser('~')}")
        print(f"   Current user: {os.environ.get('USER', 'unknown')}")
        print(f"   PythonAnywhere username: {os.environ.get('USER', 'unknown')}")
        
        # Check PythonAnywhere-specific paths
        pa_paths = [
            '/home/adamcordova',
            '/var/www',
            '/tmp'
        ]
        
        for path in pa_paths:
            if os.path.exists(path):
                print(f"   ✅ {path}: exists")
            else:
                print(f"   ❌ {path}: not found")
    
    print()

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("🐍 PythonAnywhere Dependency Verification")
    print("=" * 60)
    print()
    
    check_python_version()
    check_pythonanywhere_specific()
    check_file_permissions()
    check_requirements_file()
    check_installed_packages()
    check_imports()
    check_project_specific_imports()
    check_database_access()
    
    print("=" * 60)
    print("✅ Verification Complete!")
    print("=" * 60)
    print()
    print("📝 Summary:")
    print("   - Check the output above for any ❌ errors")
    print("   - Install missing packages with: pip install <package_name>")
    print("   - For project-specific issues, check the import paths")
    print("   - For database issues, check file permissions")
    print()

if __name__ == "__main__":
    main() 