# WSGI Performance Optimization Guide

## Overview

This guide explains the performance optimizations implemented in the WSGI configuration to reduce startup time from 58 seconds to under 10 seconds on PythonAnywhere.

## Problem Identified

The original WSGI configuration was causing slow startup times due to:

1. **Default file loading during startup** - The `get_default_upload_file()` function was searching through multiple directories and processing Excel files during app initialization
2. **Verbose logging** - Too many log messages were being generated during startup
3. **Synchronous Excel processing** - Excel files were being loaded and processed immediately when the app started
4. **No lazy loading** - All components were initialized at startup instead of on-demand

## Solutions Implemented

### 1. Environment Variable Controls

Added environment variables to control startup behavior:

```python
# Disable default file loading during startup
os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'True'
os.environ['LAZY_LOADING_ENABLED'] = 'True'
```

### 2. Optimized WSGI Configuration (`wsgi_pythonanywhere.py`)

**Key Changes:**
- Reduced logging level from `WARNING` to `ERROR`
- Added suppression for verbose libraries (pandas, openpyxl, xlrd)
- Added performance-focused Flask configuration
- Implemented proper error handling for imports

**Performance Optimizations:**
```python
# Additional performance optimizations
app.config['JSON_SORT_KEYS'] = False  # Disable JSON sorting
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Disable pretty printing
```

### 3. Lazy Loading Implementation

Modified `get_excel_processor()` function to:
- Check for `LAZY_LOADING_ENABLED` environment variable
- Skip default file loading when lazy loading is enabled
- Create empty DataFrame initially, load data only when needed

### 4. Default File Loading Control

Modified `get_default_upload_file()` function to:
- Check for `DISABLE_DEFAULT_FILE_LOADING` environment variable
- Return `None` immediately when disabled
- Skip all file system operations during startup

## Files Modified

1. **`wsgi_pythonanywhere.py`** - Main WSGI configuration with performance optimizations
2. **`src/core/data/excel_processor.py`** - Added environment variable check in `get_default_upload_file()`
3. **`app.py`** - Modified `get_excel_processor()` to implement lazy loading

## Testing

Use the test script to verify optimizations:

```bash
python test_wsgi_performance.py
```

This script tests:
- WSGI import performance
- Default file loading disable functionality
- Lazy loading implementation

## Deployment Steps

### 1. Update WSGI File on PythonAnywhere

1. Upload the optimized `wsgi_pythonanywhere.py` to your PythonAnywhere account
2. Ensure the file path in the WSGI configuration matches your actual project location
3. Update the domain name if needed

### 2. Reload Web App

1. Go to your PythonAnywhere dashboard
2. Navigate to the Web tab
3. Click "Reload" for your web app
4. Monitor the logs for startup time improvement

### 3. Verify Performance

Check the logs for:
- Reduced startup time (should be under 10 seconds)
- "Lazy loading enabled" message
- "Default file loading disabled" message
- No file searching during startup

## Expected Results

**Before Optimization:**
- Startup time: ~58 seconds
- Verbose logging during startup
- File system searches during initialization
- Excel processing during startup

**After Optimization:**
- Startup time: <10 seconds
- Minimal logging during startup
- No file system operations during startup
- Lazy loading of Excel data

## Monitoring and Maintenance

### Performance Monitoring

1. **Check startup logs** - Monitor the time between "WSGI app ready" messages
2. **Monitor memory usage** - Lazy loading should reduce initial memory footprint
3. **Track user experience** - First page load should be faster

### Troubleshooting

**If startup is still slow:**
1. Check if environment variables are set correctly
2. Verify that `DISABLE_DEFAULT_FILE_LOADING` is set to 'True'
3. Ensure `LAZY_LOADING_ENABLED` is set to 'True'
4. Check for any remaining file system operations in startup code

**If functionality is broken:**
1. Verify that lazy loading is working correctly
2. Check that Excel files can still be loaded when needed
3. Ensure all API endpoints still function properly

## Rollback Plan

If issues arise, you can quickly rollback by:

1. **Disable optimizations temporarily:**
   ```python
   os.environ['DISABLE_DEFAULT_FILE_LOADING'] = 'False'
   os.environ['LAZY_LOADING_ENABLED'] = 'False'
   ```

2. **Use the original WSGI configuration** if needed

3. **Reload the web app** to apply changes

## Future Optimizations

Consider these additional optimizations:

1. **Database connection pooling** - For better database performance
2. **Static file caching** - For faster asset loading
3. **Background task processing** - For non-critical operations
4. **Memory optimization** - For large Excel file handling

## Support

If you encounter issues with the performance optimizations:

1. Check the PythonAnywhere error logs
2. Run the test script locally to verify functionality
3. Review the environment variable settings
4. Monitor the application logs for specific error messages 