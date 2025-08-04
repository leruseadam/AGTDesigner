# PythonAnywhere Excel File Loading Fix

## Overview
This document provides solutions for Excel file loading issues on PythonAnywhere, including optimizations, diagnostics, and fixes.

## Key Improvements Made

### 1. Enhanced ExcelProcessor.load_file() Method
- **File Validation**: Added comprehensive file existence, size, and permission checks
- **Memory Management**: Implemented chunked reading for large files (>10MB)
- **Multiple Excel Engines**: Fallback from openpyxl to xlrd for better compatibility
- **Memory Optimization**: Automatic garbage collection and categorical data types
- **Error Handling**: Detailed error logging and graceful failure recovery

### 2. PythonAnywhere-Specific Configuration
- **File Size Limits**: 50MB maximum file size for PythonAnywhere
- **Memory Monitoring**: Optional psutil integration for memory tracking
- **Optimized Settings**: Environment-specific configurations
- **Cache Management**: Reduced cache size for PythonAnywhere constraints

### 3. Diagnostic Tools
- **Test Script**: `test_pythonanywhere_file_loading.py` for comprehensive diagnostics
- **Environment Detection**: Automatic PythonAnywhere detection
- **File Path Testing**: Validation of common file locations
- **Library Testing**: Excel library availability and functionality tests

## Common Issues and Solutions

### Issue 1: File Not Found
**Symptoms**: "File does not exist" or "No default file found"
**Solutions**:
1. Run the diagnostic test: `./run_pythonanywhere_test.sh`
2. Check file locations: `~/Downloads/` and `./uploads/`
3. Upload files manually through the web interface
4. Use the generated test file if no files are available

### Issue 2: Memory Errors
**Symptoms**: MemoryError or "File too large" errors
**Solutions**:
1. Files are automatically chunked if >10MB
2. Memory usage is monitored and logged
3. Garbage collection is forced after file loading
4. Consider splitting large files into smaller ones

### Issue 3: Excel Engine Errors
**Symptoms**: "Failed to read with openpyxl" errors
**Solutions**:
1. Multiple engines are tried automatically (openpyxl → xlrd)
2. File format validation is performed
3. Check file corruption with the diagnostic script

### Issue 4: Permission Errors
**Symptoms**: "File not readable" or access denied
**Solutions**:
1. Check file permissions with the diagnostic script
2. Ensure uploads directory exists and is writable
3. Verify file ownership and access rights

## Usage Instructions

### 1. Run Diagnostics
```bash
# Make script executable (if needed)
chmod +x run_pythonanywhere_test.sh

# Run comprehensive diagnostics
./run_pythonanywhere_test.sh
```

### 2. Check Logs
- **Test Log**: `pythonanywhere_test.log`
- **Application Logs**: `logs/` directory
- **Console Output**: Real-time diagnostic information

### 3. Upload Files
1. Use the web interface to upload Excel files
2. Files are automatically validated and optimized
3. Check the uploads directory for processed files

### 4. Monitor Performance
- Memory usage is logged during file loading
- Load times are measured and reported
- File sizes and row counts are displayed

## Configuration Options

### Environment Detection
The system automatically detects PythonAnywhere and applies appropriate settings:
- Reduced file size limits
- Memory optimization
- Chunked file reading
- Enhanced error handling

### Manual Configuration
Edit `config_pythonanywhere.py` to customize settings:
```python
# File size limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
CHUNK_SIZE = 1000  # Rows per chunk

# Memory settings
ENABLE_MEMORY_MONITORING = True
FORCE_GARBAGE_COLLECTION = True
```

## Troubleshooting Steps

### Step 1: Run Diagnostics
```bash
./run_pythonanywhere_test.sh
```

### Step 2: Check Environment
- Verify PythonAnywhere detection
- Check available memory and disk space
- Validate file paths and permissions

### Step 3: Test File Loading
- Look for Excel files in common locations
- Test with generated sample file
- Monitor memory usage during loading

### Step 4: Review Logs
- Check for specific error messages
- Verify file sizes and formats
- Monitor performance metrics

### Step 5: Manual Upload
- Use web interface to upload files
- Check upload directory for processed files
- Verify file loading through the application

## Performance Optimizations

### Memory Management
- Automatic garbage collection
- Categorical data types for string columns
- Chunked reading for large files
- Memory usage monitoring

### File Processing
- Multiple Excel engine support
- File validation and error recovery
- Optimized data type handling
- Efficient caching strategies

### Error Recovery
- Graceful failure handling
- Detailed error logging
- Automatic retry mechanisms
- Fallback options for different scenarios

## Support

If you continue to experience issues:

1. **Run the diagnostic script** and share the log files
2. **Check the console output** for specific error messages
3. **Verify file formats** and sizes
4. **Test with the generated sample file**
5. **Monitor memory usage** during file loading

The enhanced file loading system should handle most PythonAnywhere-specific issues automatically, but the diagnostic tools will help identify any remaining problems. 