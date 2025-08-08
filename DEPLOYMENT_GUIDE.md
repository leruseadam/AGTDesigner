# Label Maker Application - Deployment Guide

## Overview
This application has been consolidated to use a single codebase that works both locally and on PythonAnywhere. The pythonanywhere_deployment folder has been removed and all optimizations are now in the main files.

## Key Changes Made

### 1. **Consolidated Codebase**
- Removed separate `pythonanywhere_deployment` folder
- Updated main `app.py` with pythonanywhere-compatible optimizations
- Standardized templates and static files
- Added performance flags for consistent behavior

### 2. **Performance Optimizations**
- Added `DISABLE_STARTUP_FILE_LOADING = False` flag for consistent startup behavior
- Optimized ExcelProcessor initialization with thread locks
- Simplified session management
- Reduced memory usage and startup time

### 3. **Essential API Routes**
The optimized app.py includes these essential routes:
- `/api/upload-status` - Check file upload status
- `/api/available-tags` - Get available tags
- `/api/selected-tags` - Get selected tags
- `/api/move-tags` - Move tags between available/selected
- `/api/generate` - Generate labels
- `/api/clear-filters` - Clear filters
- `/api/dropdowns` - Get filter options
- `/api/update-lineage` - Update lineage

## Deployment Instructions

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### PythonAnywhere Deployment
1. Upload all files to your PythonAnywhere account
2. Create a virtual environment and install requirements:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.11 labelmaker
   pip install -r requirements.txt
   ```
3. Set the WSGI file to point to `wsgi.py`
4. Configure the web app to use the virtual environment

## File Structure
```
├── app.py                    # Main application (optimized)
├── wsgi.py                   # WSGI entry point for PythonAnywhere
├── requirements.txt          # Dependencies
├── templates/               # HTML templates (optimized)
├── static/                  # CSS/JS files (optimized)
├── src/                     # Core modules (optimized)
└── DEPLOYMENT_GUIDE.md     # This file
```

## Performance Features
- Lazy loading of ExcelProcessor
- Thread-safe operations
- Optimized session management
- Reduced memory footprint
- Faster startup times

## Troubleshooting
- If you encounter import errors, ensure all dependencies are installed
- For PythonAnywhere, make sure the virtual environment is activated
- Check logs for any initialization errors
- The application now uses consistent behavior across environments 