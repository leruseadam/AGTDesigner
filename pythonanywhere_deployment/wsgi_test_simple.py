#!/usr/bin/env python3
"""
Simple test WSGI file for PythonAnywhere.
Minimal functionality to test basic deployment.
"""

import sys
import os

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# Create basic Flask app
from flask import Flask
application = Flask(__name__)

@application.route('/')
def index():
    return "Label Maker - Simple Test Mode", 200

@application.route('/health')
def health():
    return "OK", 200

@application.route('/test1')
def test1():
    return "Test 1 working", 200

@application.route('/test2')
def test2():
    return "Test 2 working", 200

@application.route('/test3')
def test3():
    return "Test 3 working", 200

# Basic configuration
application.config['DEBUG'] = False
application.config['TESTING'] = False
application.config['PROPAGATE_EXCEPTIONS'] = True
application.secret_key = 'simple-test-key-2024'

if __name__ == "__main__":
    application.run() 