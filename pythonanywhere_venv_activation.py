#!/usr/bin/env python3
"""
PythonAnywhere Virtual Environment Activation Guide
"""

import os
import time

def create_venv_activation_guide():
    """Create a guide for activating virtual environment in PythonAnywhere."""
    
    timestamp = int(time.time())
    
    print("=== PYTHONANYWHERE VIRTUAL ENVIRONMENT ACTIVATION ===")
    print(f"Timestamp: {timestamp}")
    print()
    
    print("=== METHOD 1: Using workon command ===")
    print("1. Go to PythonAnywhere dashboard")
    print("2. Navigate to 'Consoles' tab")
    print("3. Click 'New console' → 'Bash'")
    print("4. In the console, type:")
    print("   workon your-virtual-environment-name")
    print()
    print("Common virtual environment names:")
    print("- venv_pythonanywhere")
    print("- myenv")
    print("- agtvenv")
    print("- labelmaker")
    print()
    
    print("=== METHOD 2: Using source command ===")
    print("If workon doesn't work, try:")
    print("source /home/adamcordova/AGTDesigner/venv_pythonanywhere/bin/activate")
    print()
    
    print("=== METHOD 3: Direct activation ===")
    print("Or try the full path:")
    print("source /home/adamcordova/AGTDesigner/venv_pythonanywhere/bin/activate")
    print()
    
    print("=== CHECK IF VENV EXISTS ===")
    print("First, check if your virtual environment exists:")
    print("ls /home/adamcordova/AGTDesigner/")
    print("ls /home/adamcordova/")
    print()
    
    print("=== FIND YOUR VENV ===")
    print("Look for directories like:")
    print("- venv_pythonanywhere/")
    print("- venv/")
    print("- env/")
    print("- .venv/")
    print()
    
    print("=== ACTIVATION COMMANDS ===")
    print("Once you find your venv, use one of these:")
    print()
    print("Option 1:")
    print("workon venv_pythonanywhere")
    print()
    print("Option 2:")
    print("source /home/adamcordova/AGTDesigner/venv_pythonanywhere/bin/activate")
    print()
    print("Option 3:")
    print("source /home/adamcordova/venv_pythonanywhere/bin/activate")
    print()
    
    print("=== VERIFY ACTIVATION ===")
    print("After activation, verify with:")
    print("which python")
    print("pip list")
    print()
    
    print("=== INSTALL DEPENDENCIES ===")
    print("Once activated, install dependencies:")
    print("pip install flask pandas python-docx docxtpl openpyxl Pillow flask-cors flask-caching")
    print()
    
    print("=== CREATE NEW VENV IF NEEDED ===")
    print("If no virtual environment exists, create one:")
    print("cd /home/adamcordova/AGTDesigner")
    print("python3 -m venv venv_pythonanywhere")
    print("source venv_pythonanywhere/bin/activate")
    print("pip install flask pandas python-docx docxtpl openpyxl Pillow flask-cors flask-caching")
    print()
    
    print("=== WEB APP VENV CONFIGURATION ===")
    print("In your web app settings:")
    print("1. Go to Web tab")
    print("2. Click on your web app")
    print("3. Look for 'Virtual environment' section")
    print("4. Set it to: /home/adamcordova/AGTDesigner/venv_pythonanywhere")
    print("5. Save and reload")
    print()
    
    print("=== COMMON ISSUES ===")
    print("If 'workon' command not found:")
    print("- Use 'source' command instead")
    print("- Check if virtual environment exists")
    print("- Create new virtual environment if needed")
    print()
    
    print("=== QUICK COMMANDS ===")
    print("Copy and paste these commands in order:")
    print()
    print("# Check if venv exists")
    print("ls /home/adamcordova/AGTDesigner/")
    print()
    print("# Activate venv (try each until one works)")
    print("workon venv_pythonanywhere")
    print("# OR")
    print("source /home/adamcordova/AGTDesigner/venv_pythonanywhere/bin/activate")
    print()
    print("# Verify activation")
    print("which python")
    print("pip list")
    print()
    print("# Install dependencies")
    print("pip install flask pandas python-docx docxtpl openpyxl Pillow flask-cors flask-caching")
    
    return timestamp

if __name__ == "__main__":
    create_venv_activation_guide() 