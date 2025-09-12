import sys
import os
import traceback

# Set environment variables
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['FLASK_ENV'] = 'production'

# Try multiple possible paths for the app
possible_paths = [
    '/home/AGTDesigner/pythonanywhere_deployment',
    '/home/adamcordova/AGTDesigner',
    '/home/adamcordova/AGTDesigner/pythonanywhere_deployment'
]

application = None
error_message = ""

for project_dir in possible_paths:
    if os.path.exists(project_dir):
        try:
            # Add the app directory to Python path
            sys.path.insert(0, project_dir)
            
            # Change to the app directory
            os.chdir(project_dir)
            
            # Try to import the Flask app using create_app function
            from app import create_app
            application = create_app()
            application.config['DEBUG'] = False
            break
            
        except Exception as e:
            error_message = f"Error in {project_dir}: {str(e)}\n{traceback.format_exc()}"
            continue

# If all paths failed, create an error app
if application is None:
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return f'<h1>App Error</h1><p>Could not load app from any path.</p><p>Error: {error_message}</p>', 500
    
    @application.route('/health')
    def health():
        return 'OK', 200
