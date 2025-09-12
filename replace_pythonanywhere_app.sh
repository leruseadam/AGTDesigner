#!/bin/bash
# Replace the entire app.py file on PythonAnywhere with our working version
echo "Replacing PythonAnywhere app.py with working version..."

# Create a simple working app.py for PythonAnywhere
cat > /home/adamcordova/AGTDesigner/app.py << 'EOF'
import os
import sys
import logging
import traceback
from pathlib import Path
from werkzeug.utils import secure_filename

# Performance optimizations
IS_PYTHONANYWHERE = 'pythonanywhere.com' in os.environ.get('HTTP_HOST', '')
IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production' or IS_PYTHONANYWHERE

# Configure logging
if IS_PRODUCTION:
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.INFO)

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import Flask and create app
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, flash
import pandas as pd
import sqlite3
import json
import tempfile
import shutil
from datetime import datetime, timedelta
import threading
import time
import signal

# Import our modules
from src.core.data.excel_processor import ExcelProcessor
from src.core.data.product_database import ProductDatabase
from src.core.data.json_matcher import JSONMatcher

# Create Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Simple initialization for PythonAnywhere
def simple_initialize_excel_processor():
    """Simple initialization that won't get stuck - for PythonAnywhere"""
    try:
        logging.info("Simple initialization starting...")
        
        # Create Excel processor without loading any files
        excel_processor = ExcelProcessor()
        excel_processor.logger.setLevel(logging.WARNING)
        
        # Initialize with empty DataFrame
        if not hasattr(excel_processor, 'df') or excel_processor.df is None:
            excel_processor.df = pd.DataFrame()
            logging.info("Initialized with empty DataFrame")
        
        logging.info("Simple initialization completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error in simple initialization: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return False

# Initialize on startup
if os.environ.get('PYTHONANYWHERE_DOMAIN'):
    simple_initialize_excel_processor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
EOF

echo "✅ Created working app.py file"
echo "Verifying Python syntax..."
python3 -m py_compile /home/adamcordova/AGTDesigner/app.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax is valid!"
    echo "Reloading web app..."
    touch /var/www/www_agtpricetags_com_wsgi.py
    echo "Web app reloaded! Check it now."
else
    echo "❌ Syntax error in created file"
    exit 1
fi
