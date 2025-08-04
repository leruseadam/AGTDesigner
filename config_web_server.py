"""
Web Server Configuration for Label Maker
Optimized for PythonAnywhere and other web hosting environments.
"""

import os
import logging

# Web Server Mode
WEB_SERVER_MODE = True
DEVELOPMENT_MODE = False

# Performance optimizations for web server
WEB_SERVER_OPTIMIZATIONS = {
    'disable_startup_file_loading': True,
    'minimal_processing': True,
    'fast_upload': True,
    'reduced_memory_usage': True,
    'optimized_caching': True,
    'background_processing': True
}

# File handling for web server
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB limit for web server
ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}

# Database and caching
DATABASE_PATH = 'data/product_database.db'
CACHE_SIZE_LIMIT = 2  # Reduced for web server
CACHE_MEMORY_LIMIT = 50 * 1024 * 1024  # 50MB cache limit

# Processing settings
CHUNK_SIZE = 500  # Smaller chunks for web server
LARGE_FILE_THRESHOLD = 5 * 1024 * 1024  # 5MB threshold
ENABLE_PRODUCT_DB_INTEGRATION = False  # Disabled for web server performance

# Logging configuration
LOGGING_CONFIG = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': [
        {
            'class': 'logging.StreamHandler',
            'level': logging.INFO,
        }
    ]
}

# Session configuration
SESSION_TYPE = 'filesystem'
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
SESSION_FILE_DIR = 'cache/sessions'

# Security settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
CSRF_ENABLED = True
CSRF_TIME_LIMIT = 3600

# Rate limiting
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS = 10  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# File cleanup
AUTO_CLEANUP_ENABLED = True
CLEANUP_INTERVAL = 3600  # 1 hour
MAX_FILE_AGE = 86400  # 24 hours

def get_web_server_config():
    """Get web server specific configuration."""
    return {
        'web_server_mode': WEB_SERVER_MODE,
        'development_mode': DEVELOPMENT_MODE,
        'optimizations': WEB_SERVER_OPTIMIZATIONS,
        'upload_folder': UPLOAD_FOLDER,
        'max_content_length': MAX_CONTENT_LENGTH,
        'allowed_extensions': ALLOWED_EXTENSIONS,
        'database_path': DATABASE_PATH,
        'cache_size_limit': CACHE_SIZE_LIMIT,
        'cache_memory_limit': CACHE_MEMORY_LIMIT,
        'chunk_size': CHUNK_SIZE,
        'large_file_threshold': LARGE_FILE_THRESHOLD,
        'enable_product_db_integration': ENABLE_PRODUCT_DB_INTEGRATION,
        'logging_config': LOGGING_CONFIG,
        'session_type': SESSION_TYPE,
        'permanent_session_lifetime': PERMANENT_SESSION_LIFETIME,
        'session_file_dir': SESSION_FILE_DIR,
        'secret_key': SECRET_KEY,
        'csrf_enabled': CSRF_ENABLED,
        'csrf_time_limit': CSRF_TIME_LIMIT,
        'rate_limit_enabled': RATE_LIMIT_ENABLED,
        'rate_limit_requests': RATE_LIMIT_REQUESTS,
        'rate_limit_window': RATE_LIMIT_WINDOW,
        'auto_cleanup_enabled': AUTO_CLEANUP_ENABLED,
        'cleanup_interval': CLEANUP_INTERVAL,
        'max_file_age': MAX_FILE_AGE,
    }

def is_web_server():
    """Check if running on a web server environment."""
    return (
        'PYTHONANYWHERE_SITE' in os.environ or
        'PYTHONANYWHERE_DOMAIN' in os.environ or
        os.path.exists('/var/log/pythonanywhere') or
        'pythonanywhere.com' in os.environ.get('HTTP_HOST', '') or
        'heroku' in os.environ.get('DYNO', '').lower() or
        'railway' in os.environ.get('RAILWAY_ENVIRONMENT', '').lower() or
        'vercel' in os.environ.get('VERCEL', '').lower()
    ) 