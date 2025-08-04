#!/usr/bin/env python3
"""
Simple PythonAnywhere File Upload Fix
Fixed version without indentation issues
"""

import os
import sys

def fix_upload_issues():
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
        
        # Create PythonAnywhere WSGI configuration
        create_wsgi_config(project_dir)
        
        print("✅ PythonAnywhere upload fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during upload fix: {e}")
        return False

def create_wsgi_config(project_dir):
    """Create PythonAnywhere-specific WSGI configuration."""
    
    wsgi_content = """import sys
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
"""
    
    wsgi_path = os.path.join(project_dir, 'wsgi_pythonanywhere.py')
    with open(wsgi_path, 'w') as f:
        f.write(wsgi_content)
    
    print(f"✅ Created PythonAnywhere WSGI configuration: {wsgi_path}")

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
    # Run the fix
    success = fix_upload_issues()
    
    if success:
        # Test the functionality
        test_success = test_upload_functionality()
        
        print("\n🎉 PythonAnywhere upload fix completed!")
        print("\n📋 Next steps:")
        print("1. Update your PythonAnywhere WSGI file to use wsgi_pythonanywhere.py")
        print("2. Reload your web app on PythonAnywhere")
        print("3. Test file upload functionality")
        
        if test_success:
            print("✅ Upload functionality test passed!")
        else:
            print("❌ Upload functionality test failed!")
    else:
        print("\n❌ PythonAnywhere upload fix failed!")
        sys.exit(1) 