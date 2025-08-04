# PythonAnywhere Default File Loading Fix

## Problem Description
The PythonAnywhere version of the Label Maker application is not loading the most recent default file on startup. This prevents users from seeing the current inventory data when they first access the application.

## Root Cause Analysis

### 1. File Location Differences
- **Local Environment**: Files are stored in `~/Downloads/` and found easily
- **PythonAnywhere**: Files may be in different locations due to the server environment structure

### 2. PythonAnywhere Environment Detection
The original code had limited PythonAnywhere detection, which could cause the application to miss PythonAnywhere-specific file paths.

### 3. File Path Variations
PythonAnywhere can have different directory structures:
- `/home/adamcordova/uploads/`
- `/home/adamcordova/AGTDesigner/uploads/`
- `/home/adamcordova/AGTDesigner/AGTDesigner/uploads/`
- `/home/adamcordova/Downloads/`

## Solutions Implemented

### 1. Enhanced PythonAnywhere Detection
```python
# Enhanced PythonAnywhere detection
is_pythonanywhere = (
    os.path.exists("/home/adamcordova") or
    'PYTHONANYWHERE_SITE' in os.environ or
    'PYTHONANYWHERE_DOMAIN' in os.environ or
    os.path.exists('/var/log/pythonanywhere') or
    'pythonanywhere.com' in os.environ.get('HTTP_HOST', '') or
    "pythonanywhere" in current_dir.lower()
)
```

### 2. Expanded Search Locations
Added more PythonAnywhere-specific search paths:
```python
pythonanywhere_paths = [
    "/home/adamcordova/uploads",
    "/home/adamcordova/AGTDesigner/uploads",
    "/home/adamcordova/AGTDesigner/AGTDesigner/uploads",
    "/home/adamcordova/Downloads",
    "/home/adamcordova/AGTDesigner",
    "/home/adamcordova/AGTDesigner/AGTDesigner",
]
```

### 3. Enhanced Logging
Added detailed logging to track file discovery:
- File size information
- Modification timestamps
- Search location status
- Error handling for inaccessible directories

## Diagnostic Tools Created

### 1. `debug_pythonanywhere_default_file.py`
Comprehensive diagnostic script that:
- Checks PythonAnywhere environment detection
- Searches all possible file locations
- Tests file permissions
- Attempts to load files with ExcelProcessor
- Provides detailed output for troubleshooting

### 2. `upload_latest_to_pythonanywhere.py`
Automated upload script that:
- Finds the most recent AGT file locally
- Uploads it to PythonAnywhere using SCP
- Verifies the upload was successful

### 3. `run_pythonanywhere_diagnostic.sh`
Shell script that:
- Uploads the diagnostic script to PythonAnywhere
- Runs the diagnostic remotely
- Provides easy one-command troubleshooting

## Usage Instructions

### Option 1: Run Diagnostic (Recommended)
```bash
./run_pythonanywhere_diagnostic.sh
```

### Option 2: Upload Latest File
```bash
python3 upload_latest_to_pythonanywhere.py
```

### Option 3: Manual Diagnostic
```bash
# Upload diagnostic script
scp debug_pythonanywhere_default_file.py adamcordova@ssh.pythonanywhere.com:/home/adamcordova/AGTDesigner/

# Run diagnostic
ssh adamcordova@ssh.pythonanywhere.com "cd /home/adamcordova/AGTDesigner && python3 debug_pythonanywhere_default_file.py"
```

## Expected Results

After implementing these fixes:

1. **Enhanced Detection**: The application will properly detect when running on PythonAnywhere
2. **Comprehensive Search**: All possible file locations will be searched
3. **Better Logging**: Detailed logs will help identify any remaining issues
4. **Automatic Upload**: Latest files can be easily uploaded to PythonAnywhere

## Troubleshooting

### If No Files Are Found:
1. Run the diagnostic script to see what locations are being searched
2. Check if files exist in the expected locations
3. Use the upload script to transfer the latest file
4. Verify file permissions on PythonAnywhere

### If Files Are Found But Not Loading:
1. Check file permissions (readable by the web app user)
2. Verify file format (must be .xlsx)
3. Check file size (should be under 50MB for PythonAnywhere)
4. Review application logs for loading errors

### If Upload Fails:
1. Verify SSH access to PythonAnywhere
2. Check that the uploads directory exists
3. Ensure sufficient disk space on PythonAnywhere
4. Verify file permissions on the target directory

## Files Modified

1. **`src/core/data/excel_processor.py`**
   - Enhanced `get_default_upload_file()` function
   - Improved PythonAnywhere detection
   - Added more search locations
   - Enhanced logging and error handling

2. **`debug_pythonanywhere_default_file.py`** (New)
   - Comprehensive diagnostic script

3. **`upload_latest_to_pythonanywhere.py`** (New)
   - Automated file upload script

4. **`run_pythonanywhere_diagnostic.sh`** (New)
   - One-command diagnostic runner

## Next Steps

1. **Deploy the fixes** to PythonAnywhere
2. **Run the diagnostic** to verify the current state
3. **Upload the latest file** if needed
4. **Restart the web app** to load the new default file
5. **Monitor the logs** to ensure proper loading

## Verification

After deployment, verify the fix by:
1. Checking the application logs for successful file loading
2. Confirming the default file list appears in the UI
3. Verifying the file timestamp matches the most recent upload
4. Testing that new file uploads work correctly 