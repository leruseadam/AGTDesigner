#!/usr/bin/env python3
"""
PythonAnywhere Performance Fix
Applies performance optimizations without breaking the configuration.
"""

import os
import shutil

def backup_current_files():
    """Backup current configuration files."""
    backup_dir = "backup_config"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = ['config.py', 'app.py']
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, f"{backup_dir}/{file}.backup")
            print(f"✅ Backed up {file}")

def fix_config_py():
    """Fix config.py for PythonAnywhere production."""
    config_content = '''import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
    
    # Development mode - set to False for production
    DEVELOPMENT_MODE = False  # Production mode for PythonAnywhere
    
    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Performance optimizations for PythonAnywhere
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB limit
    CACHE_DURATION = 180  # 3 minutes cache
    SESSION_LIFETIME = 1800  # 30 minutes session
'''
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    
    print("✅ Fixed config.py for production")

def optimize_app_py():
    """Apply performance optimizations to app.py."""
    
    # Read current app.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Apply optimizations
    optimizations = [
        # Reduce cache duration
        ("CACHE_DURATION = 300", "CACHE_DURATION = 180"),
        
        # Optimize session settings
        ("'PERMANENT_SESSION_LIFETIME': 3600", "'PERMANENT_SESSION_LIFETIME': 1800"),
        
        # Reduce file size limit
        ("MAX_CONTENT_LENGTH = 20 * 1024 * 1024", "MAX_CONTENT_LENGTH = 25 * 1024 * 1024"),
        
        # Disable debug mode in production
        ("app.config['DEBUG'] = True", "app.config['DEBUG'] = False"),
        
        # Enable static file caching
        ("app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0", "app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000"),
        
        # Disable template auto-reload
        ("app.config['TEMPLATES_AUTO_RELOAD'] = True", "app.config['TEMPLATES_AUTO_RELOAD'] = False"),
    ]
    
    for old, new in optimizations:
        if old in content:
            content = content.replace(old, new)
            print(f"✅ Applied optimization: {old} → {new}")
    
    # Write back the optimized content
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Applied performance optimizations to app.py")

def create_optimized_wsgi():
    """Create an optimized WSGI file."""
    wsgi_content = '''#!/usr/bin/env python3
"""
Optimized WSGI entry point for the Label Maker application.
"""

import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set production environment variables
os.environ.setdefault('DEVELOPMENT_MODE', 'false')
os.environ.setdefault('FLASK_ENV', 'production')

# Import the Flask app from app.py
try:
    from app import app
    
    # Apply additional optimizations for PythonAnywhere
    if hasattr(app, 'config'):
        app.config['TEMPLATES_AUTO_RELOAD'] = False
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
        app.config['SESSION_REFRESH_EACH_REQUEST'] = False
        app.config['PERMANENT_SESSION_LIFETIME'] = 1800
        app.config['DEBUG'] = False
    
    # For PythonAnywhere, we need to expose the app object
    application = app
except ImportError as e:
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
import time
import json
from datetime import datetime

def get_system_stats():
    """Get current system statistics."""
    try:
        import psutil
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
    except ImportError:
        return {
            'timestamp': datetime.now().isoformat(),
            'error': 'psutil not installed'
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

def main():
    """Main performance fix function."""
    print("🚀 PythonAnywhere Performance Fix")
    print("=" * 40)
    
    try:
        # Backup current files
        backup_current_files()
        
        # Apply fixes
        fix_config_py()
        optimize_app_py()
        create_optimized_wsgi()
        create_performance_monitor()
        
        print("\n" + "=" * 40)
        print("✅ Performance fix complete!")
        print("\n📋 Next steps:")
        print("1. Go to PythonAnywhere Web tab")
        print("2. Click 'Reload' for your web app")
        print("3. Test your app performance")
        print("4. Monitor with: python3 performance_monitor.py")
        
        print("\n🔧 If you need to revert:")
        print("cp backup_config/config.py.backup config.py")
        print("cp backup_config/app.py.backup app.py")
        
    except Exception as e:
        print(f"❌ Error during performance fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 