import sys
import os

# Use PythonAnywhere's built-in virtual environment
# This will use whatever virtual environment is configured in the Web tab

# Add the project directory to Python path
sys.path.insert(0, '/home/adamcordova/AGTDesigner')

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

if __name__ == "__main__":
    application.run() 