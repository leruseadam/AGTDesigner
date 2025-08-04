#!/usr/bin/env python3
"""
Simplified Flask app for PythonAnywhere deployment.
Removes complex imports and global variables that cause issues.
"""

import os
import sys
import logging
from flask import Flask, request, jsonify, send_file, render_template, session
from flask_cors import CORS

# Force unbuffered output for PythonAnywhere
os.environ['PYTHONUNBUFFERED'] = '1'

# Add project directory to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variables
os.environ['PYTHONANYWHERE'] = 'true'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'label-maker-production-key-2024'
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    # Enable CORS
    CORS(app)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    @app.route('/')
    def index():
        """Main page."""
        try:
            return render_template('index.html')
        except Exception as e:
            return f"Error loading main page: {str(e)}", 500
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return "OK", 200
    
    @app.route('/api/status')
    def api_status():
        """API status endpoint."""
        return jsonify({
            'status': 'running',
            'environment': 'production',
            'python_version': sys.version
        })
    
    @app.route('/test')
    def test():
        """Test endpoint."""
        return "Test endpoint working", 200
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        """File upload endpoint."""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # For now, just return success
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': file.filename
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Upload error: {str(e)}'}), 500
    
    @app.route('/api/templates')
    def get_templates():
        """Get available templates."""
        try:
            templates = [
                {'id': 'horizontal', 'name': 'Horizontal'},
                {'id': 'vertical', 'name': 'Vertical'},
                {'id': 'mini', 'name': 'Mini'},
                {'id': 'double', 'name': 'Double'}
            ]
            return jsonify(templates)
        except Exception as e:
            return jsonify({'error': f'Template error: {str(e)}'}), 500
    
    @app.route('/api/generate', methods=['POST'])
    def generate_labels():
        """Generate labels endpoint."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # For now, return a simple response
            return jsonify({
                'message': 'Label generation endpoint working',
                'received_data': data
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Generation error: {str(e)}'}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run(debug=False) 