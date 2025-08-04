# Web Server Deployment Guide

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
