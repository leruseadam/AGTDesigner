#!/usr/bin/env python3
"""
Script to restore the working WSGI configuration
"""

def print_restore_instructions():
    """Print instructions for restoring the working WSGI configuration."""
    
    print("🔧 Restore Working WSGI Configuration")
    print("=" * 50)
    print()
    
    print("📋 STEP 1: Check What Changed")
    print("-" * 40)
    print("1. Go to PythonAnywhere dashboard")
    print("2. Click 'Web' tab")
    print("3. Click on your web app")
    print("4. Check 'Error log' for recent changes")
    print("5. Look at the current WSGI file content")
    print()
    
    print("📋 STEP 2: Restore Original WSGI Content")
    print("-" * 40)
    print("Edit the WSGI file: /var/www/www_agtpricetags_com_wsgi.py")
    print("Replace with this basic working content:")
    print()

def get_basic_working_wsgi():
    """Return the basic working WSGI content."""
    
    return '''#!/usr/bin/env python3
"""
Basic working WSGI configuration
"""

import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Import the Flask app
from app import app
application = app

if __name__ == "__main__":
    application.run()
'''

def get_original_wsgi_content():
    """Return what the original WSGI file probably looked like."""
    
    return '''#!/usr/bin/env python3
"""
Original working WSGI configuration
"""

import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'www.agtpricetags.com'

# Import the Flask app
from app import app
application = app

if __name__ == "__main__":
    application.run()
'''

def get_troubleshooting_steps():
    """Return troubleshooting steps for restoring functionality."""
    
    return '''📋 TROUBLESHOOTING STEPS:

1. CHECK PYTHONANYWHERE SETTINGS:
   - Go to 'Web' tab
   - Click on your web app
   - Check 'Code' section
   - Verify Python version matches your environment
   - Check if any settings were accidentally changed

2. VERIFY PROJECT FILES:
   - Go to 'Files' tab
   - Navigate to /home/adamcordova/AGTDesigner/
   - Ensure all files are still there
   - Check file permissions

3. TEST IN CONSOLE:
   - Go to 'Consoles' tab
   - Start a new console
   - Run: cd /home/adamcordova/AGTDesigner
   - Run: python -c "from app import app; print('App works')"

4. CHECK DEPENDENCIES:
   - Run: pip list | grep flask
   - Run: pip list | grep pandas
   - Ensure all required packages are installed

5. RESTORE FROM BACKUP:
   - If you have a backup of the working WSGI file, restore it
   - Or use the basic working content above
'''

def main():
    """Main function."""
    
    print_restore_instructions()
    
    print("📄 BASIC WORKING WSGI CONTENT:")
    print("=" * 40)
    print(get_basic_working_wsgi())
    print()
    
    print("📄 ORIGINAL WSGI CONTENT (if you had one):")
    print("=" * 40)
    print(get_original_wsgi_content())
    print()
    
    print(get_troubleshooting_steps())
    print()
    
    print("💡 Quick Actions:")
    print("1. Try the basic WSGI content first")
    print("2. Check if any PythonAnywhere settings changed")
    print("3. Verify your project files are intact")
    print("4. Test the app import in console")
    print()
    
    print("🔍 What specifically changed?")
    print("- Did you modify the WSGI file recently?")
    print("- Did PythonAnywhere update anything?")
    print("- Did you change any project files?")
    print("- When did it stop working?")

if __name__ == "__main__":
    main() 