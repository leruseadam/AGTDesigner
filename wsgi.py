#!/usr/bin/env python3
"""
PythonAnywhere WSGI configuration for AGT Designer.

HOW TO ADD / WIRE A STORE
--------------------------
1. Add the store name to VALID_STORES in app.py (e.g. 'AGT_NewStore').
2. Upload its SQLite database to the uploads/ directory as:
       product_database_AGT_NewStore.db
3. In the SERVER-ONLY wsgi file (/var/www/adamcordova_pythonanywhere_com_wsgi.py)
   add one line in the "Per-store POSaBit menu-feed keys" section:
       os.environ['POSABIT_MENU_FEED_KEY_AGT_NEWSTORE'] = '<uuid>'
   The slug is the store name uppercased with spaces→underscores.

All other settings (token, base URL, performance flags) are shared and
only need to be set once.

IMPORTANT: NEVER commit real API tokens or feed keys to this file.
           Keep them only in the PythonAnywhere server-side wsgi file.
"""

import os
import sys
import logging

# ---------------------------------------------------------------------------
# Python path / working directory
# ---------------------------------------------------------------------------
project_dir = '/home/adamcordova/AGTDesigner'

if os.path.exists(project_dir):
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    os.chdir(project_dir)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    logging.error(f"Project directory {project_dir} not found, using {current_dir}")

# ---------------------------------------------------------------------------
# Platform flags
# ---------------------------------------------------------------------------
os.environ['PYTHONANYWHERE_SITE'] = 'True'
os.environ['PYTHONANYWHERE_DOMAIN'] = 'pythonanywhere.com'
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# ---------------------------------------------------------------------------
# Performance tuning
# ---------------------------------------------------------------------------
os.environ['FORCE_FAST_LOAD'] = 'True'
os.environ['DISABLE_STARTUP_FILE_LOADING'] = 'True'
os.environ['MAX_MEMORY_MB'] = '450'
os.environ['CACHE_SIZE_LIMIT'] = '100'
os.environ['BATCH_SIZE_LIMIT'] = '500'

# ---------------------------------------------------------------------------
# POSaBit API — shared credentials
# Set ONLY in the server-side wsgi file, never committed to git.
#
#   os.environ['POSABIT_API_TOKEN']    = '<token>'
#   os.environ['POSABIT_API_BASE_URL'] = 'https://app.posabit.com/api'
#   os.environ['USE_POSABIT_PRODUCTS'] = 'true'
#
# ---------------------------------------------------------------------------
# Per-store POSaBit menu-feed keys
# Format: POSABIT_MENU_FEED_KEY_<STORE_NAME_UPPER>
# The fallback key (POSABIT_MENU_FEED_KEY) is used when no store-specific
# key is found.  Wire every store below in the server-side wsgi file.
#
#   os.environ['POSABIT_MENU_FEED_KEY']               = '<bothell-uuid>'  # default / Bothell
#   os.environ['POSABIT_MENU_FEED_KEY_AGT_BOTHELL']   = '<bothell-uuid>'
#   os.environ['POSABIT_MENU_FEED_KEY_AGT_BURIEN']    = '<burien-uuid>'
#   os.environ['POSABIT_MENU_FEED_KEY_AGT_GOLDBAR']   = '<goldbar-uuid>'
#   os.environ['POSABIT_MENU_FEED_KEY_AGT_LYNNWOOD']  = '<lynnwood-uuid>'
#   os.environ['POSABIT_MENU_FEED_KEY_AGT_SEATTLE']   = '<seattle-uuid>'
#   os.environ['POSABIT_MENU_FEED_KEY_AGT_SHORELINE'] = '<shoreline-uuid>'
#   os.environ['POSABIT_MENU_FEED_KEY_AGT_WALLA_WALLA'] = '<walla-walla-uuid>'
#
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Logging — keep it quiet in production
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(stream=sys.__stderr__)]
)
for _lib in ['werkzeug', 'urllib3', 'requests', 'pandas', 'openpyxl', 'xlrd']:
    logging.getLogger(_lib).setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# Load Flask application
# ---------------------------------------------------------------------------
try:
    from app import app as application

    application.config.update(
        DEBUG=False,
        TESTING=False,
        TEMPLATES_AUTO_RELOAD=False,
        SEND_FILE_MAX_AGE_DEFAULT=31536000,   # 1 year cache for static files
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50 MB max upload
        JSON_SORT_KEYS=False,
        JSONIFY_PRETTYPRINT_REGULAR=False,
    )

    logging.info("WSGI application loaded successfully")

except ImportError as e:
    logging.error(f"Failed to import Flask app: {e}")
    logging.error(f"Python path: {sys.path}")
    logging.error(f"Working directory: {os.getcwd()}")
    if os.path.exists('.'):
        logging.error(f"Directory contents: {os.listdir('.')}")
    raise
except Exception as e:
    logging.error(f"Error configuring Flask app: {e}")
    raise

# ---------------------------------------------------------------------------
# Direct execution (local dev only)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    application.run(debug=False)
