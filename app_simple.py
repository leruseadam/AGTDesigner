#!/usr/bin/env python3
"""
Simple Label Maker App - Fixed for deployment
"""

import os
import sys
import logging

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import Flask first
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_url_path='/static', static_folder='static')
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'label-maker-secret-key-2024')
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
    
    # Enable CORS
    CORS(app)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Basic routes
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/test')
    def test():
        return jsonify({'status': 'ok', 'message': 'Flask app is running'})
    
    @app.route('/api/status')
    def api_status():
        return jsonify({
            'server': 'running',
            'message': 'Label Maker API is operational'
        })
    
    return app

def main():
    """Run the application"""
    app = create_app()
    
    # Get configuration from environment
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting Label Maker on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()