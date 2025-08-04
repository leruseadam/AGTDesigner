#!/usr/bin/env python3
import sys
import os

# Print diagnostic information
print("=== WSGI Diagnostic ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Add project directory
project_dir = '/home/adamcordova/AGTDesigner'
if os.path.exists(project_dir):
    print(f"✓ Found project directory: {project_dir}")
    sys.path.insert(0, project_dir)
else:
    print(f"✗ Project directory not found: {project_dir}")

# Try to import
try:
    from app import create_app
    print("✓ Successfully imported create_app")
    application = create_app()
    print("✓ Successfully created application")
except Exception as e:
    print(f"✗ Error: {e}")
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return f"Error: {e}", 500

if __name__ == "__main__":
    application.run()