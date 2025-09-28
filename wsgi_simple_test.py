#!/usr/bin/env python3.11
"""
Simple WSGI test file for debugging
"""

import os
import sys

# Add project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

def application(environ, start_response):
    """Simple WSGI application for testing"""
    
    # Get the request path
    path = environ.get('PATH_INFO', '/')
    
    # Simple HTML response
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>WSGI Test</title>
    </head>
    <body>
        <h1>WSGI Test Successful!</h1>
        <p>Path: {path}</p>
        <p>Python version: {sys.version}</p>
        <p>Current directory: {os.getcwd()}</p>
        <p>Project directory exists: {os.path.exists(project_dir)}</p>
        <p>Files in current directory: {', '.join(os.listdir('.'))}</p>
        
        <h2>Testing Flask App Import:</h2>
    """
    
    try:
        from app import app
        html += f"<p style='color: green;'>✅ Flask app imported successfully!</p>"
        html += f"<p>App name: {app.name}</p>"
        
        # Test a simple route
        with app.test_client() as client:
            response = client.get('/')
            html += f"<p>Home route status: {response.status_code}</p>"
            
    except Exception as e:
        html += f"<p style='color: red;'>❌ Flask app import failed: {e}</p>"
        import traceback
        html += f"<pre>{traceback.format_exc()}</pre>"
    
    html += """
    </body>
    </html>
    """
    
    # Return response
    status = '200 OK'
    headers = [('Content-Type', 'text/html')]
    start_response(status, headers)
    return [html.encode('utf-8')]

if __name__ == "__main__":
    # For testing locally
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
