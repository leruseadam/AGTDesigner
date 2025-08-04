#!/usr/bin/env python3
import sys
import os

# Add multiple possible paths
possible_paths = [
    '/home/adamcordova/AGTDesigner',
    '/home/adamcordova/AGTDesigner/labelMaker_ newgui BACKUP 6.24 copy 17',
    os.path.dirname(os.path.abspath(__file__))
]

for path in possible_paths:
    if os.path.exists(path):
        sys.path.insert(0, path)
        break

# Try to create app
try:
    from app import create_app
    application = create_app()
except Exception as e:
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return f"Error: {e}", 500

if __name__ == "__main__":
    application.run()