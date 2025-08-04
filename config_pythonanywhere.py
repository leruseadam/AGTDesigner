"""
PythonAnywhere-specific configuration for Label Maker
Optimized for the PythonAnywhere environment with memory and file system constraints.
"""

import os
import logging

# PythonAnywhere-specific settings
PYTHONANYWHERE_MODE = True

# File size limits for PythonAnywhere
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
CHUNK_SIZE = 1000  # Number of rows to read at once for large files
LARGE_FILE_THRESHOLD = 10 * 1024 * 1024  # 10MB - files larger than this use chunked reading

# Memory optimization settings
ENABLE_MEMORY_MONITORING = True
FORCE_GARBAGE_COLLECTION = True
USE_CATEGORICAL_DTYPES = True
CATEGORICAL_THRESHOLD = 0.5  # Convert to categorical if unique values < 50% of total rows

# Excel engine preferences for PythonAnywhere
EXCEL_ENGINES = ['openpyxl', 'xlrd']  # Try openpyxl first, then xlrd

# File path handling for PythonAnywhere
PYTHONANYWHERE_HOME = os.path.expanduser('~')
PYTHONANYWHERE_DOWNLOADS = os.path.join(PYTHONANYWHERE_HOME, 'Downloads')
PYTHONANYWHERE_UPLOADS = os.path.join(os.getcwd(), 'uploads')

# Logging configuration for PythonAnywhere
PYTHONANYWHERE_LOGGING = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': [
        {
            'class': 'logging.StreamHandler',
            'level': logging.INFO,
        }
    ]
}

# Cache settings for PythonAnywhere
CACHE_SIZE_LIMIT = 3  # Maximum number of files to cache
CACHE_MEMORY_LIMIT = 100 * 1024 * 1024  # 100MB cache limit

# Performance monitoring
ENABLE_PERFORMANCE_MONITORING = True
PERFORMANCE_LOG_INTERVAL = 60  # Log performance stats every 60 seconds

# Error handling
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # seconds

# File validation
VALIDATE_FILE_EXTENSIONS = ['.xlsx', '.xls']
VALIDATE_FILE_CONTENT = True
VALIDATE_FILE_PERMISSIONS = True

def get_pythonanywhere_config():
    """Get PythonAnywhere-specific configuration."""
    return {
        'max_file_size': MAX_FILE_SIZE,
        'chunk_size': CHUNK_SIZE,
        'large_file_threshold': LARGE_FILE_THRESHOLD,
        'excel_engines': EXCEL_ENGINES,
        'downloads_path': PYTHONANYWHERE_DOWNLOADS,
        'uploads_path': PYTHONANYWHERE_UPLOADS,
        'enable_memory_monitoring': ENABLE_MEMORY_MONITORING,
        'force_garbage_collection': FORCE_GARBAGE_COLLECTION,
        'use_categorical_dtypes': USE_CATEGORICAL_DTYPES,
        'categorical_threshold': CATEGORICAL_THRESHOLD,
        'cache_size_limit': CACHE_SIZE_LIMIT,
        'cache_memory_limit': CACHE_MEMORY_LIMIT,
        'retry_attempts': RETRY_ATTEMPTS,
        'retry_delay': RETRY_DELAY,
        'validate_file_extensions': VALIDATE_FILE_EXTENSIONS,
        'validate_file_content': VALIDATE_FILE_CONTENT,
        'validate_file_permissions': VALIDATE_FILE_PERMISSIONS,
    }

def is_pythonanywhere():
    """Check if running on PythonAnywhere."""
    return (
        'PYTHONANYWHERE_SITE' in os.environ or
        'PYTHONANYWHERE_DOMAIN' in os.environ or
        os.path.exists('/var/log/pythonanywhere') or
        'pythonanywhere.com' in os.environ.get('HTTP_HOST', '')
    )

def get_optimized_settings():
    """Get optimized settings based on environment."""
    if is_pythonanywhere():
        return get_pythonanywhere_config()
    else:
        # Return default settings for local development
        return {
            'max_file_size': 100 * 1024 * 1024,  # 100MB for local
            'chunk_size': 5000,  # Larger chunks for local
            'large_file_threshold': 50 * 1024 * 1024,  # 50MB for local
            'excel_engines': ['openpyxl'],
            'downloads_path': os.path.expanduser('~/Downloads'),
            'uploads_path': os.path.join(os.getcwd(), 'uploads'),
            'enable_memory_monitoring': False,
            'force_garbage_collection': False,
            'use_categorical_dtypes': False,
            'categorical_threshold': 0.8,
            'cache_size_limit': 10,
            'cache_memory_limit': 500 * 1024 * 1024,  # 500MB for local
            'retry_attempts': 1,
            'retry_delay': 0,
            'validate_file_extensions': ['.xlsx', '.xls'],
            'validate_file_content': False,
            'validate_file_permissions': False,
        } 