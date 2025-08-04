#!/usr/bin/env python3
"""
Web Server Deployment Script for Label Maker
Optimizes the application for web server deployment on PythonAnywhere and similar platforms.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_web_server_config():
    """Create web server optimized configuration."""
    logger.info("Creating web server configuration...")
    
    # Import web server config
    from config_web_server import get_web_server_config, is_web_server
    
    if not is_web_server():
        logger.warning("Not running on web server environment, but continuing with web server optimizations...")
    
    config = get_web_server_config()
    
    # Create necessary directories
    directories = [
        'uploads',
        'output',
        'cache',
        'cache/sessions',
        'logs',
        'data'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Set proper permissions
    for directory in directories:
        try:
            os.chmod(directory, 0o755)
            logger.info(f"Set permissions for: {directory}")
        except Exception as e:
            logger.warning(f"Could not set permissions for {directory}: {e}")
    
    return config

def optimize_for_web_server():
    """Apply web server optimizations."""
    logger.info("Applying web server optimizations...")
    
    # 1. Disable startup file loading
    logger.info("Disabling startup file loading for web server...")
    
    # 2. Set environment variables
    os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'
    os.environ['WEB_SERVER_MODE'] = 'True'
    os.environ['DEVELOPMENT_MODE'] = 'False'
    
    logger.info("Set environment variables for web server mode")
    
    # 3. Create optimized WSGI file
    create_optimized_wsgi()
    
    # 4. Create requirements file for web server
    create_web_server_requirements()
    
    logger.info("Web server optimizations completed")

def create_optimized_wsgi():
    """Create an optimized WSGI file for web server deployment."""
    logger.info("Creating optimized WSGI file...")
    
    wsgi_content = '''#!/usr/bin/env python3
"""
Optimized WSGI entry point for Label Maker web server deployment.
"""

import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set web server environment variables
os.environ['WEB_SERVER_MODE'] = 'True'
os.environ['DEVELOPMENT_MODE'] = 'False'
os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'

# Import the Flask app from app.py
from app import app

# For web servers, we need to expose the app object
application = app

if __name__ == "__main__":
    app.run()
'''
    
    with open('wsgi_web_server.py', 'w') as f:
        f.write(wsgi_content)
    
    logger.info("Created optimized WSGI file: wsgi_web_server.py")

def create_web_server_requirements():
    """Create a requirements file optimized for web server deployment."""
    logger.info("Creating web server requirements file...")
    
    requirements_content = '''# Web Server Optimized Requirements for Label Maker
# Minimal dependencies for web server deployment

# Core Flask dependencies
Flask==2.3.3
Werkzeug==2.3.7
Jinja2==3.1.2

# Excel processing (optimized for web server)
openpyxl==3.1.2
pandas==2.0.3
numpy==1.24.3

# Document generation
python-docx==0.8.11
docxtpl==0.16.7

# Image processing
Pillow==10.0.0

# Utilities
python-dateutil==2.8.2
click==8.1.7

# Security
Flask-WTF==1.1.1
WTForms==3.0.1

# Session management
Flask-Session==0.5.0

# Logging and monitoring
colorlog==6.7.0
'''
    
    with open('requirements_web_server.txt', 'w') as f:
        f.write(requirements_content)
    
    logger.info("Created web server requirements file: requirements_web_server.txt")

def create_deployment_guide():
    """Create a deployment guide for web server."""
    logger.info("Creating web server deployment guide...")
    
    guide_content = '''# Web Server Deployment Guide

## PythonAnywhere Deployment

### 1. Upload Files
- Upload all project files to your PythonAnywhere account
- Ensure the directory structure is maintained

### 2. Create Virtual Environment
```bash
python3.10 -m venv ~/labelmaker-venv
source ~/labelmaker-venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements_web_server.txt
```

### 4. Configure Web App
1. Go to Web tab in PythonAnywhere dashboard
2. Create new web app (Manual configuration, Python 3.10)
3. Set source code path: `/home/yourusername/labelmaker`
4. Set working directory: `/home/yourusername/labelmaker`
5. Set virtual environment: `/home/yourusername/labelmaker-venv`

### 5. Configure WSGI File
- Edit the WSGI file in the Web tab
- Replace content with the content from `wsgi_web_server.py`

### 6. Set Environment Variables
In the Web tab → Environment variables section, add:
- `WEB_SERVER_MODE` = `True`
- `DEVELOPMENT_MODE` = `False`
- `DISABLE_DEFAULT_FILE_LOADING` = `True`
- `SECRET_KEY` = `your-secure-secret-key-here`

### 7. Configure Static Files
- URL: `/static/`
- Directory: `/home/yourusername/labelmaker/static`

### 8. Reload Web App
- Click "Reload" button in the Web tab
- Check error logs if any issues occur

## Performance Optimizations Applied

1. **Disabled startup file loading** - Faster startup times
2. **Minimal processing mode** - Reduced memory usage
3. **Optimized file uploads** - Faster upload processing
4. **Reduced cache sizes** - Lower memory footprint
5. **Background processing** - Non-blocking operations

## Troubleshooting

### Common Issues:
1. **Import errors** - Check virtual environment and dependencies
2. **Permission errors** - Ensure proper file permissions
3. **Memory issues** - Check memory usage and optimize further if needed
4. **Upload timeouts** - Use the web-optimized upload endpoint

### Performance Monitoring:
- Check `/api/performance` endpoint for performance stats
- Monitor memory usage in PythonAnywhere dashboard
- Use `/api/health` endpoint for system health

## Usage

### Upload Files:
- Use the web interface to upload Excel files
- Files are processed in the background for better performance
- Check upload status via the status endpoint

### Default File Loading:
- Default file loading is disabled for faster startup
- Upload files manually through the web interface
- Files are saved in the uploads directory
'''
    
    with open('WEB_SERVER_DEPLOYMENT_GUIDE.md', 'w') as f:
        f.write(guide_content)
    
    logger.info("Created deployment guide: WEB_SERVER_DEPLOYMENT_GUIDE.md")

def main():
    """Main deployment function."""
    logger.info("=== Web Server Deployment Script ===")
    
    try:
        # Create web server configuration
        config = create_web_server_config()
        
        # Apply optimizations
        optimize_for_web_server()
        
        # Create deployment files
        create_optimized_wsgi()
        create_web_server_requirements()
        create_deployment_guide()
        
        logger.info("=== Web Server Deployment Complete ===")
        logger.info("Next steps:")
        logger.info("1. Upload files to your web server")
        logger.info("2. Follow the deployment guide in WEB_SERVER_DEPLOYMENT_GUIDE.md")
        logger.info("3. Use the web-optimized upload endpoint: /upload-web-optimized")
        logger.info("4. Monitor performance via /api/performance endpoint")
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 