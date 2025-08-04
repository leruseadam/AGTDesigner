# PythonAnywhere Configuration
import os

# Set environment variables for PythonAnywhere
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Database path for PythonAnywhere
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_database.db')

# Static files configuration
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Web server configuration
HOST = '0.0.0.0'
PORT = 8000
DEBUG = False 