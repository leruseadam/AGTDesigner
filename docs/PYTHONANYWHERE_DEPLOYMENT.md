# PythonAnywhere Deployment Guide

## Prerequisites
- PythonAnywhere account
- Your code uploaded to PythonAnywhere

## Step 1: Upload Your Code
1. Go to your PythonAnywhere dashboard
2. Navigate to the Files tab
3. Upload your project files or clone from GitHub

## Step 2: Install Dependencies
1. Open a Bash console in PythonAnywhere
2. Navigate to your project directory
3. Install dependencies:
```bash
pip install --user -r requirements.txt
```

## Step 3: Configure WSGI File
1. Go to the Web tab in your PythonAnywhere dashboard
2. Click on your web app
3. Click on the WSGI configuration file link
4. Replace the content with the following:

```python
#!/usr/bin/env python3
"""
WSGI entry point for the Label Maker application.
This file is used by PythonAnywhere to serve the Flask application.
"""

import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the Flask app from app.py
from app import app

# For PythonAnywhere, we need to expose the app object
application = app

if __name__ == "__main__":
    app.run()
```

## Step 4: Configure Web App
1. In the Web tab, set the following:
   - **Source code**: `/home/yourusername/yourprojectdirectory`
   - **Working directory**: `/home/yourusername/yourprojectdirectory`
   - **WSGI configuration file**: Use the file you just edited

## Step 5: Set Environment Variables (if needed)
1. In the Web tab, go to Environment variables
2. Add any required environment variables:
   - `FLASK_ENV=production`
   - `DEVELOPMENT_MODE=false`

## Step 6: Reload Web App
1. Click the "Reload" button in the Web tab
2. Check the error logs if there are any issues

## Troubleshooting

### Common Issues:

1. **ModuleNotFoundError: No module named 'flask_app'**
   - Solution: Make sure your WSGI file imports from `app` not `flask_app`
   - The correct import is: `from app import app`

2. **Import errors for other modules**
   - Make sure all dependencies are installed: `pip install --user -r requirements.txt`
   - Check that the Python path includes your project directory

3. **Permission errors**
   - Make sure your project directory has the correct permissions
   - Check that PythonAnywhere can access your files

4. **Static files not loading**
   - Make sure your static folder is properly configured
   - Check that the static URL path is correct

### Debugging:
1. Check the error logs in the Web tab
2. Use the PythonAnywhere console to test imports
3. Verify file paths and permissions

## File Structure
Your project should have this structure on PythonAnywhere:
```
/home/yourusername/yourproject/
├── app.py
├── wsgi.py
├── requirements.txt
├── static/
├── templates/
├── src/
└── config/
```

## Notes
- PythonAnywhere uses Python 3.9 by default
- Make sure all file paths use forward slashes (/)
- The `application` variable in the WSGI file is what PythonAnywhere looks for
- Static files are served from the `static/` directory automatically 