"""
Performance configuration for the Label Maker application.
This file contains settings to optimize startup time and overall performance.
"""

# Startup Performance Settings
DISABLE_STARTUP_FILE_LOADING = True  # Skip loading default file on startup for faster reloads
LAZY_LOADING_ENABLED = True  # Enable lazy loading of data
DISABLE_PRODUCT_DB_ON_STARTUP = True  # Disable product database integration on startup

# Logging Performance Settings
REDUCE_LOGGING_VERBOSITY = True  # Reduce logging verbosity for faster startup
LOG_LEVEL = 'WARNING'  # Set default log level (DEBUG, INFO, WARNING, ERROR)

# File Processing Performance Settings
ENABLE_FAST_LOADING = True  # Use fast loading mode for Excel files
ENABLE_LAZY_PROCESSING = True  # Enable lazy processing for better performance
ENABLE_MINIMAL_PROCESSING = True  # Enable minimal processing mode for uploads
ENABLE_BATCH_OPERATIONS = True  # Enable batch operations instead of row-by-row
ENABLE_VECTORIZED_OPERATIONS = True  # Enable vectorized operations where possible

# Cache Settings
CACHE_DURATION = 300  # Cache duration in seconds (5 minutes)
CACHE_SIZE = 128  # Cache size for better performance

# Development vs Production Settings
DEVELOPMENT_MODE = True  # Set to False for production
DEBUG_MODE = False  # Set to True for debugging (slower)

# Flask Configuration Overrides
FLASK_CONFIG = {
    'TEMPLATES_AUTO_RELOAD': True,  # Enable template auto-reload for development
    'SEND_FILE_MAX_AGE_DEFAULT': 0,  # Disable static file caching for development
    'DEBUG': False,  # Disable debug mode for better performance
    'PROPAGATE_EXCEPTIONS': False,  # Disable exception propagation for performance
    'MAX_CONTENT_LENGTH': 20 * 1024 * 1024,  # 20MB max file size
    'SESSION_REFRESH_EACH_REQUEST': False,  # Don't refresh session on every request
    'PERMANENT_SESSION_LIFETIME': 3600,  # 1 hour session lifetime
}

def get_performance_config():
    """Get the current performance configuration."""
    return {
        'startup': {
            'disable_startup_file_loading': DISABLE_STARTUP_FILE_LOADING,
            'lazy_loading_enabled': LAZY_LOADING_ENABLED,
            'disable_product_db_on_startup': DISABLE_PRODUCT_DB_ON_STARTUP,
        },
        'logging': {
            'reduce_verbosity': REDUCE_LOGGING_VERBOSITY,
            'log_level': LOG_LEVEL,
        },
        'processing': {
            'enable_fast_loading': ENABLE_FAST_LOADING,
            'enable_lazy_processing': ENABLE_LAZY_PROCESSING,
            'enable_minimal_processing': ENABLE_MINIMAL_PROCESSING,
            'enable_batch_operations': ENABLE_BATCH_OPERATIONS,
            'enable_vectorized_operations': ENABLE_VECTORIZED_OPERATIONS,
        },
        'cache': {
            'duration': CACHE_DURATION,
            'size': CACHE_SIZE,
        },
        'mode': {
            'development': DEVELOPMENT_MODE,
            'debug': DEBUG_MODE,
        },
        'flask': FLASK_CONFIG,
    }

def print_performance_config():
    """Print the current performance configuration."""
    config = get_performance_config()
    print("Current Performance Configuration:")
    print("=" * 40)
    
    for section, settings in config.items():
        print(f"\n{section.upper()}:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    print_performance_config() 