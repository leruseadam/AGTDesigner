import sys
import os

os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['FLASK_ENV'] = 'production'

sys.path.insert(0, '/home/adamcordova/AGTDesigner')

try:
    from app import create_app
    application = create_app()
    application.config['DEBUG'] = False
except:
    from flask import Flask
    application = Flask(__name__)
    @application.route('/')
    def error():
        return '<h1>Error</h1>', 500 