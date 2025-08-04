import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/home/adamcordova/AGTDesigner')

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()

# Add a simple test route to verify the app is working
@application.route('/test')
def test():
    return "Hello! Your Flask app is working! 🎉"

# Add a simple health check route
@application.route('/health')
def health():
    return "OK - Flask app is running"

if __name__ == "__main__":
    application.run() 