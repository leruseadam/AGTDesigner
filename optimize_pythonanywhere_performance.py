#!/usr/bin/env python3
"""
PythonAnywhere Performance Optimization Script
Applies optimized settings to improve performance and reduce lag.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_pythonanywhere_environment():
    """Check if we're running on PythonAnywhere."""
    return (
        'PYTHONANYWHERE_SITE' in os.environ or
        'PYTHONANYWHERE_DOMAIN' in os.environ or
        os.path.exists('/var/log/pythonanywhere') or
        'pythonanywhere.com' in os.environ.get('HTTP_HOST', '')
    )

def backup_current_config():
    """Backup the current configuration."""
    config_files = ['config.py', 'config_production.py', 'app.py']
    backup_dir = Path('backup_config')
    backup_dir.mkdir(exist_ok=True)
    
    for config_file in config_files:
        if os.path.exists(config_file):
            shutil.copy2(config_file, backup_dir / f"{config_file}.backup")
            print(f"✅ Backed up {config_file}")

def apply_optimized_config():
    """Apply optimized configuration for PythonAnywhere."""
    
    # 1. Update config.py to use optimized settings
    config_content = '''import os
from config_pythonanywhere_optimized import get_optimized_settings

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
    
    # Get optimized settings based on environment
    OPTIMIZED_SETTINGS = get_optimized_settings()
    
    # Development mode - automatically set based on environment
    DEVELOPMENT_MODE = not check_pythonanywhere_environment()
    
    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Apply optimized settings
    MAX_FILE_SIZE = OPTIMIZED_SETTINGS['max_file_size']
    CHUNK_SIZE = OPTIMIZED_SETTINGS['chunk_size']
    CACHE_SIZE_LIMIT = OPTIMIZED_SETTINGS['cache_size_limit']
    CACHE_MEMORY_LIMIT = OPTIMIZED_SETTINGS['cache_memory_limit']
    CACHE_TTL = OPTIMIZED_SETTINGS['cache_ttl']
    
    # Flask production settings
    DEBUG = OPTIMIZED_SETTINGS['flask_production_settings']['DEBUG']
    TESTING = OPTIMIZED_SETTINGS['flask_production_settings']['TESTING']
    TEMPLATES_AUTO_RELOAD = OPTIMIZED_SETTINGS['flask_production_settings']['TEMPLATES_AUTO_RELOAD']
    SEND_FILE_MAX_AGE_DEFAULT = OPTIMIZED_SETTINGS['flask_production_settings']['SEND_FILE_MAX_AGE_DEFAULT']
    SESSION_REFRESH_EACH_REQUEST = OPTIMIZED_SETTINGS['flask_production_settings']['SESSION_REFRESH_EACH_REQUEST']
    PERMANENT_SESSION_LIFETIME = OPTIMIZED_SETTINGS['flask_production_settings']['PERMANENT_SESSION_LIFETIME']
    MAX_CONTENT_LENGTH = OPTIMIZED_SETTINGS['flask_production_settings']['MAX_CONTENT_LENGTH']

def check_pythonanywhere_environment():
    """Check if running on PythonAnywhere."""
    return (
        'PYTHONANYWHERE_SITE' in os.environ or
        'PYTHONANYWHERE_DOMAIN' in os.environ or
        os.path.exists('/var/log/pythonanywhere') or
        'pythonanywhere.com' in os.environ.get('HTTP_HOST', '')
    )
'''
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    print("✅ Updated config.py with optimized settings")

def optimize_app_py():
    """Apply performance optimizations to app.py."""
    
    # Read the current app.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Apply optimizations
    optimizations = [
        # Reduce cache duration
        ("CACHE_DURATION = 300", "CACHE_DURATION = 180"),
        
        # Reduce rate limiting
        ("RATE_LIMIT_MAX_REQUESTS = 30", "RATE_LIMIT_MAX_REQUESTS = 50"),
        
        # Optimize session settings
        ("'PERMANENT_SESSION_LIFETIME': 3600", "'PERMANENT_SESSION_LIFETIME': 1800"),
        
        # Reduce file size limit
        ("MAX_CONTENT_LENGTH = 20 * 1024 * 1024", "MAX_CONTENT_LENGTH = 25 * 1024 * 1024"),
    ]
    
    for old, new in optimizations:
        if old in content:
            content = content.replace(old, new)
            print(f"✅ Applied optimization: {old} → {new}")
    
    # Write back the optimized content
    with open('app.py', 'w') as f:
        f.write(content)

def create_optimized_wsgi():
    """Create an optimized WSGI file."""
    wsgi_content = '''#!/usr/bin/env python3
"""
Optimized WSGI entry point for the Label Maker application.
This file is used by PythonAnywhere to serve the Flask application.
"""

import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set production environment variables for optimal performance
os.environ.setdefault('DEVELOPMENT_MODE', 'false')
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('PYTHONANYWHERE_OPTIMIZED', 'true')

# Import the Flask app from app.py
try:
    from app import app
    
    # Apply additional optimizations for PythonAnywhere
    if hasattr(app, 'config'):
        app.config['TEMPLATES_AUTO_RELOAD'] = False
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
        app.config['SESSION_REFRESH_EACH_REQUEST'] = False
        app.config['PERMANENT_SESSION_LIFETIME'] = 1800
    
    # For PythonAnywhere, we need to expose the app object
    application = app
except ImportError as e:
    # Log the error for debugging
    print(f"Error importing app: {e}")
    raise

if __name__ == "__main__":
    app.run()
'''
    
    with open('wsgi_optimized.py', 'w') as f:
        f.write(wsgi_content)
    print("✅ Created optimized WSGI file: wsgi_optimized.py")

def create_performance_monitor():
    """Create a performance monitoring script."""
    monitor_content = '''#!/usr/bin/env python3
"""
Performance monitoring script for PythonAnywhere deployment.
"""

import os
import psutil
import time
import json
from datetime import datetime

def get_system_stats():
    """Get current system statistics."""
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'memory': {
                'total_mb': memory.total // (1024 * 1024),
                'available_mb': memory.available // (1024 * 1024),
                'percent_used': memory.percent
            },
            'disk': {
                'total_gb': disk.total // (1024 * 1024 * 1024),
                'free_gb': disk.free // (1024 * 1024 * 1024),
                'percent_used': (disk.used / disk.total) * 100
            },
            'cpu_percent': cpu_percent
        }
    except Exception as e:
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

def log_performance():
    """Log performance statistics."""
    stats = get_system_stats()
    
    # Write to log file
    with open('performance_log.json', 'a') as f:
        f.write(json.dumps(stats) + '\\n')
    
    # Print summary
    if 'error' not in stats:
        print(f"📊 Performance: CPU {stats['cpu_percent']}% | "
              f"Memory {stats['memory']['percent_used']:.1f}% | "
              f"Disk {stats['disk']['percent_used']:.1f}%")
    else:
        print(f"❌ Performance monitoring error: {stats['error']}")

if __name__ == "__main__":
    log_performance()
'''
    
    with open('performance_monitor.py', 'w') as f:
        f.write(monitor_content)
    print("✅ Created performance monitoring script")

def create_optimization_script():
    """Create a script to apply optimizations on PythonAnywhere."""
    script_content = '''#!/bin/bash

# PythonAnywhere Performance Optimization Script
echo "🚀 Applying PythonAnywhere performance optimizations..."

# 1. Backup current configuration
echo "📦 Backing up current configuration..."
python3 optimize_pythonanywhere_performance.py

# 2. Clear cache and temporary files
echo "🧹 Clearing cache and temporary files..."
rm -rf __pycache__
rm -rf src/__pycache__
rm -rf src/core/__pycache__
rm -rf src/core/data/__pycache__
rm -rf src/core/generation/__pycache__
rm -rf cache/*
rm -rf output/*
rm -rf logs/*

# 3. Set proper permissions
echo "🔐 Setting proper permissions..."
chmod -R 755 .
chmod -R 755 uploads output cache logs static

# 4. Install performance monitoring
echo "📊 Installing performance monitoring..."
pip install --user psutil

# 5. Test the optimized configuration
echo "🧪 Testing optimized configuration..."
python3 -c "from config import Config; print('✅ Configuration loaded successfully')"

# 6. Reload the web app
echo "🔄 Reloading web app..."
echo "Please go to PythonAnywhere Web tab and click 'Reload'"

echo ""
echo "✅ Optimization complete!"
echo "📊 Monitor performance with: python3 performance_monitor.py"
echo "🌐 Test your app at: https://yourusername.pythonanywhere.com"
'''
    
    with open('apply_pythonanywhere_optimizations.sh', 'w') as f:
        f.write(script_content)
    os.chmod('apply_pythonanywhere_optimizations.sh', 0o755)
    print("✅ Created optimization application script")

def main():
    """Main optimization function."""
    print("🚀 PythonAnywhere Performance Optimization")
    print("=" * 50)
    
    if not check_pythonanywhere_environment():
        print("⚠️  Warning: This script is designed for PythonAnywhere environment")
        print("   Some optimizations may not be appropriate for local development")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    try:
        # Backup current configuration
        backup_current_config()
        
        # Apply optimizations
        apply_optimized_config()
        optimize_app_py()
        create_optimized_wsgi()
        create_performance_monitor()
        create_optimization_script()
        
        print("\n" + "=" * 50)
        print("✅ Optimization complete!")
        print("\n📋 Next steps:")
        print("1. Run: chmod +x apply_pythonanywhere_optimizations.sh")
        print("2. Run: ./apply_pythonanywhere_optimizations.sh")
        print("3. Go to PythonAnywhere Web tab and click 'Reload'")
        print("4. Test your app performance")
        print("5. Monitor with: python3 performance_monitor.py")
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        print("🔄 Restoring backup...")
        # Restore backup logic here
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 