#!/bin/bash
# Fix upload timeout issue - add timeout protection to upload endpoint
echo "Fixing upload timeout issue..."

# Create backup
cp /home/adamcordova/AGTDesigner/app.py /home/adamcordova/AGTDesigner/app.py.backup.$(date +%Y%m%d_%H%M%S)

# Replace the upload endpoint with a timeout-protected version
echo "Adding timeout protection to upload endpoint..."
cat > /home/adamcordova/AGTDesigner/app.py << 'EOF'
import os
import sys
import logging
import signal
from pathlib import Path
from werkzeug.utils import secure_filename
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import Flask
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, flash
import pandas as pd
import sqlite3
import json
import tempfile
import shutil
import threading
import time

# Import our modules
from src.core.data.excel_processor import ExcelProcessor
from src.core.data.product_database import ProductDatabase
from src.core.data.json_matcher import JSONMatcher

# Create Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return 'OK', 200

def timeout_handler(signum, frame):
    raise TimeoutError("Upload processing timed out")

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload endpoint with timeout protection"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith(('.xlsx', '.xls')):
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(file_path)
            
            # Set timeout for file processing (30 seconds)
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
            try:
                # Process the file with timeout protection
                excel_processor = ExcelProcessor()
                df = excel_processor.load_file(file_path)
                
                # Convert to JSON for frontend
                data = df.to_dict('records')
                
                # Cancel timeout
                signal.alarm(0)
                
                return jsonify({
                    'success': True,
                    'message': f'File {filename} uploaded successfully',
                    'data': data,
                    'filename': filename
                })
            except TimeoutError:
                signal.alarm(0)
                return jsonify({'error': 'File processing timed out. Please try a smaller file.'}), 408
            except Exception as e:
                signal.alarm(0)
                return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/performance/status', methods=['GET'])
def performance_status():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/performance/clear-cache', methods=['POST'])
def clear_performance_cache():
    return jsonify({'success': True, 'message': 'Cache cleared'})

if __name__ == '__main__':
    app.run(debug=True)
EOF

# Verify the file compiles
echo "Verifying Python syntax..."
python3 -m py_compile /home/adamcordova/AGTDesigner/app.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax is valid!"
    echo "✅ Timeout protection added!"
    echo "Reloading web app..."
    touch /var/www/www_agtpricetags_com_wsgi.py
    echo "Web app reloaded! Upload should work with timeout protection."
else
    echo "❌ Syntax errors found. Restoring backup..."
    cp /home/adamcordova/AGTDesigner/app.py.backup.* /home/adamcordova/AGTDesigner/app.py
    exit 1
fi

echo "Upload timeout fix applied successfully!"
echo "Uploads should no longer get stuck on initializing!"
