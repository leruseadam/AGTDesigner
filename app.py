#!/usr/bin/env python3
"""
Fixed Flask application with proper route registration
"""

# --- PERFORMANCE FLAGS ---
DISABLE_STARTUP_FILE_LOADING = False  # STANDARDIZED: Enable default file loading on startup for both environments

import os
import sys
import logging
import threading
import pandas as pd
from pathlib import Path
from flask import (
    Flask, 
    request, 
    jsonify, 
    send_file, 
    render_template,
    session,
    send_from_directory,
    current_app,
    g
)
from flask_cors import CORS
from docx import Document
from docxtpl import DocxTemplate, InlineImage
from io import BytesIO
from datetime import datetime, timezone
from functools import lru_cache
import json
from copy import deepcopy
from docx.shared import Pt, RGBColor, Mm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pprint
import re
import traceback
from docxcompose.composer import Composer
from openpyxl import load_workbook
from PIL import Image as PILImage
import copy
from docx.enum.section import WD_ORIENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_ROW_HEIGHT_RULE
from src.core.generation.template_processor import get_font_scheme, TemplateProcessor
from src.core.generation.tag_generator import get_template_path
import time
from src.core.generation.mini_font_sizing import (
    get_mini_font_size_by_marker,
    set_mini_run_font_size
)
from src.core.data.excel_processor import ExcelProcessor, get_default_upload_file
import random
from flask_caching import Cache
import hashlib
import glob
import subprocess
from collections import defaultdict
import shutil

current_dir = os.path.dirname(os.path.abspath(__file__))

# Global variables for lazy loading
_initial_data_cache = None
_cache_timestamp = None
CACHE_DURATION = 300  # Cache for 5 minutes

# Global ExcelProcessor instance
_excel_processor = None
_excel_processor_reset_flag = False

# Global ProductDatabase instance
_product_database = None

# Global JSONMatcher instance
_json_matcher = None

# Global processing status with better state management
processing_status = {}  # filename -> status
processing_timestamps = {}  # filename -> timestamp
processing_lock = threading.Lock()

# Thread lock for ExcelProcessor initialization
excel_processor_lock = threading.Lock()

# Cache will be initialized after app creation
cache = None

# Rate limiting for API endpoints
RATE_LIMIT_WINDOW = 60  # 1 minute window
RATE_LIMIT_MAX_REQUESTS = 30  # Max requests per minute per IP

# Simple in-memory rate limiter
rate_limit_data = defaultdict(list)

# Performance optimization flags
LAZY_LOADING_ENABLED = True

def reset_excel_processor():
    """Reset the global ExcelProcessor to force reloading of the default file."""
    global _excel_processor, _excel_processor_reset_flag
    
    with excel_processor_lock:
        _excel_processor = None
        _excel_processor_reset_flag = True
        logging.info("ExcelProcessor reset requested")

def force_reload_excel_processor(new_file_path):
    """Force reload the ExcelProcessor with a new file."""
    global _excel_processor
    
    with excel_processor_lock:
        try:
            new_processor = ExcelProcessor()
            if new_processor.load_file(new_file_path):
                _excel_processor = new_processor
                logging.info(f"ExcelProcessor reloaded with file: {new_file_path}")
                return True
            else:
                logging.error(f"Failed to load file: {new_file_path}")
                return False
        except Exception as e:
            logging.error(f"Error reloading ExcelProcessor: {e}")
            return False

def cleanup_old_processing_status():
    """Clean up old processing status entries."""
    global processing_status, processing_timestamps
    
    current_time = time.time()
    cutoff_time = current_time - 3600  # 1 hour
    
    with processing_lock:
        old_files = [filename for filename, timestamp in processing_timestamps.items() 
                    if timestamp < cutoff_time]
        
        for filename in old_files:
            processing_status.pop(filename, None)
            processing_timestamps.pop(filename, None)
        
        if old_files:
            logging.info(f"Cleaned up {len(old_files)} old processing status entries")

def update_processing_status(filename, status):
    """Update processing status for a file."""
    global processing_status, processing_timestamps
    
    with processing_lock:
        processing_status[filename] = status
        processing_timestamps[filename] = time.time()
        logging.info(f"Processing status updated for {filename}: {status}")

def get_excel_processor():
    """Get the global ExcelProcessor instance with lazy loading."""
    global _excel_processor, _excel_processor_reset_flag
    
    with excel_processor_lock:
        if _excel_processor is None or _excel_processor_reset_flag:
            try:
                logging.info("Initializing ExcelProcessor...")
                _excel_processor = ExcelProcessor()
                _excel_processor_reset_flag = False
                
                if not DISABLE_STARTUP_FILE_LOADING:
                    default_file = get_default_upload_file()
                    if default_file:
                        logging.info(f"Loading default file: {default_file}")
                        if not _excel_processor.load_file(default_file):
                            logging.warning(f"Failed to load default file: {default_file}")
                    else:
                        logging.info("No default file found")
                
                logging.info("ExcelProcessor initialized successfully")
            except Exception as e:
                logging.error(f"Error initializing ExcelProcessor: {e}")
                _excel_processor = None
                raise
        
        return _excel_processor

def get_product_database():
    """Get the global ProductDatabase instance."""
    global _product_database
    return _product_database

def get_json_matcher():
    """Get the global JSONMatcher instance."""
    global _json_matcher
    return _json_matcher

def disable_product_db_integration():
    """Disable product database integration."""
    global _product_database
    _product_database = None
    logging.info("Product database integration disabled")

def get_cached_initial_data():
    """Get cached initial data."""
    global _initial_data_cache, _cache_timestamp
    return _initial_data_cache, _cache_timestamp

def set_cached_initial_data(data):
    """Set cached initial data."""
    global _initial_data_cache, _cache_timestamp
    _initial_data_cache = data
    _cache_timestamp = time.time()

def clear_initial_data_cache():
    """Clear the initial data cache."""
    global _initial_data_cache, _cache_timestamp
    _initial_data_cache = None
    _cache_timestamp = None

def set_landscape(doc):
    """Set document to landscape orientation."""
    for section in doc.sections:
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = Mm(297)
        section.page_height = Mm(210)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def sanitize_filename(filename):
    """Sanitize filename for safe storage."""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    return filename

def cleanup_old_files():
    """Clean up old temporary files."""
    try:
        upload_folder = os.path.join(current_dir, 'uploads')
        if not os.path.exists(upload_folder):
            return {'success': True, 'removed_count': 0}
        
        current_time = time.time()
        cutoff_time = current_time - 3600  # 1 hour
        
        removed_count = 0
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                if file_time < cutoff_time:
                    try:
                        os.remove(file_path)
                        removed_count += 1
                    except Exception as e:
                        logging.warning(f"Could not remove old file {filename}: {e}")
        
        return {'success': True, 'removed_count': removed_count}
    except Exception as e:
        logging.error(f"Error cleaning up old files: {e}")
        return {'success': False, 'error': str(e)}

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_url_path='/static', static_folder='static')
    
    # Basic configuration
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB max file size
    app.config['TESTING'] = False
    app.config['SESSION_REFRESH_EACH_REQUEST'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session lifetime
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_MAX_SIZE'] = 8192
    
    # Secret key
    app.secret_key = os.environ.get('SECRET_KEY', 'label-maker-secret-key-2024-production')
    
    # CORS configuration
    allowed_origins = [
        'https://yourdomain.com',
        'https://www.yourdomain.com',
        'http://localhost:9090',
        'http://127.0.0.1:9090'
    ]
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
    
    # PythonAnywhere-specific configuration
    PYTHONANYWHERE_MODE = os.environ.get('PYTHONANYWHERE', 'false').lower() == 'true'
    
    if PYTHONANYWHERE_MODE:
        app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
        app.config['UPLOAD_FOLDER'] = os.path.join(current_dir, 'uploads')
        uploads_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(uploads_dir, mode=0o755, exist_ok=True)
        try:
            os.chmod(uploads_dir, 0o755)
        except Exception as e:
            logging.warning(f"Could not set uploads directory permissions: {e}")
        logging.info(f"PythonAnywhere mode enabled. Upload folder: {uploads_dir}")
    else:
        upload_folder = os.path.join(current_dir, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        app.config['UPLOAD_FOLDER'] = upload_folder

    # Define all routes inside the create_app function
    @app.route('/api/status', methods=['GET'])
    def api_status():
        """Check API server status and data loading status."""
        try:
            excel_processor = get_excel_processor()
            if excel_processor is None:
                return jsonify({
                    'server': 'running',
                    'data_loaded': False,
                    'data_shape': None,
                    'last_loaded_file': None,
                    'selected_tags_count': 0,
                    'error': 'Unable to initialize data processor'
                })
            
            status = {
                'server': 'running',
                'data_loaded': excel_processor.df is not None and not excel_processor.df.empty,
                'data_shape': excel_processor.df.shape if excel_processor.df is not None else None,
                'last_loaded_file': getattr(excel_processor, '_last_loaded_file', None),
                'selected_tags_count': len(excel_processor.selected_tags) if hasattr(excel_processor, 'selected_tags') else 0,
            }
            return jsonify(status)
        except Exception as e:
            logging.error(f"Error in status endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/favicon.ico')
    def favicon():
        """Serve the favicon."""
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/')
    def index():
        """Main index page."""
        try:
            cache_bust = str(int(time.time()))
            
            # Only clear session data, don't reset global state
            uploaded_file = session.pop('file_path', None)
            
            # Remove uploaded file if it exists and is not the default file
            if uploaded_file:
                default_file = get_default_upload_file()
                if uploaded_file != default_file and os.path.exists(uploaded_file):
                    try:
                        os.remove(uploaded_file)
                    except Exception:
                        pass
            
            # Periodic cleanup (less frequent - every 50th page load)
            if random.random() < 0.02:  # 2% chance to run cleanup
                try:
                    cleanup_result = cleanup_old_files()
                    if cleanup_result['success'] and cleanup_result['removed_count'] > 0:
                        logging.info(f"Auto-cleanup removed {cleanup_result['removed_count']} files")
                except Exception as cleanup_error:
                    logging.warning(f"Auto-cleanup failed: {cleanup_error}")
            
            # Don't load data here - let frontend load via API calls
            initial_data = None
            
            return render_template('index.html', initial_data=initial_data, cache_bust=cache_bust)
            
        except Exception as e:
            logging.error(f"Error in index route: {str(e)}")
            return render_template('index.html', error=str(e), cache_bust=str(int(time.time())))

    @app.route('/splash')
    def splash():
        """Serve the splash screen."""
        return render_template('splash.html')

    @app.route('/generation-splash')
    def generation_splash():
        """Serve the generation splash screen."""
        return render_template('generation-splash.html')

    @app.route('/upload', methods=['POST'])
    def upload_file():
        """Handle file upload."""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if file and file.filename.lower().endswith('.xlsx'):
                filename = sanitize_filename(file.filename)
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(temp_path)
                
                # Store uploaded file path in session
                session['file_path'] = temp_path
                
                # Clear selected tags in session to ensure fresh start
                session['selected_tags'] = []
                
                return jsonify({'message': 'File uploaded successfully', 'filename': filename})
            else:
                return jsonify({'error': 'Invalid file type. Please upload an Excel (.xlsx) file.'}), 400
        except Exception as e:
            logging.error(f"Upload error: {str(e)}")
            return jsonify({'error': 'Upload failed'}), 500

    @app.route('/test')
    def test_route():
        """Test route for debugging."""
        return jsonify({'status': 'ok', 'message': 'Test route working'})

    @app.route('/api/upload-status', methods=['GET'])
    def upload_status():
        """Get upload processing status."""
        try:
            filename = request.args.get('filename')
            if filename:
                status = processing_status.get(filename, 'unknown')
                return jsonify({'filename': filename, 'status': status})
            else:
                return jsonify({'status': 'no_file_specified'})
        except Exception as e:
            logging.error(f"Error getting upload status: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/available-tags', methods=['GET'])
    def get_available_tags():
        """Get available tags from the Excel processor."""
        try:
            excel_processor = get_excel_processor()
            if excel_processor is None:
                return jsonify({'error': 'Excel processor not initialized'}), 500
            
            filters = request.args.to_dict()
            available_tags = excel_processor.get_available_tags(filters)
            return jsonify(available_tags)
        except Exception as e:
            logging.error(f"Error getting available tags: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/selected-tags', methods=['GET'])
    def get_selected_tags():
        """Get currently selected tags."""
        try:
            excel_processor = get_excel_processor()
            if excel_processor is None:
                return jsonify({'error': 'Excel processor not initialized'}), 500
            
            selected_tags = excel_processor.get_selected_tags()
            return jsonify(selected_tags)
        except Exception as e:
            logging.error(f"Error getting selected tags: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/generate', methods=['POST'])
    def generate_labels():
        """Generate labels from selected tags."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            template_type = data.get('template_type', 'vertical')
            selected_tags = data.get('selected_tags', [])
            
            excel_processor = get_excel_processor()
            if excel_processor is None:
                return jsonify({'error': 'Excel processor not initialized'}), 500
            
            # Select the tags
            excel_processor.select_tags(selected_tags)
            
            # Get selected records
            selected_records = excel_processor.get_selected_records(template_type)
            
            if not selected_records:
                return jsonify({'error': 'No records selected'}), 400
            
            # Generate the document
            # This is a simplified version - you'll need to implement the actual generation logic
            return jsonify({
                'message': 'Labels generated successfully',
                'record_count': len(selected_records)
            })
            
        except Exception as e:
            logging.error(f"Error generating labels: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        try:
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time(),
                'version': '1.0.0'
            })
        except Exception as e:
            logging.error(f"Health check error: {e}")
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

    return app

def initialize_excel_processor():
    """Initialize the Excel processor with default file."""
    try:
        excel_processor = get_excel_processor()
        if excel_processor is None:
            logging.error("Failed to initialize Excel processor")
            return False
        
        # Load default file if available
        if not DISABLE_STARTUP_FILE_LOADING:
            default_file = get_default_upload_file()
            if default_file:
                logging.info(f"Loading default file: {default_file}")
                if not excel_processor.load_file(default_file):
                    logging.warning(f"Failed to load default file: {default_file}")
                    return False
            else:
                logging.info("No default file found")
        
        return True
    except Exception as e:
        logging.error(f"Error initializing Excel processor: {e}")
        return False

class LabelMakerApp:
    def __init__(self):
        self.app = create_app()
        self._configure_logging()
    
    def _configure_logging(self):
        """Configure logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('label_maker.log')
            ]
        )
    
    def run(self):
        """Run the Flask application."""
        try:
            # Initialize Excel processor
            if not initialize_excel_processor():
                logging.warning("Failed to initialize Excel processor")
            
            # Run the app
            self.app.run(host='0.0.0.0', port=9090, debug=False)
        except Exception as e:
            logging.error(f"Error running application: {e}")
            raise

# Create the Flask app
app = create_app()

# Initialize Flask-Caching after app creation
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

if __name__ == "__main__":
    label_maker = LabelMakerApp()
    label_maker.run() 