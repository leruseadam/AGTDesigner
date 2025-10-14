# Concurrent Users Configuration
# Optimized for 7+ simultaneous users

import os

# Check environment
IS_PYTHONANYWHERE = os.environ.get('PYTHONANYWHERE_DOMAIN') is not None
IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production' or IS_PYTHONANYWHERE

# Flask Server Configuration
FLASK_CONFIG = {
    # Server settings for concurrent users
    'threaded': True,                    # Enable threading for concurrent requests
    'processes': 1,                      # Single process (PythonAnywhere limitation)
    'host': '0.0.0.0',                  # Accept connections from any IP
    'port': int(os.environ.get('FLASK_PORT', 5000)),
    
    # Performance settings
    'debug': not IS_PRODUCTION,         # Debug mode only in development
    'use_reloader': not IS_PRODUCTION,  # Auto-reload only in development
    'use_debugger': not IS_PRODUCTION,  # Debugger only in development
}

# Database Configuration for Concurrent Users
DATABASE_CONFIG = {
    # Connection pooling
    'max_connections': 10 if not IS_PYTHONANYWHERE else 5,  # More connections for concurrent users
    'connection_timeout': 30,            # 30 second timeout
    'connection_retry_delay': 0.5,       # 0.5 second retry delay
    
    # Transaction settings
    'transaction_timeout': 60,           # 60 second transaction timeout
    'lock_timeout': 10,                  # 10 second lock timeout
    
    # Batch processing
    'batch_size': 25,                    # Smaller batches for better concurrency
    'batch_timeout': 5.0,                # 5 second batch timeout
    
    # PythonAnywhere optimizations
    'pythonanywhere_optimizations': IS_PYTHONANYWHERE,
}

# Session Configuration
SESSION_CONFIG = {
    'max_sessions': 1000,                # Increased from 500 for more users
    'session_timeout': 3600,             # 1 hour session timeout
    'cleanup_interval': 300,             # Clean up old sessions every 5 minutes
    'storage_type': 'filesystem',        # Filesystem storage for persistence
}

# Upload Configuration
UPLOAD_CONFIG = {
    'max_file_size': 50 * 1024 * 1024 if not IS_PYTHONANYWHERE else 10 * 1024 * 1024,  # 50MB local, 10MB PythonAnywhere
    'chunk_size': 8192,                  # 8KB chunks for better concurrency
    'max_concurrent_uploads': 3,         # Limit concurrent uploads
    'upload_timeout': 300,               # 5 minute upload timeout
}

# Performance Monitoring
PERFORMANCE_CONFIG = {
    'enable_monitoring': True,
    'cpu_threshold': 80,                 # Alert if CPU > 80%
    'memory_threshold': 512 * 1024 * 1024,  # Alert if memory > 512MB
    'response_time_threshold': 5,        # Alert if response time > 5 seconds
    'concurrent_user_threshold': 10,     # Alert if > 10 concurrent users
}

# Caching Configuration
CACHE_CONFIG = {
    'enable_caching': True,
    'cache_size': 100,                   # Cache up to 100 items
    'cache_timeout': 300,                # 5 minute cache timeout
    'cache_type': 'memory',              # In-memory caching
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO' if IS_PRODUCTION else 'DEBUG',
    'max_file_size': 10 * 1024 * 1024,  # 10MB max log file size
    'backup_count': 3,                   # Keep 3 backup log files
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}

def get_optimized_config():
    """Get optimized configuration for concurrent users."""
    return {
        'flask': FLASK_CONFIG,
        'database': DATABASE_CONFIG,
        'session': SESSION_CONFIG,
        'upload': UPLOAD_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'cache': CACHE_CONFIG,
        'logging': LOGGING_CONFIG,
        'environment': {
            'is_pythonanywhere': IS_PYTHONANYWHERE,
            'is_production': IS_PRODUCTION,
            'max_concurrent_users': 7,
            'recommended_concurrent_users': 5 if IS_PYTHONANYWHERE else 10,
        }
    }

def print_concurrent_user_info():
    """Print information about concurrent user support."""
    config = get_optimized_config()
    env = config['environment']
    
    print("👥 CONCURRENT USER SUPPORT")
    print("=" * 50)
    print(f"✅ Supported concurrent users: {env['max_concurrent_users']}")
    print(f"✅ Recommended concurrent users: {env['recommended_concurrent_users']}")
    print(f"✅ Environment: {'PythonAnywhere' if env['is_pythonanywhere'] else 'Local/Production'}")
    print()
    print("📊 Configuration:")
    print(f"   Database connections: {config['database']['max_connections']}")
    print(f"   Session timeout: {config['session']['session_timeout']}s")
    print(f"   Max file size: {config['upload']['max_file_size']/1024/1024:.0f}MB")
    print(f"   Threading: {'Enabled' if config['flask']['threaded'] else 'Disabled'}")
    print()
    print("⚠️  Limitations:")
    if env['is_pythonanywhere']:
        print("   - PythonAnywhere has CPU/memory limits")
        print("   - Reduced database connections (5 max)")
        print("   - Smaller file upload limits (10MB)")
        print("   - Single process limitation")
    else:
        print("   - Default Flask server (not production-grade)")
        print("   - Limited by system resources")
    print()
    print("🚀 Recommendations:")
    print("   - Use Gunicorn or uWSGI for production")
    print("   - Consider load balancing for >10 users")
    print("   - Monitor CPU/memory usage")
    print("   - Implement request queuing for heavy operations")

if __name__ == "__main__":
    print_concurrent_user_info()
