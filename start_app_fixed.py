#!/usr/bin/env python3
"""
Fixed App Startup Script
Starts the app on a different port to avoid conflicts
"""

import os
import sys

# Set the port to avoid conflicts
os.environ['FLASK_PORT'] = '5002'

print("🚀 Starting Label Maker App on port 5002...")
print("📍 App will be available at: http://127.0.0.1:5002")

# Import and run the app
from app import LabelMakerApp

if __name__ == "__main__":
    label_maker = LabelMakerApp()
    label_maker.run() 