#!/usr/bin/env python3
"""
PythonAnywhere Diagnostic Script
Checks directory structure, imports, and configuration
"""

import os
import sys
from datetime import datetime

def run_diagnostics():
    """Run comprehensive diagnostics"""
    
    print("🔍 PythonAnywhere Diagnostic Tool")
    print("=" * 50)
    print(f"⏰ Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 User: {os.environ.get('USER', 'unknown')}")
    print(f"🐍 Python: {sys.version}")
    print()
    
    # Check directory structure
    print("📁 Directory Structure:")
    print("-" * 25)
    
    home_dir = os.path.expanduser("~")
    print(f"Home directory: {home_dir}")
    
    # Look for project directories
    project_dirs = []
    for item in os.listdir(home_dir):
        if any(keyword in item.lower() for keyword in ['agt', 'label', 'designer', 'fresh']):
            full_path = os.path.join(home_dir, item)
            if os.path.isdir(full_path):
                project_dirs.append((item, full_path))
                print(f"  📂 {item} -> {full_path}")
    
    if not project_dirs:
        print("  ❌ No project directories found!")
        return False
    
    # Check AGTDesigner specifically
    agt_path = os.path.join(home_dir, "AGTDesigner")
    if os.path.exists(agt_path):
        print(f"  ✅ AGTDesigner found at: {agt_path}")
        current_project = agt_path
    else:
        print("  ⚠️  AGTDesigner not found, using first available project")
        current_project = project_dirs[0][1]
    
    print()
    
    # Check project contents
    print("📄 Project Contents:")
    print("-" * 20)
    
    os.chdir(current_project)
    contents = os.listdir('.')
    
    required_files = ['app.py', 'wsgi.py', 'requirements.txt']
    for file in required_files:
        if file in contents:
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (missing)")
    
    # Check for WSGI files
    wsgi_files = [f for f in contents if f.startswith('wsgi') and f.endswith('.py')]
    if wsgi_files:
        print(f"  📝 WSGI files found: {', '.join(wsgi_files)}")
    
    print()
    
    # Test Python imports
    print("🐍 Python Import Tests:")
    print("-" * 22)
    
    # Add current directory to path
    if current_project not in sys.path:
        sys.path.insert(0, current_project)
    
    # Test basic imports
    imports_to_test = [
        ('flask', 'Flask'),
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'),
        ('docxtpl', 'docxtpl'),
        ('app', 'Flask app')
    ]
    
    for module, description in imports_to_test:
        try:
            if module == 'app':
                from app import app
                print(f"  ✅ {description}")
            else:
                __import__(module)
                print(f"  ✅ {description}")
        except ImportError as e:
            print(f"  ❌ {description}: {e}")
        except Exception as e:
            print(f"  ⚠️  {description}: {e}")
    
    print()
    
    # Check database
    print("🗃️  Database Check:")
    print("-" * 16)
    
    db_paths = ['product_database.db', 'uploads/product_database.db']
    db_found = False
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path)
            print(f"  ✅ Database found: {db_path} ({db_size:,} bytes)")
            db_found = True
            break
    
    if not db_found:
        print("  ⚠️  Database not found - may need initialization")
    
    print()
    
    # Environment check
    print("⚙️  Environment:")
    print("-" * 13)
    
    env_vars = ['PYTHONANYWHERE_DOMAIN', 'PYTHONANYWHERE_SITE', 'FLASK_ENV']
    for var in env_vars:
        value = os.environ.get(var, 'not set')
        print(f"  {var}: {value}")
    
    print()
    
    # Recommendations
    print("💡 Recommendations:")
    print("-" * 17)
    
    print(f"  🎯 Use WSGI file: {current_project}/wsgi_pythonanywhere_python311.py")
    print(f"  🚀 For speed: {current_project}/wsgi_ultra_optimized.py")
    print(f"  📁 Source directory: {current_project}")
    print(f"  📂 Static files: {current_project}/static/")
    
    return True

if __name__ == "__main__":
    try:
        success = run_diagnostics()
        if success:
            print("\n✅ Diagnostics completed successfully!")
        else:
            print("\n❌ Diagnostics found issues!")
    except Exception as e:
        print(f"\n💥 Diagnostic error: {e}")
        print("Please check your PythonAnywhere setup.")