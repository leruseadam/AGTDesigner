#!/usr/bin/env python3
"""
Auto Upload Web Interface

This creates a simple web interface that automatically runs the enhanced auto-upload
script when the page is loaded, making it easy to sync files without manual commands.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import threading
import time

app = Flask(__name__)

# Global variable to store upload status
upload_status = {
    'running': False,
    'completed': False,
    'result': None,
    'timestamp': None
}

def run_auto_upload():
    """Run the enhanced auto-upload script in a separate thread."""
    global upload_status
    
    upload_status['running'] = True
    upload_status['completed'] = False
    upload_status['result'] = None
    upload_status['timestamp'] = datetime.now().isoformat()
    
    try:
        # Run the enhanced auto-upload script (non-interactive version)
        result = subprocess.run(
            [sys.executable, 'enhanced_auto_upload_noninteractive.py'],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        upload_status['result'] = {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        upload_status['result'] = {
            'success': False,
            'stdout': '',
            'stderr': 'Upload timed out after 2 minutes',
            'returncode': -1
        }
    except Exception as e:
        upload_status['result'] = {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }
    finally:
        upload_status['running'] = False
        upload_status['completed'] = True

@app.route('/')
def index():
    """Main page that automatically triggers upload."""
    return render_template('auto_upload.html')

@app.route('/api/upload-status')
def get_upload_status():
    """Get the current upload status."""
    return jsonify(upload_status)

@app.route('/api/start-upload')
def start_upload():
    """Manually start the upload process."""
    if upload_status['running']:
        return jsonify({'error': 'Upload already running'})
    
    # Start upload in background thread
    thread = threading.Thread(target=run_auto_upload)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Upload started'})

@app.route('/api/trigger-auto-upload')
def trigger_auto_upload():
    """Automatically trigger upload when page loads."""
    if not upload_status['running'] and not upload_status['completed']:
        # Start upload in background thread
        thread = threading.Thread(target=run_auto_upload)
        thread.daemon = True
        thread.start()
        return jsonify({'message': 'Auto-upload triggered'})
    else:
        return jsonify({'message': 'Upload already in progress or completed'})

if __name__ == '__main__':
    print("🚀 Starting Auto Upload Web Interface...")
    print("📱 Open your browser to: http://localhost:5002")
    print("🔄 Auto-upload will trigger automatically when you visit the page")
    app.run(host='0.0.0.0', port=5002, debug=True) 