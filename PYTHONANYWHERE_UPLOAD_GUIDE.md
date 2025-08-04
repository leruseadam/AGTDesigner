# PythonAnywhere File Upload Guide

## Automatic Method (Recommended)
1. Place Excel files in your Downloads folder
2. Run the file monitor: `python file_monitor.py`
3. Files will be automatically copied to the uploads directory

## Manual Method
1. Upload files directly through the web interface
2. Files will be stored in the uploads directory automatically

## Troubleshooting
- If files aren't loading, check the uploads directory: `ls uploads/`
- Ensure files have .xlsx or .xls extensions
- Check file permissions and size limits
- Use the diagnostic script: `python tests/test_pythonanywhere_file_loading.py`

## File Locations
- Downloads: ~/Downloads/
- Uploads: ./uploads/
- Backups: ./backup/
