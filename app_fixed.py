#!/usr/bin/env python3
"""
Fixed Flask application with proper route registration
"""

import os
import sys
import time
import logging
import traceback
from flask import Flask, request, jsonify, render_template, session, send_from_directory, g
from flask_caching import Cache
from functools import lru_cache
import threading

# Add the project directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Global variables
processing_status = {}
processing_timestamps = {}
processing_lock = threading.Lock()
UNDO_STACK_KEY = 'undo_stack'

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_url_path='/static', static_folder='static')
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = 'False'
    
    # Configure app
    app.config['SESSION_REFRESH_EACH_REQUEST'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600
    
    # Session configuration
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_MAX_SIZE'] = 8192
    
    upload_folder = os.path.join(current_dir, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.secret_key = os.environ.get('SECRET_KEY', 'label-maker-secret-key-2024-production')
    
    # Define all routes here so they get properly registered
    @app.route('/')
    def index():
        """Main page route."""
        try:
            cache_bust = str(int(time.time()))
            return render_template('index.html', cache_bust=cache_bust)
        except Exception as e:
            logging.error(f"Error in index route: {str(e)}")
            return render_template('index.html', error=str(e), cache_bust=str(int(time.time())))

    @app.route('/test')
    def test_route():
        """Simple test route to verify routing is working."""
        return jsonify({'message': 'Test route working!', 'status': 'success'})

    @app.route('/api/status', methods=['GET'])
    def api_status():
        """API status endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'message': 'Flask app is running correctly'
        })

    @app.route('/favicon.ico')
    def favicon():
        """Serve favicon."""
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    return app

# Create the Flask app
app = create_app()

# Initialize Flask-Caching
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False) 