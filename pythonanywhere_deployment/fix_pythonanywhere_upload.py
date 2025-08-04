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
    PYTHONANYWHERE_MODE = os.environ.get('PYTHONANYWHERE', 'false').lower() == 'true'
    
    if PYTHONANYWHERE_MODE:
        # PythonAnywhere-specific settings
        app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
        app.config['UPLOAD_FOLDER'] = os.path.join(project_dir, 'uploads')
        
        # Ensure uploads directory exists with proper permissions
        uploads_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(uploads_dir, mode=0o755, exist_ok=True)
        
        # Set proper permissions
        try:
            os.chmod(uploads_dir, 0o755)
        except Exception as e:
            logging.warning(f"Could not set uploads directory permissions: {e}")
        
        logging.info(f"PythonAnywhere mode enabled. Upload folder: {uploads_dir}")
    else:
        # Standard configuration
        upload_folder = os.path.join(current_dir, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        app.config['UPLOAD_FOLDER'] = upload_folder
'''
    
    # Find the upload folder configuration section
    upload_config_pattern = 'upload_folder = os.path.join(current_dir, \'uploads\')'
    
    if upload_config_pattern in content:
        # Replace the existing configuration
        new_content = content.replace(
            upload_config_pattern,
            pythonanywhere_config
        )
        
        # Write updated content
        with open(app_py_path, 'w') as f:
            f.write(new_content)
        
        print("✅ Updated app.py with PythonAnywhere configuration")
    else:
        print("⚠️  Could not find upload folder configuration in app.py")

def create_pythonanywhere_wsgi(project_dir):
    """Create PythonAnywhere-specific WSGI configuration."""
    
    wsgi_content = '''#!/usr/bin/env python3
"""
WSGI entry point for the Label Maker application.
Optimized for PythonAnywhere deployment with file upload support.
"""

import sys
import os
import logging
from datetime import datetime

# Disable stdout/stderr buffering to prevent BlockingIOError
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Get the current directory (project root)
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Add virtual environment to Python path
venv_path = os.path.join(project_dir, 'venv_pythonanywhere')
venv_site_packages = os.path.join(venv_path, 'lib', 'python3.11', 'site-packages')

if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)
    print(f"✅ Virtual environment site-packages added: {venv_site_packages}")
else:
    print(f"⚠️  Virtual environment site-packages not found at: {venv_site_packages}")
    print("Continuing without virtual environment...")

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE'] = 'true'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Configure basic logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Suppress verbose logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)

# Ensure uploads directory exists with proper permissions
uploads_dir = os.path.join(project_dir, 'uploads')
os.makedirs(uploads_dir, mode=0o755, exist_ok=True)
try:
    os.chmod(uploads_dir, 0o755)
    print(f"✅ Uploads directory configured: {uploads_dir}")
except Exception as e:
    print(f"⚠️  Could not set uploads directory permissions: {e}")

# Import the Flask app
try:
    from app import create_app
    print("✅ Successfully imported Flask app")
except ImportError as e:
    print(f"❌ Error importing Flask app: {e}")
    raise

# Create the application instance
try:
    application = create_app()
    print("✅ Application created successfully")
except Exception as e:
    print(f"❌ Error creating application: {e}")
    raise

# Configure for production
application.config['DEBUG'] = False
application.config['TESTING'] = False
application.config['PROPAGATE_EXCEPTIONS'] = True

# Set production secret key
if not application.secret_key or application.secret_key == 'dev':
    application.secret_key = os.environ.get('SECRET_KEY', 'label-maker-production-key-2024')

print(f"✅ Label Maker application created successfully at {datetime.now()}")

# WSGI application entry point
if __name__ == "__main__":
    application.run()
'''
    
    wsgi_path = os.path.join(project_dir, 'wsgi_pythonanywhere.py')
    
    with open(wsgi_path, 'w') as f:
        f.write(wsgi_content)
    
    # Set executable permissions
    os.chmod(wsgi_path, 0o755)
    
    print(f"✅ Created PythonAnywhere WSGI file: {wsgi_path}")

def create_upload_test_script(project_dir):
    """Create a test script to verify upload functionality."""
    
    test_script = '''#!/usr/bin/env python3
"""
Test script to verify PythonAnywhere upload functionality
"""

import os
import sys
import tempfile
import shutil

def test_upload_functionality():
    """Test upload directory and file creation."""
    
    print("🧪 Testing PythonAnywhere Upload Functionality...")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(project_dir, 'uploads')
    
    print(f"Project directory: {project_dir}")
    print(f"Uploads directory: {uploads_dir}")
    
    # Test 1: Check if uploads directory exists
    if os.path.exists(uploads_dir):
        print("✅ Uploads directory exists")
    else:
        print("❌ Uploads directory does not exist")
        return False
    
    # Test 2: Check permissions
    try:
        stat_info = os.stat(uploads_dir)
        permissions = oct(stat_info.st_mode)[-3:]
        print(f"✅ Uploads directory permissions: {permissions}")
        
        if permissions == '755':
            print("✅ Permissions are correct")
        else:
            print(f"⚠️  Permissions should be 755, got {permissions}")
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
        return False
    
    # Test 3: Test file creation
    try:
        test_file = os.path.join(uploads_dir, 'test_upload.txt')
        with open(test_file, 'w') as f:
            f.write('Test upload functionality')
        
        print("✅ Successfully created test file")
        
        # Clean up
        os.remove(test_file)
        print("✅ Successfully removed test file")
        
    except Exception as e:
        print(f"❌ Error creating test file: {e}")
        return False
    
    # Test 4: Test Flask app import
    try:
        sys.path.insert(0, project_dir)
        from app import create_app
        
        app = create_app()
        upload_folder = app.config.get('UPLOAD_FOLDER')
        print(f"✅ Flask app created successfully")
        print(f"✅ Upload folder configured: {upload_folder}")
        
    except Exception as e:
        print(f"❌ Error importing Flask app: {e}")
        return False
    
    print("✅ All upload tests passed!")
    return True

if __name__ == "__main__":
    success = test_upload_functionality()
    sys.exit(0 if success else 1)
'''
    
    test_path = os.path.join(project_dir, 'test_pythonanywhere_upload.py')
    
    with open(test_path, 'w') as f:
        f.write(test_script)
    
    # Set executable permissions
    os.chmod(test_path, 0o755)
    
    print(f"✅ Created upload test script: {test_path}")

if __name__ == "__main__":
    success = fix_pythonanywhere_upload()
    
    if success:
        # Create test script
        project_dir = os.path.dirname(os.path.abspath(__file__))
        create_upload_test_script(project_dir)
        
        print("\n🎉 PythonAnywhere upload fix completed!")
        print("\nNext steps:")
        print("1. Upload the updated files to PythonAnywhere")
        print("2. Run: python test_pythonanywhere_upload.py")
        print("3. Update your WSGI file to use wsgi_pythonanywhere.py")
        print("4. Reload your web app")
    else:
        print("\n❌ PythonAnywhere upload fix failed!")
        sys.exit(1) 