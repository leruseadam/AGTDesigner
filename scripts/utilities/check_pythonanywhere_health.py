#!/usr/bin/env python3
"""
PythonAnywhere App Health Check
Run this script on PythonAnywhere to diagnose 502 errors
"""
import os
import sys
import sqlite3

def check_health():
    print("=" * 60)
    print("PythonAnywhere App Health Check")
    print("=" * 60)
    print()
    
    # Base directory
    base_dir = '/home/adamcordova/AGTDesigner'
    
    # 1. Check working directory
    print(f"1. Current directory: {os.getcwd()}")
    print(f"   Expected directory: {base_dir}")
    print(f"   ✅ Match" if os.getcwd() == base_dir else f"   ⚠️  Different")
    print()
    
    # 2. Check if app.py exists
    app_py = os.path.join(base_dir, 'app.py')
    print(f"2. app.py location:")
    print(f"   Path: {app_py}")
    if os.path.exists(app_py):
        size = os.path.getsize(app_py)
        print(f"   ✅ EXISTS (Size: {size:,} bytes)")
    else:
        print(f"   ❌ NOT FOUND")
    print()
    
    # 3. Check database
    print("3. Database check:")
    db_path = os.path.join(base_dir, 'uploads', 'product_database_AGT_Bothell.db')
    print(f"   Path: {db_path}")
    
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"   ✅ EXISTS (Size: {size:,} bytes)")
        
        # Try to connect and count products
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"   Tables: {[t[0] for t in tables]}")
            
            # Count products
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            print(f"   Products count: {count:,}")
            
            # Count strains
            try:
                cursor.execute("SELECT COUNT(*) FROM strains")
                strain_count = cursor.fetchone()[0]
                print(f"   Strains count: {strain_count:,}")
            except:
                print(f"   Strains count: N/A")
            
            conn.close()
        except Exception as e:
            print(f"   ⚠️  Database connection error: {e}")
    else:
        print(f"   ❌ NOT FOUND")
        
        # Check for fallback database
        fallback_db = os.path.join(base_dir, 'uploads', 'product_database.db')
        if os.path.exists(fallback_db):
            print(f"   ℹ️  Fallback database exists: {fallback_db}")
    print()
    
    # 4. Check uploads directory
    print("4. Uploads directory:")
    uploads_dir = os.path.join(base_dir, 'uploads')
    print(f"   Path: {uploads_dir}")
    
    if os.path.exists(uploads_dir):
        files = os.listdir(uploads_dir)
        print(f"   ✅ EXISTS ({len(files)} files)")
        
        db_files = [f for f in files if f.endswith('.db')]
        if db_files:
            print(f"   Database files found:")
            for db_file in db_files:
                db_full_path = os.path.join(uploads_dir, db_file)
                size = os.path.getsize(db_full_path)
                print(f"     - {db_file} ({size:,} bytes)")
        else:
            print(f"   ⚠️  No .db files found")
            
        excel_files = [f for f in files if f.endswith(('.xlsx', '.xls'))]
        if excel_files:
            print(f"   Excel files: {len(excel_files)}")
    else:
        print(f"   ❌ NOT FOUND")
    print()
    
    # 5. Check templates directory
    print("5. Templates directory:")
    templates_dir = os.path.join(base_dir, 'templates')
    print(f"   Path: {templates_dir}")
    
    if os.path.exists(templates_dir):
        files = os.listdir(templates_dir)
        print(f"   ✅ EXISTS ({len(files)} files)")
        html_files = [f for f in files if f.endswith('.html')]
        print(f"   HTML files: {len(html_files)}")
    else:
        print(f"   ❌ NOT FOUND")
    print()
    
    # 6. Check static directory
    print("6. Static directory:")
    static_dir = os.path.join(base_dir, 'static')
    print(f"   Path: {static_dir}")
    
    if os.path.exists(static_dir):
        try:
            subdirs = [d for d in os.listdir(static_dir) if os.path.isdir(os.path.join(static_dir, d))]
            print(f"   ✅ EXISTS")
            print(f"   Subdirectories: {subdirs}")
        except:
            print(f"   ✅ EXISTS")
    else:
        print(f"   ❌ NOT FOUND")
    print()
    
    # 7. Check src directory
    print("7. Source code directory:")
    src_dir = os.path.join(base_dir, 'src')
    print(f"   Path: {src_dir}")
    
    if os.path.exists(src_dir):
        print(f"   ✅ EXISTS")
        # Check core subdirectories
        for subdir in ['core', 'core/data', 'core/generation']:
            subdir_path = os.path.join(src_dir, subdir)
            if os.path.exists(subdir_path):
                print(f"   ✅ {subdir}/ exists")
            else:
                print(f"   ❌ {subdir}/ missing")
    else:
        print(f"   ❌ NOT FOUND")
    print()
    
    # 8. Check Python path
    print("8. Python configuration:")
    print(f"   Python version: {sys.version.split()[0]}")
    print(f"   Python path entries:")
    for i, path in enumerate(sys.path[:5], 1):
        print(f"     {i}. {path}")
    print()
    
    # 9. Test app import
    print("9. Testing Flask app import:")
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
        print(f"   Added {base_dir} to sys.path")
    
    try:
        os.chdir(base_dir)
        print(f"   Changed directory to {base_dir}")
        
        from app import app
        print(f"   ✅ Flask app imported successfully!")
        print(f"   App name: {app.name}")
        
        # Check if app has necessary attributes
        if hasattr(app, 'config'):
            print(f"   ✅ App has config")
        if hasattr(app, 'url_map'):
            route_count = len(list(app.url_map.iter_rules()))
            print(f"   ✅ App has {route_count} routes")
            
    except Exception as e:
        print(f"   ❌ Error importing app:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        print("\n   Traceback:")
        traceback.print_exc()
    print()
    
    # 10. Check permissions
    print("10. File permissions:")
    try:
        # Check if we can write to uploads
        test_file = os.path.join(uploads_dir, '.test_write')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"   ✅ Can write to uploads/ directory")
    except Exception as e:
        print(f"   ⚠️  Cannot write to uploads/: {e}")
    print()
    
    # 11. Environment check
    print("11. Environment variables:")
    pythonanywhere_vars = [
        'PYTHONANYWHERE_SITE',
        'PYTHONANYWHERE_DOMAIN',
        'FLASK_ENV',
        'FLASK_DEBUG'
    ]
    for var in pythonanywhere_vars:
        value = os.environ.get(var, '(not set)')
        print(f"   {var}: {value}")
    print()
    
    print("=" * 60)
    print("Health check complete!")
    print("=" * 60)
    print()
    print("NEXT STEPS:")
    print("1. If any checks show ❌, fix those issues first")
    print("2. If all checks pass ✅, reload your web app")
    print("3. Check error logs at: /var/log/")
    print("4. If still not working, check WSGI configuration")
    print()

if __name__ == "__main__":
    check_health()

