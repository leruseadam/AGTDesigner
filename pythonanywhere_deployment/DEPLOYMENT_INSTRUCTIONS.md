# PythonAnywhere Deployment Instructions

## Quick Setup

1. **Upload all files** to your PythonAnywhere project directory
2. **Open PythonAnywhere Bash Console** and run:
   ```bash
   cd /home/yourusername/AGTDesigner
   python fix_pythonanywhere_upload.py
   python test_pythonanywhere_upload.py
   ```
3. **Update WSGI file** with content from `wsgi_pythonanywhere.py`
4. **Set environment variables** in Web tab:
   - PYTHONANYWHERE=true
   - FLASK_ENV=production
   - FLASK_DEBUG=false
5. **Reload web app**

## File Structure
```
/home/yourusername/AGTDesigner/
├── app.py                          # Main application
├── wsgi_pythonanywhere.py          # WSGI configuration
├── fix_pythonanywhere_upload.py    # Fix script
├── test_pythonanywhere_upload.py   # Test script
├── src/                           # Source code
├── static/                        # Static files
├── templates/                     # Templates
└── uploads/                       # Upload directory (created by fix script)
```

## Troubleshooting
- Check error logs in PythonAnywhere Web tab
- Run test script to verify setup
- Ensure all dependencies are installed
