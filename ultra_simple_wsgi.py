#!/usr/bin/env python3
import sys
import os
import time

# Simple timestamp
TIMESTAMP = int(time.time())
print(f"ULTRA SIMPLE WSGI - TIMESTAMP: {TIMESTAMP}")

# Add project directory
sys.path.insert(0, '/home/adamcordova/AGTDesigner')

# Try to import the app
try:
    from app import create_app
    application = create_app()
    print(f"SUCCESS: App loaded at {TIMESTAMP}")
except Exception as e:
    print(f"ERROR: {e} at {TIMESTAMP}")
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f"Error: {e} - Timestamp: {TIMESTAMP}", 500

if __name__ == "__main__":
    application.run() 