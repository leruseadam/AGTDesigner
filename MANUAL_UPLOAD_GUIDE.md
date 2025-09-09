# Manual Database Upload Guide

## Files Ready for Upload

The following compressed database archive has been created for manual upload:

- **File**: `manual_database_upload_20250908_125200.tar.gz`
- **Size**: ~28 MB (compressed)
- **Contents**: 
  - `product_database.db` (main database)
  - `product_database/` directory (Excel files and backups)

## Manual Upload Options

### Option 1: PythonAnywhere File Manager (Recommended)

1. **Log into PythonAnywhere**:
   - Go to https://www.pythonanywhere.com
   - Log in with your credentials

2. **Open File Manager**:
   - Click on "Files" tab
   - Navigate to `/home/adamcordova/AGTDesigner/`

3. **Upload the Archive**:
   - Click "Upload a file" button
   - Select `manual_database_upload_20250908_125200.tar.gz`
   - Wait for upload to complete

4. **Extract the Archive**:
   - Open a Bash console in PythonAnywhere
   - Run: `cd /home/adamcordova/AGTDesigner`
   - Run: `tar -xzf manual_database_upload_20250908_125200.tar.gz`
   - Run: `rm manual_database_upload_20250908_125200.tar.gz` (cleanup)

5. **Restart Web App**:
   - Go to "Web" tab in PythonAnywhere
   - Click "Reload" button to restart your web app

### Option 2: SSH Upload (If you have SSH access)

1. **Upload via SCP**:
   ```bash
   scp manual_database_upload_20250908_125200.tar.gz adamcordova@ssh.pythonanywhere.com:/home/adamcordova/AGTDesigner/
   ```

2. **Extract on Server**:
   ```bash
   ssh adamcordova@ssh.pythonanywhere.com
   cd /home/adamcordova/AGTDesigner
   tar -xzf manual_database_upload_20250908_125200.tar.gz
   rm manual_database_upload_20250908_125200.tar.gz
   ```

3. **Restart Web App**:
   - Go to PythonAnywhere "Web" tab
   - Click "Reload" button

### Option 3: Web Interface Upload (Alternative)

If the archive is still too large for web upload, you can:

1. **Upload Individual Files**:
   - Upload `product_database.db` directly
   - Upload Excel files from `uploads/product_database/` one by one

2. **Use the Database Upload Endpoint**:
   - Go to your web app
   - Use the database upload feature in the web interface
   - Upload the main database file

## Verification

After upload, verify the database is working:

1. **Check Web App**:
   - Visit your web application
   - Try to load products or use the database features
   - Check if data appears correctly

2. **Check File Sizes**:
   - Verify `product_database.db` exists and has the correct size
   - Check that Excel files are in the `uploads/product_database/` directory

## Troubleshooting

If the upload fails:

1. **File Size Issues**:
   - The archive is ~28MB, which should work with most upload methods
   - If still too large, try uploading individual files

2. **Permission Issues**:
   - Make sure you have write permissions in the target directory
   - Check that the web app can access the database file

3. **Database Lock Issues**:
   - Restart the web app after upload
   - Check that no other processes are using the database

## File Locations

After successful upload, files should be located at:
- `/home/adamcordova/AGTDesigner/product_database.db`
- `/home/adamcordova/AGTDesigner/uploads/product_database/`

The web application should automatically detect and use these files.
