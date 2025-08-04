# --- PERFORMANCE FLAGS ---
DISABLE_STARTUP_FILE_LOADING = False  # STANDARDIZED: Enable default file loading on startup for both environments

import os

import sys  # Add this import
import logging
import threading
import pandas as pd  # Add this import
from pathlib import Path
from flask import (
    Flask, 
    request, 
    jsonify, 
    send_file, 
    render_template,
    session,  # Add this
    send_from_directory,
    current_app,
    g  # Add this for per-request globals
)
from flask_cors import CORS
from docx import Document
from docxtpl import DocxTemplate, InlineImage
from io import BytesIO
from datetime import datetime, timezone
from functools import lru_cache
import json  # Add this import
from copy import deepcopy
from docx.shared import Pt, RGBColor, Mm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH  # Add this import
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
_excel_processor_reset_flag = False  # Flag to track when processor has been explicitly reset

# Global ProductDatabase instance
_product_database = None

# Global JSONMatcher instance
_json_matcher = None

# Global processing status with better state management
processing_status = {}  # filename -> status
processing_timestamps = {}  # filename -> timestamp
processing_lock = threading.Lock()  # Add thread lock for status updates

# Thread lock for ExcelProcessor initialization
excel_processor_lock = threading.Lock()  # Add thread lock for ExcelProcessor initialization

# Cache will be initialized after app creation
cache = None

# Rate limiting for API endpoints
RATE_LIMIT_WINDOW = 60  # 1 minute window
RATE_LIMIT_MAX_REQUESTS = 30  # Max requests per minute per IP

# Simple in-memory rate limiter
rate_limit_data = defaultdict(list)

# Performance optimization flags
LAZY_LOADING_ENABLED = True  # Enable lazy loading by default for faster startup

def reset_excel_processor():
    """Reset the global ExcelProcessor to force reloading of the default file."""
    global _excel_processor, _excel_processor_reset_flag
    
    with excel_processor_lock:
        _excel_processor = None
        _excel_processor_reset_flag = True
        logging.info("ExcelProcessor reset requested")

def force_reload_excel_processor(new_file_path):
    """Force reload ExcelProcessor with a new file path."""
    global _excel_processor, _excel_processor_reset_flag
    
    with excel_processor_lock:
        _excel_processor = None
        _excel_processor_reset_flag = True
        
        # Update the default file path
        try:
            from src.core.data.excel_processor import set_default_upload_file
            set_default_upload_file(new_file_path)
            logging.info(f"Default file path updated to: {new_file_path}")
        except Exception as e:
            logging.error(f"Error updating default file path: {e}")
    
    # Force reload
    get_excel_processor()

def cleanup_old_processing_status():
    """Clean up old processing status entries."""
    current_time = time.time()
    with processing_lock:
        for filename in list(processing_status.keys()):
            if filename in processing_timestamps:
                if current_time - processing_timestamps[filename] > 3600:  # 1 hour
                    del processing_status[filename]
                    del processing_timestamps[filename]

def update_processing_status(filename, status):
    """Update processing status for a file."""
    with processing_lock:
        processing_status[filename] = status
        processing_timestamps[filename] = time.time()

def get_excel_processor():
    """Get or create the global ExcelProcessor instance."""
    global _excel_processor, _excel_processor_reset_flag
    
    with excel_processor_lock:
        if _excel_processor is None or _excel_processor_reset_flag:
            try:
                _excel_processor = ExcelProcessor()
                _excel_processor_reset_flag = False
                logging.info("ExcelProcessor initialized successfully")
            except Exception as e:
                logging.error(f"Error initializing ExcelProcessor: {e}")
                _excel_processor = None
                _excel_processor_reset_flag = False
    
    return _excel_processor

def get_product_database():
    """Get or create the global ProductDatabase instance."""
    global _product_database
    if _product_database is None:
        try:
            from src.core.data.product_database import ProductDatabase
            _product_database = ProductDatabase()
        except Exception as e:
            logging.error(f"Error initializing ProductDatabase: {e}")
            _product_database = None
    return _product_database

def get_json_matcher():
    """Get or create the global JSONMatcher instance."""
    global _json_matcher
    if _json_matcher is None:
        try:
            from src.core.data.json_matcher import JSONMatcher
            _json_matcher = JSONMatcher()
        except Exception as e:
            logging.error(f"Error initializing JSONMatcher: {e}")
            _json_matcher = None
    return _json_matcher

def disable_product_db_integration():
    """Disable product database integration."""
    global _product_database
    _product_database = None
    logging.info("Product database integration disabled")

def get_cached_initial_data():
    """Get cached initial data."""
    global _initial_data_cache, _cache_timestamp
    if _initial_data_cache is not None and _cache_timestamp is not None:
        if time.time() - _cache_timestamp < CACHE_DURATION:
            return _initial_data_cache
    return None

def set_cached_initial_data(data):
    """Set cached initial data."""
    global _initial_data_cache, _cache_timestamp
    _initial_data_cache = data
    _cache_timestamp = time.time()

def clear_initial_data_cache():
    """Clear cached initial data."""
    global _initial_data_cache, _cache_timestamp
    _initial_data_cache = None
    _cache_timestamp = None

def set_landscape(doc):
    """Set document orientation to landscape."""
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Mm(297)
    section.page_height = Mm(210)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(current_dir, 'uploads')
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize cache
    global cache
    cache = Cache(app)
    
    # Enable CORS
    CORS(app)
    
    # Initialize ExcelProcessor on startup
    initialize_excel_processor()
    
    # --- ROUTES ---
    
    @app.route('/api/status', methods=['GET'])
    def api_status():
        """Check API server status and data loading status."""
        try:
            excel_processor = get_session_excel_processor()
            if excel_processor is None:
                return jsonify({
                    'server': 'running',
                    'data_loaded': False,
                    'data_shape': None,
                    'last_loaded_file': None,
                    'selected_tags_count': 0,
                    'error': 'Unable to initialize data processor'
                })
            
            # Get session manager for additional status info
            try:
                from src.core.data.session_manager import get_session_manager
                session_manager = get_session_manager()
                session_stats = session_manager.get_session_stats()
                session_id = session_manager.get_current_session_id()
                has_pending_changes = session_manager.has_pending_changes(session_id)
            except Exception as session_error:
                logging.warning(f"Error getting session stats: {session_error}")
                session_stats = {}
                has_pending_changes = False
            
            status = {
                'server': 'running',
                'data_loaded': excel_processor.df is not None and not excel_processor.df.empty,
                'data_shape': excel_processor.df.shape if excel_processor.df is not None else None,
                'last_loaded_file': getattr(excel_processor, '_last_loaded_file', None),
                'selected_tags_count': len(excel_processor.selected_tags) if hasattr(excel_processor, 'selected_tags') else 0,
                'session_stats': session_stats,
                'has_pending_changes': has_pending_changes
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
        try:
            # --- LIGHTWEIGHT PAGE LOAD (minimal work) ---
            cache_bust = str(int(time.time()))
            
            # Only clear session data, don't reset global state
            uploaded_file = session.pop('file_path', None)
            # Don't clear selected_tags - they should persist across page loads
            
            # Remove uploaded file if it exists and is not the default file
            if uploaded_file:
                from src.core.data.excel_processor import get_default_upload_file
                default_file = get_default_upload_file()
                if uploaded_file != default_file and os.path.exists(uploaded_file):
                    try:
                        os.remove(uploaded_file)
                    except Exception:
                        pass
            
            # Periodic cleanup (less frequent - every 50th page load)
            import random
            if random.random() < 0.02:  # 2% chance to run cleanup
                try:
                    cleanup_result = cleanup_old_files()
                    if cleanup_result['success'] and cleanup_result['removed_count'] > 0:
                        logging.info(f"Auto-cleanup removed {cleanup_result['removed_count']} files")
                except Exception as cleanup_error:
                    logging.warning(f"Auto-cleanup failed: {cleanup_error}")
            
            # Don't load data here - let frontend load via API calls
            # This makes page loads much faster
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
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if file:
                # Save file to uploads directory
                filename = sanitize_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Store file path in session
                session['file_path'] = file_path
                
                # Process file in background
                process_excel_background(filename, file_path)
                
                return jsonify({
                    'message': 'File uploaded successfully',
                    'filename': filename,
                    'status': 'processing'
                })
            
            return jsonify({'error': 'Invalid file'}), 400
            
        except Exception as e:
            logging.error(f"Upload error: {str(e)}")
            return jsonify({'error': f'Upload failed: {str(e)}'}), 500

    # Add a simple test route to verify routing is working
    @app.route('/test')
    def test_route():
        """Simple test route to verify routing is working."""
        return jsonify({'message': 'Test route working!', 'status': 'success'})

    # Add all the other routes here...
    # (This is where all the duplicate routes from the original file would go)
    
    return app

# Global function to check session size
def check_session_size():
    """Check if session is too large and clear it if necessary."""
    try:
        # Only check if session has data
        if not session:
            return False
            
        # Try to serialize session data safely
        session_copy = {}
        for key, value in session.items():
            try:
                # Test if this value can be pickled
                import pickle
                pickle.dumps(value)
                session_copy[key] = value
            except (pickle.PicklingError, TypeError):
                # Skip unpicklable objects
                logging.warning(f"Skipping unpicklable session key: {key}")
                continue
        
        # Check size of serializable data
        import pickle
        session_data = pickle.dumps(session_copy)
        if len(session_data) > 3000:  # 3KB limit to stay well under 4KB
            logging.warning(f"Session too large ({len(session_data)} bytes), clearing session data")
            session.clear()
            return True
    except Exception as e:
        logging.error(f"Error checking session size: {e}")
    return False

def optimize_session_data():
    """Optimize session data to reduce size."""
    try:
        # Only optimize if session has data
        if not session:
            return False
            
        # Only keep essential session data
        essential_keys = ['selected_tags', 'file_path', 'UNDO_STACK_KEY']
        session_copy = {}
        
        for key in essential_keys:
            if key in session:
                try:
                    if key == 'selected_tags':
                        # Store only tag names, not full objects
                        if isinstance(session[key], list):
                            # Convert to strings if they aren't already
                            session_copy[key] = []
                            for tag in session[key]:
                                if isinstance(tag, str):
                                    session_copy[key].append(tag)
                                elif isinstance(tag, dict) and 'Product Name*' in tag:
                                    session_copy[key].append(tag['Product Name*'])
                                else:
                                    session_copy[key].append(str(tag))
                        else:
                            session_copy[key] = []
                    elif key == 'UNDO_STACK_KEY':
                        # Limit undo stack to 3 entries max
                        undo_stack = session[key][-3:] if len(session[key]) > 3 else session[key]
                        session_copy[key] = undo_stack
                    else:
                        session_copy[key] = session[key]
                except Exception as e:
                    logging.warning(f"Error processing session key {key}: {e}")
                    continue
        
        # Test if the optimized data can be serialized
        try:
            import pickle
            pickle.dumps(session_copy)
            
            # Clear and restore only essential data
            session.clear()
            session.update(session_copy)
            
            logging.info("Session data optimized")
            return True
        except (pickle.PicklingError, TypeError) as e:
            logging.warning(f"Optimized session data still contains unpicklable objects: {e}")
            return False
            
    except Exception as e:
        logging.error(f"Error optimizing session data: {e}")
        return False

# Initialize Excel processor and load default data on startup
def initialize_excel_processor():
    """Initialize ExcelProcessor and load default data."""
    try:
        processor = get_excel_processor()
        if processor is not None:
            logging.info("ExcelProcessor initialized successfully")
        else:
            logging.error("Failed to initialize ExcelProcessor")
    except Exception as e:
        logging.error(f"Error initializing ExcelProcessor: {e}")

def save_template_settings(template_type, font_settings):
    """Save template settings to cache."""
    try:
        cache_key = f"template_settings_{template_type}"
        cache.set(cache_key, font_settings, timeout=3600)  # 1 hour cache
        return True
    except Exception as e:
        logging.error(f"Error saving template settings: {e}")
        return False

class LabelMakerApp:
    """Main application class for the Label Maker."""
    
    def __init__(self):
        self.app = create_app()
    
    def _configure_logging(self):
        # Configure logging only once
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('label_maker.log')
            ]
        )
    
    def run(self):
        """Run the application."""
        self._configure_logging()
        self.app.run(debug=True, host='0.0.0.0', port=5000)

def get_session_excel_processor():
    """Get ExcelProcessor for current session."""
    try:
        # Try to get from session first
        if 'excel_processor' in session:
            return session['excel_processor']
        
        # Fall back to global processor
        processor = get_excel_processor()
        if processor is not None:
            # Store in session for future use
            session['excel_processor'] = processor
        return processor
    except Exception as e:
        logging.error(f"Error getting session ExcelProcessor: {e}")
        return None

def get_session_json_matcher():
    """Get JSONMatcher for current session."""
    try:
        # Try to get from session first
        if 'json_matcher' in session:
            return session['json_matcher']
        
        # Fall back to global matcher
        matcher = get_json_matcher()
        if matcher is not None:
            # Store in session for future use
            session['json_matcher'] = matcher
        return matcher
    except Exception as e:
        logging.error(f"Error getting session JSONMatcher: {e}")
        return None

# Create the application instance for WSGI
application = create_app()

if __name__ == "__main__":
    app = LabelMakerApp()
    app.run() 