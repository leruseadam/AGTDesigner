import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
sys.path.insert(0, project_dir)

# Add virtual environment site-packages to Python path
venv_site_packages = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/lib/python3.11/site-packages'
if venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run() 