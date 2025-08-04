import sys
import os

os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['FLASK_ENV'] = 'production'

project_dir = '/home/adamcordova/AGTDesigner'
sys.path.insert(0, project_dir)

try:
    venv_path = os.path.join(project_dir, 'venv_pythonanywhere')
    activate_script = os.path.join(venv_path, 'bin', 'activate_this.py')
    if os.path.exists(activate_script):
        with open(activate_script) as file_:
            exec(file_.read(), dict(__file__=activate_script))
except:
    pass

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