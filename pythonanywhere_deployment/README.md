# PythonAnywhere Deployment

This is a clean deployment package for PythonAnywhere.

## Setup Instructions

1. Upload all files to your PythonAnywhere account
2. Install dependencies: `pip3.10 install --user -r requirements.txt`
3. Set up the web app to point to app.py
4. The database is included and ready to use

## Files Included

- app.py (main application)
- requirements.txt (dependencies)
- src/ (source code)
- static/ (static files)
- templates/ (HTML templates)
- product_database.db (SQLite database)
- Excel database files
- README.md (this file)

## Database

The SQLite database is included and contains all product data.
No additional database setup is required.

## Notes

- Sessions directory will be created automatically
- All temporary files are excluded
- This deployment matches the local version exactly
