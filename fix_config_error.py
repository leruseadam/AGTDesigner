#!/usr/bin/env python3
"""
Quick fix for config.py error on PythonAnywhere
Restores the original config.py file to fix the NameError.
"""

import os

def fix_config_error():
    """Fix the config.py error by restoring the original configuration."""
    
    # Original config.py content
    config_content = '''import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
    
    # Development mode - set to False for production
    DEVELOPMENT_MODE = False  # Set to False for PythonAnywhere production
    
    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
'''
    
    # Write the fixed config.py
    with open('config.py', 'w') as f:
        f.write(config_content)
    
    print("✅ Fixed config.py - restored original configuration")
    print("✅ Set DEVELOPMENT_MODE = False for production")
    print("✅ Ready to reload web app")

if __name__ == "__main__":
    fix_config_error() 