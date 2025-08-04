import sys
import os

# Add the project directory to Python path
project_dir = '/home/adamcordova/AGTDesigner'
sys.path.insert(0, project_dir)

# Add virtual environment site-packages to Python path (for Python 3.11)
venv_site_packages = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/lib/python3.11/site-packages'
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Also add the virtual environment's lib directory
venv_lib = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/lib'
if os.path.exists(venv_lib) and venv_lib not in sys.path:
    sys.path.insert(0, venv_lib)

# Set the Python executable path
os.environ['VIRTUAL_ENV'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere'
os.environ['PATH'] = '/home/adamcordova/AGTDesigner/venv_pythonanywhere/bin:' + os.environ.get('PATH', '')

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run() 