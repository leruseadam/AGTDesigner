# LabelMaker - PythonAnywhere Deployment

This is a clean deployment package for PythonAnywhere.

## Quick Setup

1. Upload all files to your PythonAnywhere account
2. Install dependencies: `pip3.10 install --user -r requirements.txt`
3. Set up web app to point to `app.py`
4. The database is included and ready to use

## Files Included

- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `src/` - Source code directory
- `static/` - Static files (CSS, JS, images)
- `templates/` - HTML templates
- `product_database.db` - SQLite database with all product data
- Excel database files - Product data sources

## Database

The SQLite database (`product_database.db`) is included and contains all your product data.
No additional database setup is required.

## Web App Configuration

1. Go to Web tab in PythonAnywhere dashboard
2. Add new web app → Manual configuration
3. Python 3.10
4. Source code: `/home/yourusername/pythonanywhere_deployment/`
5. WSGI file: `/home/yourusername/pythonanywhere_deployment/app.py`

## Notes

- Sessions directory will be created automatically
- All temporary files are excluded
- This deployment matches your local version exactly
- No environment variables required
