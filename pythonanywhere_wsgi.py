# PythonAnywhere WSGI Configuration for Label Maker
# Copy this content into your PythonAnywhere WSGI file

import sys
import os

# Add the project directory to Python path
project_dir = '/home/yourusername/AGTDesigner'
sys.path.insert(0, project_dir)

# Activate virtual environment
activate_this = '/home/yourusername/AGTDesigner/venv_pythonanywhere/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run() 