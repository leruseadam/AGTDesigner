#!/usr/bin/env python3
"""
PythonAnywhere File Upload Fix
Comprehensive fix for file upload issues on PythonAnywhere
"""

import os
import sys
import logging
import shutil
import stat
from pathlib import Path

def fix_pythonanywhere_upload():
    """Fix PythonAnywhere file upload issues."""
    
    print("🔧 Fixing PythonAnywhere File Upload Issues...")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Project directory: {project_dir}")
    
    # Create uploads directory with proper permissions
    uploads_dir = os.path.join(project_dir, 'uploads')
    print(f"Uploads directory: {uploads_dir}")
    
    try:
        # Create uploads directory if it doesn't exist
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir, mode=0o755, exist_ok=True)
            print(f"✅ Created uploads directory: {uploads_dir}")
        else:
            print(f"✅ Uploads directory already exists: {uploads_dir}")
        
        # Set proper permissions on uploads directory
        os.chmod(uploads_dir, 0o755)
        print(f"✅ Set uploads directory permissions to 755")
        
        # Create other necessary directories
        directories = ['output', 'cache', 'logs', 'temp']
        for dir_name in directories:
            dir_path = os.path.join(project_dir, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, mode=0o755, exist_ok=True)
                print(f"✅ Created {dir_name} directory: {dir_path}")
            else:
                os.chmod(dir_path, 0o755)
                print(f"✅ Set {dir_name} directory permissions to 755")
        
        # Test file creation in uploads directory
        test_file = os.path.join(uploads_dir, 'test_upload_permissions.txt')
        try:
            with open(test_file, 'w') as f:
                f.write('Test upload permissions')
            print(f"✅ Successfully created test file: {test_file}")
            
            # Clean up test file
            os.remove(test_file)
            print(f"✅ Successfully removed test file")
            
        except Exception as e:
            print(f"❌ Failed to create test file: {e}")
            return False
        
        # Update app.py configuration
        update_app_config(project_dir)
        
        # Create PythonAnywhere-specific WSGI configuration
        create_pythonanywhere_wsgi(project_dir)
        
        print("✅ PythonAnywhere upload fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during upload fix: {e}")
        return False

def update_app_config(project_dir):
    """Update app.py configuration for PythonAnywhere."""
    
    app_py_path = os.path.join(project_dir, 'app.py')
    
    if not os.path.exists(app_py_path):
        print(f"❌ app.py not found: {app_py_path}")
        return
    
    print("📝 Updating app.py configuration...")
    
    # Read current app.py
    with open(app_py_path, 'r') as f:
        content = f.read()
    
    # Check if PythonAnywhere-specific configuration is already present
    if 'PYTHONANYWHERE_MODE' in content:
        print("✅ PythonAnywhere configuration already present in app.py")
        return
    
    # Add PythonAnywhere-specific configuration
    pythonanywhere_config = '''
# PythonAnywhere-specific configuration
import os
if os.path.exists('/home/adamcordova'):
    # Running on PythonAnywhere
    os.environ['PYTHONANYWHERE_MODE'] = 'True'
    os.environ['UPLOAD_FOLDER'] = '/home/adamcordova/AGTDesigner/uploads'
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = 'False'
'''
    
    # Find the right place to insert the configuration (after imports)
    lines = content.split('\n')
    insert_index = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            insert_index = i + 1
        elif line.strip() and not line.strip().startswith('#'):
            break
    
    # Insert the configuration
    lines.insert(insert_index, pythonanywhere_config)
    
    # Write back to app.py
    with open(app_py_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ Updated app.py with PythonAnywhere configuration")

def create_pythonanywhere_wsgi(project_dir):
    """Create PythonAnywhere-specific WSGI configuration."""
    
    wsgi_content = '''import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Activate virtual environment
activate_this = os.path.join(project_dir, 'venv_pythonanywhere', 'bin', 'activate_this.py')
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

# Set PythonAnywhere environment variables
os.environ['PYTHONANYWHERE_MODE'] = 'True'
os.environ['UPLOAD_FOLDER'] = os.path.join(project_dir, 'uploads')
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
'''
    
    wsgi_path = os.path.join(project_dir, 'wsgi_pythonanywhere.py')
    with open(wsgi_path, 'w') as f:
        f.write(wsgi_content)
    
    print(f"✅ Created PythonAnywhere WSGI configuration: {wsgi_path}")

def create_upload_test_script(project_dir):
    """Create a test script to verify upload functionality."""
    
    test_script = '''#!/usr/bin/env python3
"""
Test script to verify PythonAnywhere upload functionality
"""

import os
import sys

def test_upload_functionality():
    """Test upload directory and permissions."""
    
    print("🧪 Testing PythonAnywhere Upload Functionality...")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Project directory: {project_dir}")
    
    # Test uploads directory
    uploads_dir = os.path.join(project_dir, 'uploads')
    print(f"Uploads directory: {uploads_dir}")
    
    if os.path.exists(uploads_dir):
        print(f"✅ Uploads directory exists")
        
        # Test permissions
        stat_info = os.stat(uploads_dir)
        permissions = oct(stat_info.st_mode)[-3:]
        print(f"✅ Uploads directory permissions: {permissions}")
        
        # Test file creation
        test_file = os.path.join(uploads_dir, 'test_upload.txt')
        try:
            with open(test_file, 'w') as f:
                f.write('Test upload functionality')
            print(f"✅ Successfully created test file")
            
            # Clean up
            os.remove(test_file)
            print(f"✅ Successfully removed test file")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create test file: {e}")
            return False
    else:
        print(f"❌ Uploads directory does not exist")
        return False

if __name__ == "__main__":
    success = test_upload_functionality()
    if success:
        print("🎉 Upload functionality test passed!")
    else:
        print("❌ Upload functionality test failed!")
        sys.exit(1)
'''
    
    test_path = os.path.join(project_dir, 'test_pythonanywhere_upload.py')
    with open(test_path, 'w') as f:
        f.write(test_script)
    
    # Make it executable
    os.chmod(test_path, 0o755)
    
    print(f"✅ Created upload test script: {test_path}")

if __name__ == "__main__":
    # Run the fix
    success = fix_pythonanywhere_upload()
    
    if success:
        # Create test script
        project_dir = os.path.dirname(os.path.abspath(__file__))
        create_upload_test_script(project_dir)
        
        print("\n🎉 PythonAnywhere upload fix completed!")
        print("\n📋 Next steps:")
        print("1. Run: python test_pythonanywhere_upload.py")
        print("2. Update your PythonAnywhere WSGI file to use wsgi_pythonanywhere.py")
        print("3. Reload your web app on PythonAnywhere")
    else:
        print("\n❌ PythonAnywhere upload fix failed!")
        sys.exit(1) 