#!/usr/bin/env python3
"""
Fix for PythonAnywhere server issues including uWSGI, logging, and product processing
"""

import os
import shutil
import time

def backup_current_files():
    """Backup current files before making changes."""
    backup_dir = "backup_server_fix"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'app.py',
        'wsgi.py',
        'src/core/data/excel_processor.py'
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, f"{backup_dir}/{os.path.basename(file)}.backup")
            print(f"✅ Backed up {file}")

def fix_logging_errors():
    """Fix logging errors that are causing server issues."""
    
    # Read the current app.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Add proper logging configuration for PythonAnywhere
    logging_config = '''
# PythonAnywhere-specific logging configuration
import logging
import sys

# Configure logging to prevent errors
logging.basicConfig(
    level=logging.WARNING,  # Reduce log level to prevent spam
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pythonanywhere.log') if os.path.exists('/home/adamcordova') else logging.NullHandler()
    ]
)

# Suppress verbose logging from third-party libraries
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('watchdog').setLevel(logging.ERROR)

# PythonAnywhere-specific error handling
def safe_log(logger, level, message, *args, **kwargs):
    """Safely log messages to prevent logging errors."""
    try:
        if level == 'debug':
            logger.debug(message, *args, **kwargs)
        elif level == 'info':
            logger.info(message, *args, **kwargs)
        elif level == 'warning':
            logger.warning(message, *args, **kwargs)
        elif level == 'error':
            logger.error(message, *args, **kwargs)
        else:
            logger.info(message, *args, **kwargs)
    except Exception as e:
        # Fallback to print if logging fails
        print(f"Logging error: {e} - Message: {message}")

'''
    
    # Find where to insert the logging configuration (after imports)
    if 'import logging' in content:
        # Insert after the last import
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_index = i + 1
        
        lines.insert(insert_index, logging_config)
        content = '\n'.join(lines)
        print("✅ Added PythonAnywhere logging configuration")
    else:
        print("⚠️  Could not find import section to add logging configuration")
    
    # Write back the updated content
    with open('app.py', 'w') as f:
        f.write(content)

def fix_product_name_processing():
    """Fix product name processing issues."""
    
    # Read the current excel_processor.py
    with open('src/core/data/excel_processor.py', 'r') as f:
        content = f.read()
    
    # Add safe product name processing
    safe_processing = '''
def safe_product_name(name):
    """Safely process product names to prevent 'NO NAME' issues."""
    if not name or pd.isna(name):
        return "Unknown Product"
    
    # Convert to string and clean
    name_str = str(name).strip()
    
    if not name_str or name_str.lower() in ['nan', 'none', 'null', '']:
        return "Unknown Product"
    
    # Remove problematic characters
    name_str = re.sub(r'[\\x00-\\x1f\\x7f-\\x9f]', '', name_str)
    
    return name_str

def safe_product_type(product_type):
    """Safely process product types."""
    if not product_type or pd.isna(product_type):
        return "Unknown Type"
    
    type_str = str(product_type).strip()
    
    if not type_str or type_str.lower() in ['nan', 'none', 'null', '']:
        return "Unknown Type"
    
    return type_str

'''
    
    # Find where to insert the safe processing functions
    if 'def normalize_name(name):' in content:
        # Insert before normalize_name function
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('def normalize_name(name):'):
                insert_index = i
                break
        
        lines.insert(insert_index, safe_processing)
        content = '\n'.join(lines)
        print("✅ Added safe product name processing")
    else:
        print("⚠️  Could not find normalize_name function to add safe processing")
    
    # Write back the updated content
    with open('src/core/data/excel_processor.py', 'w') as f:
        f.write(content)

def create_pythonanywhere_wsgi():
    """Create a PythonAnywhere-specific WSGI file."""
    
    wsgi_content = '''#!/usr/bin/env python3
"""
PythonAnywhere WSGI configuration
"""

import os
import sys

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set environment variables for PythonAnywhere
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'www.agtpricetags.com'

# Configure logging for PythonAnywhere
import logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/home/adamcordova/pythonanywhere.log')
    ]
)

# Suppress verbose logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)

# Import and configure the Flask app
from app import app

# Configure Flask for PythonAnywhere
app.config['DEBUG'] = False
app.config['TESTING'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

# Set the application
application = app

if __name__ == "__main__":
    application.run()
'''
    
    with open('wsgi_pythonanywhere.py', 'w') as f:
        f.write(wsgi_content)
    
    print("✅ Created PythonAnywhere-specific WSGI file")

def create_server_monitor():
    """Create a server monitoring script."""
    
    monitor_script = '''#!/usr/bin/env python3
"""
PythonAnywhere Server Monitor
"""

import os
import time
import psutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/adamcordova/server_monitor.log'),
        logging.StreamHandler()
    ]
)

def check_server_status():
    """Check server status and resources."""
    try:
        # Check disk space
        disk_usage = psutil.disk_usage('/home/adamcordova')
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        
        # Check memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        logging.info(f"Server Status - Disk: {disk_percent:.1f}%, Memory: {memory_percent:.1f}%, CPU: {cpu_percent:.1f}%")
        
        # Check for potential issues
        if disk_percent > 90:
            logging.warning(f"Disk usage is high: {disk_percent:.1f}%")
        
        if memory_percent > 80:
            logging.warning(f"Memory usage is high: {memory_percent:.1f}%")
        
        if cpu_percent > 80:
            logging.warning(f"CPU usage is high: {cpu_percent:.1f}%")
            
    except Exception as e:
        logging.error(f"Error checking server status: {e}")

def check_log_files():
    """Check for log file issues."""
    log_files = [
        '/home/adamcordova/pythonanywhere.log',
        '/home/adamcordova/AGTDesigner/pythonanywhere.log',
        '/var/log/pythonanywhere/error.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                # Check file size
                size = os.path.getsize(log_file)
                if size > 10 * 1024 * 1024:  # 10MB
                    logging.warning(f"Log file is large: {log_file} ({size / 1024 / 1024:.1f}MB)")
                
                # Check for recent errors
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent_lines = lines[-100:]  # Last 100 lines
                    
                    error_count = sum(1 for line in recent_lines if 'ERROR' in line or '--- Logging error ---' in line)
                    if error_count > 10:
                        logging.warning(f"Many errors in log file: {log_file} ({error_count} errors in last 100 lines)")
                        
            except Exception as e:
                logging.error(f"Error checking log file {log_file}: {e}")

def cleanup_old_files():
    """Clean up old files to free space."""
    try:
        # Clean up old log files
        log_dir = '/home/adamcordova/AGTDesigner/logs'
        if os.path.exists(log_dir):
            for file in os.listdir(log_dir):
                file_path = os.path.join(log_dir, file)
                if os.path.isfile(file_path):
                    # Remove files older than 7 days
                    if time.time() - os.path.getmtime(file_path) > 7 * 24 * 3600:
                        os.remove(file_path)
                        logging.info(f"Removed old log file: {file}")
        
        # Clean up old uploads
        uploads_dir = '/home/adamcordova/AGTDesigner/uploads'
        if os.path.exists(uploads_dir):
            for file in os.listdir(uploads_dir):
                file_path = os.path.join(uploads_dir, file)
                if os.path.isfile(file_path):
                    # Remove files older than 30 days
                    if time.time() - os.path.getmtime(file_path) > 30 * 24 * 3600:
                        os.remove(file_path)
                        logging.info(f"Removed old upload file: {file}")
                        
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")

def main():
    """Main monitoring function."""
    logging.info("Starting server monitor...")
    
    while True:
        try:
            check_server_status()
            check_log_files()
            cleanup_old_files()
            
            # Wait 5 minutes before next check
            time.sleep(300)
            
        except KeyboardInterrupt:
            logging.info("Server monitor stopped by user")
            break
        except Exception as e:
            logging.error(f"Error in server monitor: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    main()
'''
    
    with open('server_monitor.py', 'w') as f:
        f.write(monitor_script)
    
    print("✅ Created server monitoring script")

def create_emergency_restart_script():
    """Create an emergency restart script."""
    
    restart_script = '''#!/bin/bash
"""
Emergency restart script for PythonAnywhere
"""

echo "Emergency restart script for PythonAnywhere"
echo "=========================================="

# Stop the current web app
echo "Stopping web app..."
cd /home/adamcordova/AGTDesigner

# Clear any stuck processes
pkill -f "python.*app.py" || true
pkill -f "uwsgi" || true

# Clear log files
echo "Clearing log files..."
rm -f /home/adamcordova/pythonanywhere.log
rm -f /home/adamcordova/AGTDesigner/pythonanywhere.log
rm -f /home/adamcordova/AGTDesigner/logs/*.log

# Clear cache
echo "Clearing cache..."
rm -rf /home/adamcordova/AGTDesigner/__pycache__
rm -rf /home/adamcordova/AGTDesigner/src/__pycache__
find /home/adamcordova/AGTDesigner -name "*.pyc" -delete

# Clear session data
echo "Clearing session data..."
rm -f /home/adamcordova/AGTDesigner/session_*

# Restart the web app
echo "Restarting web app..."
echo "Please go to PythonAnywhere Web tab and click 'Reload'"

echo "Emergency restart complete!"
echo "Check the web app status in PythonAnywhere Web tab"
'''
    
    with open('emergency_restart.sh', 'w') as f:
        f.write(restart_script)
    
    # Make it executable
    os.chmod('emergency_restart.sh', 0o755)
    
    print("✅ Created emergency restart script")

def create_pythonanywhere_config():
    """Create PythonAnywhere-specific configuration."""
    
    config_content = '''# PythonAnywhere-specific configuration
import os

class PythonAnywhereConfig:
    """Configuration specific to PythonAnywhere environment."""
    
    # Server settings
    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = False
    SEND_FILE_MAX_AGE_DEFAULT = 31536000
    
    # Logging settings
    LOG_LEVEL = 'WARNING'
    LOG_FILE = '/home/adamcordova/pythonanywhere.log'
    
    # Performance settings
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
    CACHE_DURATION = 180  # 3 minutes
    SESSION_LIFETIME = 1800  # 30 minutes
    
    # File processing settings
    CHUNK_SIZE = 500
    LARGE_FILE_THRESHOLD = 5 * 1024 * 1024  # 5MB
    ENABLE_MEMORY_MONITORING = True
    FORCE_GARBAGE_COLLECTION = True
    
    # Database settings
    DATABASE_PATH = '/home/adamcordova/AGTDesigner/product_database.db'
    
    # Upload settings
    UPLOAD_FOLDER = '/home/adamcordova/AGTDesigner/uploads'
    MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25MB
    
    # Error handling
    SUPPRESS_ERRORS = True
    SAFE_LOGGING = True
    
    @classmethod
    def get_config(cls):
        """Get configuration as dictionary."""
        return {key: value for key, value in cls.__dict__.items() 
                if not key.startswith('_') and not callable(value)}

# Export configuration
PYTHONANYWHERE_CONFIG = PythonAnywhereConfig.get_config()
'''
    
    with open('config_pythonanywhere_optimized.py', 'w') as f:
        f.write(config_content)
    
    print("✅ Created PythonAnywhere-specific configuration")

def main():
    """Main fix function."""
    print("🔧 PythonAnywhere Server Issues Fix")
    print("=" * 40)
    
    try:
        # Backup current files
        backup_current_files()
        
        # Apply fixes
        fix_logging_errors()
        fix_product_name_processing()
        create_pythonanywhere_wsgi()
        create_server_monitor()
        create_emergency_restart_script()
        create_pythonanywhere_config()
        
        print("\n" + "=" * 40)
        print("✅ Server fixes complete!")
        print("\n📋 Fixes applied:")
        print("1. Fixed logging errors and configuration")
        print("2. Added safe product name processing")
        print("3. Created PythonAnywhere-specific WSGI file")
        print("4. Added server monitoring script")
        print("5. Created emergency restart script")
        print("6. Added PythonAnywhere-specific configuration")
        
        print("\n📋 Next steps:")
        print("1. Update your PythonAnywhere WSGI file to use wsgi_pythonanywhere.py")
        print("2. Reload your web app in PythonAnywhere")
        print("3. Run: python3 server_monitor.py (optional)")
        print("4. Use: ./emergency_restart.sh if issues persist")
        
        print("\n🔧 WSGI Configuration:")
        print("In PythonAnywhere Web tab, set your WSGI file to:")
        print("wsgi_pythonanywhere.py")
        
        print("\n🔧 If you need to revert:")
        print("cp backup_server_fix/app.py.backup app.py")
        print("cp backup_server_fix/excel_processor.py.backup src/core/data/excel_processor.py")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 