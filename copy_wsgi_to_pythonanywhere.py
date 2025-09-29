#!/usr/bin/env python3
"""
Copy Fixed WSGI File to PythonAnywhere Location
Copies the corrected WSGI file to the PythonAnywhere web app location
"""

import os
import shutil

def copy_wsgi_file():
    """Copy the fixed WSGI file to PythonAnywhere location"""
    
    print("🔧 Copying Fixed WSGI File to PythonAnywhere...")
    print("=" * 50)
    
    # Source WSGI file (our corrected one)
    source_wsgi = "/home/adamcordova/AGTDesigner/wsgi_pythonanywhere_python311.py"
    
    # Target WSGI file (the one PythonAnywhere uses)
    target_wsgi = "/var/www/www_agtpricetags_com_wsgi.py"
    
    print(f"📁 Source WSGI: {source_wsgi}")
    print(f"📁 Target WSGI: {target_wsgi}")
    
    # Check if source file exists
    if not os.path.exists(source_wsgi):
        print(f"❌ Source WSGI file not found: {source_wsgi}")
        return False
    
    # Check if target file exists
    if not os.path.exists(target_wsgi):
        print(f"❌ Target WSGI file not found: {target_wsgi}")
        return False
    
    try:
        # Create backup of target file
        backup_file = target_wsgi + '.backup'
        shutil.copy2(target_wsgi, backup_file)
        print(f"✅ Created backup: {backup_file}")
        
        # Copy our corrected WSGI file to the target location
        shutil.copy2(source_wsgi, target_wsgi)
        print("✅ WSGI file copied successfully!")
        
        # Verify the copy
        with open(target_wsgi, 'r') as f:
            content = f.read()
        
        # Check for key elements
        checks = [
            ('from app import app', 'App import'),
            ('application = app', 'Application assignment'),
            ('adamcordova-4822.postgres.pythonanywhere-services.com', 'PostgreSQL host'),
            ('os.environ[\'DB_HOST\']', 'Database host env var'),
            ('configure_production_logging', 'Production logging')
        ]
        
        print("\n🔍 Verifying copied WSGI file:")
        all_good = True
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ Missing: {description}")
                all_good = False
        
        if all_good:
            print("\n🎉 WSGI file copied and verified successfully!")
            return True
        else:
            print("\n⚠️ Some elements are missing from copied WSGI file")
            return False
        
    except PermissionError:
        print(f"❌ Permission denied: Cannot write to {target_wsgi}")
        print("💡 You may need to run this with sudo")
        return False
    except Exception as e:
        print(f"❌ Error copying WSGI file: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Copy Fixed WSGI File to PythonAnywhere")
    print("=" * 45)
    
    # Copy the WSGI file
    success = copy_wsgi_file()
    
    print("\n💡 Next Steps:")
    if success:
        print("🎉 WSGI file copied successfully!")
        print("1. Go to PythonAnywhere Web tab")
        print("2. Click Reload button")
        print("3. Wait 60 seconds")
        print("4. Refresh your web app")
        print("5. Database should now show 15,939 products!")
    else:
        print("⚠️ WSGI file copy failed")
        print("1. Check the error messages above")
        print("2. Try running with sudo if permission denied")
        print("3. Manually copy the file if needed")

if __name__ == "__main__":
    main()
