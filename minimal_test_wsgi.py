#!/usr/bin/env python3
import sys
import os
import time

# Force reload with timestamp
TIMESTAMP = 1754283094
print(f"MINIMAL WSGI LOADED - TIMESTAMP: {TIMESTAMP}")

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Try to create a simple Flask app
try:
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def hello():
        return f"Hello from minimal WSGI! Timestamp: {TIMESTAMP}"
    
    print("✓ Minimal Flask app created")
except Exception as e:
    print(f"✗ Error creating minimal app: {e}")
    # Create a dummy application
    class DummyApp:
        def __call__(self, environ, start_response):
            status = '200 OK'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return [f"Error: {e} - Timestamp: {TIMESTAMP}".encode()]
    
    application = DummyApp()

if __name__ == "__main__":
    application.run()
