#!/usr/bin/env python3
"""
PythonAnywhere WSGI Configuration Fix Script

This script helps fix the WSGI configuration for PythonAnywhere deployment
by detecting the correct paths and creating a proper WSGI file.
"""

import os
import sys
import subprocess
from pathlib import Path

def get_pythonanywhere_info():
    """Get PythonAnywhere-specific information."""
    username = os.environ.get('USER', 'unknown')
    home_dir = os.path.expanduser('~')
    
    print(f"🔍 PythonAnywhere Info:")
    print(f"   Username: {username}")
    print(f"   Home directory: {home_dir}")
    print(f"   Current working directory: {os.getcwd()}")
    
    return username, home_dir

def find_project_directory():
    """Find the project directory."""
    current_dir = Path.cwd()
    
    # Look for common project indicators
    project_indicators = ['app.py', 'requirements.txt', 'src/', 'templates/']
    
    for indicator in project_indicators:
        if (current_dir / indicator).exists():
            print(f"✅ Found project directory: {current_dir}")
            return str(current_dir)
    
    # If not found in current directory, check parent
    parent_dir = current_dir.parent
    for indicator in project_indicators:
        if (parent_dir / indicator).exists():
            print(f"✅ Found project directory: {parent_dir}")
            return str(parent_dir)
    
    print(f"⚠️  Could not determine project directory")
    return str(current_dir)

def find_virtual_environment():
    """Find the virtual environment more comprehensively."""
    print("🔍 Searching for virtual environment...")
    
    # Check if we're currently in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"✅ Currently in virtual environment: {sys.prefix}")
        return sys.prefix
    
    project_dir = Path(find_project_directory())
    
    # Common virtual environment names and locations
    search_paths = [
        # Project directory and subdirectories
        project_dir / 'venv_pythonanywhere',
        project_dir / 'venv',
        project_dir / '.venv',
        project_dir / 'env',
        
        # Home directory
        Path.home() / 'venv_pythonanywhere',
        Path.home() / 'venv',
        Path.home() / '.venv',
        Path.home() / 'env',
    ]
    
    for path in search_paths:
        if path.exists():
            # Check for activate_this.py
            activate_script = path / 'bin' / 'activate_this.py'
            if activate_script.exists():
                print(f"✅ Found virtual environment: {path}")
                return str(path)
    
    # Try to find by checking which python is being used
    try:
        result = subprocess.run(['which', 'python'], capture_output=True, text=True)
        if result.returncode == 0:
            python_path = result.stdout.strip()
            print(f"🔍 Python path: {python_path}")
            
            # Extract virtual environment path from python path
            if 'venv' in python_path or 'env' in python_path:
                venv_path = Path(python_path).parent.parent
                if (venv_path / 'bin' / 'activate_this.py').exists():
                    print(f"✅ Found virtual environment from Python path: {venv_path}")
                    return str(venv_path)
    except Exception as e:
        print(f"⚠️  Could not determine Python path: {e}")
    
    print(f"⚠️  No virtual environment found")
    return None

def create_wsgi_file(project_dir, venv_path=None):
    """Create a proper WSGI file."""
    wsgi_content = f'''import sys
import os

# Get the current directory (project root)
project_dir = '{project_dir}'
sys.path.insert(0, project_dir)

# Try to activate virtual environment if it exists
'''
    
    if venv_path:
        wsgi_content += f'''venv_path = '{venv_path}'
activate_this = os.path.join(venv_path, 'bin', 'activate_this.py')

if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))
    print(f"✅ Virtual environment activated: {{venv_path}}")
else:
    print(f"⚠️  Virtual environment not found at: {{venv_path}}")
    print("Continuing without virtual environment activation...")
'''
    else:
        wsgi_content += '''# No virtual environment found
print("⚠️  No virtual environment configured")
'''
    
    wsgi_content += '''
# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Import the Flask app
try:
    from app import create_app
    print("✅ Flask app imported successfully")
except ImportError as e:
    print(f"❌ Error importing Flask app: {e}")
    raise

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run()
'''
    
    # Write the WSGI file
    wsgi_path = Path(project_dir) / 'wsgi.py'
    with open(wsgi_path, 'w') as f:
        f.write(wsgi_content)
    
    print(f"✅ Created WSGI file: {wsgi_path}")
    return str(wsgi_path)

def test_wsgi_file(wsgi_path):
    """Test the WSGI file."""
    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', wsgi_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ WSGI file syntax is valid")
            return True
        else:
            print(f"❌ WSGI file syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing WSGI file: {e}")
        return False

def main():
    """Main deployment function."""
    print("🚀 PythonAnywhere WSGI Configuration Fix")
    print("=" * 50)
    
    # Get PythonAnywhere info
    username, home_dir = get_pythonanywhere_info()
    
    # Find project directory
    project_dir = find_project_directory()
    
    # Find virtual environment
    venv_path = find_virtual_environment()
    
    # Create WSGI file
    wsgi_path = create_wsgi_file(project_dir, venv_path)
    
    # Test WSGI file
    if test_wsgi_file(wsgi_path):
        print("\n🎉 WSGI configuration completed successfully!")
        print("\n📋 Next steps:")
        print("1. In PythonAnywhere Web tab, update your WSGI configuration file to:")
        print(f"   {wsgi_path}")
        print("2. Set your virtual environment path to:")
        if venv_path:
            print(f"   {venv_path}")
        else:
            print("   (Leave blank if no virtual environment)")
        print("3. Reload your web app")
        print("\n🔗 Your app should be available at:")
        print(f"   https://{username}.pythonanywhere.com")
    else:
        print("\n❌ WSGI configuration failed. Please check the errors above.")

if __name__ == "__main__":
    main() 